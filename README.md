# DVWS Pentesting - Session Complète

## 📋 Résumé de la Session

Cette session de pentesting a été réalisée sur le site DVWS (Damn Vulnerable Web Service) à l'adresse `http://10.0.1.10:5780/website/`.

## 🎯 Objectifs Atteints

### 1. **Crack de Mot de Passe**
- **Cible** : Utilisateur `admin` sur la page de login
- **Méthode** : Brute force avec wordlist rockyou.txt
- **Résultat** : Mot de passe trouvé : `canyouletmein`
- **Script** : `password_cracker_mein.py`

### 2. **Injection de Commandes**
- **Vulnérabilité** : Command Injection sur `/vulnerabilities/exec/`
- **Technique** : Utilisation du pipe (`|`) pour chaîner les commandes
- **Commandes testées** : `whoami`, `hostname`, `wc -l /etc/passwd`
- **Script** : `command_injection_simple.py`

### 3. **Découverte de Flag**
- **Fichier** : `/var/www/DVWS/website/index.php`
- **Flag trouvé** : `SC01{Retour_aux_sources}`
- **Méthode** : Injection de commandes pour lire le fichier source
- **Script** : `find_flag.py`

### 4. **Analyse des Permissions**
- **Utilisateur** : `www-data` (UID: 33)
- **Permissions** : Limitées aux fichiers web uniquement
- **Accès sudo** : Aucun
- **Scripts** : `check_permissions.py`, `simple_reverse_shell.py`, `netcat_reverse_shell.py`

## 📁 Structure du Projet

```
dvws_pentesting/
├── scripts/                    # Scripts Python utilisés
│   ├── password_cracker_mein.py
│   ├── command_injection_simple.py
│   ├── count_passwd_lines.py
│   ├── find_flag.py
│   ├── check_permissions.py
│   ├── simple_reverse_shell.py
│   └── netcat_reverse_shell.py
├── results/                    # Résultats et captures
├── docs/                      # Documentation
└── README.md                  # Ce fichier
```

## 🔧 Scripts Développés

### 1. **password_cracker_mein.py**
- **Fonction** : Brute force du mot de passe admin
- **Fonctionnalités** :
  - Gestion des tokens CSRF
  - Filtrage des mots de passe contenant "mein"
  - Gestion des erreurs d'encodage
  - Détection précise des échecs de connexion

### 2. **command_injection_simple.py**
- **Fonction** : Test d'injection de commandes
- **Fonctionnalités** :
  - Connexion automatique
  - Injection via pipe (`|`)
  - Exécution de commandes système
  - Extraction des résultats

### 3. **count_passwd_lines.py**
- **Fonction** : Compter les lignes de `/etc/passwd`
- **Résultat** : 30 lignes confirmées

### 4. **find_flag.py**
- **Fonction** : Recherche de flags dans le code source
- **Résultat** : Flag `SC01{Retour_aux_sources}` trouvé

### 5. **check_permissions.py**
- **Fonction** : Analyse complète des permissions utilisateur
- **Informations collectées** :
  - Utilisateur actuel et groupes
  - Permissions sudo
  - Accès aux répertoires système
  - Processus en cours

### 6. **simple_reverse_shell.py**
- **Fonction** : Tentative de reverse shell
- **Méthode** : Injection de commandes pour shell interactif

### 7. **netcat_reverse_shell.py**
- **Fonction** : Reverse shell avec netcat
- **Fonctionnalités** :
  - Listener netcat
  - Multiple méthodes de reverse shell
  - Analyse des permissions en parallèle

## 🛡️ Vulnérabilités Identifiées

1. **Weak Authentication**
   - Mot de passe faible (`canyouletmein`)
   - Pas de protection contre le brute force

2. **Command Injection**
   - Injection directe de commandes système
   - Pas de validation des entrées utilisateur
   - Utilisation du pipe pour contourner les restrictions

3. **Information Disclosure**
   - Flags cachés dans le code source
   - Accès aux fichiers système via injection

## 📊 Résultats de Sécurité

### Permissions de l'utilisateur `www-data` :
- **UID/GID** : 33/33
- **Groupes** : www-data uniquement
- **Sudo** : Aucune permission
- **Accès root** : Refusé
- **Fichiers système** : Lecture limitée
- **Fichiers web** : Accès complet

### Recommandations :
1. Implémenter une authentification forte
2. Valider et échapper toutes les entrées utilisateur
3. Utiliser des comptes de service avec permissions minimales
4. Implémenter des mécanismes de détection d'intrusion

## 🚀 Utilisation

1. **Installation des dépendances** :
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install requests beautifulsoup4
   ```

2. **Exécution des scripts** :
   ```bash
   python3 scripts/password_cracker_mein.py
   python3 scripts/command_injection_simple.py
   # etc.
   ```

## 📝 Notes Techniques

- **CSRF Protection** : Gestion des tokens CSRF pour les pages de login
- **Encoding** : Gestion des problèmes d'encodage avec `utf-8` et `errors='ignore'`
- **Error Handling** : Gestion robuste des erreurs de connexion
- **Session Management** : Utilisation de sessions persistantes

## 🎓 Apprentissages

Cette session a permis de démontrer :
- L'importance de la validation des entrées
- Les risques de l'injection de commandes
- L'efficacité des attaques par dictionnaire
- L'analyse des permissions système
- Les techniques de reverse shell

---
*Session réalisée le 9 septembre 2024*

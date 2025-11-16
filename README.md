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

## 📁 Structure du Projet

```
CyberRange_StarterPack/
├── scripts/                    # Scripts Python utilisés
│   ├── password_cracker_mein.py
│   ├── command_injection_simple.py
│   ├── count_passwd_lines.py
│   └── find_flag.py
├── results/                   # Résultats et captures
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

## 🚀 Utilisation

1. **Installation des dépendances** :
   ```bash
   cd CyberRange_StarterPack
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Exécution des scripts** :
   ```bash
   python3 scripts/password_cracker_mein.py
   python3 scripts/command_injection_simple.py
   python3 scripts/find_flag.py
   # etc.
   ```
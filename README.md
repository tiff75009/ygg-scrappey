# YGG-Scrappey 🚀

update : je viens de push une version patché.

Proxy intelligent pour YGGtorrent avec contournement Cloudflare automatique et intégration Prowlarr/Radarr/Sonarr.

## ✨ Fonctionnalités

- ✅ Contournement automatique de Cloudflare via Scrappey
- ✅ Proxy transparent pour YGGtorrent
- ✅ Intégration native avec Prowlarr
- ✅ Compatible Radarr/Sonarr via Prowlarr
- ✅ Installation automatisée
- ✅ Gestion simple des cookies

## 📋 Prérequis

- Docker et Docker Compose installés
- Un compte [Scrappey](https://scrappey.com) (clé API requise)
- Un compte YGGtorrent actif

## 🚀 Installation Rapide

```bash
# Cloner le dépôt
git clone https://github.com/votre-repo/ygg-scrappey-clean
cd ygg-scrappey-clean

# Lancer l'installation automatique
chmod +x install.sh
./install.sh
```

Le script vous guidera pour configurer :
1. Votre clé API Scrappey
2. Votre cookie YGGtorrent
3. Le proxy (optionnel)
4. L'IP du serveur

## 🔧 Installation Manuelle

### 1. Configuration

Copiez et éditez le fichier `.env` :
```bash
cp .env.example .env
nano .env
```

Remplissez les valeurs :
```env
SCRAPPEY_KEY=votre_cle_scrappey
YGG_COOKIE=cookie_complet_ygg
HTTP_PROXY=  # Optionnel
SERVER_IP=localhost  # Ou votre IP
```

### 2. Obtenir le Cookie YGG

1. Connectez-vous à YGGtorrent dans votre navigateur
2. Ouvrez les DevTools (F12)
3. Allez dans **Application** > **Cookies** > **yggtorrent**
4. Copiez TOUS ces cookies :
   - `yggxf_user`
   - `yggxf_csrf`
   - `yggxf_session`
   - `ygg_`

Format final :
```
yggxf_user=XXX; yggxf_csrf=XXX; yggxf_session=XXX; ygg_=XXX
```

### 3. Démarrage

```bash
# Construire et démarrer les services
docker-compose up -d --build

# Vérifier les logs
docker-compose logs -f
```

## 📡 Configuration Prowlarr

1. Accédez à Prowlarr : http://localhost:9696
2. **Settings** > **Indexers**
3. Cliquez sur **+**
4. Cherchez **"YGGtorrent Proxy"**
5. Ajoutez-le (aucune configuration requise)
6. Testez avec une recherche

## 🔄 Connexion à Radarr/Sonarr

### Depuis Prowlarr (Recommandé)

1. Dans Prowlarr : **Settings** > **Apps**
2. Cliquez sur **+**
3. Sélectionnez **Radarr** ou **Sonarr**
4. Configurez :
   - **Name** : Radarr/Sonarr
   - **Sync Level** : Full Sync
   - **Server** : http://radarr:7878 (ou votre URL)
   - **API Key** : (depuis Radarr/Sonarr Settings > General)
5. **Test** puis **Save**

## 🔄 Mise à jour du Cookie

Si votre cookie expire :

```bash
./update-cookie.sh
```

Ou manuellement :
```bash
# Éditez le fichier .env
nano .env
# Modifiez la ligne YGG_COOKIE=...

# Redémarrez le proxy
docker-compose restart ygg-scrappey
```

## 📂 Structure du Projet

```
ygg-scrappey-clean/
├── docker-compose.yml      # Configuration Docker
├── .env.example           # Exemple de configuration
├── install.sh             # Script d'installation
├── update-cookie.sh       # Script de mise à jour cookie
├── ygg-scrappey/
│   ├── Dockerfile        # Image du proxy
│   ├── main.py          # Code du proxy
│   └── requirements.txt # Dépendances Python
└── prowlarr/
    ├── Dockerfile       # Image Prowlarr custom
    └── init-indexer.sh  # Script d'init auto

```

## 🛠️ Commandes Utiles

```bash
# Voir les logs
docker-compose logs -f

# Logs d'un service spécifique
docker logs ygg-scrappey -f
docker logs prowlarr -f

# Redémarrer les services
docker-compose restart

# Arrêter tout
docker-compose down

# Reconstruire après modification
docker-compose up -d --build

# Test direct du proxy
curl "http://localhost:5000/engine/search?name=test&do=search"
```

## ❓ Dépannage

### "No results" dans Prowlarr

1. Cookie expiré → Utilisez `./update-cookie.sh`
2. Vérifiez les logs : `docker logs ygg-scrappey`
3. Testez directement : `curl "http://localhost:5000/engine/search?name=avatar&do=search"`

### Erreur 429 dans Radarr

1. Redémarrez Prowlarr : `docker restart prowlarr`
2. Dans Prowlarr > Settings > Indexers > YGGtorrent Proxy
3. Réduisez Query Limit et Grab Limit à 5

### Cloudflare bloque

1. Vérifiez votre clé Scrappey
2. Vérifiez le proxy HTTP si utilisé
3. Consultez les logs : `docker logs ygg-scrappey`

## 📝 Variables d'Environnement

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `SCRAPPEY_KEY` | Clé API de scrappey.com | ✅ |
| `YGG_COOKIE` | Cookie complet YGGtorrent | ✅ |
| `HTTP_PROXY` | Proxy HTTP (format: http://user:pass@host:port) | ❌ |
| `SERVER_IP` | IP/hostname du serveur (défaut: localhost) | ❌ |

## 🔒 Sécurité

- Ne partagez jamais votre `.env`
- Ajoutez `.env` à votre `.gitignore`
- Renouvelez régulièrement votre cookie YGG
- Utilisez un proxy pour plus d'anonymat

## 📜 License

MIT

## 🤝 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.

---

*Fait avec ❤️ pour la communauté*

#!/bin/bash
# Script d'installation automatique YGG-Scrappey

echo "╔══════════════════════════════════════════════╗"
echo "║         YGG-SCRAPPEY INSTALLATION            ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Installez Docker d'abord."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé."
    exit 1
fi

# Créer le fichier .env s'il n'existe pas
if [ ! -f .env ]; then
    echo "📝 Configuration initiale..."
    cp .env.example .env
    
    echo ""
    echo "Configuration requise:"
    echo "1. Clé API Scrappey (obtenir sur scrappey.com)"
    read -p "Entrez votre clé Scrappey: " SCRAPPEY_KEY
    
    echo ""
    echo "2. Cookie YGG (voir README pour obtenir le cookie)"
    echo "Format: yggxf_user=XXX; yggxf_csrf=XXX; yggxf_session=XXX; ygg_=XXX"
    read -p "Collez votre cookie YGG complet: " YGG_COOKIE
    
    echo ""
    echo "3. Proxy HTTP (optionnel, appuyez Enter pour passer)"
    read -p "Proxy (format: http://user:pass@host:port): " HTTP_PROXY
    
    echo ""
    echo "4. IP du serveur (défaut: localhost)"
    read -p "IP du serveur [localhost]: " SERVER_IP
    SERVER_IP=${SERVER_IP:-localhost}
    
    # Écrire le .env
    cat > .env << EOF
# Configuration YGG-Scrappey
SCRAPPEY_KEY=${SCRAPPEY_KEY}
YGG_COOKIE=${YGG_COOKIE}
HTTP_PROXY=${HTTP_PROXY}
SERVER_IP=${SERVER_IP}
EOF
    
    echo "✅ Configuration sauvegardée dans .env"
else
    echo "✅ Fichier .env détecté"
fi

# Construction des images
echo ""
echo "🔨 Construction des images Docker..."
docker-compose build --no-cache

# Démarrage des services
echo ""
echo "🚀 Démarrage des services..."
docker-compose up -d

# Attente du démarrage
echo ""
echo "⏳ Attente du démarrage des services (30 secondes)..."
sleep 30

# Test de connexion
echo ""
echo "🧪 Test de connexion..."
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/" | grep -q "200"; then
    echo "✅ Proxy YGG actif sur http://localhost:5000"
else
    echo "⚠️ Le proxy ne répond pas correctement"
fi

if curl -s -o /dev/null -w "%{http_code}" "http://localhost:9696/" | grep -q "200"; then
    echo "✅ Prowlarr actif sur http://localhost:9696"
else
    echo "⚠️ Prowlarr ne répond pas correctement"
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║         INSTALLATION TERMINÉE !              ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "📌 Prochaines étapes:"
echo ""
echo "1. Accédez à Prowlarr: http://localhost:9696"
echo "2. Settings > Indexers"
echo "3. Cliquez sur +"
echo "4. Cherchez 'YGGtorrent Proxy'"
echo "5. Ajoutez-le (pas de configuration nécessaire)"
echo "6. Testez avec une recherche"
echo ""
echo "7. Pour connecter à Radarr/Sonarr:"
echo "   Settings > Apps > Add > Radarr/Sonarr"
echo ""
echo "📖 Commandes utiles:"
echo "   docker-compose logs -f        # Voir les logs"
echo "   docker-compose restart        # Redémarrer"
echo "   docker-compose down           # Arrêter"
echo "   ./update-cookie.sh            # Mettre à jour le cookie YGG"
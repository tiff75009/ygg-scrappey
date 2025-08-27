#!/bin/bash
# Script pour mettre à jour le cookie YGG

echo "╔══════════════════════════════════════════════╗"
echo "║      MISE À JOUR DU COOKIE YGG              ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

echo "📋 Pour obtenir votre cookie YGG:"
echo "1. Connectez-vous à YGGtorrent dans votre navigateur"
echo "2. Ouvrez les DevTools (F12)"
echo "3. Allez dans Application/Storage > Cookies > yggtorrent"
echo "4. Copiez TOUTES ces valeurs:"
echo "   - yggxf_user"
echo "   - yggxf_csrf"
echo "   - yggxf_session"
echo "   - ygg_"
echo ""
echo "Format: cookie1=value1; cookie2=value2; cookie3=value3"
echo ""
echo "📝 Collez votre nouveau cookie complet:"
read -r NEW_COOKIE

# Mettre à jour le .env
if [ -f .env ]; then
    # Sauvegarder
    cp .env .env.bak
    
    # Mettre à jour le cookie
    sed -i.tmp '/^YGG_COOKIE=/d' .env
    echo "YGG_COOKIE=${NEW_COOKIE}" >> .env
    rm -f .env.tmp
    
    echo ""
    echo "✅ Cookie mis à jour dans .env"
else
    echo "❌ Fichier .env non trouvé!"
    exit 1
fi

# Redémarrer le proxy
echo ""
echo "🔄 Redémarrage du proxy..."
docker-compose stop ygg-scrappey
docker-compose rm -f ygg-scrappey
docker-compose up -d ygg-scrappey

echo ""
echo "⏳ Attente du redémarrage (10 secondes)..."
sleep 10

# Test
echo ""
echo "🧪 Test de connexion..."
RESULTS=$(curl -s "http://localhost:5000/engine/search?name=test&do=search" | grep -c "/torrent/")

if [ "$RESULTS" -gt 0 ]; then
    echo "✅ Cookie valide - $RESULTS torrents trouvés!"
    echo ""
    echo "📌 Testez maintenant dans Prowlarr"
else
    echo "⚠️ Aucun résultat trouvé"
    echo "Le cookie est peut-être invalide ou expiré"
fi
@echo off
echo ╔══════════════════════════════════════════════╗
echo ║         PUSH VERS GITHUB                     ║
echo ╚══════════════════════════════════════════════╝
echo.

REM Initialiser Git si nécessaire
if not exist .git (
    echo 📦 Initialisation du repository Git...
    git init
    git branch -M main
)

REM Ajouter le remote
echo 🔗 Configuration du remote GitHub...
git remote remove origin 2>nul
git remote add origin https://github.com/tiff75009/ygg-scrappey.git

REM Ajouter tous les fichiers
echo 📝 Ajout des fichiers...
git add .

REM Créer le commit
echo 💾 Création du commit...
git commit -m "🚀 Version propre et fonctionnelle de YGG-Scrappey" -m "" -m "✨ Fonctionnalités:" -m "- Proxy intelligent pour YGGtorrent avec contournement Cloudflare" -m "- Intégration automatique avec Prowlarr" -m "- Compatible Radarr/Sonarr via Prowlarr" -m "- Installation automatisée avec script interactif" -m "- Gestion simple des cookies YGG" -m "- Configuration via variables d'environnement (.env)" -m "" -m "📦 Structure:" -m "- Docker Compose pour orchestration" -m "- Script d'installation automatique" -m "- Script de mise à jour du cookie" -m "- Documentation complète" -m "- Code optimisé et commenté" -m "" -m "🔧 Installation simple:" -m "chmod +x install.sh && ./install.sh"

REM Pousser vers GitHub
echo.
echo 🚀 Push vers GitHub...
set /p FORCE="Voulez-vous forcer le push? (écrasera le contenu existant) [y/N]: "

if /i "%FORCE%"=="y" (
    git push -f origin main
    echo ✅ Push forcé effectué!
) else (
    git push origin main
    if errorlevel 1 (
        echo.
        echo ⚠️  Le push a échoué. Probablement du contenu existant sur GitHub.
        echo.
        echo Options:
        echo 1. Forcer le push écrase tout : git push -f origin main
        echo 2. Pull puis merge : git pull origin main --allow-unrelated-histories
        echo 3. Créer une nouvelle branche : git push origin main:nouvelle-version
    )
)

echo.
echo 📌 URL du repository: https://github.com/tiff75009/ygg-scrappey
echo.
echo Pour cloner ailleurs:
echo git clone https://github.com/tiff75009/ygg-scrappey.git
echo.
pause
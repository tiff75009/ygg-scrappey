FROM linuxserver/prowlarr:latest

# Installer wget et curl pour le script d'init
RUN apk add --no-cache wget curl

# Copier le script d'initialisation
COPY prowlarr/init-indexer.sh /custom-cont-init.d/99-ygg-setup.sh

# Rendre le script exécutable
RUN chmod +x /custom-cont-init.d/99-ygg-setup.sh
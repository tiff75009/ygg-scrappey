FROM linuxserver/prowlarr:latest

# Copier le script d'initialisation
COPY prowlarr/init-prowlarr.sh /init-prowlarr.sh

# Rendre le script exécutable
RUN chmod +x /init-prowlarr.sh

# Modifier l'entrée par défaut pour exécuter notre script
ENTRYPOINT ["/init-prowlarr.sh"]

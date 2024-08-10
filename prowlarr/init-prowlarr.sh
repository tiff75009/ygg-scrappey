#!/bin/bash

# Fonction pour modifier le fichier yggcookie.yml
modify_yggcookie() {
    local file="/config/Definitions/yggcookie.yml"
    local custom_file="/config/Definitions/Custom/yggcookie-custom.yml"

    # Attendre que le fichier yggcookie.yml soit créé
    while [ ! -f "$file" ]
    do
        echo "Attente de la création du fichier yggcookie.yml..."
        sleep 5
    done

    # Créer le dossier Custom s'il n'existe pas
    mkdir -p /config/Definitions/Custom

    # Copier et modifier le fichier yggcookie.yml
    sed -e 's|id: yggcookie|id: yggcustom|g' \
        -e 's|name: YGG cookie|name: YGG cookie custom|g' \
        -e "s|https://www.ygg.re|http://${SERVER_IP}:5000|g" \
        "$file" > "$custom_file"

    # Donner les bonnes permissions au fichier
    chown abc:abc "$custom_file"

    echo "Fichier yggcookie-custom.yml créé et modifié dans le dossier Custom."
}

# Exécuter la fonction de modification en arrière-plan
modify_yggcookie &

# Exécuter le script d'initialisation original de Prowlarr
exec /init

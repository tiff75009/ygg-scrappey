# YGG-Scrappey avec Prowlarr

   Ce projet combine YGG-Scrappey, un proxy pour YGG, avec Prowlarr pour faciliter l'accès aux torrents YGG tout en contournant les protections anti-bot.

   ## Prérequis

   - Docker
   - Docker Compose

   ## Installation

   1. Clonez ce dépôt :
      ```
      git clone https://github.com/votre-nom-utilisateur/ygg-scrappey-prowlarr.git
      cd ygg-scrappey-prowlarr
      ```

   2. Copiez le fichier `docker-compose.yml.example` en `docker-compose.yml` et modifiez-le pour configurer vos variables d'environnement :
      ```
      cp docker-compose.yml.example docker-compose.yml
      ```
      Modifiez les valeurs suivantes dans `docker-compose.yml` :
      - `SCRAPPEY_KEY`: Votre clé API Scrappey
      - `YGG_COOKIE`: Votre cookie YGG
      - `HTTP_PROXY`: Votre proxy HTTP (si nécessaire)
      - `SERVER_IP`: L'adresse IP de votre serveur

   3. Lancez les conteneurs :
      ```
      docker-compose up -d
      ```

   ## Configuration de Prowlarr

   1. Accédez à l'interface web de Prowlarr (http://votre-ip:9696).
   2. Allez dans "Indexers" > "Add Indexer".
   3. Recherchez "YGG cookie custom" dans la liste.
   4. Configurez-le en utilisant l'URL `http://ygg-scrappey:5000`.

   ## Mise à jour

   Pour mettre à jour les conteneurs, exécutez :
   ```
   docker-compose pull
   docker-compose up -d
   ```

   ## Avertissement

   Ce projet est fourni à des fins éducatives et de recherche uniquement. Assurez-vous de respecter les conditions d'utilisation de YGG et les lois en vigueur dans votre pays.

   ## Licence

   Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
   
# YGG-Scrappey avec Prowlarr

Ce projet combine YGG-Scrappey, un proxy pour YGG, avec Prowlarr pour faciliter l'accès aux torrents YGG tout en contournant les protections anti-bot.

## Prérequis

- Docker
- Docker Compose
- Un serveur avec Squid Proxy (voir la section Installation de Squid)
- Une clé API Scrappey (https://scrappey.com/)
  - Inscrivez-vous sur le site de Scrappey
  - Obtenez votre clé API dans les paramètres de votre compte
  - Cette clé est nécessaire pour contourner les protections anti-bot

## Installation

### Installation de Squid Proxy

1. Mettez à jour votre système et installez Squid :
   ```
   sudo apt update
   sudo apt install squid apache2-utils -y
   ```

2. Remplacez le contenu du fichier de configuration Squid (`/etc/squid/squid.conf`) par ce qui suit :
   ```
   auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd
   auth_param basic realm proxy
   acl authenticated proxy_auth REQUIRED
   acl localnet src 0.0.0.1-0.255.255.255  # RFC 1122 "this" network (LAN)
   acl localnet src 10.0.0.0/8             # RFC 1918 local private network (LAN)
   acl localnet src 100.64.0.0/10          # RFC 6598 shared address space (CGN)
   acl localnet src 169.254.0.0/16         # RFC 3927 link-local (directly plugged) machines
   acl localnet src 172.16.0.0/12          # RFC 1918 local private network (LAN)
   acl localnet src 192.168.0.0/16         # RFC 1918 local private network (LAN)
   acl localnet src fc00::/7               # RFC 4193 local private network range
   acl localnet src fe80::/10              # RFC 4291 link-local (directly plugged) machines
   acl SSL_ports port 443
   acl Safe_ports port 80          # http
   acl Safe_ports port 21          # ftp
   acl Safe_ports port 443         # https
   acl Safe_ports port 70          # gopher
   acl Safe_ports port 210         # wais
   acl Safe_ports port 1025-65535  # unregistered ports
   acl Safe_ports port 280         # http-mgmt
   acl Safe_ports port 488         # gss-http
   acl Safe_ports port 591         # filemaker
   acl Safe_ports port 777         # multiling http
   http_access deny !Safe_ports
   http_access deny CONNECT !SSL_ports
   http_access allow authenticated
   http_access deny all
   include /etc/squid/conf.d/*.conf
   http_port 3128
   coredump_dir /var/spool/squid
   refresh_pattern ^ftp:           1440    20%     10080
   refresh_pattern ^gopher:        1440    0%      1440
   refresh_pattern -i (/cgi-bin/|\?) 0     0%      0
   refresh_pattern .               0       20%     4320
   ```

3. Activez Squid pour qu'il démarre au boot :
   ```
   sudo systemctl enable squid
   ```

4. Configurez l'authentification du proxy Squid :
   ```
   sudo touch /etc/squid/passwd
   sudo chown proxy: /etc/squid/passwd
   sudo htpasswd /etc/squid/passwd [username]
   ```
   Remplacez `[username]` par le nom d'utilisateur que vous souhaitez utiliser pour l'authentification du proxy.

5. Redémarrez Squid :
   ```
   sudo systemctl restart squid
   ```

### Installation de YGG-Scrappey et Prowlarr

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
   - `YGG_COOKIE`: Votre cookie YGG (voir la section "Configuration du cookie YGG" ci-dessous)
   - `HTTP_PROXY`: L'URL de votre proxy Squid (ex: `http://username:password@votre_ip:3128`)
   - `SERVER_IP`: L'adresse IP de votre serveur

3. Lancez les conteneurs :
   ```
   docker-compose up -d
   ```

## Configuration du cookie YGG

Le cookie YGG est une partie cruciale de la configuration. Il permet à YGG-Scrappey de s'authentifier auprès du site YGG. Voici comment obtenir et configurer correctement le cookie :

1. Connectez-vous à votre compte YGG dans votre navigateur.

2. Ouvrez les outils de développement (F12 sur la plupart des navigateurs).

3. Allez dans l'onglet "Application" (Chrome) ou "Stockage" (Firefox).

4. Dans la section "Cookies", sélectionnez le domaine YGG.

5. Recherchez les cookies suivants :
   - `yggxf_user`
   - `v21_promo_details`
   - `ygg_`

6. Copiez la valeur de ces trois cookies et combinez-les dans le format suivant :
   ```
   yggxf_user=VALEUR; v21_promo_details=VALEUR; ygg_=VALEUR
   ```

   Par exemple :
   ```
   yggxf_user=144387%2C9fsefesWzKJPPftWSJ0uXgrdgd7XFSJ0nwSOk9uu0vaO; v21_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA4LzEwLzIwMjQgMjM6NTk6NTkiLCJ0cyI6MTcyMzMyNzE5OX0=; ygg_=p2gmfsjbhlgfrlspkmmflnrt48vb078d
   ```

7. Utilisez cette chaîne complète comme valeur pour la variable d'environnement `YGG_COOKIE` dans votre `docker-compose.yml`.

**Important** : 
- N'incluez PAS le cookie `cf_clearance` s'il est présent. Ce cookie est géré automatiquement par YGG-Scrappey.
- Assurez-vous de ne pas inclure d'espaces supplémentaires dans la chaîne de cookie.
- Le cookie est sensible et ne doit pas être partagé. Gardez-le confidentiel.

Votre cookie YGG peut expirer après un certain temps. Si vous rencontrez des problèmes de connexion, essayez de mettre à jour le cookie en suivant ces étapes à nouveau.

## Obtenir le cookie YGG et le User-Agent

Pour obtenir le cookie YGG et le User-Agent nécessaires à la configuration :

1. Connectez-vous à votre compte YGG dans votre navigateur.
2. Ouvrez les outils de développement (F12 sur la plupart des navigateurs).
3. Allez dans l'onglet "Network" (Réseau).
4. Actualisez la page YGG.
5. Dans la liste des requêtes, cliquez sur celle qui correspond à "www.ygg.re".
6. Dans les en-têtes de la requête, vous trouverez :
   - La ligne "Cookie" : c'est votre cookie YGG complet.
   - La ligne "User-Agent" : c'est votre User-Agent.

Notez ces deux informations, elles seront nécessaires pour la configuration de YGG-Scrappey et Prowlarr.

## Configuration de Prowlarr

1. Accédez à l'interface web de Prowlarr (http://votre-ip:9696).
2. Allez dans "Indexers" > "Add Indexer".
3. Recherchez "YGG cookie custom" dans la liste.
4. Dans la configuration de l'indexeur :
   - Remplissez le champ "Cookie" avec le même cookie YGG que vous avez utilisé dans la configuration de YGG-Scrappey.
   - Remplissez le champ "User-Agent" avec le User-Agent que vous avez obtenu de votre navigateur.

Ces informations permettent à Prowlarr de s'authentifier correctement auprès de YGG via YGG-Scrappey.

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
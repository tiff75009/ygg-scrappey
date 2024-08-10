# YGG-Scrappey avec Prowlarr

Ce projet combine YGG-Scrappey, un proxy pour YGG, avec Prowlarr pour faciliter l'accès aux torrents YGG tout en contournant les protections anti-bot.

## Prérequis

- Docker
- Docker Compose
- Un serveur avec Squid Proxy (voir la section Installation de Squid)

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
   - `YGG_COOKIE`: Votre cookie YGG
   - `HTTP_PROXY`: L'URL de votre proxy Squid (ex: `http://username:password@votre_ip:3128`)
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

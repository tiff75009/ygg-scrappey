#!/bin/bash
# Script d'initialisation automatique de l'indexeur YGG

echo "[init-indexer] Attente du démarrage de Prowlarr..."
sleep 20

SERVER_IP="${SERVER_IP:-localhost}"
CFG_DIR="/config/Definitions/Custom"

echo "[init-indexer] Création du dossier Custom..."
mkdir -p "$CFG_DIR"

echo "[init-indexer] Création de la définition YGG..."

cat > "${CFG_DIR}/ygg-proxy.yml" << EOF
---
id: ygg-proxy
name: YGGtorrent Proxy
description: "YGGtorrent via proxy local"
language: fr-FR
type: private
encoding: UTF-8
links:
  - http://${SERVER_IP}:5000/

caps:
  categorymappings:
    - {id: 2000, cat: Movies, desc: "Movies"}
    - {id: 5000, cat: TV, desc: "TV"}
    - {id: 3000, cat: Audio, desc: "Audio"}
    - {id: 4000, cat: PC, desc: "Games"}
    - {id: 7000, cat: Books, desc: "Books"}
    - {id: 8000, cat: Other, desc: "Other"}

  modes:
    search: [q]
    tv-search: [q]
    movie-search: [q]

settings: []

search:
  paths:
    - path: "/engine/search"
      
  inputs:
    name: "{{ .Keywords }}"
    do: "search"

  rows:
    selector: "table.table tbody tr:has(a[href*=\"/torrent/\"])"

  fields:
    title:
      selector: "td:nth-child(2) a"
      
    details:
      selector: "td:nth-child(2) a"
      attribute: href
      filters:
        - name: prepend
          args: "http://${SERVER_IP}:5000"
    
    download:
      selector: "td:nth-child(2) a"
      attribute: href
      filters:
        - name: regexp
          args: "/torrent/(\\\\d+)"
        - name: append
          args: "-dummy"
        - name: replace
          args: ["/torrent/(\\\\d+).*", "http://${SERVER_IP}:5000/engine/download_torrent?id=\$1"]
    
    size:
      selector: "td:nth-child(6)"
      filters:
        - name: replace
          args: ["o\$", "B"]
        - name: replace
          args: ["Ko", "KB"]
        - name: replace  
          args: ["Mo", "MB"]
        - name: replace
          args: ["Go", "GB"]
        - name: replace
          args: ["To", "TB"]
    
    seeders:
      selector: "td:nth-child(8)"
      filters:
        - name: regexp
          args: "(\\\\d+)"
    
    leechers:
      selector: "td:nth-child(9)"
      filters:
        - name: regexp
          args: "(\\\\d+)"
          
    category:
      text: 2000
      
    downloadvolumefactor:
      text: 1
      
    uploadvolumefactor:
      text: 1

    minimumratio:
      text: 1
      
    minimumseedtime:
      text: 172800
EOF

# Corriger les permissions
chown -R abc:abc /config

echo "[init-indexer] ✅ Définition YGG installée!"
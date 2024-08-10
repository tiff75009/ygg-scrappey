# Utiliser une image de base Python officielle
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de dépendances et d'application
COPY ygg-scrappey/requirements.txt .
COPY ygg-scrappey/main.py .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port sur lequel l'application s'exécute
EXPOSE 5000

# Commande pour exécuter l'application
CMD ["python", "main.py"]

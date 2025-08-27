FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances
COPY ygg-scrappey/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY ygg-scrappey/main.py .

# Exposer le port
EXPOSE 5000

# Lancer l'application
CMD ["python", "main.py"]
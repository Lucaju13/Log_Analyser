# Utilisation d'une image de base Python avec les outils nécessaires pour PyQt5
FROM python:3.9-slim

# Installation des dépendances nécessaires pour PyQt5
RUN apt-get update && apt-get install -y \
    python3-pyqt5 \
    python3-pyqt5.qtmultimedia \
    python3-pyqt5.qtopengl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copie le fichier requirements.txt et installez les dépendances Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copie l'application dans le conteneur
COPY . /app

# Définissez le répertoire de travail
WORKDIR /app

# Commande pour lancer l'application
CMD ["python", "effarouchement.py"]

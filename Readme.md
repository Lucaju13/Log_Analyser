# Log Analyser

## Construisez l'image Docker
docker build -t votre_application_pyqt5 .

# Exécutez le conteneur Docker
docker run -it --rm --name votre_application_en_cours d'application votre_application_pyqt5

## Remarque importante

Les applications GUI (interface graphique) ne peuvent pas être exécutées directement dans un conteneur Docker sans configurations supplémentaires, car Docker est conçu pour les applications serveur et non pour les applications avec interface utilisateur graphique. Pour les applications GUI, vous pouvez utiliser X11 forwarding ou un outil comme VNC pour afficher l'interface graphique.

Voici une façon simple de configurer X11 forwarding pour une application GUI :
Sur le système hôte (votre ordinateur), exécutez la commande suivante pour permettre à Docker d'utiliser votre affichage :

```cmd
xhost +local:docker
```

Exécutez le conteneur Docker avec les variables d'environnement nécessaires pour le forwarding X11 :

```cmd
docker run -it --rm --name votre_application_en_cours d'application -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix votre_application_pyqt5
```

Cela permettra à votre application PyQt5 de s'afficher correctement en utilisant l'affichage de votre machine hôte.

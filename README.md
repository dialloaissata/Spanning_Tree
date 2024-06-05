# Utilisation de l’environnement de développement
Deux scripts sont à utiliser pour démarrer l’environnement de développement :
• network.py mets en place le réseau virtuel
• run.py démarre les contrôleurs des commutateurs présents dans le réseau
Démarrez les deux scripts dans deux terminaux séparés, en commençant par
network.py.
Lorsque vous effectuerez des modifications, vous redémarrerez le script run.py.
Ce script possède une interface en ligne de commande vous permettant de vi-
sualiser le réseau et les états des ports, et de tester vore implémentation de
STP.
## Voici la liste des commandes disponibles :
• start : démarre les contrôleurs des switch
• stop : arête les contrôleurs des switch
• quit : arête le script
• reset : réinitialise les états et rôles des commutateurs et des ports
• info : Affiche des informations sur les contrôleurs
• draw init : Initialise les fonctions liés au dessin
• draw once : Dessine le réseau dans un fichier png
• draw start : Démarre le dessin automatique du réseau
• draw stop : Arête le dessin automatique du réseau
• priority <bridge> <prio> : Définie la priorité du commutateur bridge
• port <bridge> <port> <state> : Active ou désactive un port
• cost <bridge> <port> <cost> : Définie le coût d’un port
10

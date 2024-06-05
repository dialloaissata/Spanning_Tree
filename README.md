## Spanning Tree Protocol
### 1. Avant de commencer
Ce projet doit être rendu avec un rapport au format PDF, qui sera pris en
compte dans la notation. N’oubliez pas d’indiquer votre nom dans le rapport.
Votre code Python doit être lisible et commenté. Vous trouverez le code de base
et tous les autres fichiers nécessaires à la réalisation de ce projet sur Moodle.
Tout au long du sujet, des explications vous seront données sur certaines
spécificités liées à Python et au protocole Spanning Tree Protocol (STP). Des
pointeurs vers de la documentation vous seront données en bas de page. Bien
que leur lecture soit facultative, ils vous permettront d’approfondir vos connais-
sances.
### 2. Description rapide
Spanning Tree Protocol est un protocole distribué permettant la transformation
d’un réseau contenant des boucles de commutateurs en arborescence virtuelle.
Son fonctionnement complet est décrit dans la spécification IEEE 802.1D1 , par-
ties 8 et 9.
Un commutateur implémente le protocole STP en envoyant et en recevant
des paquets appelés Bridge Protocol Data Units (BPDU). Le contenu de ces
paquets permet au commutateur de déterminer quel port il doit désactiver ou
activer pour contribuer à la transformation de la topologie.
Le but de ce projet est d’implémenter une version simplifiée de ce protocole.
#### 2.1 Code fourni
Le code qui vous est fourni est décomposé en plusieurs dossiers :
• data contient le code du plan de données du commutateur (vous n’aurez
pas à y toucher)
• control contient le code du plan de contrôle du commutateur
• tools contient des outils qui vous aideront à réaliser ce projet
Les instructions pour la mise en place de l’environnement de développement
sont données en Annexe A, et son utilisation est expliquée en Annexe B.
1 Spécifiation IEEE 802.1D
13
Détails du protocole
Le protocole STP établie une arborescence à partir d’une topologie de réseau
contenant des circuits. Pour déterminer cette arborescence, les commutateurs
implémentant STP envoient régulièrement des paquets, nommés Bridge Protocol
Data Unit (BPDU). Ces BPDU permettent de déterminer l’état des ports des
commutateurs.
Chaque commutateur possède :
• Un identifiant, découpé en deux parties (priorité et adresse Medium Access
Control (MAC))
• Des informations spécifiques à chacun de ses ports
– l’identifiant du port
– le coût de traversée du port
– l’état du port
– le rôle du port
Un des commutateurs du réseau est élu racine. Chaque réseau possède une
racine, qui est le commutateur avec l’identifiant le plus petit.
3.1
États des ports
Les ports ont plusieurs états :
• Blocking: Le port traite des BPDU sans en émettre, et ne transmet pas
de données
• Listening, Learning: Le port émet et traite des BPDU mais ne transmet
pas de données
• Forwarding: Le port émet et traite des BPDU et transmet les données
• Disabled: Le port n’émet et ne traite pas de BPDU, et ne transmet pas
de données
Disabled
Blocking
Listening
Learning
Forwarding
Handle BPDU
No
Yes
Yes
Yes
Yes
Send BPDU
No
No
Yes
Yes
Yes
Table 1: États des ports
2
Learn
No
No
No
Yes
Yes
Forward
No
No
No
No
YesLes ports peuvent changer d’état, suite à la réception d’un BPDU ou à
l’expiration d’un temporisateur.
Listen
start
Learn
Block
Forward
Figure 1: Changement d’état des ports
Chaque commutateur stocke, en plus des informations qui lui sont propres,
l’id de la racine du réseau, et pour chaque port, en plus des informations qui lui
sont propres, le meilleur BPDU qu’il ait reçu pour ce port.
3.2
Rôles des ports
Les ports ont aussi des rôles :
• Root: Port montant vers le commutateur racine du réseau
• Designated: Port descendant, transmettant des données
• Blocked: Port bloqué, ne transmettant pas de données
• Disable: Port désactivé manuellement
3.3
Traitement d’un BPDU
Lorsqu’un commutateur reçoit un BPDU sur un port, ce BPDU est comparé
avec le BPDU déjà stocké pour ce port. Si le BPDU reçu est meilleur, il remplace
l’existant. Les états et rôles de chacun des ports est en suite recalculé.
3.4
Assignation des états et rôles des ports
Si le commutateur est la racine du réseau (c’est-à-dire que l’identifiant de la
racine qu’il stocke est égal à son identifiant) alors on génère un BPDU qui
correspond à ce que le commutateur enverrait sur ce port. Si ce BPDU est
meilleur ou égal au BPDU stocké pour le port, le port devient désigné, sinon le
port devient bloqué.
Sinon, on récupère le meilleur BPDU stocké dans les ports. Le port dont
l’identifiant est le même que l’identifiant du port du meilleur BPDU devient le
port racine. Pour les autres ports, on génère un BPDU qui correspond à ce que
3le commutateur enverrait sur ce port. Si ce BPDU est meilleur que le BPDU
stocké pour le port, le port devient désigné, sinon le port devient bloqué.
Lorsque qu’un port devient racine ou désigné, son état devient Listenning.
3.5
Émission des BPDU
Seul le commutateur racine émet continuellement des BPDU. Les autres com-
mutateur se content de relayer les BPDU qu’ils reçoivent, lorsqu’ils les reçoivent
sur leur port racine.
Lorsqu’un commutateur qui n’est pas commutateur racine émet un BPDU,
il ajoute le coût de la traversée du port sortant au coût à la racine du BPDU
avant de l’émettre.
3.6
Temporisateurs
Un commutateur implémentant STP maintient plusieurs temporisateurs :
• Un temporisateur global au commutateur :
– hello timer: Lorsque ce temporisateur est expiré, le commutateur,
s’il est racine, émet des BPDU sur chacun de ses ports. Ce tempo-
risateur est réinitialisé à chaque fois que le commutateur émet des
BPDU
• Des temporisateurs spécifiques à chaque port :
– message age : Lorsque ce temporisateur expire, les données contenus
dans le port expirent. Le BPDU stocké dans le port est réinitialisé,
le rôle du port devient désigné et son état devient Listening. Le
temporisateur est réinitialisé à chaque mise à jour d’état ou réception
d’un BPDU
– hold timer : Tant que ce temporisateur n’a pas expiré, le port ne
peut transmettre de BPDU. Le temporisateur est réinitialisé à chaque
envoi de BPDU
– forward delay : Lorsque ce temporisateur expire
- Si le port est dans l’état Listening, il passe en Learning, et le
temporisateur est réinitialisé
- Si le port est dans l’état Learning, il passe en Forwarding, et le
temporisateur est réinitialisé
4Les temporisateurs ont tous une durée définie par défaut :
Temporisateur
message age
forward delay
hold timer
hello timer
Durée (secondes)
20
15
1
2
Table 2: Durée des temporisateurs
4Questions
4.1Comparaison des BPDU
Le fonctionnement du Spanning Tree Protocol se base principalement sur la
comparaison de BPDU.
1. Indiquez dans votre rapport les éléments qui sont utilisés et l’ordre dans
lequel ils sont comparés.
2. Implémentez les méthodes lt et eq de la classe ConfigBPDU. Une
fois implémentés, ces méthodes vous permettront d’utiliser les opérateurs
<, > et == pour comparer deux instances de cette classe2 .
3. Testez votre implémentation en exécutant les tests correspondant (./tests.py
compare).
4.2
Réaction à la réception d’un BPDU
Maintenant qu’il est possible de comparer des BPDU, nous allons implémenter
la gestion de la réception d’un BPDU
4. Implémentez la méthode update config de la classe PortData afin de
respecter le comportement décrit dans la partie 3.3.
5. Implémentez la méthode port assignation de la classe STPController,
en respectant les instructions données dans la partie 3.4.
6. Testez votre implémentation en exécutant les tests correspondant (./tests.py
handle).
2 Documentation de
lt
et
eq
54.3
Implémentation préliminaire
Nous allons réaliser une première implémentation simplifiée mais fonctionnelle
de STP. Elle différera de l’implémentation finale en le fait qu’ici tous les com-
mutateur émettrons des BPDU en continue.
7. Implémentez les méthode transmit config et broadcast config de la
classe STPController.
8. Testez votre implémentation en exécutant les tests correspondant (./tests.py
emit).
Vous avez maintenant une implémentation de STP capable de converger vers
une arborescence.
9. Faites fonctionner cette implémentation avec le simulateur fourni. Incluez
dans votre rapport une visualisation de la topologie du réseau.
10. Indiquez dans votre rapport les limites de cette implémentation. Référez-
vous à la spécification et indiquez quelle modification permet de résoudre
quelle limite. Vous vous intéresserez particulièrement aux différents tem-
porisateurs, et au fait que seule la racine émette des BPDU en continu.
4.4
Temporisateurs et implémentation complète
11. Modifiez les méthodes tick et handle bpdu de la classe STPController
afin de respecter le comportement décrit dans la partie 3.5
12. Testez votre implémentation en exécutant les tests correspondant (./tests.py
root broadcast).
Nous allons finalement implémenter les temporisateurs nécessaires au fonc-
tionnement complet de STP. Vous récupérerez l’horodatage actuel en secondes
à l’aide de la fonction time de la classe STPController. Pour chaque tempo-
risateur, vous stockerez l’horodatage d’expiration du temporisateur. Vous le
comparerez à l’horodatage actuel pour savoir si le temporisateur est expiré ou
non.
13. Initialisez les valeurs des durées des temporisateurs dans la méthode init
de la classe STPController en utilisant le tableau 2.
4.4.1
3
Temporisateur hello timer
14. Initialisez la variable hello timer expiry dans la méthode init de la
classe STPController. Elle correspond à la date d’expiration du hello timer.
15. Modifiez la méthode broadcast config de la classe STPController afin
de réinitialiser la valeur de hello timer expiry si le hello timer est
expiré.
3 Documentation de
init
616. Modifiez la méthode tick de la classe STPController pour diffuser les
BPDU uniquement si le hello timer est expiré.
17. Testez votre implémentation en exécutant les tests correspondant (./tests.py
hello timer).
4.4.2
Temporisateur hold timer
18. Initialisez la variable hold timer expiry dans la méthode initialize de
la classe PortData. Elle correspond à la date d’expiration du hold timer.
19. Modifiez la méthode can send de la classe PortData afin de renvoyer
true uniquement si le hold timer est expiré. Pensez à réinitialiser le
temporisateur.
20. Testez votre implémentation en exécutant les tests correspondant (./tests.py
hold timer).
4.4.3
Temporisateur message age
21. Initialisez la variable message age expiry dans la méthode initialize
de la classe PortData. Elle correspond à la date d’expiration du tempo-
risateur message age.
22. Modifiez la méthode update config de la classe PortData afin de réinitialiser
le temporisateur message age. Pensez aussi à effectuer l’assignation des
ports après cette réinitialisation.
23. Modifiez la méthode update state de la classe PortData pour réinitialiser
le temporisateur message age.
24. Modifiez la méthode tick de la classe STPController afin d’y implémenter
le comportement décrit dans la partie 3.6.
25. Testez votre implémentation en exécutant les tests correspondant (./tests.py
message age).
4.4.4
Temporisateur forward delay
26. Initialisez la variable forward delay expiry dans la méthode initialize
de la classe PortData. Elle correspond à la date d’expiration du tempo-
risateur message age.
27. Implémentez la méthode do forward de la classe PortData afin d’y implémenter
le comportement décrit dans la partie 3.6. Vous vérifierez l’expiration du
temporisateur dans la méthode et n’oublierez pas de le réinitialiser.
28. Modifiez la méthode tick de la classe STPController afin d’y appeler
forward delay sur chacun des ports.
729. Modifiez la méthode initialize de la classe PortData et remplacez l’état
par défaut du port par Blocking.
30. Testez votre implémentation en exécutant les tests correspondant (./tests.py
forward delay).
4.5
Analyse
31. Faites fonctionner cette implémentation avec le simulateur fournie.
32. Expliquez les mécanismes de cette implémentation qui permettent à tout
instant d’éviter les boucles, dans des topologies de tailles raisonnables.
33. Donnez les limites de cette implémentation et expliquez comment Rapid
Spanning Tree Protocol permet de les dépasser.
8Annexes
A
Mise en place de l’environnement de développement
L’environnement de développement que vous utiliserez lors du développement
de ce projet est l’environnement p4-utils4 . Il est distribué sous forme d’une
image disque de machine virtuelle, téléchargeable ici.
Nous vous conseillons aussi d’installer un logiciel de virtualisation, tel que
QEMU5 ou VirtualBox6 .
Les instructions fournies ici utiliseront VirtualBox. Les ordinateurs de l’université
devraient en être déjà équipés. Si vous souhaitez travailler sur votre ordinateur
personnel, il est laissé à votre soin l’installation de VirtualBox.
Commencez par télécharger l’image disque de la machine virtuelle, puis
extrayez-la.
Ouvrez VirtualBox, puis cliquez sur Nouvelle pour créer une nouvelle ma-
chine virtuelle. Sélectionnez Type : Linux et Version : Ubuntu 18.04. Laissez
le champ Image ISO vide, donnez-lui un nom et cliquez sur Suivant.
Définissez la mémoire à assigner à la machine virtuelle. 4 Go sont généralement
recommandés, mais 2 Go sont suffisants. Cliquez sur Suivant.
Sélectionnez Utiliser une image disque existante, cliquez sur le bouton avec
l’icône de dossier, puis sur le bouton Ajouter et sélectionnez le fichier qcow2
extrait précédemment. Cliquez sur Choisir, puis sur Suivant.
Cliquez sur Terminer. Vous pouvez maintenant lancer la machine virtuelle
en cliquant sur Démarrer.
Vous pourrez vous connecter à la machine virtuelle en utilisant le nom
d’utilisateur p4 et le mot de passe p4. Attention : la machine est, par défaut,
en disposition QWERTY. Vous devrez taper p’ sur un clavier AZERTY pour
vous y connecter. Vous pourrez changer la disposition clavier en utilisant la
commande suivante :
$ sudo l o a d k e y s f r
Vous pouvez maintenant obtenir l’adresse ip de la machine virtuelle et vous
y connectez via SSH. Si vous utilisez VS-Code, vous pouvez utiliser la fonction-
nalité de développement distant via SSH7 .
Téléchargez et extrayez le code fourni sur Moodle dans la machine virtuelle.
4 Projet p4-utils
5 Site de QEMU
6 Site de VirtualBox
7 Documentation de Visual Studio Code
9B
Utilisation de l’environnement de développement
Deux scripts sont à utiliser pour démarrer l’environnement de développement :
• network.py mets en place le réseau virtuel
• run.py démarre les contrôleurs des commutateurs présents dans le réseau
Démarrez les deux scripts dans deux terminaux séparés, en commençant par
network.py.
Lorsque vous effectuerez des modifications, vous redémarrerez le script run.py.
Ce script possède une interface en ligne de commande vous permettant de vi-
sualiser le réseau et les états des ports, et de tester vore implémentation de
STP.
Voici la liste des commandes disponibles :
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

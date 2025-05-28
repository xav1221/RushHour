# RushHour
Le but du projet est d’implémenter le plus complètement possible le jeu (frontend et backend) du jeu Rush Hour.  Le but du jeu : faire sortir la voiture rouge. 


# Cahier de charge Niveau 0 

Premiere étape : afficher l’interface 6x6 avec les 3 voitures de tailles différentes :

![image](https://github.com/user-attachments/assets/6606afa5-6059-4d20-bc46-b6546ea0ed88)


2e etapes fais bouger les voitures : pouvoir selectionner la voiture a faire bouger et la deplacer suivant son horientation. 
En selectionnant une voiture, les contours de celle-ci deviennent jaune et on peut la deplacer horizontalement ou verticalement selon 

![image](https://github.com/user-attachments/assets/e2027e6b-5222-45e7-bc91-4b1a715e7ecc)


3eme étapes : afficher 3 types de configuration et un bouton de solution qui demande une solution pour faire sortir la voiture rouge.
•	Barre grise en haut avec 4 boutons : Carte 1, 2, 3, Solution.
•	Cliquer sur Carte X recharge immédiatement la configuration X.
•	Cliquer sur Solution imprime “Solution demandée !” dans la console.
•	Cliquer un vehicule sélectionne/déplace un véhicule comme avant.


![image](https://github.com/user-attachments/assets/9630d7f0-83e2-4c07-b9e1-11901c29d158)

****Voir la vidéo d’animation via le lien youtube****
https://youtu.be/SkkKlCLOKbk

Derniere partie pour le niveau 0 : pour chacune des cartes et de l’avancement du joueur, le clic sur le bouton ‘donner la solution’ réalise les mouvements nécessaires à faire sortir la voiture rouge
•	Cliquez sur Carte 1/2/3 pour charger la configuration.
•	Cliquez sur la grille pour sélectionner un véhicule, puis utilisez les flèches pour bouger manuellement.
•	Cliquez sur Solution pour lancer l’animation automatique des mouvements trouvés par le BFS, faisant sortir la voiture rouge.

****Voir la vidéo d’animation via le lien youtube****
https://youtube.com/shorts/n47NxX0UYao?feature=share





# Cahier de charge Niveau 1

possibilité de créer des cartes de configuration aléatoires 
algorithme qui trouve la solution dans tous les cas ou indique si aucune solution existe 
belle interface utilisateur

Amélioaration faites :
Hour Niveau 1 :
1.	Fond animé “cosmique”
o	Champ d’étoiles qui défilent lentement derrière la grille, simulant un starfield.
2.	Boutons stylés
o	Rectangles à coins arrondis et bordure blanche.
o	Effet “hover” : ils s’éclaircissent quand la souris passe dessus.
3.	Grille thématique
o	Fond sombre ((20,20,40)) et lignes de grille nuancées pour un look “galactique”.
4.	Véhicules en 2D stylisés
o	Carrosserie à coins arrondis avec bordure sombre.
o	Vitres claires et petites roues dessinées pour un rendu plus “dessiné”.
5.	Traînées lumineuses
o	À chaque déplacement (manuel ou automatique), une traînée semi-transparente s’estompe progressivement derrière le véhicule.
6.	Surbrillance cyclique
o	Lorsque vous sélectionnez un véhicule, un contour animé change de teinte (arc-en-ciel) toutes les secondes.
7.	Animation fluide
o	Boucle à 60 FPS pour un rendu continu des effets (trails, étoiles, confettis…).
8.	Confettis de victoire
o	À la victoire (colonne de sortie atteinte), on déclenche une pluie de confettis colorés qui tombent et disparaissent.
9.	Messages dynamiques
o	“BRAVO LA VOITURE EST SORTIE DES BOUCHONS” centré, multi-ligne.
o	“Aucune solution possible ” centré si le solveur BFS ne trouve pas de solution.
10.	Voiture rouge arc-en-ciel
o	Dès qu’elle atteint la colonne de sortie (victoire manuelle ou auto), la voiture rouge clignote en couleurs arc-en-ciel.


![image](https://github.com/user-attachments/assets/b476b013-e732-4cd2-935d-4c7ee5198ef5)

****Voir la vidéo d’animation via le lien youtube****
https://youtube.com/shorts/qmLO3Gsur04?feature=share






# Cahier de charge Niveau 2

Cahier des charges niveau 2 : 
faire sortir la voiture rouge avec un nombre minimal de mouvements 
aucune configuration sans solution n’est présenté à l’utilisateur 
avoir la solution à n’importe quelle carte de configuration sans délai (temps de calcul faible) 
Et toute autre ajout qui vous paraît pertinent !

Amélioaration faites :


1.	Chemin minimal garanti
•	Le solveur utilise un BFS pur pour toujours trouver le nombre de déplacements le plus court nécessaire à faire sortir la voiture rouge.
•	On affiche ce “Min : X” dès qu’on clique sur « Solution ».
2.	Uniquement des grilles solvables
•	La génération aléatoire boucle jusqu’à obtenir une configuration avec une solution non vide.
•	L’utilisateur ne tombe jamais sur un plateau sans issue.
3.	Solution instantanée
•	Pour chaque clic sur « Solution », la recherche est quasi instantanée sur un 6×6 et quelques véhicules.
•	On pré-calcule aussi la solution immédiatement après la génération d’une grille aléatoire.
4.	Compteurs de coups
•	Min : X (nombre minimal de déplacements) et Joués : Y (coups effectués manuellement ou en animation) s’affichent sous la barre de boutons.
•	Un compteur de déplacements apparaît également juste sous le bouton « Solution » pour une visibilité immédiate.



![image](https://github.com/user-attachments/assets/7add2ffe-4fef-424f-b8dd-6edc8a55c792)

****Voir la vidéo d’animation via le lien youtube****
https://youtube.com/shorts/oWSuT561dH8?feature=share







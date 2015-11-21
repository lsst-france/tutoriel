# tutoriel

Cet tutoriel accompagne la page du LogBook installée dans le Wiki

http://lsst.in2p3.fr/wiki/index.php?title=Utilisation_de_la_cha%C3%AEne_EUPS_%2B_scons

Un petit script python peut en outre installer l'exemple complet dans votre directory personnel:

git clone <...>tutoriel.git
python tutoriel/tutoriel.py

Ceci :

- initialise une base de données locale pour EUPS (si besoin)
- crée deux packages:

 my_lib

 my_pack

- Installe les deux packages dans votre directory courant
- configure les deux packages
- construit les deux packages
- exécute les programmes de test
- remet en état la base de données eups en supprimant la déclaration des deux packages
 


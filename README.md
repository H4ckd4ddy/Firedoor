# Firedoor

Le but de ce projet est de concevoir un gestionnaire de serveur : 

* standalone
* simple
* modulaire

## Introduction

Lors de la mise en service d'un serveur, après l'installation de l'OS, nous obtenons une machine vierge, disponsant la plupart du temps d'un unique acces SSH pour l'administrer.

L'objectif de Firedoor, et d'intervenir à ce moment là, pour securiser cet unique accès, et vous accompagner dans la gestion et securisation de votre serveur.

## Standalone ?

Firedoor est entirerement developpé en Python, puis packadgé par PyInstall pour obtenir un binaire sans dependance.

## Simple ?

Firedoor s'installe en une commande, après cela, toutes les actions d'administration se font depuis l'interface web via des menus intuitifs.

*Pour ceux qui n'ont pas besoins de boutons, il est possible d'effectuer l'administration directement en ligne de commande, avec les mêmes fonctionnalités*

## Modulaire ?

Firedoor est un peu comme une passerelle qui fait le lien entre les differents services de votre machine au travers des differents modules.
Dans Firedoor, **TOUT EST MODULE**, y compris ses fonctionnalitées principales (*core modules*).

Une template de module à été établie, qui definie les variables et methodes auquelles les modules on accès, ainsi que leurs entrypoints

On peut ajouter n'importe quelle fonctionnalité imaginable et l'ajouter, sans jamais toucher au code principal de Firedoor.

Chaque module et un dossier, qu'il suffi de glisser dans le dossier modules avant de generer le binaire.


Voici quelques exemples du fonctionnement modulaire de Firedoor :

### Installation

Lors de son installation Firedoor va inventorier ses modules afin de voir si ils disposent d'un entrypoint d'installation.
Si c'est le cas, les pré-requis de chacun vont êtres validés pour garantir le bon fonctionnement de chaque modules

### Interfaces web

Lors de l'accès à l'interface web, Firedoor liste les modules disposants d'une interface web, afin de les integrer graphiquement.

### CLI

De la même maniere lors de la saisi d'un commande, les arguments sont directement envoyé dans l'entrypoint CLI du module concerné (si il en dispose)

## Modules en développement

| Nom           | Type               |  Fontion                      |
| :------------ | :----------------- | :---------------------------- |
| Settings      | Core module        | Permet de modifier les parametres basiques (MDP, Hostname, port...) |
| Locked        | Core module | Cache les ports d'administration (SSH, FTP...) quand ils ne sont pas utiles. Cela permet de prevenir les scans et les indexations comme Shodan ou ZoomEye |
| Rules manager | Module additionnel | Permet de gerer simplement les regles du firewall pour rendre accessible les services legitimes |
| SSHTTP        | Module additionnel | Client ligne de commande web pour administrer votre serveur depuis n'importe quel poste sans rien installer |
| Monitoring    | Module additionnel | Assure la surveillance l'enregistrement et la consultation des constantes vitales de votre serveur |
| Flows         | Module additionnel | Analyse du trafic entrant, WAF, detection DoS/DDoS |
| Docker        | Module additionnel | Permet la visualisation et l'administration de ses conteneurs Docker |
| Updater       | Module additionnel | Verifie les MAJ à effectuer et permet de definire une politique de MAJ automatique |
| Apache manager | Module additionnel | Tout est dans le titre (gestion de confs, vHosts, certificats) |
| Bake-up       | Module additionnel | [Sauvegarde incrementielle par Hard-linking](https://github.com/H4ckd4ddy/Bake-up) |

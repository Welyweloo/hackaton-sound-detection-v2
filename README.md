# Hackathon Février 2021 

## Auteurs projet initial : https://github.com/Welyweloo/hackaton-sound-detection
Aurélie - Benjamin - Maxime - Viverk

## Auteurs du projet présent (v2 du projet initial) : 
Aurélie Anglio

## Thème
Conception d'un prototype de reconnaissance et traitement de signal audio à connecter sur un Wello (vélo-cargo électrique à énergie solaire) à destination de la délégation ministérielle pour l'intelligence artificielle.
> Pour plus d'informations sur le Wello : https://www.wello.io/

## Installation 

Ce programme a été testé avec la configuration suivante:

Pour la détection, l'enregistrement et la reconnaissance d'un son :
- Ubuntu 20.04
- Python3.8
  
Pour l'interface web (serveur web) :
- Ubuntu 20.04
- Python3.8
- Django 3.0.8

Client web compatible:
- Chrome Version 88.0.4324.150 (Build officiel) (x86_64)

Attention la reconnaissance vocale depuis l'interface web (SpeechToText) ne fonctionne que sous Chrome sur ordinateur.
Solution pour utiliser le micro sans https: 
> Aller sur `chrome://flags/#unsafely-treat-insecure-origin-as-secure`
 
> Autoriser `Insecure origins treated as secure`

> Source: https://medium.com/@Carmichaelize/enabling-the-microphone-camera-in-chrome-for-local-unsecure-origins-9c90c3149339

1. Cloner ce dépôt : 
```bash
git clone https://github.com/Welyweloo/hackaton-sound-detection.git
cd sound-detector
```

2. Installer les pré-requis et configurer :

### Installation du serveur web:
```bash
cd django
pip install -r requirements.txt
```
Il faut modifier le fichier settings.py avec vos informations.
Pour settings.py, il faut modifier avec vos informations les lignes 120 à 129 :
```python
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yourownkey' #Define your own key

EMAIL_HOST = 'smtp.free.fr' #Pick your own
EMAIL_PORT = 587
EMAIL_HOST_USER = 'youremail@email.email'
EMAIL_HOST_PASSWORD = 'yourpassword'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
```

Vous pouvez maintenant lancer le serveur web:
```bash
python3 manage.py runserver 0.0.0.0:8080
```

Aller sur le back office : `http://URL_SERVEUR/admin/`

>Username : `admin`

>Password : `wello`

Modifier l'e-mail de la station de police (PoliceStations > PoliceStation Object > Email) avec l'email sur lequel vous souhaitez recevoir les alertes.
### Installation du détecteur de son:
```bash
cd sound-detector
sudo apt-get install portaudio19-dev
pip install -r requirements.txt
```

Editer le fichier sound-detector/sound-detector/conf.ini 
```
[RASPBERRY]
;Modifier avec l'adresse ip et le port de votre serveur web
Address=http://192.168.0.5:8000  
```

Dans le fichier detect-record-classify.py, la constante THRESHOLD détermine le seuil (RMS - niveau sonore moyen) qui permet de déclencher l'enregistrement audio. 

Le print ligne 202, vous permettra de déterminer le seuil compte tenu de votre environnement.
```python
rms_val = self.rms(input)
print(rms_val)
```

### Etapes

1. Lancer le programme de reconnaissance et traitement de signal audio 
```bash
python3 detect-record-classify.py
```
2. Identification 
>Votre numéro de Matricule:
`1`

>Numéro d'immatriculation du Wello:
`DMIA`

>Identifiant de votre assistant connecté:
`2912`


## Use Cases 

Ce programme est développé pour répondre aux fonctionnalités mentionnées ci-dessus. Pour toute démonstration, vous trouverez ci-dessous le scénario pour lequel il a été conçu.

Utilisateur: *Agent de proximité partant en patrouille*

> [Vidéo démonstrative](https://www.canva.com/design/DAEWTc_HAPo/mJoT_4-7748GrmqfJFJtEA/watch?utm_content=DAEWTc_HAPo&utm_campaign=designshare&utm_medium=link&utm_source=publishsharelink)

1. **En tant qu'Utilisateur**, **je peux** monter à bord de mon Wello et fixer mon assistant connecté (le Raspberry sur lequel sont branchés un micro, une carte 4G) **afin** qu'il soit stable.

    >**Point technique** : L'interface web est codée en PHP et JS Vanilla, elle communique avec le Raspberry via une API qui stocke les données sur une base de données MySQL.


2. **En tant qu'Utilisateur**, **je peux** saisir  partir d'une interface web sur mobile l'immatriculation de mon Wello **afin** que l'assistant connecté sache à bord de quel Wello il effectuera sa mission.

    >**Point technique** : Le numéro d'immatriculation sera utile pour chaque saisie en base de données, l'objectif est d'identifier le Wello.

3. **En tant qu'Utilisateur**, **je peux** cliquer sur 'Commencer ma tournée' sur interface web sur mobile **afin** de lancer le programme de reconnaissance et traitement de signal audio.

    >**Point technique** : Le programme écoutera en permanence les sons environnants, selon l'intensité du bruit, il déclenchera ou non un enregistrement qui sera analysé par un moteur Tensorflow grâce à une intelligennce artificielle entraînée sur 524 types de sons. En quelques secondes la nature du son sera stockée en base de donnée, ainsi que la date et l'heure.

4. **En tant qu'Utilisateur**, **je peux** visualiser via interface web sur mobile le statut du programme : signal vert (ok) ou signal rouge clignonant (problème), **afin** de savoir si un son anormal a été identifié.

    >**Point technique** : Ce signal pourra éventuellement être remplacé par une led directemennt branchée sur un port GPIO du Raspberry.

5. **En tant qu'Utilisateur**, après avoir entendu un son et constaté le changement de signal au rouge clignotant sur interface web sur mobile **je suis** informé qu'une notice a été envoyée aux équipes de renfort, **afin** qu'elles se tiennent prêtes le temps que j'arrive sur site.

6. **En tant qu'Utilisateur**, après mon arrivée sur site, **je peux** signaler une fausse alerte via une interface web, **afin** de signifier aux équipes que le son n'a occasionné aucun danger.

7. **En tant qu'Utilisateur**, après mon arrivée sur site, **je peux** cliquer sur le bouton 'Confirmer le signalement' sur l'interface web, **afin** de démarrer un enregistrement vocal pendant que je sécurise les lieux. 

8. **En tant qu'Utilisateur**, **je peux**  transmettre des informations verbales aux renforts ainsi que le code interne de la situation rencontrée (120 pour une fusillade par exemple) **afin** d'identifier les équipes et leur donner de la visibilité.

    >**Point technique** : C'est l'API Speech Recognization (Javasript) qui permettra grâce à une intelligence artificielle de réaliser du "speech to text" afin de sauvegarder le message verbal en texte dans la base de donnée.

9. **En tant qu'Assistant de Régulation**, **je peux**  être alerté sur un problème signalé par l'un agent par e-mail **afin** de faire remonter le problème à ma hiérarchie.

10. **En tant qu'Utilisateur**, **je peux** cliquer sur 'Terminer la session' quand ma tournée est terminée **afin** de stopper le programme de reconnaissance et traitement de signal audio.


## Sources utilisées 

- Pour la détection et l'enregistrement du son, la base de code est fournie ici : https://stackoverflow.com/a/50340723/13987580

- Pour la classification du son, la base de code est fournie ici :  https://www.tensorflow.org/hub/tutorials/yamnet

- Pour la création du code de reconnaissance vocale, la documentation est fournie ici : https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition/onresult

## Amélioration à apporter

- Refonte du front-end avec le framework VueJS (en guise d'apprentissage)
- Ajout de fonctionnalités 
- Tester le programme sur Raspberry et y apporter les modifications nécessaires pour un bon fonctionnement (version de Tensorflow etc...)
- Améliorer le code pour une meilleure détection et classification de son (le programme n'arrive pas a bien isoler les sons parasites pour l'instant, il fonctionne quand l'environnement est plutôt silencieux)


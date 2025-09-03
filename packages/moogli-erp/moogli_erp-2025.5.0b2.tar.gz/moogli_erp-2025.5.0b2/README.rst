==========
CAERP
==========

Un progiciel de gestion pour les CAE (Coopérative d'activité et d'emploi),
les collectifs d'entrepreneurs indépendants.

Licence
-------

Ceci est un logiciel libre, pour les conditions d'accès, d'utilisation,
de copie et d'exploitation, voir LICENSE.txt

Nouvelles fonctionnalités/Anomalies
-----------------------------------

Site officiel : http://endi.coop

L'essentiel du développement est réalisé sur financement de Coopérer pour
entreprendre. Si vous souhaitez plus d'information, une offre d'hébergement,
vous pouvez les contacter info@cooperer.coop

Si vous rencontrez un bogue, ou avez une idée de fonctionnalité, il est possible
de signaler cela aux développeurs directement ou en utilisant le système de
tickets de GitLab (framagit).
Exception : pour les bogues de sécurité, merci d'écrire un courriel à votre administrateur.

Instructions pour l'installation du logiciel (en environnement de prod)
-----------------------------------------------------------------------

Installation des paquets (nécessaire pour l'installation dans un environnement virtuel):

Sous Debian/Ubuntu:


NB : Il est possible soit d'utiliser le dépôt nodesource pour avoir une version adaptée de nodejs. Soit de faire les
builds JS avec docker-compose pour compiler le javascript
(voir : https://caerp.readthedocs.io/fr/latest/javascript/build_docker.html)

.. code-block:: console

    apt install virtualenvwrapper libmariadb-dev libmariadb-dev-compat npm build-essential libjpeg-dev libfreetype6 libfreetype6-dev libssl-dev libxml2-dev zlib1g-dev python3-mysqldb redis-server libxslt1-dev python3-pip fonts-open-sans libcairo2 libglib2.0-dev libpango1.0-0 libgdk-pixbuf-2.0-0

Il faudra, en plus, si vous n'utilisez ***pas*** docker-compose installer npm de la manière suivante :

.. code-block:: console

    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - &&\

    apt install npm

Sous Fedora:

.. code-block:: console

    dnf install virtualenvwrapper mardiadb-devel python-devel libxslt-devel libxml2-devel libtiff-devel libjpeg-devel libzip-devel freetype-devel lcms2-devel libwebp-devel tcl-devel tk-devel gcc redis-server open-sans-fonts

Téléchargement de l'application

.. code-block:: console

    git clone https://framagit.org/caerp/caerp.git
    cd caerp

Téléchargement des dépendances JS (requiert nodejs >= 16.x)

.. code-block:: console

    npm --prefix js_sources install
    npm --prefix vue_sources install

Compilation du code JS

.. code-block:: console

    make prodjs devjs
    make prodjs2 devjs2

Création d'un environnement virtuel Python.

.. code-block:: console

    cd caerp
    mkvirtualenv caerp -p python3 -r requirements.txt


Installation de l'application

.. code-block:: console

    python setup.py install
    cp development.ini.sample development.ini


Éditer le fichier development.ini et configurer votre logiciel (Accès à la base
de données, différents répertoires de ressources statiques ...).

Initialiser la base de données

.. code-block:: console

    caerp-admin development.ini syncdb

Si vous utilisez un paquet tiers utilisant d'autres base de données (comme
caerp_payment en mode production)

.. code-block:: console

    caerp-migrate app.ini syncdb --pkg=caerp_payment

.. note::

    L'application synchronise alors automatiquement les modèles de données.

Puis créer un compte administrateur

.. code-block:: console

    caerp-admin development.ini useradd [--user=<user>] [--pwd=<password>] [--firstname=<firstname>] [--lastname=<lastname>] [--group=<group>] [--email=<email>]

N.B : pour un administrateur, préciser

.. code-block:: console

    --group=admin


Installation (en environnement de dev)
--------------------------------------

Docker-compose permet de faciliter le déploiement d'un environnement de dév complet. Le tableau suivant récapitule les
 différentes options possibles.

======================== ======================================================= =======================================
Composant                Fonctionnement recommandé                               Fonctionnement alternatif (déconseillé)
======================== ======================================================= =======================================
serveur MariaDB          natif ou docker-compose (make dev_db_serve)
serveur Redis            natif ou docker-compose (make dev_db_serve)
serveur web de dév       natif/bare-metal (make dev_serve)  True   False
build JS (Marionette/BB) docker-compose (make prodjs_dc devjs_dc)                 natif (make prodjs devjs)
build JS (VueJS)         docker-compose (make prodjs2_dc devjs2_dc)               natif (make prodjs2 devjs2)
build CSS                natif (make css_watch)
build JS (legacy)        natif (make js)
Postupgrade              docker-compose (make postupgrade_dev)                   natif (make postupgrade_dev_legacy)
======================== ======================================================= =======================================


.. warning::
    La suite de la doc ne couvre que les cas recommandés.

Installer les dépendendances système (cf ligne ``apt`` ou ``dnf``, selon votre
OS, dans la partie concernant l'installation en prod).

Ensuite, installez votre CAERP de dév avec les commandes suivantes :

.. code-block:: console

    sudo apt/dnf install […] (idem à la section concernant la prod)
    git clone https://framagit.org/caerp/caerp.git
    cd caerp
    cp development.ini.sample development.ini

..warning::
    Assurez-vous ensuite d'utiliser une verison de Python compatible avec CAERP ; à défaut, suivez la section
    « Pour les distribution possédant des versions de python incompatibles » avant de passer à la suite.

..note::
    Si vous utilisez docker-compose pour le serveur mariadb, décommentez les lignes concernant docker-compose afin de
    bien viser le serveur mariadb dans docker-compose.

Installez les dépendances hors système :

    make postupgrade_dev

Il est possible de charger une base de données de démonstration complète
(écrase votre BDD caerp si elle existe) avec :

.. code-block::

   caerp-load-demo-data development.ini
   caerp-migrate development.ini upgrade

Pour les distribution possédant des versions de python incompatibles
--------------------------------------------------------------------

Pour le moment, CAErp ne supporte pas les versions de pythons > 3.10,
on peut donc passer par pyenv pour installer une version de python
supportée par le projet via `pyenv` :

.. code-block:: console

    $ curl https://pyenv.run | bash

Après avoir suivi les instructions, il est possible d'initialiser un
environement (en utilisant python 3.9 par exemple) :

.. code-block:: console

    $ sudo apt install liblzma-dev  # dnf install xz-devel sous RH
    $ cd workspace/caerp            # votre dossier dans lequel est cloné caerp
    $ pyenv install 3.9
    $ pyenv virtualenv 3.9 caerp
    $ pyenv activate caerp
    (caerp) $ pip install -e .[dev]


Exécution des tâches asynchrones
---------------------------------

Un service de tâches asynchrones basé sur celery et redis est en charge de
l'exécution des tâches les plus longues.

Voir :
https://framagit.org/caerp/caerp_celery

pour plus d'informations.

Mise à jour (en environnement de prod)
--------------------------------------

La mise à jour d'CAERP en prod s'effectue en plusieurs temps (il est préférable de
sauvegarder vos données avant de lancer les commandes suivantes)

Mise à jour des dépendances python et du numéro de version

.. code-block:: console

    pip install .


Mise à jour de la structure de données

.. code-block:: console

    caerp-migrate app.ini upgrade

Si vous utilisez un paquet tiers utilisant d'autres base de données (comme
caerp_payment en mode production)

.. code-block:: console

    caerp-migrate app.ini upgrade --pkg=caerp_payment

Configuration des données par défaut dans la base de données

.. code-block:: console

    caerp-admin app.ini syncdb

Met à jour les dépendances JS

.. code-block:: console

    npm --prefix js_sources install

Compile le JavaScript :

    make prodjs

Puis lancer l'application web

.. code-block:: console

    pserve --reload development.ini

.. warning::

    Il est possible, sous Linux, que vous obteniez l'erreur suivante au lancement de pserve :

        [ERROR] watchdog error: [Errno 24] inotify instance limit reached

    La solution est la suivante :

        sudo bash -c 'echo "fs.inotify.max_user_instances = 1100000" >> /etc/sysctl.d/40-max-user-watches.conf'
        sudo sysctl -p

    De même, si jamais pserve ne recharge pas tout le temps et/ou semble impossible à arrêter avec Ctrl+C, il faut changer un autre paramètre :

        sudo bash -c 'echo "fs.inotify.max_user_watches = 1100000" >> /etc/sysctl.d/40-max-user-watches.conf'
        sudo sysctl -p

    (il peut être nécessaire de relancer la session utilisateur)



.. warning::

    Si ``pserve --reload`` dysfonctionne sans message d'erreur : changements non détectés + impossible à stopper avec Ctrl+C.

    Vous pouvez essayer d'installer watchman (``apt install watchman`` sous Debian/Ubuntu). Ça changera de backend de surveillance pour passer de **watchdog** à **watchman**. Il n'y a rien à configurer, si les deux sont installés, watchman sera préfér à watchdog.


Mise à jour/changement de branche (environnement de dév)
---------------------------------------------------------
Ces instructions sont à suivre une fois à jour sur la branche git
souhaitée. Elles sont sans risque : au pire elles ne feront rien si tout est
déjà à jour.

La commande suivante devrait s'occuper de tout

.. code-block:: console

    make postupgrade_dev


.. note::

    Le fichier Makefile est commenté si besoin de plus d'infos/détails sur ce
    que fait cette commande.


Standards de codage Python
^^^^^^^^^^^^^^^^^^^^^^^^^^

Le code CAERP doit être formatté en respectant la pep8_.

À cette fin il est recommandé d'utiliser un analyseur de code comme flake8_.

En complément, afin d'assurer une uniformisation dans la mise en forme du code,
l'outil de formattage de code black_ doit être utilisé pour le développement.

Il peut être configuré `au niveau de votre éditeur`_ (le plus confortable) et/ou en
pre-commit.

.. _pep8: https://www.python.org/dev/peps/pep-0008/
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _black: https://black.readthedocs.io/en/stable/index.html
.. _au niveau de votre éditeur: https://black.readthedocs.io/en/stable/integrations/editors.html

.. note::

   Pour activer le pre-commit hook (une fois pour toutes) : depuis le venv :

   ``pre-commit install``

   Ensuite, à chaque commit, lorsque votre code n'est pas formatté correctement
   selon black le reformatera au moment du commit **et fera échouer
   le commit**. Il faudra alors ajouter (``git add``) les modifications
   apportées par black et commiter à nouveau.

Il est également possible de lancer black manuellement sur l'ensemble du projet :

.. code-block:: console

   make black

(si vous n'utilisez pas black en local, l'intégration continue vous le rappelera 😁)


Standards de codage Javascript Marionette
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Le code javascript Backbone/Marionette de CAERP (dans js_sources/src) doit être
formatté à l'aide de prettier.

.. code-block:: console

    cd js_sources/
    npm install -D
    npm prettier --config=./.prettierrc --write src/

Idéalement le code doit être vérifié à l'aide de eslint.

.. code-block:: console

    cd js_sources/
    npm install -D
    npm eslint -c ./.eslintrc src/

Ces deux outils peuvent être intégrés dans la majorité des éditeurs de code.


Base de données avec docker-compose (MariaDB + redis)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pour héberger sur un conteneur docker jettable et reproductible sans toucher à
la machine hôte, une configuration docker-compose est disponible.

Pour installer l'environnement (la première fois) :

.. code-block:: console

   sudo apt install docker-compose
   sudo usermod -a -G docker $USER


Pour l'utiliser, plusieurs raccourcis sont offerts :

.. code-block:: console

    # Faire tourner une BDD que l'on stoppera avec ctrl+c
    make dev_db_serve
    # Démarrer une BDD
    make dev_db_start
    # Arêtter une BDD démarrée avec la commande précédente
    make dev_db_stop
    # Effacer les données de la BDD de dév
    make dev_db_clear

Des configurations adaptées à docker-compose sont commentées dans ``test.ini.sample`` et
``developement.ini.sample``.

Compilation dynamique des assets (JS/CSS) avec docker compose
-----------------------------------------------------------------

Pour compiler uniquement les fichiers js

.. code-block:: console

    docker compose -f js-docker-compose.yaml up

Pour compiler les fichiers css

.. code-block:: console

    docker compose -f css-docker-compose.yaml up


Tests
------

Copier et personnaliser le fichier de configuration

.. code-block:: console

    cp test.ini.sample test.ini

Lancer les tests

.. code-block:: console

   py.test caerp/tests

Documentation utilisateur
--------------------------

Le guide d'utilisation se trouve à cette adresse :
https://doc.endi.coop

*****


:Ce projet est testé avec: `BrowserStack <https://www.browserstack.com/>`_

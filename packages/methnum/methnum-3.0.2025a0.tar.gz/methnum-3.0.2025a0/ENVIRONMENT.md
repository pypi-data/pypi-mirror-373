# Environnement MethNum

## Présentation

L'environnement `methnum` est une adaptation de la librairie générique [`travo`](https://gitlab.com/travo-cr/travo/) au cours de Méthodes Numériques de l'Université Paris-Saclay.
Cette suite de scripts est installée sur toutes les plateformes de l'Université Paris-Saclay, et permet aux étudiants de télécharger et de soumettre leurs travaux numériques, et aux enseignants de collecter les copies, les corriger, les annoter et les retourner aux étudiants. 
Les technologies au cœur de cette architecture sont [`gitlab`](https://gitlab.dsi.universite-paris-saclay.fr/MethNum) et [`nbgrader`](https://nbgrader.readthedocs.io/en/stable/).

Les étudiants peuvent accéder à tout le contenu des cours de Méthodes Numériques du L1 au L3 en tapant :
```
methnum start
```
dans une console d'une des plateformes de l'Université, et se laisser guider par le tableau de bord.

## <a name="install"></a> Installation de l'environnement methnum

L'environnement `methnum` est nativement installé sur le [MyDocker](https://mydocker.universite-paris-saclay.fr/shell/join/QRsHUzWOFhAQvoaPzXHV) de l'Université Paris-Saclay.
Il est conseillé d'utiliser cette plateforme pour avoir un environnement maîtrisé et commun à toute l'équipe pédagogique. 

### Installation conseillée

```
pip install methnum
```
Il est conseillé de le faire dans un environnement [`mamba`](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html).

### Installation des scripts methnum

A des fins de développement ou de gestion fine des enseignements, il peut toutefois être installé simplement sur des ordinateurs individuels.

Il est conseillé de développer le cours dans le même environnement python que celui fournit aux étudiants. Pour cela il faut installer python via *Mamba* (https://mamba.readthedocs.io/en/latest/index.html). Puis :
```
git clone https://gitlab.dsi.universite-paris-saclay.fr/MethNum/ComputerLab ComputerLab
```
puis tapez :
```
cd ComputerLab/.binder
mamba env create
```
Puis, il faut activer l'environnement `methnum` par :
```
conda activate methnum
```
Dans l'éventualité où une nouvelle version des scripts ou de l'environnement est disponible, mettez à jour votre copie de `ComputerLab`:
```
cd ComputerLab/.binder
git pull
```
puis tapez :
```
mamba env update -n methnum -f environment.yml --prune # installation du nouvel environnement
```

:::{note}
:class: dropdown
# Installation en salle de TP

Ces commandes peuvent être nécessaires au SIF pour mettre à jour l'environnement utilisé par les étudiants ***dans toutes les salles de TP de l'université***.
```
ssh -Y prenom.nom@ssh2.pgip.universite-paris-saclay.fr
cd MethNum/ComputerLab/.binder  # a cloner si absent
/public/methnum/miniconda3/bin/mamba env update -f environment.yml --prune
```
:::


## Description des scripts principaux fournis avec methnum

A défaut d'utiliser le tableau de bord, les étudiants et enseignants peuvent accéder à différentes commandes `methnum`.

### Téléchargement d'une séance : fetch

Étudiants et enseignants peuvent télécharger un sujet sans réponse en tapant une première fois :
```
methnum fetch L1/Seance1
```
La séance est automatiquement placée dans un dossier `MethNum` placé dans le `$HOME`. **Ce dossier ne doit pas être déplacé ni renommé.** Techniquement, la personne qui exécute cette commande réalise un *fork* du dépôt gitlab public.

### Poster ses réponses : submit

Une séance dont les réponses ont été partiellement ou totalement rentrées peut être postée 
sur un [dépôt gitlab personnel privé](https://gitlab.dsi.universite-paris-saclay.fr/) autant de fois 
que nécessaire par la commande :
```
methnum submit L1/Seance1 GROUPE
```
Si le dépôt n'existe pas au premier `submit`, il est créé, et les droits de lecture et écriture sont donnés aux enseignants, mais pas aux autres étudiants.
La notion de groupe ici est très importante, car elle permet à l'enseignant référent du groupe de ne récupérer que ses copies : le dépôt personnel de l'étudiant est créé avec un lien de *fork* avec le dépôt commun à son groupe contenant les sujets.

À partir du premier `submit`, toute future commande `fetch` va télécharger la séance depuis le gitlab personnel et non depuis le dépôt public qui contient les sujets vierges. Cela permet de se servir de son dépôt gitlab comme d'un dépôt de sauvegarde en ligne pour transférer son travail d'une plateforme à une autre (voir schéma ci-dessous).

<img src="figures/methnum_structure.png" alt="Markdown Monster icon" style="float: left; margin-right: 10px;" />


___
À partir d'ici nous allons décrire les fonctions destinées aux enseignants. Pour chaque année, un notebook `MethNum-Dashboard.md` est fourni.
Cette interface graphique fournit une vue simplifiée des commandes ci-dessous pour faciliter le travail routinier de la correction de copies. 
Les commandes exposées ci-dessous permettent de réaliser du débogage par lignes de commande.
___

### Lancer la correction automatique : student_autograde et forge_autograde

Lors d'un `submit`, une nouvelle version de la copie de l'étudiant est postée sur son dépôt personnel. Si un fichier `.gitlab-ci.yaml` est présent, le serveur lance un 
processus d'intégration continue, qui fait appel à la fonction `student_autograde` : celle-ci lance la procédure de correction automatique et génère des *artefacts*. Ces derniers sont les
fichiers de sortie générés pas la notation automatique, à savoir essentiellement le fichier contenant l'exécution du notebook (`TD1.ipynb` par exemple) et le base de données contenant les notes (`.gradebook.db`).
Ces artefacts sont exposés sur le web dans la rubrique "CI/CD" du dépôt gitlab de l'étudiant, en cliquant sur le dernier job lancé puis *Browse* à droite.

En cas de nécessité, il est possible de forcer le lancement de la correction automatique par l'enseignant via la commande :
```
methnum force_autograde L1/Seance1 *TAG*
```
où le wildcard `*TAG* ` peut être rien, ou un nom d'étudiant, complété ou non par un wildcard. 

*NB : l'intégration continue a un temps maximal d'exécution de 10 minutes, 
il faut donc veiller à proposer des devoirs dont l'exécution est plus courte.*



### Ramasser les travaux : collect

Un enseignant peut récupérer tous les travaux de son groupe via la commande :
```
methnum collect_in_submitted L1/Seance1 GROUPE
```
Les copies sont téléchargées dans un dossier nommé `./submitted`. Techniquement, par cette commande l'enseignant recherche tous les *forks* du sujet posté dans le dépôt https://gitlab.dsi.universite-paris-saclay.fr/MethNum/2020-2021/L1/GROUPE/Seance1. L'enseignant peut les voir sur le web en cliquant sur le nombre à côté du symbôle *fork* du dépôt vierge, ou après le `collect` dans le dossier `./submitted`.

### Ramasser les notes issues de la correction automatique : collect_autograded

Un enseignant peut récupérer tous les travaux de son groupe via les deux commandes :
```
methnum collect_autograded L1/Seance1 GROUPE
```
Les copies sont téléchargées dans un dossier nommé `./autograded`. Techniquement, par cette commande l'enseignant recherche tous les *forks* du sujet posté dans le dépôt https://gitlab.dsi.universite-paris-saclay.fr/MethNum/2020-2021/L1/GROUPE/Seance1. 
La correction automatique a eu lieu par intégration continue sur le serveur gitlab lors du dernier `submit`. 
Pour chaque *fork* détecté, les artefacts sont téléchargés dans le dossier nommé `./autograded`, en particulier la base de données contenant l'exécution du notebook et les notes automatiques (`.gradebook.db`).

Afin de fusionner ces notes individuelles avec la base de données de notes locale de l'enseignant, il faut ensuite taper : 
```
methnum collect_autograded_post L1/Seance1 GROUPE
```
Les trois commandes précédentes ont été fusionnées dans le bouton `collect` fourni avec le `MethNum-Dashboard.md` de l'UE.

### Noter manuellement les travaux : formgrader

Pour lancer l'interface de correction manuelle, il faut taper la commande :
```
methnum formgrader Seance1  # ne pas mettre L1
```
puis se laisser guider par l'interface de [`nbgrader`](https://nbgrader.readthedocs.io/en/stable/).

Pour commencer à corriger la série de copies, il faut cliquer sur `Seance1` et ensuite sur "Submission #1". 

*NB : à noter que si vous voulez voir le nom de l'élève, cliquer sur le petit œil à côté.*

Corriger la copie en cliquant sur "Full credit", "No credit", les petites flèches, ou "extra credit", ajouter des commentaires dans les cases dédiées. 
- *Le gros point d'interrogation en bas à droite propose des raccourcis clavier (Tab par exemple)*
    
* *Si l'enseignant souhaite debugger une réponse, la page html ne permet pas de le faire, par contre aller dans le navigateur du serveur Jupyter (onglet précédent) et naviguer dans `./submitted/PRENOM.NOM/Examen/ et lancer le notebook de PRENOM.NOM.*

Pour passer à la copie suivante, cliquer en haut sur "Next" et recommencer.



Une fois la correction manuelle réalisée, la base de données locale de l'enseignant `.gradebook.db` contient les notes et commentaires pour chaque évaluation et chaque étudiant.



### Envoyer les résultats : generate_feedback et release_feedback

La commande `generate_feedback` permet de fabriquer des fichiers .html représentant les copies notées et annotées dans le dossier `./feedback` :
```
methnum generate_feedback L1/Seance1 *TAG*
```
où le wildcard `*TAG* ` peut être rien, ou un nom d'étudiant, complété ou non par un wildcard.

Puis, la commande : 
```
methnum release_feedback L1/Seance1 *TAG*
```
découpe la base de données de notes locale pour déposer un fichier `.gradebook.db` propre à chaque étudiant dans le dossier `autograded`.
La commande réalise ensuite un `submit` au nom de l'enseignant dans le dépôt de l'étudiant avec ce fichier de note. L'intégration continue permet aussi de générer de nouveaux artefacts,
contenant cette fois-ci la copie notée et annotée complète.

### Récupérer la copie notée : fetch_feedback

Un badge avec la note de l'étudiant va s'afficher automatiquement dans son tableau de bord. S'il souhaite consulter sa copie, le détail des notes et les commentaires de l'enseignant, il suffit de cliquer sur le badge.

L'étudiant peut aussi récupérer manuellement sa copie notée et commentée par la commande :
```
methnum fetch_feedback L1/Seance1
```
Un dossier `feedback` apparait dans son dossier `MethNum/L1/Seance1` avec notamment des fichiers .html pour voir les commentaires de l'enseignant et les points par question.


### Un soucis avec une copie : autograde

Certaines copies peuvent avoir eu un soucis lors de l'intégration continue, par exemple une boucle infinie. Dans ce cas, il faut trouver
les lignes de code problématiques dans le notebook situé dans le dossier `submitted`, les corriger, et taper au choix une des deux commandes. La première commande réalise un `submit` au nom de l'enseignant,
attend la fin de la correction automatique, récupère le nouveau `.gradebook.db` de l'étudiant et le fusionne avec la base de données de l'enseignant. :
```
methnum forge_autograde L1/Seance1 *TAG*
```
où `*TAG*` est un mot clé désignant la copie de l'étudiant (`prenom.nom` par exemple). Cette 
La seconde réalise directement en local la correction automatique à partir du fichier modifié dans `submitted` (mais la modification n'est pas postée à l'étudiant) :
```
methnum nbgrader_autograde L1/Seance1 *TAG*
```
Cette dernière commande est équivalent à cliquer sur le petit éclair bleu dans l'interface de correction du `formgrader`.

Si le problème a été résolu, l'enseignant peut passer à la correction manuelle avec le `formgrader`.


**Rappel: aucun document contenant des noms d'étudiants ne doit être posté sur le gitlab enseignant.**



### Création de contenu : generate_assignment

Une séance de cours doit être placé dans le dossier `source` du dépôt enseignant. Le nom du sous-dossier est la clé pour retrouver cette séquence pédagogique dans toute la suite de l'UE.

Pour créer un jupyter notebook qui sera évaluable par la librairie nbgrader, il faut indiquer dans le notebook quelles cellules contiennent des réponses et combien de points elles valent. 
Pour cela, aller dans le menu Affichage -> Barre d'outil de cellules -> Create Assignment. Des bandeaux bleus apparaissent au-dessus des cellules dans lesquels un barême peut être préciser. 

Il est conseillé de mettre la cellule en mode 
* "Read only" si elle contient du simple texte, 
* "Manually graded task" si elle contient des consignes, 
* "Autograded answer" si elle contient des réponses sous forme de code,
* "Autograded test" si elle contient des tests pour la notation automatique,
* "Manually graded answer" si elle contient des réponses sous forme de texte.

Toute cellule contenant des réponses doit avoir les réponses à retirer placées entre les balises `### BEGIN SOLUTION ... ### END SOLUTION`. 

L'enseignant peut aussi donner des indications de notations à ces collègues dans les cellules de consigne avec les balises `### BEGIN MARK SCHEME ... ### END MARK SCHEME`.

Concernant les tests, il faut les penser le plus robuste possible et donc bien rédiger la consigne. Des tests peuvent rester visibles pour l'étudiant.
D'autres peuvent être cachés s'ils sont placés entre les balises `### BEGIN HIDDEN TESTS ... END HIDDEN TESTS`.

Pour générer la séance de cours vierge de solutions, l'enseignant tape la commande : 
```
methnum generate_assignment L1/Seance1
```
Cette commande fonctionne rarement du premier coup, car il est très facile d'oublier des balises ou d'avoir oublié de mettre une cellule en "Autograded answer" alors qu'elle contient des balises `### BEGIN SOLUTION`. Bien lire le message d'erreur
rapporté par la commande et chercher la cellule qui pose un soucis. Quand tout est prêt, la séance version enseignante est dans le dossier `source/Seance1`
tandis que la version étudiante est dans le dossier `release/Seance1`. Elle contient aussi un fichier `.gitlab-ci.yml` configurant
les étapes de l'intégration continue réalisée lors d'un `submit`. Le détail de ce fichier est éditable à la fin du fichier `__init__.py` contenu dans le dépôt https://gitlab.dsi.universite-paris-saclay.fr/MethNum/methnum.

### Distribuer une séance sur gitlab : release


Quand le sujet du cours est prêt, il faut poster les documents de la séance sans les réponses dans le groupe gitlab accessible aux étudiants :

https://gitlab.dsi.universite-paris-saclay.fr/MethNum/2020-2021/L1

Pour cela, il faut exécuter la commande suivante :
```
methnum release L1/Seance1 public/private
```
Ce script:
1. poste la séance avec solutions dans le gitlab enseignant. 
2. poste la séance sans solutions dans le gitlab étudiant
 
Si le mot "Seance" n'est pas présent dans le nom du sous-répertoire, le script propose de poster le sujet en mode private (inaccessible aux étudiants) ou public (accessible). Cela permet de tester l'envoi d'un sujet d'évaluation sans le rendre disponible. 
Ne pas oublier de reposter le sujet une dernière fois en mode public pour le rendre accessible !

Vérifier ici https://gitlab.dsi.universite-paris-saclay.fr/MethNum/2020-2021/L1 :
1. que le sujet est bien posté
2. **qu'il ne contient pas les solutions !**

Le fait de poster sur le gitlab enseignant exécute un script d'intégration continue `.gitlab-ci.yml`, lequel lance le script `make_website.sh`.
Ce dernier génère le site web associé au cours à la volée avec le nouveau contenu. L'URL du site web est donné dans la page web du dépôt enseignant, pui Settings -> Pages.

Quelques scripts supplémentaires peuvent aider à la création de contenus.

#### remove_solution

Ce script exécute simplement les deux premières étapes du script ``generate_assignment`` avec une nomenclature plus souple, pour par exemple créer des projets python sous forme de jupyter notebook sans leurs solutions et sans nécessité de le poster. La syntaxe est :
```
methnum remove_solution MONSUJET
```
où MONSUJET est un dossier contenant le ou les notebooks dont on veut retirer les solutions.

#### convert_beamer_to_ipynb

Ce paragraphe ne concerne que les séances qui sont en format latex et doivent être converties en jupyter notebook.
```
convert_beamer_to_ipynb -f Seance1/SEANCE_1.tex --title "Séance 1 : types et variables"
```
Cette commande produit le fichier Markdown `Seance1/SEANCE_1.md`. Il y a probablement des erreurs de conversion à reprendre, mais en général il vaut mieux simplifier la structure de la slide du .tex et recommencer la conversion jusqu'à obtenir un résultat convenable.

Pour information, ce script est utilisé actuellement pour générer le site web du cours à partir des fichiers latex.


### Commencer une nouvelle année 

Pour commencer une nouvelle année, il faut créer un nouveau groupe `20XX-20XX+1` sur gitlab https://gitlab.dsi.universite-paris-saclay.fr/MethNum.
Puis créer les sous-groupes par filière `L1`, `L2` et `L3`. Ces dépôts doivent être publics. Ensuite, rajouter les enseignants en tant que membres du groupe principal
`20XX-20XX+1`, avec le statut de Développeur. Dans les dépôts enseignants, rajouter le groupe `20XX-20XX+1` en tant que membre du dépôt.

Puis dans les scripts de l'UE (https://gitlab.dsi.universite-paris-saclay.fr/MethNum/methnum), éditer la fin du fichier `__init__.py` avec les nouvelles informations.

On peut toujours rajouter des enseignants en cours d'année, en les invitant au groupe principal `20XX-20XX+1`. En revanche, ainsi ils n'auront pas accès aux dépôts étudiants postés **avant** leur inscription. Pour leur donner cet accès **a posteriori**, recopier ce script, l'adapter et le lancer de n'importe quelle plateforme avec `methnum`:
```
from methnum import course

group = "LDD-STAPS"  # le nom du groupe
assignments = ["L2/Seance3", "L2/Seance4", "L2/DM1"]  # les seances anterieures a l'inscription
for assignment in assignments:
    course.ensure_instructor_access(assignment, student_group=group)
```


## FAQ

- Dans une salle de cours, en lançant `methnum jupyter lab` Firefox renvoie une page d'erreur disant ne pas pouvoir se connecter. Que fais-je?

*Il faut aller dans les Préférences de Firefox, menu Général et tout en bas Paramètres Réseau. Cliquer sur Paramètres et Détection automatique du proxy. Relancer la commande.*

- La commande `methnum jupyter notebook` renvoie 

        [NotebookApp] The version of the Assignment List nbextension does not match the server extension; the nbextension version is 0.5.5 while the server version is 0.6.0.dev. This can happen if you have recently upgraded nbgrader, and may cause this extension to not work correctly. To fix the problem, please see the nbgrader installation instructions: http://nbgrader.readthedocs.io/en/stable/user_guide/installation.html
        
    Que faire ?
    
*Lancer `methnum update`.*   

- En lançant l'autograde, le terminal m'informe que la correction a échoué pour certaines copies. Comment investiguer ?

*Ouvrir l'interface de correction avec `methnum jupyter lab`, onglet Formgrader puis cliquer sur le nombre de soumissions du devoir.
Les copies en question indiquent "needs autograding". Pour chacune d'entre elles, cliquer sur le petit éclair bleu (qui lance l'autograde) à droite et étudier les messages d'erreur. Réparer la copie en la retrouvant dans le dossier `submitted` et rappuyer sur l'éclair jusqu'à ce que le problème soit corrigé.*

- L'autograde me renvoie un message du type suivant. Que faire ?

        [WARNING] Attribute 'cell_type' for cell cell-7bcf63f282d8b3be has changed! (should be: code, got: markdown)
        [ERROR] There was an error processing assignment: /Users/.../submitted/groupe.prenom.nom/Seance1
        [ERROR] Traceback (most recent call last):
            [...]
            nbformat.validator.NotebookValidationError: 'id' is a required property
            
            Failed validating 'required' in notebook:
            
            On instance:
            {'cell_type': 'code',
             'execution_count': None,
             'metadata': {'deletable': False,
                          'nbgrader': {'cell_type': 'code',
                                       'checksum': 'b8b252f10b3ed0ab912009c790261954',
                                       'grade': True,
                                       'grade_id': 'cell-7bcf63f282d8b3be',
                                       'locked': False,
                                       'points': 1,
                                       'schema_version': 3,
                                       'solution': True}},
             'outputs': ['...0 outputs...'],
             'source': 'a=90\nimport math\nb=(math.pi/180)\nprint(a*b)\n'}

*La première ligne du message signifie qu'une cellule notée en tant que code a été changée par l'étudiant en markdown. La dernière ligne du message donne idée du contenu de la cellule fautive, et le grade_id son numéro.
  Ouvrir le notebook problématique, avec l'affichage de l'interface nbgrader : Affichage -> Barre d'outil de cellule -> Create Assignment. Chercher la cellule incriminée portant le grade_id du messsage d'erreur et le contenu indiqué. Changer son type en code (menu déroulant Markdown), sauvegarder la copie et relancer l'autograde.*

- L'autograde me renvoie un message du type suivant. Que faire ?

        [AutogradeApp | INFO] Converting notebook /builds/prenom.nom/MethNum-L1-Seance1/submitted/prenom.nom/Seance1/TD1.ipynb
        [AutogradeApp | WARNING] Cell with id 'cell-0dfd76d62c0f40f2' exists multiple times!
        [AutogradeApp | WARNING] Attribute 'checksum' for cell cell-9cfba94efb70a639 has changed! (should be: 18570bd54e48c8ab4f372594127fdfb7, got: 3b743df83e44762f3895e6aa7e195b8f)
        [AutogradeApp | WARNING] Attribute 'checksum' for cell cell-0e1be44ae6598166 has changed! (should be: 189286c222d66b26a16d86d8d147df84, got: 524b43ad1a6532257309e7824ad3120a)
        ...
        [AutogradeApp | WARNING] Attribute 'checksum' for cell cell-580cf6b6893a7258 has changed! (should be: e4b39430d4055c5379a33aef4e55f1da, got: bf22dd41ab8bb922288c3ca510552f3d)
        [AutogradeApp | WARNING] Removing failed assignment: /builds/alex.pierron/MethNum-L3-Seance4/autograded/alex.pierron/Seance4
        [AutogradeApp | ERROR] One or more notebooks in the assignment use an old version 
            of the nbgrader metadata format. Please **back up your class files 
            directory** and then update the metadata using:
      
            nbgrader update .
      
*Hélas la dernière ligne ne donne pas la bonne manière de corriger ce soucis. En revanche, la seconde avec `cell exists multiple times` est le vrai problème.
Ouvrir le notebook problématique, avec l'affichage de l'interface nbgrader : Affichage -> Barre d'outil de cellule -> Create Assignment. Chercher la cellule incriminée portant le grade_id du message d'erreur et le contenu indiqué. Une fois la cellule en double repérée, ouvrir le notebook version MarkDown avec un éditeur de texte de votre choix et supprimer la cellule en double. Relancer l'autograde.*



## License

Le contenu de ce projet est soumis à la licence [BSD 3-clause "New"](LICENSE).

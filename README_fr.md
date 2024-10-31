<!-- LANGUAGE_LINKS_START -->
[🇩🇪 German](README_de.md) | [🇬🇧 English](README_en.md) | [🇪🇸 Spanish](README_es.md) | <span style="color: grey;">🇫🇷 French</span> | [🇮🇹 Italian](README_it.md)
<!-- LANGUAGE_LINKS_END -->

# Script pour extraire et réécrire les référentiels Git

L'objectif principal de ce script était de restaurer la structure des référentiels d'origine, qui étaient à l'origine exploités comme des sous-modules mais ont été convertis en référentiels monstres monolithiques par les opérateurs de fork. De tels flux de travail rendent pratiquement impossible l'annulation des modifications de ces forks ou ne peuvent être mis en œuvre que très difficilement via une fusion, un rebase ou un choix privilégié.

Ce script offre la possibilité d'extraire ces référentiels à partir de sous-répertoires. Les référentiels ainsi créés peuvent ensuite être intégrés dans les référentiels du sous-module d'origine de la même manière que les référentiels distants. Cependant, ceux-ci divergent généralement. Par conséquent, les fusions ne fonctionnent toujours pas, du moins pas sans effort. Afin de protéger l’historique local des validations de fusion inutiles et de maintenir l’historique linéaire, une sélection manuelle est généralement recommandée.

Étant donné que l'automatisation à l'aide de Migit est également possible pour mettre automatiquement en miroir les forks, vous pouvez renoncer à utiliser directement les référentiels réels et utiliser uniquement les versions miroir converties.

Migit s'appuie sur l'outil « git-filter-repo » pour recycler tous les sous-dossiers d'un référentiel monolithique dans le modèle de référentiel d'origine. Des référentiels entiers peuvent également être réécrits.
Les messages de validation sont réécrits ou complétés autant que possible en utilisant des conventions de format communes, les identifiants de validation sont ajustés et, si nécessaire, le contenu original des validations est ajouté. Les références aux commits sources vers les référentiels sources sont insérées dans les commits réécrits, ce qui garantit une meilleure traçabilité, par exemple des cerises pioches. Les référentiels extraits sont stockés en fonction de leur nom dans un dossier de déploiement et en tant que sauvegarde avec un horodatage en tant que référentiels distincts. Pendant le processus de déploiement, un lien symbolique sans horodatage est toujours créé vers le dernier référentiel extrait. Les référentiels ainsi créés peuvent, par exemple, être traités automatiquement comme miroirs ou traités ultérieurement selon les besoins. 

Cependant, un problème demeure : les opérateurs de fork n'ont peut-être utilisé que des fusions sur les sous-modules d'origine pour se faciliter les choses, ce qui peut même avoir été fait automatiquement ou avec le support de scripts, ou les référentiels ont été arbitrairement initialisés à partir d'un niveau de version arbitraire à un moment donné. indiquer. À long terme, cela crée inévitablement un désordre complexe dans l’histoire des forks. De plus, il peut y avoir une culture des commits bâclée et malheureusement il n’existe pas de véritable remède à cela, ce qui signifie que ces commits ne peuvent être optimisés que dans une mesure limitée en termes de contenu. Malheureusement, ce gâchis de backport ne peut être résolu que partiellement, voire pas du tout, en supprimant les commits vides ou dégénérés, au moins en les organisant chronologiquement et en appliquant certaines conventions de formatage courantes.

# Contenu

  * [Exigences](#exigences)
  * [Utilisation](#utiliser)
  * [Options](#possibilités)
  * [Exemples](#exemples)

## Exigences

Le script nécessite l'outil git-filter-repo. Assurez-vous qu'il est installé. Voir : https://github.com/newren/git-filter-repo#how-do-i-install-it
```bash
  * git >= 2.24.0
  * python3 >= 3.5
  * wget
```

## utiliser

### ./migit -u <clone url> [OPTIONS]
 
Spécifiez l'URL de clonage du référentiel Git à réécrire.
Si l'URL est le premier argument, la spécification de l'indicateur « -u » peut être omise.
```bash
 ./migit <clone url> [OPTIONS]
```
Les protocoles pris en charge sont http, https, git et ssh. Pour les chemins locaux, n'utilisez pas file://, juste le chemin relatif vers le référentiel ! 

## Possibilités

### -P, --prefix-source-url=<PREFIX> # à partir de la version 0.8
 
Modèle de préfixe d'URL pour l'URL de validation source. Ceci définit le lien vers la validation source à laquelle l'ID de validation sera ajouté.
L'URL du préfixe est généralement obtenue automatiquement à partir de l'URL du clone, seule l'accessibilité étant vérifiée.
Si cela échoue, ceci sera affiché. Dans un tel cas, aucun commit source n'est entré dans les commits réécrits et il est recommandé de définir le paramètre dans ce cas.
Un avis :
--pattern-source-url=<PREFIX> est obsolète, mais est toujours utilisable en raison de la rétrocompatibilité !

Exemple : un lien vers un commit sur GitHub se compose généralement de l'adresse de base du projet respectif et du hachage du commit.
```bash
 https://github.com/tuxbox-fork-migrations/migit/commit/942564882104d6de56eb817e6c5bbc3d4e66a5a3
```
Le paramètre doit alors être spécifié comme suit :
```bash
 -P https://github.com/tuxbox-fork-migrations/migit/commit
```
Un avis :
Il convient également de noter que l'extraction de l'adresse de base à partir de référentiels locaux ou d'URL ne fonctionne pas pour les protocoles ssh ou git. Si un lien de validation source est souhaité,
Le paramètre doit donc toujours être défini explicitement pour garantir que l'adresse de base est correctement installée. Sinon, la ligne du lien ne sera pas saisie.

### -T, --target-root-project-name=<NAME>
Nom du dossier cible dans le dossier de déploiement.
Par défaut : nom du projet cloné et horodatage de la réécriture. Par défaut, le nom du projet est généré à partir de l'URL de clonage.

### -p, --project-name-prefix=<PREFIX>
Préfixe du dossier cible qui précède le nom du référentiel extrait.

### -s, --project-name-suffix=<SUFFIX>
Suffixe du dossier de destination ajouté au nom du référentiel extrait.

### -S, --sous-répertoire
Sous-répertoire à extraire.
Si un référentiel doit être complètement réécrit, ce paramètre peut simplement être omis ou simplement préciser un point :
```bash
 --subdir .
#oder
  -S .
```
### --subdir-list='<LIST>'
Liste des sous-répertoires à réécrire. La liste du répertoire doit être entourée des apostrophes 'sub1 sub2...'.                       
Les espaces sont des séparateurs. 
Par défaut : tous les sous-répertoires de premier niveau du répertoire racine.
                                  
### --exclude-subdir-list='<LIST>'
Liste des sous-répertoires à ne pas extraire. La liste doit être entourée des apostrophes 'subx suby...'. L'espace comme séparateur.
L'option --subdir ne doit pas être définie ici ! 

### --commit-introduction=<PATTERN>
Introductions de validation de modèle sur la première ligne de chaque validation réécrite. Par défaut : le nom du sous-répertoire respectif ou le nom du dépôt d'origine.
Cela est particulièrement logique si des sous-répertoires sont extraits et qu'une introduction uniforme au message de validation est généralement souhaitée.

### --commit-suffix=<SUFFIX>
Ajoute une signature (au sens d'un suffixe) à la fin de chaque message de validation modifié.

### -d, --deploy-dir=<DIR>
Répertoire cible (dossier de déploiement) dans lequel les référentiels réécrits sont stockés. Par défaut : ./deploy

### -q
Supprime l'affichage de la progression. Cela a du sens si le script doit être exécuté automatiquement, par exemple dans des tâches cron. Dans ce mode, le script renvoie également EXIT_STATUTS 0 en cas d'erreurs,
afin que le script n'abandonne pas d'éventuelles tâches automatisées dans lesquelles il est intégré, des processus plus complexes. Seuls les journaux d'état contenant des informations sur l'appel et les messages d'erreur sont générés. Ces sorties peuvent également être utilisées pour la journalisation.

### --id-rsa-file=<PATH>
Chemin relatif vers le fichier de clé privée SSH

### --réinitialiser
Réinitialise tous les messages de validation réécrits. Cela signifie que les entrées que Migit a saisies dans les commits seront à nouveau supprimées. Les descriptions des e-mails et des auteurs ne sont pas affectées.
Il convient de noter que Migit ne peut réinitialiser que les entrées effectuées par Migit lui-même. Tout ce qui a été saisi dans les messages de validation sous « Origin commit data » est donc supprimé. 

### --branch-list=<'BRANCH1 BRANCH2 ...'>
Spécifie une ou plusieurs branches à traiter. Par défaut, toutes les branches du référentiel source sont réécrites.

### --replace-refs {delete-no-add, delete-and-add, update-no-add, update-or-add, update-and-add}
Ces options déterminent la manière dont les références de remplacement sont gérées une fois les validations modifiées :

`delete-no-add` : Toutes les références de remplacement existantes seront supprimées et aucune nouvelle ne sera ajoutée.
`delete-and-add` : les références de remplacement existantes sont supprimées, mais de nouvelles sont ajoutées pour chaque réécriture de validation.
`update-no-add` : les références de remplacement existantes seront mises à jour pour pointer vers les nouveaux hachages de validation, mais aucun nouveau ne sera ajouté.
`update-or-add` : les nouvelles références de remplacement sont ajoutées uniquement pour les validations qui ne sont pas utilisées pour mettre à jour une référence de remplacement existante. Les existants sont mis à jour.
`update-and-add` : les références de remplacement existantes sont mises à jour et de nouvelles références de remplacement sont ajoutées pour chaque réécriture de validation.

Par défaut, update-and-add est utilisé si $GIT_DIR/filter-repo/already_ran n'existe pas, sinon update-or-add.
Par défaut, cette option, même si elle est définie sur visible, garantit généralement que les références qui pointent vers d'autres commits via leur ID de commit, par exemple dans les messages de commit, sont ajustées en conséquence afin qu'elles ne pointent pas.
À titre d'exemple, il peut y avoir une validation qui est l'annulation d'une autre validation. Lors de l'annulation, Git inclut généralement toujours l'ID de validation de la validation annulée dans le message de validation.
Cela serait également ajusté afin que la référence continue de pointer vers le commit approprié.
Les références déjà rompues, telles que celles créées lors de la sélection de commits contenant un ID de commit, ne peuvent pas être restaurées.


### --prune-empty {toujours, auto, jamais}

Cette option contrôle si et comment les commits vides sont supprimés :

`always` : supprime toujours tous les commits vides.

`auto` : (par défaut) : supprime uniquement les commits qui deviennent vides à la suite de la réécriture (pas ceux qui étaient déjà vides dans le dépôt d'origine, sauf si leur commit parent a été supprimé).

`ever` : ne supprime jamais les commits vides.

Lorsque le parent d'un commit est supprimé, le premier ancêtre non supprimé devient le nouveau commit parent.

### --prune-degenerate {toujours, auto, jamais}
Cette option gère spécifiquement les commits de fusion qui pourraient être « dégénérés » en supprimant d'autres commits :

`always` : supprime tous les commits de fusion dégénérés.

`auto` : (Par défaut) : supprime uniquement les validations de fusion qui ont été dégénérées par l'édition (pas celles qui ont déjà été dégénérées à l'origine).

`never` : ne supprime pas les validations de fusion dégénérées.

Une validation de fusion est considérée comme dégénérée si elle a moins de deux parents, si une validation assume les deux rôles de parent ou si l'un des parents est l'ancêtre de l'autre.

### --non-ff
Cette option affecte le comportement de --prune-degenerate et est utile dans les projets qui utilisent toujours --no-ff (pas d'avance rapide). Cela empêche la suppression du premier commit parent même s'il devient l'ancêtre d'un autre parent.


## Exemples

### Extraire tous les sous-répertoires d'un référentiel
```bash
./migit -u https://github.com/example/repository.git
```
Les commits sont généralement réécrits comme ceci :
```bash
subdir1: this is a commit message
    
    
    Origin commit data
    ------------------
    Branch: refs/heads/master
    Author: john doe <jd@gmx.de>
    Date: 2020-06-02 (Tue, 02 Jun 2020)
    
    Origin message was:
    ------------------
    - this is a commit message
```

### Extraire un sous-répertoire spécifique d'un référentiel en spécifiant le commit source
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1 --commit-suffix='Automatically migrated by Migit'
```
Les commits sont réécrits comme ceci :
```bash
    subdir1: small fixes for something
    
    
    Origin commit data
    ------------------
    Branch: refs/heads/master
    Commit: https://github.com/example/repository/commit/fc0a536efa2aa3598c294b2c9030d2844f970be9
    Author: john doe <jd@gmx.de>
    Date: 2023-06-10 (Sat, 10 Jun 2023)
    
    Origin message was:
    ------------------
    - small fixes for something
    
    ------------------
    Automatically migrated by Migit

```

### Extraire plusieurs sous-répertoires d'un référentiel en spécifiant le commit source
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir-list='subdir1 subdir2'
```
Les commits sont réécrits comme dans l'exemple précédent, mais cette fois pour des sous-répertoires spécifiques.

### Extraire les sous-répertoires d'un référentiel, mais exclure certains sous-répertoires, en spécifiant la validation source
```bash
./migit-u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --exclude-subdir-list='subdir1 subdir2'
```
Les commits sont réécrits comme dans l'exemple précédent mais tous les sous-répertoires à l'exception de subdir1 et subdir2 sont extraits.

### Extraire les sous-répertoires des niveaux plus profonds d'un référentiel, en spécifiant la validation source
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1/nextdir/tool
```
Les commits sont réécrits comme dans l'exemple précédent mais seul le sous-répertoire 'tool' est extrait.

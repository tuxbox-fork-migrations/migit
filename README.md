# Script zur Extraktion und Umschreibung von Git-Repositories

Das Hauptziel dieses Skripts besteht darin, ursprüngliche als Submodule betriebene Repositories, die zu einem monolithischen Repository geforkt wurden, wieder in ihre ursprüngliche Struktur zurückzuführen. Wenn Änderungen in Forks von dort mit Cherry-Picks zurückgeführt werden sollen, gestaltet sich dies oft als umständlich und fehleranfällig. Merges funktionieren dann generell überhaupt nicht mehr.

Dieses Skript bietet so eine Möglichkeit, die zurückportierten Repositories, wie Remote-Repositories in lokale Repositories einzubinden. Dies ähnelt dem Verknüpfen als Tracking-Branch, allerdings divergieren diese in der Regel. Daher funktionieren Merges normalerweise generell nicht, zumindest nicht ohne gewissen Aufwand. Um die lokale Historie vor unnötigen Merge-Commits zu bewahren und die Historie linear zu halten, ist manuelles Cherry-Picking zu empfehlen.

Da sich eine Automatisierung anbietet, um Forks migriert zu spiegeln, kann man so auf die direkte Verwendung der originalen Fork-Repositories verzichten und stattdessen nur die migrierten Spiegel-Versionen nutzen.

Verwendet wird das Tool "git-filter-repo", um Unterordner von einem monolithischen Repository zurück in das ursprüngliche Repository-Modell zu migrieren. Es können auch ganze Repositories migriert werden. Dabei werden die Commit-Messages so weit wie möglich mit gängigen Formatkonventionen umgeschrieben und die ursprünglichen Inhalte der Commits ergänzend eingepflegt. Optional kann ein Verweis auf die Quellcommits der Forks in die umgeschriebenen Commits eingefügt werden. Die migrierten Repositories werden in einem Deploy-Ordner namentlich und mit Zeitstempel als separate Repositories abgelegt. Beim Deploy-Vorgang wird zudem immer ein Symlink ohne Zeitstempel auf das zuletzt migrierte Projekt angelegt. Diese können beispielsweise automatisiert als Spiegel oder je nach Bedarf weiterverarbeitet werden. 

Ein Problem besteht allerdings darin, dass Forkbetreiber möglicherweise, um es sich vermeintlich einfach zu machen nur Merges verwended haben. Und das möglicherweise sogar automatisiert oder scriptgestützt, oder die Repositories wurden irgendwann willkürlich von einem beliebigen Versionsstand initialisiert, ohne die Historie vollständig zu übernehmen. Dadurch sind über kurz oder lang keine Fastforward-Merges mehr möglich. Jeder nicht Fast-forward-Merge erzeugt zudem einen Merge-Commit, was auf Dauer zwangsläufig zu einer komplexen Unordnung führt. Leider lässt sich diese Unordnung bei der Rückportierung, wenn überhaupt, nur teilweise beheben, aber zumindest chronologisch einordnen.


# Inhalt

  * [Voraussetzungen](#voraussetzungen)
  * [Verwendung](#verwendung)
  * [Optionen](#optionen)
  * [Beispiele](#beispiele)

## Voraussetzungen

Das Skript erfordert das Tool git-filter-repo. Stelle sicher, dass es installiert ist. Siehe: https://github.com/newren/git-filter-repo#how-do-i-install-it
  * git >= 2.24.0
  * python3 >= 3.5

## Verwendung
Clone URL des Git-Repositories angeben, welches umgeschrieben werden soll.
```
 -u <clone url> [options]
```

## Optionen
* Muster-Präfix für Quellcommit URL. Dies legt die Eintragung für den Link zum Quellcommit fest, die der Commit-ID vorangestellt wird.
```
 -P, --pattern-source-url=<pattern>
```


* Name des Zielordners innerhalb des Deploy-Ordners. Standard: Name des geklonten Projekts und Zeitstempel der Umschreibung. Der Projektname wird standardmäßig aus der Clone-URL generiert.
```
 -T, --target-root-project-name=<name>
```


* Prefix des Zielordners das dem extrahierten Repository-Namen vorangestellt wird.
```
 -p, --project-name-prefix=<prefix>
```


* Suffix des Zielordners das dem extrahierten Repository-Namen angehängt wird.
```    
 -s, --project-name-suffix=<suffix>
```


* Unterverzeichnis das umgeschrieben werden soll.
```
 -S, --subdir
```
Soll ein Repository komplett umgeschrieben werden, dann nur einen Punkt ohne weitere Verzeichnisse angeben:
```
--subdir .
```

* Liste von Unterverzeichnissen, die umgeschrieben werden sollen. Verzeichnisliste muss mit Apostrophen 'sub1 sub2 ...' umgeben sein.                       
Leerzeichen sind Trennzeichen (Standard: Alle Unterverzeichnisse der ersten Ebene innerhalb des Stammverzeichnisses)
```                                        
 --subdir-list='<list>'
```


* Liste von Unterverzeichnissen, die nicht extrahiert werden sollen. Liste muss mit Apostrophen 'subx suby ...' umgeben sein. Leerzeichen als Trennzeichen.
```                                       
 --exclude-subdir-list='<list>'
```            


* Muster für Commit Einleitungen in der ersten Zeile aller Commits. Standard: der jeweilige Unterverzeichnisname bzw. der Original-Reponame.
Dies macht Sinn, wenn generell eine einheitliche Einleitung der Commit-Nachricht gewünscht ist.
```
 --commit-introduction=<pattern>
```


* Ausgabeverzeichnis (Deploy-Ordner) in welches die umgeschriebenen Repositories abgelegt werden. Standard: ./deploy
```
 -d, --deploy-dir=<dir>
```


## Beispiele

### Alle Unterverzeichnisse eines Repositories extrahieren
```
./migit -u https://github.com/example/repository.git
```
Commits werden so umgeschrieben:
```
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

### Bestimmtes Unterverzeichnisse eines Repositories extrahieren mit Angabe des Quellcommits
```
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1
```
Commits werden so umgeschrieben:
```
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
```

### Mehrere Unterverzeichnisse eines Repositories extrahieren mit Angabe des Quellcommits
```
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir-list='subdir1 subdir2'
```
Commits werden wie im vorherigen Beispiel umgeschrieben jedoch diesmal für bestimmte Unterverzeichnisse.


### Unterverzeichnisse eines Repositories extrahieren, aber bestimmte Unterverzeichnisse ausschließen, mit Angabe des Quellcommits
```
./migit-u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --exclude-subdir-list='subdir1 subdir2'
```
Commits werden wie im vorherigen Beispiel umgeschrieben jedoch werden alle Unterverzeichnisse außer subdir1 und subdir2 extrahiert.


### Unterverzeichnisse aus tieferen Ebenen eines Repositories extrahieren, mit Angabe des Quellcommits
```
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1/nextdir/tool
```
Commits werden wie im vorherigen Beispiel umgeschrieben jedoch wird das Unterverzeichnisse 'tool' extrahiert.
 

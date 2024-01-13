# Script zur Extraktion und Umschreibung von Git-Repositories

Das Hauptziel dieses Skripts war es, die Struktur von originalen Repositories wiederherzustellen, welche ursprünglich als Submodule betrieben wurden, aber von Forkbetreibern in monolithische Monster-Repositories umgewandelt wurden. Diese Art der Handhabung kann beim Zurückführen von Änderungen problematisch sein. Merges sind generell danach nicht mehr oder nur schwer möglich, da die Historie nach solchen Änderungen wahrscheinlich immer differieren wird. Zudem ist es oft umständlich und fehleranfällig, Änderungen mit Cherry-Picks von solchen Forks zurückzuführen.

Dieses Skript bietet die Möglichkeit, solche Repositories wieder zurück zuportierten und ähnlich wie bei der Anbindung als Tracking-Branches wie Remote-Repositories in lokale Submodul-Repositories bzw. normale Repositorioes einzubinden. Allerdings divergieren diese in der Regel. Daher funktionieren Merges normalerweise in der Regel generell nach wie vor nicht, zumindest nicht ohne gewissen Aufwand. Um die lokale Historie vor unnötigen Merge-Commits zu bewahren und die Historie linear zu halten, ist daher generell manuelles Cherry-Picking zu empfehlen.

Da sich auch eine Automatisierung mit Hilfe von Migit anbietet, um Forks migriert zu spiegeln, kann man so auf die direkte Verwendung der eigentlichen Repositories verzichten und stattdessen nur die konvertierten Spiegel-Versionen nutzen.

Migit setzt auf das Tool "git-filter-repo" auf, um beliebige Unterordner von einem monolithischen Repository zurück in das ursprüngliche Repository-Modell zu recyclen. Es können auch ganze Repositories umgewandelt werden.
Commit-Messages werden so weit wie möglich mit gängigen Formatkonventionen umgeschrieben und, sofern diese abweichend sind, die ursprünglichen Inhalte der Commits ergänzend eingepflegt. Optional kann ein Verweis auf die Quellcommits aus den Fork-Repositories in die umgeschriebenen Commits eingefügt werden. Die migrierten Repositories werden dem Namen entsprechend in einem Deploy-Ordner und als Backup mit Zeitstempel als separate Repositories abgelegt. Beim Deploy-Vorgang wird zudem immer ein Symlink ohne Zeitstempel auf das zuletzt migrierte Projekt angelegt. Die so erzeugten Repositories können so beispielsweise automatisiert als Spiegel oder je nach Bedarf weiterverarbeitet werden. 

Ein Problem besteht allerdings unverändert darin, dass Forkbetreiber möglicherweise, um es sich vermeintlich einfach zu machen nur Merges auf die Original-Submodule verwendet haben. Dies wird möglicherweise sogar automatisiert oder scriptgestützt erledigt, oder die Repositories wurden irgendwann willkürlich von einem beliebigen Versionsstand initialisiert, ohne die Historie vollständig zu übernehmen. Dadurch sind über kurz oder lang keine Fastforward-Merges mehr möglich. Jeder nicht Fastforward-Merge erzeugt zudem einen Merge-Commit, was auf Dauer zwangsläufig zu einer komplexen Unordnung in den Forks geführt habe dürfte. Dazu kann sich noch schlampige Commitkultur gesellen und dagegen ist auch nicht wirklich ein Kraut gewachsen, so das sich diese Commits inhaltlich nur beschränkt optimieren lassen. Leider lässt sich diese Unordnung bei der Rückportierung, wenn überhaupt, nur teilweise beheben, aber zumindest chronologisch einordnen und einige gängige Formatkonventionen anwenden.


# Inhalt

  * [Voraussetzungen](#voraussetzungen)
  * [Verwendung](#verwendung)
  * [Optionen](#optionen)
  * [Beispiele](#beispiele)

## Voraussetzungen

Das Skript erfordert das Tool git-filter-repo. Stelle sicher, dass es installiert ist. Siehe: https://github.com/newren/git-filter-repo#how-do-i-install-it
  * git >= 2.24.0
  * python3 >= 3.5
  * wget

## Verwendung

```bash
 ./migit -u <clone url> [OPTIONS]
 
```
Clone URL des Git-Repositories angeben, welches umgeschrieben werden soll.
Wenn die URL das erste Argument ist, dann kann die Angabe des Flags '-u' weggelassen werden.
```bash
 ./migit <clone url> [OPTIONS]
 
```
Als Protokolle werden http, https, git und ssh unterstützt. Für lokale Pfade, verwende nicht file://, sondern nur den relativen Pfad zum Repository! 


## Optionen

```bash
 -P, --prefix-source-url=<PREFIX> # ab Version 0.8
 # --pattern-source-url=<PREFIX> ist veraltet, ist aber wegen der Abwärtskompatiblität weiterhin verwendbar!
```
Muster für URL-Präfix für die Quellcommit URL. Dies legt den Link zum Quellcommit fest, an den die Commit-ID angehängt wird.
Die Prefix-URL wird normalerweise automatisch aus der Klon-URL gewonnen, wobei lediglich die Erreichbarkeit geprüft wird.
Sollte dies fehlschlagen, wird dies angezeigt. In solch einem Fall, werden in die umgeschriebenen Commits auch keine Quellcommits eingetragen und es disem Fall empfehlenswert den Parameter zu setzen.

Beispiel: Ein Link zu einem Commit bei GitHub setzt sich generell aus der Basisadresse zum jeweiligen Projekt und dem Commit-Hash zusammen.
```bash
 https://github.com/tuxbox-fork-migrations/migit/commit/942564882104d6de56eb817e6c5bbc3d4e66a5a3
```

Der Parameter sollte dann entsprechend so angegeben werden:
```bash
 -P https://github.com/tuxbox-fork-migrations/migit/commit
```

Zu beachten wäre noch, dass die Extraktion der Basisadresse aus lokalen Repositorys oder URL's für ssh- bzw. git-Protolle in der Regel nicht funktioniert. Wenn ein Quell-Commit Link gwünscht ist,
muss der Parameter explizit immer gesetzt werden, um sicherzustellen, dass die Basisadresse korrekt eingebaut wird. Andernfalls wird die Zeile für den Link nicht eingetragen.


```bash
 -T, --target-root-project-name=<NAME>
```
Name des Zielordners innerhalb des Deploy-Ordners. Standard: Name des geklonten Projekts und Zeitstempel der Umschreibung. Der Projektname wird standardmäßig aus der Clone-URL generiert.


```bash
 -p, --project-name-prefix=<PREFIX>
```
Prefix des Zielordners das dem extrahierten Repository-Namen vorangestellt wird.


```bash    
 -s, --project-name-suffix=<SUFFIX>
```
Suffix des Zielordners das dem extrahierten Repository-Namen angehängt wird.


```bash
 -S, --subdir
```
Unterverzeichnis das umgeschrieben werden soll.
Soll ein Repository komplett umgeschrieben werden, kann dieser Parameter einfach weggelassen werden oder einfach nur einen Punkt angeben:
```bash
 --subdir .
#oder
  -S .
```
Liste von Unterverzeichnissen, die umgeschrieben werden sollen. Verzeichnisliste muss mit Apostrophen 'sub1 sub2 ...' umgeben sein.                       
Leerzeichen sind Trennzeichen (Standard: Alle Unterverzeichnisse der ersten Ebene innerhalb des Stammverzeichnisses)
```bash                                        
 --subdir-list='<LIST>'
```


```bash                                       
 --exclude-subdir-list='<LIST>'
```            
Liste von Unterverzeichnissen, die nicht extrahiert werden sollen. Liste muss mit Apostrophen 'subx suby ...' umgeben sein. Leerzeichen als Trennzeichen.
Die Option --subdir darf hier nicht gesetzt sein! 


```bash
 --commit-introduction=<PATTERN>
```
Muster für Commit Einleitungen in der ersten Zeile jedes umgeschriebenen Commits. Standard: der jeweilige Unterverzeichnisname bzw. der Original-Reponame.
Dies macht vorallem Sinn wenn Unterverzeichnisse extrahiert werden und generell eine einheitliche Einleitung der Commit-Nachricht gewünscht ist.


```bash
 --commit-suffix=<SUFFIX>
```
Fügt eine Signatur (im Sinne eines Suffix') an das Ende jeder modifizierten Commit Message an.


```bash
 -d, --deploy-dir=<DIR>
```
Zielverzeichnis (Deploy-Ordner) in das die umgeschriebenen Repositories abgelegt werden. Standard: ./deploy


```bash
 -q
```
Unterdrückt die Fortschrittsanzeige. Dies ist sinnvoll, wenn das Script automatisiert ausgeführt werden soll, z.B. in Cron-Jobs. Das Skript gibt außerdem in diesem Modus bei Fehlern den EXIT_STAUTS 0 zurück,
damit das Skript mögliche automatisierte Aufgaben in dem es eingebettet ist, komplexere Vorgänge nicht abbricht. Es werden lediglich nur Statusprotokolle ausgegeben, die Angaben zum Aufruf und Fehlermeldungen enthalten. Diese Ausgaben können zur Protollierung weiter verwendet werden.


```bash
 --id-rsa-file=<PATH>
```
Relativer Pfad zur Privaten ssh Keydatei


```bash
 --reset
```
Setzt alle umgeschriebenen Commit-Messages wieder zurück. Das bedeutet, dass die Einträge, welche Migit in die Commits eingetragen hat, wieder entfernt werden. E-Mail- und Autoren-Umschreibungen bleiben unberührt.
Zu beachten ist, dass Migit nur Eintragungen zurücksetzen kann, die von Migit selbst vorgenommen wurden. Es wird daher alles entfernt, was innerhalb der Commit-Messages unter "Origin commit data" eingetragen wurde. 


```bash
 --braanch-list=<'BRANCH1 BRANCH2 ...'>
```
Legt einen oder mehrere Branches fest, die verarbeitet werden sollen. Standardmäßig werden alle Branches aus dem Quellrepository umgeschrieben.


```bash
 --replace-refs {delete-no-add, delete-and-add, update-no-add, update-or-add, update-and-add}
```
Diese Optionen bestimmen, wie mit Ersatz-Referenzen (replace refs) nach der Bearbeitung von Commits umgegangen wird:
```
    delete-no-add: 	Alle bestehenden Ersatz-Referenzen werden gelöscht, und es werden keine neuen hinzugefügt.
    delete-and-add: 	Bestehende Ersatz-Referenzen werden gelöscht, aber für jede Commit-Neuschreibung werden neue hinzugefügt.
    update-no-add: 	Bestehende Ersatz-Referenzen werden aktualisiert, um auf die neuen Commit-Hashes zu zeigen, aber es werden keine neuen hinzugefügt.
    update-or-add: 	Neue Ersatz-Referenzen werden nur für die Commits hinzugefügt, die nicht zur Aktualisierung einer bestehenden Ersatz-Referenz verwendet werden. Bestehende werden aktualisiert.
    update-and-add: 	Bestehende Ersatz-Referenzen werden aktualisiert, und es werden neue Ersatz-Referenzen für jede Commit-Neuschreibung hinzugefügt.
```
Standardmäßig wird update-and-add verwendet, wenn $GIT_DIR/filter-repo/already_ran nicht existiert, sonst update-or-add.
Diese Option sorgt standardmäßig, auch wenn sie sicht gesetzt ist, normalerweise dafür, dass Referenzen die z.B. in Commit-Nachrichten auf andere Commits über Ihre Commit-ID verweisen, entsprechend angepasst werden, so dass diese nicht verweisen.
Als Beispiel könnte ein Commit existieren, der ein Revert eines anderen Commits ist. Git trägt bei einem Revert normalerweise immer die Commit-ID des zurückgenommenen Commits in die Commit-Nachricht ein.
Diese würde also ebenso angepasst werden, so dass der Verweis weiterhin auf den passenden Commit zeigt.
Bereits kaputte Referenzen, wie sie z.B, entstehen wenn Cherry-Picks von Commits gemacht wurden, die eine Commit-ID enthalten, können nicht wieder hergestellt werden.


```bash
 --prune-empty {always, auto, never}
```
Diese Option steuert, ob und wie leere Commits entfernt werden:
```
	always: 		Entfernt immer alle leeren Commits.
	auto (Standard): 	Entfernt nur Commits, die durch die Neuschreibung leer werden (nicht solche, die im Original-Repo bereits leer waren, es sei denn, ihr Eltern-Commit wurde entfernt).
	never: 			Entfernt niemals leere Commits.
```
Wenn der Eltern-Commit eines Commits entfernt wird, wird der erste nicht entfernte Vorfahre zum neuen Eltern-Commit.


```bash
 --prune-degenerate {always, auto, never}
```
Diese Option behandelt speziell Merge-Commits, die durch das Entfernen anderer Commits "entartet" sein könnten:

	always: 		Entfernt alle entarteten Merge-Commits.
	auto (Standard): 	Entfernt nur Merge-Commits, die durch die Bearbeitung entartet sind (nicht solche, die schon ursprünglich entartet waren).
	never: 			Entfernt keine entarteten Merge-Commits.

Ein Merge-Commit gilt als entartet, wenn er weniger als zwei Eltern hat, ein Commit beide Elternrollen einnimmt, oder ein Elternteil Vorfahre des anderen ist.


```bash
 --no-ff
```
Diese Option beeinflusst das Verhalten von --prune-degenerate und ist nützlich in Projekten, die immer Merge-Commits mit --no-ff (no fast-forward) verwenden. Sie verhindert das Entfernen des ersten Eltern-Commits, selbst wenn er ein Vorfahre eines anderen Elternteils wird.


## Beispiele

### Alle Unterverzeichnisse eines Repositories extrahieren
```bash
./migit -u https://github.com/example/repository.git
```
Commits werden generell so umgeschrieben:
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

### Bestimmtes Unterverzeichnis eines Repositories extrahieren mit Angabe des Quellcommits
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1 --commit-suffix='Automatically migrated by Migit'
```
Commits werden so umgeschrieben:
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

### Mehrere Unterverzeichnisse eines Repositories extrahieren mit Angabe des Quellcommits
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir-list='subdir1 subdir2'
```
Commits werden wie im vorherigen Beispiel umgeschrieben jedoch diesmal für bestimmte Unterverzeichnisse.


### Unterverzeichnisse eines Repositories extrahieren, aber bestimmte Unterverzeichnisse ausschließen, mit Angabe des Quellcommits
```bash
./migit-u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --exclude-subdir-list='subdir1 subdir2'
```
Commits werden wie im vorherigen Beispiel umgeschrieben jedoch werden alle Unterverzeichnisse außer subdir1 und subdir2 extrahiert.


### Unterverzeichnisse aus tieferen Ebenen eines Repositories extrahieren, mit Angabe des Quellcommits
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1/nextdir/tool
```
Commits werden wie im vorherigen Beispiel umgeschrieben jedoch wird das Unterverzeichnisse 'tool' extrahiert.
 

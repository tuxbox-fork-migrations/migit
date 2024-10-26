<!-- LANGUAGE_LINKS_START -->
[🇩🇪 German](README_de.md) | [🇬🇧 English](README_en.md) | [🇪🇸 Spanish](README_es.md) | [🇫🇷 French](README_fr.md) | <span style="color: grey;">🇮🇹 Italian</span>
<!-- LANGUAGE_LINKS_END -->

# Script per estrarre e riscrivere i repository Git

L'obiettivo principale di questo script era ripristinare la struttura dei repository originali, che originariamente erano gestiti come sottomoduli ma sono stati convertiti in repository mostruosi monolitici dagli operatori fork. Tali flussi di lavoro rendono praticamente impossibile annullare le modifiche apportate a tali fork o possono essere implementati solo con grande difficoltà tramite unione, rebase o cherry pick.

Questo script offre la possibilità di estrarre tali repository dalle sottodirectory. I repository creati in questo modo possono poi essere integrati nei repository del sottomodulo originale in modo simile ai repository remoti. Tuttavia, questi di solito divergono. Pertanto, le fusioni generalmente non funzionano ancora, almeno non senza un certo sforzo. Per proteggere la cronologia locale da commit di unione non necessari e per mantenere la cronologia lineare, si consiglia generalmente la selezione manuale.

Poiché l'automazione con l'aiuto di Migit è anche possibile per eseguire automaticamente il mirroring dei fork, è possibile rinunciare direttamente all'utilizzo dei repository effettivi e utilizzare invece solo le versioni mirror convertite.

Migit si affida allo strumento "git-filter-repo" per riciclare eventuali sottocartelle da un repository monolitico nel modello di repository originale. È anche possibile riscrivere interi repository.
I messaggi di commit vengono riscritti o integrati il ​​più possibile utilizzando convenzioni di formato comuni, gli ID di commit vengono modificati e, se necessario, viene aggiunto il contenuto originale dei commit. I riferimenti ai commit di origine ai repository di origine vengono inseriti nei commit riscritti, il che garantisce una migliore tracciabilità, ad esempio dei cherry pick. I repository estratti vengono archiviati in base al loro nome in una cartella di distribuzione e come backup con un timestamp come repository separati. Durante il processo di distribuzione, viene sempre creato un collegamento simbolico senza timestamp all'ultimo repository estratto. I repository così creati possono, ad esempio, essere elaborati automaticamente come mirror o ulteriormente elaborati secondo necessità. 

Tuttavia, rimane un problema: gli operatori fork potrebbero aver utilizzato le fusioni sui sottomoduli originali solo per rendere le cose apparentemente facili per loro stessi, il che potrebbe anche essere stato fatto automaticamente o con il supporto di script, o i repository sono stati inizializzati arbitrariamente da un livello di versione arbitrario in alcuni casi. punto. Alla lunga, ciò crea inevitabilmente un complesso disordine nella storia delle forcelle. Inoltre, può esserci una cultura dei commit sciatta e sfortunatamente non esiste una vera cura per questo, il che significa che questi commit possono essere ottimizzati solo in misura limitata in termini di contenuto. Sfortunatamente, questo pasticcio del backport può essere risolto solo parzialmente, se non del tutto, rimuovendo commit vuoti o degenerati, almeno organizzandoli cronologicamente e applicando alcune convenzioni di formattazione comuni.


# Contenuto

  * [Requisiti](#requisiti)
  * [Utilizzo](#utilizzo)
  * [Opzioni](#opzioni)
  * [Esempi](#esempi)

## Requisiti

Lo script richiede lo strumento git-filter-repo. Assicurati che sia installato. Vedi: https://github.com/newren/git-filter-repo#how-do-i-install-it
  *git >= 2.24.0
  *python3 >= 3.5
  * a causa di

## utilizzo


### ./migit -u <URL clone> [OPZIONI]
 
Specificare l'URL clone del repository Git da riscrivere.
Se l'URL è il primo argomento, è possibile omettere la specifica del flag '-u'.
```bash
 ./migit <clone url> [OPTIONS]
```
I protocolli supportati sono http, https, git e ssh. Per i percorsi locali, non utilizzare file://, solo il percorso relativo al repository! 


## Opzioni

### -P, --prefix-source-url=<PREFIX> # dalla versione 0.8
 
Modello del prefisso URL per l'URL di commit di origine. Imposta il collegamento al commit di origine a cui verrà aggiunto l'ID commit.
L'URL del prefisso viene solitamente ottenuto automaticamente dall'URL clone, controllando solo l'accessibilità.
Se fallisce, verrà visualizzato. In tal caso, nei commit riscritti non viene inserito alcun commit di origine e in questo caso si consiglia di impostare il parametro.
Un avviso:
--pattern-source-url=<PREFIX> è deprecato, ma è ancora utilizzabile grazie alla compatibilità con le versioni precedenti!

Esempio: un collegamento a un commit su GitHub è generalmente costituito dall'indirizzo di base del rispettivo progetto e dall'hash del commit.
```bash
 https://github.com/tuxbox-fork-migrations/migit/commit/942564882104d6de56eb817e6c5bbc3d4e66a5a3
```
Il parametro deve quindi essere specificato come segue:
```bash
 -P https://github.com/tuxbox-fork-migrations/migit/commit
```
Un avviso:
Va inoltre notato che l'estrazione dell'indirizzo di base da repository o URL locali non funziona per i protocolli ssh o git. Se si desidera un collegamento di commit di origine,
Il parametro deve quindi essere sempre impostato esplicitamente per garantire che l'indirizzo di base sia installato correttamente. In caso contrario non verrà inserita la riga per il collegamento.


### -T, --target-root-nome-progetto=<NOME>
Nome della cartella di destinazione all'interno della cartella di distribuzione.
Predefinito: nome del progetto clonato e timestamp della riscrittura. Per impostazione predefinita, il nome del progetto viene generato dall'URL del clone.


### -p, --prefisso-nome-progetto=<PREFIX>
Prefisso della cartella di destinazione che precede il nome del repository estratto.

   
### -s, --suffisso-nome-progetto=<SUFFISSO>
Suffisso della cartella di destinazione aggiunto al nome del repository estratto.


### -S, --sottodir
Sottodirectory da estrarre.
Se un repository deve essere completamente riscritto, questo parametro può essere semplicemente omesso o specificare solo un punto:
```bash
 --subdir .
#oder
  -S .
```

### --subdir-list='<LIST>'
Elenco delle sottodirectory da riscrivere. L'elenco delle directory deve essere racchiuso tra apostrofi 'sub1 sub2...'.                       
Gli spazi sono separatori. 
Impostazione predefinita: tutte le sottodirectory di primo livello all'interno della directory root.

                                      
### --exclude-subdir-list='<LIST>'
Elenco delle sottodirectory da non estrarre. L'elenco deve essere racchiuso tra apostrofi 'subx suby...'. Lo spazio come separatore.
L'opzione --subdir non deve essere impostata qui! 


### --commit-introduction=<MODELLO>
Introduzioni del commit del modello sulla prima riga di ogni commit riscritto. Predefinito: il rispettivo nome della sottodirectory o il nome del repository originale.
Ciò ha particolarmente senso se vengono estratte sottodirectory e generalmente si desidera un'introduzione uniforme al messaggio di commit.


### --commit-suffix=<SUFFISSO>
Aggiunge una firma (nel senso di un suffisso) alla fine di ogni messaggio di commit modificato.


### -d, --deploy-dir=<DIR>
Directory di destinazione (cartella di distribuzione) in cui sono archiviati i repository riscritti. Impostazione predefinita: ./deploy


### -Q
Sopprime la visualizzazione dell'avanzamento. Ciò ha senso se lo script deve essere eseguito automaticamente, ad es. nei lavori cron. In questa modalità lo script restituisce anche EXIT_STAUTS 0 in caso di errori,
in modo che lo script non interrompa eventuali attività automatizzate in cui è incorporato, processi più complessi. Vengono emessi solo i registri di stato contenenti informazioni sulla chiamata e messaggi di errore. Queste uscite possono essere ulteriormente utilizzate per la registrazione.


### --id-rsa-file=<PERCORSO>
Percorso relativo al file della chiave ssh privata


### --reset
Reimposta tutti i messaggi di commit riscritti. Ciò significa che le voci che Migit ha inserito nei commit verranno nuovamente rimosse. Le e-mail e le descrizioni dell'autore rimangono inalterate.
Va notato che Migit può ripristinare solo le voci effettuate da Migit stessa. Tutto ciò che è stato inserito nei messaggi di commit alla voce “Dati commit origine” viene quindi rimosso. 


### --branch-list=<'RAMICO1 RAMO2 ...'>
Specifica uno o più rami da elaborare. Per impostazione predefinita, tutti i rami del repository di origine vengono riscritti.


### --replace-refs {elimina-non-aggiungi, elimina-e-aggiungi, aggiorna-no-aggiungi, aggiorna-o-aggiungi, aggiorna-e-aggiungi}
Queste opzioni determinano come vengono gestiti i riferimenti sostitutivi dopo la modifica dei commit:
```
delete-no-add: 	Alle bestehenden Ersatz-Referenzen werden gelöscht, und es werden keine neuen hinzugefügt.
delete-and-add: Bestehende Ersatz-Referenzen werden gelöscht, aber für jede Commit-Neuschreibung werden neue hinzugefügt.
update-no-add: 	Bestehende Ersatz-Referenzen werden aktualisiert, um auf die neuen Commit-Hashes zu zeigen, aber es werden keine neuen hinzugefügt.
update-or-add: 	Neue Ersatz-Referenzen werden nur für die Commits hinzugefügt, die nicht zur Aktualisierung einer bestehenden Ersatz-Referenz verwendet werden. Bestehende werden aktualisiert.
update-and-add: Bestehende Ersatz-Referenzen werden aktualisiert, und es werden neue Ersatz-Referenzen für jede Commit-Neuschreibung hinzugefügt.
```
Per impostazione predefinita, viene utilizzato update-and-add se $GIT_DIR/filter-repo/already_ran non esiste, altrimenti update-or-add.
Per impostazione predefinita, questa opzione, anche se è impostata su visibile, in genere garantisce che i riferimenti che puntano ad altri commit tramite il loro ID commit, ad esempio nei messaggi di commit, vengano modificati di conseguenza in modo che non puntino.
Ad esempio, potrebbe esserci un commit che rappresenta il ripristino di un altro commit. Durante il ripristino, Git solitamente include sempre l'ID di commit del commit ripristinato nel messaggio di commit.
Anche questo verrebbe modificato in modo che il riferimento continui a puntare al commit appropriato.
I riferimenti già interrotti, come quelli creati durante la selezione dei commit che contengono un ID commit, non possono essere ripristinati.


### --prune-empty {sempre, automatico, mai}

Questa opzione controlla se e come vengono rimossi i commit vuoti:
```
always: 	 Entfernt immer alle leeren Commits.
auto (Standard): Entfernt nur Commits, die durch die Neuschreibung leer werden (nicht solche, die im Original-Repo bereits leer waren, es sei denn, ihr Eltern-Commit wurde entfernt).
never: 		 Entfernt niemals leere Commits.
```
Quando il commit principale di un commit viene rimosso, il primo antenato non rimosso diventa il nuovo commit principale.


### --prune-degenerate {sempre, automatico, mai}
Questa opzione gestisce specificamente i commit di unione che potrebbero essere "degenerati" rimuovendo altri commit:
```
always: 	 Entfernt alle entarteten Merge-Commits.
auto (Standard): Entfernt nur Merge-Commits, die durch die Bearbeitung entartet sind (nicht solche, die schon ursprünglich entartet waren).
never: 		 Entfernt keine entarteten Merge-Commits.
```
Un commit di unione è considerato degenerato se ha meno di due genitori, un commit assume entrambi i ruoli di genitore o un genitore è un antenato dell'altro.


### --no-ff
Questa opzione influenza il comportamento di --prune-degenerate ed è utile nei progetti che utilizzano sempre i commit di unione --no-ff (nessun avanzamento rapido). Impedisce la rimozione del commit del primo genitore anche se diventa un antenato di un altro genitore.


## Esempi

### Estrai tutte le sottodirectory di un repository
```bash
./migit -u https://github.com/example/repository.git
```
I commit vengono generalmente riscritti in questo modo:
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

### Estrai una sottodirectory specifica di un repository specificando il commit di origine
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1 --commit-suffix='Automatically migrated by Migit'
```
I commit vengono riscritti in questo modo:
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

### Estrai più sottodirectory di un repository specificando il commit di origine
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir-list='subdir1 subdir2'
```
I commit vengono riscritti come nell'esempio precedente, ma questa volta per sottodirectory specifiche.


### Estrai le sottodirectory di un repository, ma escludi alcune sottodirectory, specificando il commit di origine
```bash
./migit-u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --exclude-subdir-list='subdir1 subdir2'
```
I commit vengono riscritti come nell'esempio precedente ma vengono estratte tutte le sottodirectory tranne subdir1 e subdir2.


### Estrai sottodirectory dai livelli più profondi di un repository, specificando il commit di origine
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1/nextdir/tool
```
I commit vengono riscritti come nell'esempio precedente ma viene estratta la sottodirectory 'tool'.

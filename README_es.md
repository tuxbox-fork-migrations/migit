<!-- LANGUAGE_LINKS_START -->
[🇩🇪 German](README_de.md) | [🇬🇧 English](README_en.md) | <span style="color: grey;">🇪🇸 Spanish</span> | [🇫🇷 French](README_fr.md) | [🇮🇹 Italian](README_it.md)
<!-- LANGUAGE_LINKS_END -->

# Script para extraer y reescribir repositorios Git

El objetivo principal de este script era restaurar la estructura de los repositorios originales, que originalmente funcionaban como submódulos pero que los operadores de bifurcación los convirtieron en monstruosos repositorios monolíticos. Dichos flujos de trabajo hacen que sea prácticamente imposible revertir los cambios de dichas bifurcaciones o solo pueden implementarse con gran dificultad mediante fusión, rebase o selección selectiva.

Este script proporciona la capacidad de extraer dichos repositorios de subdirectorios. Los repositorios creados de esta manera se pueden integrar en los repositorios del submódulo original de forma similar a los repositorios remotos. Sin embargo, estos suelen divergir. Por lo tanto, las fusiones generalmente todavía no funcionan, al menos no sin un poco de esfuerzo. Para proteger el historial local de confirmaciones de fusión innecesarias y mantener el historial lineal, generalmente se recomienda la selección manual.

Dado que la automatización con la ayuda de Migit también es posible para reflejar automáticamente las bifurcaciones, puede renunciar al uso de los repositorios reales directamente y, en su lugar, utilizar solo las versiones reflejadas convertidas.

Migit se basa en la herramienta "git-filter-repo" para reciclar cualquier subcarpeta de un repositorio monolítico al modelo de repositorio original. También se pueden reescribir repositorios completos.
Los mensajes de confirmación se reescriben o complementan tanto como sea posible utilizando convenciones de formato comunes, se ajustan los ID de confirmación y, si es necesario, se agrega el contenido original de las confirmaciones. Las referencias a las confirmaciones de origen a los repositorios de origen se insertan en las confirmaciones reescritas, lo que garantiza una mejor trazabilidad, por ejemplo, de selecciones selectas. Los repositorios extraídos se almacenan según su nombre en una carpeta de implementación y como una copia de seguridad con una marca de tiempo como repositorios separados. Durante el proceso de implementación, siempre se crea un enlace simbólico sin marca de tiempo al último repositorio extraído. Los repositorios así creados pueden, por ejemplo, procesarse automáticamente como mirrors o procesarse posteriormente según sea necesario. 

Sin embargo, persiste un problema: es posible que los operadores de bifurcación solo hayan utilizado fusiones en los submódulos originales para facilitarles las cosas, lo que incluso puede haber sido hecho automáticamente o con soporte de script, o que los repositorios se inicializaron arbitrariamente desde un nivel de versión arbitrario en algún momento. punto. A la larga, esto crea inevitablemente un desorden complejo en la historia de las bifurcaciones. Además, puede haber una cultura de confirmación descuidada y desafortunadamente no existe una cura real para esto, lo que significa que estas confirmaciones solo se pueden optimizar hasta cierto punto en términos de contenido. Desafortunadamente, este desorden de backport sólo puede solucionarse parcialmente, en todo caso, eliminando confirmaciones vacías o degeneradas, al menos organizándolas cronológicamente y aplicando algunas convenciones de formato comunes.


# Contenido

  * [Requisitos](#requisitos)
  * [Uso](#usar)
  * [Opciones](#opciones)
  * [Ejemplos](#ejemplos)

## Requisitos

El script requiere la herramienta git-filter-repo. Asegúrate de que esté instalado. Ver: https://github.com/newren/git-filter-repo#how-do-i-install-it
  *git>= 2.24.0
  * python3 >= 3.5
  * debido a

## usar


### ./migit -u <clon URL> [OPCIONES]
 
Especifique la URL de clonación del repositorio Git que se va a reescribir.
Si la URL es el primer argumento, se puede omitir la especificación del indicador '-u'.
```bash
 ./migit <clone url> [OPTIONS]
```
Los protocolos soportados son http, https, git y ssh. Para rutas locales, no use file://, ¡solo la ruta relativa al repositorio! 


## Opciones

### -P, --prefix-source-url=<PREFIX> # desde la versión 0.8
 
Patrón de prefijo de URL para la URL de confirmación de origen. Esto establece el enlace a la confirmación de origen a la que se agregará el ID de confirmación.
La URL del prefijo normalmente se obtiene automáticamente de la URL clonada, comprobando únicamente la accesibilidad.
Si esto falla, esto se mostrará. En tal caso, no se ingresan confirmaciones de origen en las confirmaciones reescritas y se recomienda establecer el parámetro en este caso.
Un aviso:
--pattern-source-url=<PREFIX> está en desuso, pero aún se puede utilizar debido a la compatibilidad con versiones anteriores.

Ejemplo: un enlace a una confirmación en GitHub generalmente consta de la dirección base del proyecto respectivo y el hash de confirmación.
```bash
 https://github.com/tuxbox-fork-migrations/migit/commit/942564882104d6de56eb817e6c5bbc3d4e66a5a3
```
Luego, el parámetro debe especificarse de la siguiente manera:
```bash
 -P https://github.com/tuxbox-fork-migrations/migit/commit
```
Un aviso:
También cabe señalar que extraer la dirección base de los repositorios locales o de las URL no funciona para los protocolos ssh o git. Si se desea un enlace de confirmación de fuente,
Por lo tanto, el parámetro siempre debe configurarse explícitamente para garantizar que la dirección base esté instalada correctamente. De lo contrario, no se ingresará la línea para el enlace.


### -T, --target-root-project-name=<NOMBRE>
Nombre de la carpeta de destino dentro de la carpeta de implementación.
Valor predeterminado: nombre del proyecto clonado y marca de tiempo de la reescritura. De forma predeterminada, el nombre del proyecto se genera a partir de la URL del clon.


### -p, --prefijo-nombre-proyecto=<PREFIJO>
Prefijo de la carpeta de destino que precede al nombre del repositorio extraído.

   
### -s, --project-name-suffix=<SUFIJO>
Sufijo de la carpeta de destino añadido al nombre del repositorio extraído.


### -S, --subdirectorio
Subdirectorio a extraer.
Si se va a reescribir un repositorio por completo, este parámetro puede simplemente omitirse o simplemente especificar un punto:
```bash
 --subdir .
#oder
  -S .
```

### --subdir-list='<LISTA>'
Lista de subdirectorios que se reescribirán. El listado del directorio debe estar rodeado por apóstrofes 'sub1 sub2...'.                       
Los espacios son separadores. 
Valor predeterminado: todos los subdirectorios de primer nivel dentro del directorio raíz.

                                      
### --exclude-subdir-list='<LISTA>'
Lista de subdirectorios que no se extraerán. La lista debe estar rodeada por apóstrofes 'subx suby...'. El espacio como separador.
¡La opción --subdir no debe configurarse aquí! 


### --commit-introduction=<PATRÓN>
Introducciones de confirmación de patrón en la primera línea de cada confirmación reescrita. Valor predeterminado: el nombre del subdirectorio respectivo o el nombre del repositorio original.
Esto tiene especial sentido si se extraen subdirectorios y generalmente se desea una introducción uniforme al mensaje de confirmación.


### --commit-suffix=<SUFIJO>
Agrega una firma (en el sentido de un sufijo) al final de cada mensaje de confirmación modificado.


### -d, --deploy-dir=<DIR>
Directorio de destino (carpeta de implementación) en el que se almacenan los repositorios reescritos. Valor predeterminado: ./deploy


### -q
Suprime la visualización del progreso. Esto tiene sentido si el script se va a ejecutar automáticamente, por ejemplo en trabajos cron. En este modo, el script también devuelve EXIT_STAUTS 0 en caso de errores,
para que el script no aborte posibles tareas automatizadas en las que esté incrustado, procesos más complejos. Sólo se generan registros de estado que contienen información sobre la llamada y mensajes de error. Estas salidas se pueden utilizar aún más para el registro.


### --id-rsa-file=<RUTA>
Ruta relativa al archivo de clave ssh privada


### --reiniciar
Restablece todos los mensajes de confirmación reescritos. Esto significa que las entradas que Migit ingresó en las confirmaciones se eliminarán nuevamente. Las descripciones de correo electrónico y de autor no se ven afectadas.
Cabe señalar que Migit solo puede restablecer las entradas realizadas por el propio Migit. Por lo tanto, se elimina todo lo que se ingresó en los mensajes de confirmación en "Datos de confirmación de origen". 


### --branch-list=<'SUCURSAL1 SUCURSAL2...'>
Especifica una o más ramas que se procesarán. De forma predeterminada, se reescriben todas las ramas del repositorio de origen.


### --reemplazar-refs {eliminar-no-agregar, eliminar-y-agregar, actualizar-no-agregar, actualizar-o-agregar, actualizar-y-agregar}
Estas opciones determinan cómo se manejan las referencias de reemplazo después de editar las confirmaciones:
```
delete-no-add: 	Alle bestehenden Ersatz-Referenzen werden gelöscht, und es werden keine neuen hinzugefügt.
delete-and-add: Bestehende Ersatz-Referenzen werden gelöscht, aber für jede Commit-Neuschreibung werden neue hinzugefügt.
update-no-add: 	Bestehende Ersatz-Referenzen werden aktualisiert, um auf die neuen Commit-Hashes zu zeigen, aber es werden keine neuen hinzugefügt.
update-or-add: 	Neue Ersatz-Referenzen werden nur für die Commits hinzugefügt, die nicht zur Aktualisierung einer bestehenden Ersatz-Referenz verwendet werden. Bestehende werden aktualisiert.
update-and-add: Bestehende Ersatz-Referenzen werden aktualisiert, und es werden neue Ersatz-Referenzen für jede Commit-Neuschreibung hinzugefügt.
```
De forma predeterminada, se usa actualizar y agregar si $GIT_DIR/filter-repo/already_ran no existe; de ​​lo contrario, actualizar o agregar.
De forma predeterminada, esta opción, incluso si está configurada como visible, generalmente garantiza que las referencias que apuntan a otras confirmaciones a través de su ID de confirmación, por ejemplo en mensajes de confirmación, se ajusten en consecuencia para que no apunten.
Por ejemplo, podría haber una confirmación que sea una reversión de otra confirmación. Al revertir, Git generalmente siempre incluye el ID de confirmación de la confirmación revertida en el mensaje de confirmación.
Esto también se ajustaría para que la referencia continúe apuntando al compromiso apropiado.
Las referencias que ya están rotas, como las creadas cuando se seleccionan confirmaciones que contienen un ID de confirmación, no se pueden restaurar.


### --prune-empty {siempre, auto, nunca}

Esta opción controla si se eliminan las confirmaciones vacías y cómo:
```
always: 	 Entfernt immer alle leeren Commits.
auto (Standard): Entfernt nur Commits, die durch die Neuschreibung leer werden (nicht solche, die im Original-Repo bereits leer waren, es sei denn, ihr Eltern-Commit wurde entfernt).
never: 		 Entfernt niemals leere Commits.
```
Cuando se elimina la confirmación principal de una confirmación, el primer ancestro no eliminado se convierte en la nueva confirmación principal.


### --prune-degenerate {siempre, auto, nunca}
Esta opción maneja específicamente las confirmaciones de fusión que podrían "degenerarse" al eliminar otras confirmaciones:
```
always: 	 Entfernt alle entarteten Merge-Commits.
auto (Standard): Entfernt nur Merge-Commits, die durch die Bearbeitung entartet sind (nicht solche, die schon ursprünglich entartet waren).
never: 		 Entfernt keine entarteten Merge-Commits.
```
Una confirmación de fusión se considera degenerada si tiene menos de dos padres, una confirmación asume ambos roles de padre o si uno de los padres es antepasado del otro.


### --no-ff
Esta opción afecta el comportamiento de --prune-degenerate y es útil en proyectos que siempre usan confirmaciones de combinación --no-ff (sin avance rápido). Previene la eliminación de la confirmación del primer padre incluso si se convierte en antepasado de otro padre.


## Ejemplos

### Extraer todos los subdirectorios de un repositorio
```bash
./migit -u https://github.com/example/repository.git
```
Las confirmaciones generalmente se reescriben así:
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

### Extraiga un subdirectorio específico de un repositorio especificando la confirmación de origen
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1 --commit-suffix='Automatically migrated by Migit'
```
Las confirmaciones se reescriben así:
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

### Extraiga varios subdirectorios de un repositorio especificando la confirmación de origen
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir-list='subdir1 subdir2'
```
Las confirmaciones se reescriben como en el ejemplo anterior, pero esta vez para subdirectorios específicos.


### Extraiga subdirectorios de un repositorio, pero excluya ciertos subdirectorios, especificando la confirmación de origen
```bash
./migit-u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --exclude-subdir-list='subdir1 subdir2'
```
Las confirmaciones se reescriben como en el ejemplo anterior, pero se extraen todos los subdirectorios excepto subdir1 y subdir2.


### Extraiga subdirectorios de niveles más profundos de un repositorio, especificando la confirmación de origen
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1/nextdir/tool
```
Las confirmaciones se reescriben como en el ejemplo anterior pero se extrae el subdirectorio 'herramienta'.

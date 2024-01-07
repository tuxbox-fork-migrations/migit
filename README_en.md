# Script for extracting and rewriting Git repositories

The main goal of this script was to restore the structure of original repositories, which were originally operated as submodules but were converted into monolithic monster repositories by fork operators. This type of handling can be problematic when rolling back changes. Merges are generally no longer possible or only possible with difficulty, as the history will probably always differ after such changes. In addition, it is often cumbersome and error-prone to transfer changes with cherry picks from such forks.

This script offers the possibility of reporting such repositories back and integrating them into local submodule repositories or normal repositories, similar to the connection as tracking branches such as remote repositories. However, these usually diverge. Therefore, merges still generally don't work, at least not without some effort. In order to protect the local history from unnecessary merge commits and to keep the history linear, manual cherry picking is generally recommended.

Since automation with the help of Migit is also possible to mirror migrated forks, you can avoid using the original fork repositories directly and instead only use the converted mirror versions.

Migit relies on the "git-filter-repo" tool to recycle arbitrary subfolders from a monolithic repository back into the original repository model. Entire repositories can also be converted.
Commit messages are rewritten as far as possible using common format conventions and, if they differ, the original content of the commits is added in addition. Optionally, a reference to the source commits from the fork repositories can be included in the rewritten commits. The migrated repositories are stored in a deploy folder according to the name and as a backup with a time stamp as separate repositories. During the deployment process, a symlink without a timestamp is always created to the last migrated project. The repositories created in this way can, for example, be processed automatically as mirrors or further processed as required.

However, one problem remains that fork operators may have only used merges on the original submodules to make things supposedly easy for themselves. This may even be done automatically or scripted, or the repositories may have been arbitrarily initialized from an arbitrary version level at some point without fully inheriting the history. As a result, fast forward merges will no longer be possible sooner or later. Every non-fastforward merge also creates a merge commit, which in the long run would inevitably lead to complex disorder in the forks. In addition, there can be a sloppy commit culture and there is not really a cure for this, meaning that these commits can only be optimized to a limited extent in terms of content. Unfortunately, this mess can only be partially remedied when backporting, if at all, but at least it can be arranged chronologically and some common format conventions can be applied.


# Contents

  * [Requirements](#requirements)
  * [Usage](#Usage)
  * [options](#options)
  * [Examples](#examples)

## Requirements

The script requires the git-filter-repo tool. Make sure it is installed. See: https://github.com/newren/git-filter-repo#how-do-i-install-it
  * git >= 2.24.0
  * python3 >= 3.5
  * due to

## Use
Specify the clone URL of the Git repository to be rewritten.
```bash
 ./migit -u <clone url> [OPTIONS]
```
If the URL is the first argument, then specifying the '-u' flag can be omitted.
```bash
 ./migit <clone url> [OPTIONS]
```
The protocols supported are http, https, git and ssh. For local paths, only use the relative path to the repository!

## Options
* Pattern for URL prefix for the source commit URL. This sets the link to the source commit to which the commit ID will be appended.
```bash
 -P, --prefix-source-url=<PREFIX> # from version 0.8
 # --pattern-source-url=<PREFIX> is deprecated, but is still usable due to backwards compatibility!
```
The prefix URL is usually obtained automatically from the clone URL, with only accessibility being checked.
If this fails, this will be displayed. In such a case, no source commits are entered into the rewritten commits and it is recommended to set the parameter.

Example: A link to a commit on GitHub generally consists of the base address of the respective project and the commit hash.
```bash
 https://github.com/tuxbox-fork-migrations/migit/commit/942564882104d6de56eb817e6c5bbc3d4e66a5a3
```
The parameter should then be specified as follows:
```bash
 -P https://github.com/tuxbox-fork-migrations/migit/commit
```
It should also be noted that extracting the base address from local repositories or URLs for ssh or git protocols usually does not work. If a source commit link is desired,
The parameter must be set explicitly to ensure that the base address is installed correctly. Otherwise the line for the link will not be entered.


* Name of the target folder within the deploy folder. Default: Name of the cloned project and timestamp of the rewrite. By default, the project name is generated from the clone URL.
```bash
 -T, --target-root-project-name=<NAME>
```


* Destination folder prefix that precedes the extracted repository name.
```bash
 -p, --project-name-prefix=<PREFIX>
```


* Destination folder suffix appended to the extracted repository name.
```bash
 -s, --project-name-suffix=<SUFFIX>
```


* Subdirectory to be rewritten.
```bash
 -S, --subdir
```
If a repository is to be completely rewritten, this parameter can simply be omitted or just specify one point:
```bash
 --subdir .
#or
  -S.
```

* List of subdirectories to be rewritten. Directory listing must be surrounded by apostrophes 'sub1 sub2...'.
Spaces are separators (default: all first-level subdirectories within the root directory)
```bash
 --subdir-list='<LIST>'
```


* List of subdirectories not to be extracted. List must be surrounded by apostrophes 'subx suby...'. Space as a separator.
```bash
 --exclude-subdir-list='<LIST>'
```


* Sample commit introductions on the first line of each rewritten commit. Default: the respective subdirectory name or the original repo name.
This especially makes sense if subdirectories are extracted and a uniform introduction to the commit message is generally desired.
```bash
 --commit-introduction=<PATTERN>
```


* Adds a signature (in the sense of a suffix) to the end of each modified commit message.
```bash
 --commit-suffix=<SUFFIX>
```

* Output directory (deploy folder) in which the rewritten repositories are stored. Default: ./deploy
```bash
 -d, --deploy-dir=<DIR>
```

* Suppresses the progress bar. This makes sense if the script is to be executed automatically, e.g. in cron jobs. In this mode, the script also returns EXIT_STAUTS 0 in the event of errors,
so that the script does not abort possible automated tasks in which it is embedded, more complex processes. Only status logs are output, which contain information about the call and error messages. These outputs can be further used for logging.
```bash
 -q
```

* Relative path to the private ssh key file
```bash
 --id-rsa-file=<PATH>
```


## Examples

### Extract all subdirectories of a repository
```bash
./migit -u https://github.com/example/repository.git
```
Commits are generally rewritten like this:
```bash
subdir1: this is a commit message
    
    
    Origin commit data
    ------------------
    Branch: refs/heads/master
    Author: john doe <jd@gmx.de>
    Date: 2020-06-02 (Tue, 02 Jun 2020)
    
    Origin message what:
    ------------------
    - this is a commit message
```

### Extract specific subdirectory of a repository specifying the source commit
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1 --commit-suffix=' Automatically migrated by Migit'
```
Commits are rewritten like this:
```bash
    subdir1: small fixes for something
    
    
    Origin commit data
    ------------------
    Branch: refs/heads/master
    Commit: https://github.com/example/repository/commit/fc0a536efa2aa3598c294b2c9030d2844f970be9
    Author: john doe <jd@gmx.de>
    Date: 2023-06-10 (Sat, 10 Jun 2023)
    
    Origin message what:
    ------------------
    - small fixes for something
    
    ------------------
    Automatically migrated by Migit

```

### Extract multiple subdirectories of a repository specifying the source commit
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir-list='subdir1 subdir2'
```
Commits are rewritten as in the previous example, but this time for specific subdirectories.


### Extract subdirectories of a repository, but exclude certain subdirectories, specifying the source commit
```bash
./migit-u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --exclude-subdir-list='subdir1 subdir2 '
```
Commits are rewritten as in the previous example but all subdirectories except subdir1 and subdir2 are extracted.


### Extract subdirectories from deeper levels of a repository, specifying the source commit
```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1/nextdir/tool
```
Commits are rewritten as in the previous example but the subdirectory 'tool' is extracted.
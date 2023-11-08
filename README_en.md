# Script for extracting and rewriting Git repositories

The main goal of this script was to return repositories originally operated as submodules that were forked into a monolithic repository back to their original structure. It is often cumbersome and error-prone to roll back changes from forks with cherry picks. Merges generally no longer work at all anyway.

This script offers a way to integrate the backported repositories into local repositories like remote repositories. This is similar to linking as a tracking branch. However, these usually diverge. Therefore, merges generally still don't work, at least not without some effort. In order to protect the local history from unnecessary merge commits and to keep the history linear, manual cherry picking is recommended.

Since automation is available to mirror migrated forks, you can avoid using the original fork repositories directly and instead only use the migrated mirror versions.

Migi relies on the "git-filter-repo" tool to recycle subfolders from a monolithic repository back to the original repository model. Entire repositories can also be converted. The commit messages are rewritten as much as possible using common format conventions and, if these are different, the original content of the commits is added. Optionally, a reference to the source commits of the forks can be included in the rewritten commits. The migrated repositories are stored as separate repositories by name and time stamp in a deploy folder. During the deployment process, a symlink without a time stamp is always created to the last migrated project and can, for example, be processed automatically as a mirror or further processed as required.

However, one problem remains that fork operators may have only used merges to make things supposedly easy for themselves. And this may even be automated or script-based, or the repositories were randomly initialized from an arbitrary version level at some point without fully adopting the history. As a result, fast forward merges will no longer be possible sooner or later. Every non-fast-forward merge also creates a merge commit, which inevitably leads to a complex mess in the long run. Unfortunately, this mess can only be partially remedied during the backport, if at all, but at least it can be classified chronologically.


# Contents

  * [Requirements](#requirements)
  * [Usage](#Usage)
  * [options](#options)
  * [Examples](#examples)

## Requirements

The script requires the git-filter-repo tool. Make sure it is installed. See: https://github.com/newren/git-filter-repo#how-do-i-install-it
  * git >= 2.24.0
  * python3 >= 3.5

## Use
Specify the clone URL of the Git repository to be rewritten.
```
 -u <clone url> [options]
```

## Options
* Pattern prefix for source commit URL. This specifies the entry for the link to the source commit, which is prefixed to the commit ID.
```
 -P, --pattern-source-url=<pattern>
```


* Name of the target folder within the deploy folder. Default: Name of the cloned project and timestamp of the rewrite. By default, the project name is generated from the clone URL.
```
 -T, --target-root-project-name=<name>
```


* Destination folder prefix that precedes the extracted repository name.
```
 -p, --project-name-prefix=<prefix>
```


* Destination folder suffix appended to the extracted repository name.
```
 -s, --project-name-suffix=<suffix>
```


* Subdirectory to be rewritten.
```
 -S, --subdir
```
If a repository is to be completely rewritten, then only specify one point without any additional directories:
```
--subdir .
```

* List of subdirectories to be rewritten. Directory listing must be surrounded by apostrophes 'sub1 sub2...'.
Spaces are separators (default: all first-level subdirectories within the root directory)
```
 --subdir-list='<list>'
```


* List of subdirectories not to be extracted. List must be surrounded by apostrophes 'subx suby...'. Space as a separator.
```
 --exclude-subdir-list='<list>'
```


* Pattern for commit introductions in the first line of all commits. Default: the respective subdirectory name or the original repo name.
This makes sense if you generally want a uniform introduction to the commit message.
```
 --commit-introduction=<pattern>
```


* Output directory (deploy folder) in which the rewritten repositories are stored. Default: ./deploy
```
 -d, --deploy-dir=<dir>
```

* Suppresses the progress bar
```
 -q
```


## Examples

### Extract all subdirectories of a repository
```
./migit -u https://github.com/example/repository.git
```
Commits are rewritten like this:
```
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
```
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1
```
Commits are rewritten like this:
```
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
```

### Extract multiple subdirectories of a repository specifying the source commit
```
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir-list='subdir1 subdir2'
```
Commits are rewritten as in the previous example, but this time for specific subdirectories.


### Extract subdirectories of a repository, but exclude certain subdirectories, specifying the source commit
```
./migit-u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --exclude-subdir-list='subdir1 subdir2 '
```
Commits are rewritten as in the previous example but all subdirectories except subdir1 and subdir2 are extracted.


### Extract subdirectories from deeper levels of a repository, specifying the source commit
```
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1/nextdir/tool
```
Commits are rewritten as in the previous example but the subdirectory 'tool' is extracted.
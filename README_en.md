# Script to extract and rewrite Git repositories

The main goal of this script was to revert repositories originally run as submodules that were forked into a monolithic repository back to their original structure. It often turns out to be cumbersome and error-prone when changes from forks are to be rolled back with cherry picks. Merges generally don't work anymore anyway.

This script provides such a way to mount the backported repositories, like remote repositories, into local repositories. This is similar to linking as a tracking branch. However, these usually diverge. As a result, merges generally still don't generally work, at least not without some effort. In order to protect the local history from unnecessary merge commits and to keep the history linear, manual cherry picking is recommended.

Since an automation is available to mirror migrated forks, you can do without the direct use of the original fork repositories and instead only use the migrated mirror versions.

Migi relies on the git-filter-repo tool to recycle subfolders from a monolithic repository back to the original repository model. Entire repositories can also be converted. The commit messages are rewritten as far as possible with common format conventions and, if they differ, the original content of the commit is added. Optionally, a reference to the source commits of the forks can be included in the rewritten commits. The migrated repositories are stored in a deploy folder as separate repositories with names and a time stamp. During the deploy process, a symlink without a time stamp is always created on the last migrated project and can, for example, be automatically processed as a mirror or further processed as required.

One problem, however, remains that fork operators may have only used merges to make it supposedly easy. And that may even be automated or script-supported, or the repositories were arbitrarily initialized from any version at some point without completely adopting the history. As a result, sooner or later fast-forward merges will no longer be possible. Any non-fast-forward merge also creates a merge commit, which inevitably leads to complex clutter over time. Unfortunately, this mess can only be partially fixed in the backport, if at all, but at least put it in chronological order.


# Contents

  * [requirements](#requirements)
  * [use](#use)
  * [options](#options)
  * [Examples](#examples)

## Requirements

The script requires the git-filter-repo tool. Make sure it's installed. See: https://github.com/newren/git-filter-repo#how-do-i-install-it
  * git >= 2.24.0
  * python3 >= 3.5

## Use
Specify the clone URL of the Git repository to be rewritten.
```
 -u <clone url> [options]
```

## options
* Pattern prefix for source commit URL. This specifies the entry for the link to the source commit, which is prepended to the commit ID.
```
 -P, --pattern-source-url=<pattern>
```


* Name of the target folder inside the deploy folder. Default: Cloned project name and rewrite timestamp. The project name is generated from the clone URL by default.
```
 -T, --target-root-project-name=<name>
```


* Prefix of the destination folder that will be added to the extracted repository name.
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
If a repository is to be completely rewritten, then only specify one point without further directories:
```
--subdir .
```

* List of subdirectories to be rewritten. Directory listing must be surrounded by apostrophes 'sub1 sub2 ...'.
Spaces are delimiters (default: all first-level subdirectories within the root directory)
```
 --subdir-list='<list>'
```


* List of subdirectories not to be extracted. List must be surrounded by apostrophes 'subx suby ...'. Space as separator.
```
 --exclude-subdir-list='<list>'
```


* Pattern for commit headers on the first line of all commits. Default: the respective subdirectory name or the original repo name.
This makes sense if a uniform introduction of the commit message is generally desired.
```
 --commit-introduction=<pattern>
```


* Output directory (deploy folder) in which the rewritten repositories are stored. Default: ./deploy
```
 -d, --deploy-dir=<dir>
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
    
    Origin message was:
    ------------------
    - this is a commit message
```

### Extract specific subdirectories of a repository, specifying the source commit
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
    
    Origin message was:
    ------------------
    - small fixes for something
```

### Extract multiple subdirectories of a repository specifying the source commit
```
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir-list='subdir1 subdir2'
```
Commits are rewritten as in the previous example, but this time for specific subdirectories.


### Extract subdirectories of a repository, but exclude specific subdirectories, specifying the source commit
```
./migit-u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --exclude-subdir-list='subdir1 subdir2 '
```
Commits are rewritten as in the previous example, but all subdirectories except subdir1 and subdir2 are extracted.


### Extract subdirectories from lower levels of a repository, specifying the source commit
```
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1/nextdir/tool
```
Commits are rewritten as in the previous example, but the 'tool' subdirectory is extracted.
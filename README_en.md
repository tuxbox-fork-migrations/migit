<!-- LANGUAGE_LINKS_START -->
[🇩🇪 German](README_de.md) | <span style="color: grey;">🇬🇧 English</span>
<!-- LANGUAGE_LINKS_END -->


# Script for extracting and rewriting Git repositories

Version: 0.9.39

The main goal of this script was to restore the structure of original repositories, which were originally operated as submodules but were converted into monolithic monster repositories by fork operators. Such workflows make it virtually impossible to revert changes from such forks or can only be implemented with great difficulty via merge, rebase or cherry pick.

This script provides the ability to extract such repositories from subdirectories. The repositories created in this way can then be integrated into the original submodule repositories in a similar way to remote repositories. However, these usually diverge. Therefore, merges still generally don't work, at least not without some effort. In order to protect the local history from unnecessary merge commits and to keep the history linear, manual cherry picking is generally recommended.

Since automation with the help of Migit is also possible to automatically mirror forks, you can forego using the actual repositories directly and instead only use the converted mirror versions.

Migit relies on the `git-filter-repo` tool to recycle any subfolders from a monolithic repository back into the original repository model. Entire repositories can also be rewritten.
Commit messages are rewritten or supplemented as much as possible using common format conventions, commit IDs are adjusted and, if necessary, the original content of the commits is added. References to the source commits to the source repositories are inserted into the rewritten commits, which ensures better traceability, for example of cherry picks. The extracted repositories are stored according to their name in a deploy folder and as a backup with a timestamp as separate repositories. During the deployment process, a symlink without a timestamp is always created to the last extracted repository. The repositories created in this way can, for example, be processed automatically as mirrors or further processed as required.

However, one problem remains that fork operators may have only used merges on the original submodules to make things supposedly easy for themselves, which may even have been done automatically or with script support, or the repositories were arbitrarily initialized from an arbitrary version level at some point. In the long run, this inevitably creates a complex disorder in the history of the forks. In addition, there can be a sloppy commit culture and unfortunately there is no real cure for this, meaning that these commits can only be optimized to a limited extent in terms of content. Unfortunately, this backport mess can only be partially addressed, if at all, by removing empty or degenerate commits, at least organizing them chronologically, and applying some common formatting conventions.
# Contents

* [Requirements](#requirements)
  * [Usage](#use)
  * [Options](#options)
  * [Examples](#examples)
## Requirements

The script requires the `git-filter-repo` ​​tool. Make sure it is installed. See: https://github.com/newren/git-filter-repo#how-do-i-install-it
```bash
  * git >= 2.24.0
  * python3 >= 3.5
  * wget
```
## use

### ./migit -u <clone url> [OPTIONS]

Specify the clone URL of the Git repository to be rewritten.
If the URL is the first argument, then specifying the '-u' flag can be omitted.
```bash
 ./migit <clone url> [OPTIONS]
```
The protocols supported are http, https, git and ssh. For local paths, don't use file://, just the relative path to the repository!
## Options

### -P, --prefix-source-url=<PREFIX> # from version 0.8

URL prefix pattern for the source commit URL. This sets the link to the source commit to which the commit ID will be appended.
The prefix URL is usually obtained automatically from the clone URL, with only accessibility being checked.
If this fails, this will be displayed. In such a case, no source commits are entered into the rewritten commits and it is recommended to set the parameter in this case.
A notice:
--pattern-source-url=<PREFIX> is deprecated, but is still usable due to backwards compatibility!

Example: A link to a commit on GitHub generally consists of the base address of the respective project and the commit hash.
```bash
 https://github.com/tuxbox-fork-migrations/migit/commit/942564882104d6de56eb817e6c5bbc3d4e66a5a3
```
The parameter should then be specified as follows:
```bash
 -P https://github.com/tuxbox-fork-migrations/migit/commit
```
A notice:
It should also be noted that extracting the base address from local repositories or URLs does not work for ssh or git protocols. If a source commit link is desired,
The parameter must therefore always be set explicitly to ensure that the base address is installed correctly. Otherwise the line for the link will not be entered.
### -T, --target-root-project-name=<NAME>

Name of the target folder within the deploy folder.
Default: Name of the cloned project and timestamp of the rewrite. By default, the project name is generated from the clone URL.
### -p, --project-name-prefix=<PREFIX>

Destination folder prefix that precedes the extracted repository name.
### -s, --project-name-suffix=<SUFFIX>

Destination folder suffix appended to the extracted repository name.
### -S, --subdir

Subdirectory to be extracted.
If a repository is to be completely rewritten, this parameter can simply be omitted or just specify one point:
```bash
 --subdir .
#oder
  -S .
```
### --subdir-list='<LIST>'

List of subdirectories to be rewritten. Directory listing must be surrounded by apostrophes 'sub1 sub2...'.
Spaces are separators.
Default: All first-level subdirectories within the root directory.
### --exclude-subdir-list='<LIST>'

List of subdirectories not to be extracted. List must be surrounded by apostrophes 'subx suby...'. Space as a separator.
The --subdir option must not be set here!
### --commit-introduction=<PATTERN>

Pattern commit introductions on the first line of each rewritten commit. Default: the respective subdirectory name or the original repo name.
This especially makes sense if subdirectories are extracted and a uniform introduction to the commit message is generally desired.
### --commit-suffix=<SUFFIX>

Appends a signature (in the sense of a suffix) to the end of each modified commit message.
### -d, --deploy-dir=<DIR>

Target directory (deploy folder) in which the rewritten repositories are stored. Default: ./deploy
### -q

Suppresses the progress display. This makes sense if the script is to be executed automatically, e.g. in cron jobs. In this mode, the script also returns EXIT_STAUTS 0 in the event of errors,
so that the script does not abort possible automated tasks in which it is embedded, more complex processes. Only status logs containing information about the call and error messages are output. These outputs can be further used for logging.
### --id-rsa-file=<PATH>

Relative path to the private ssh key file
### --reset

Resets all rewritten commit messages. This means that the entries that Migit entered in the commits will be removed again. Email and author descriptions remain unaffected.
It should be noted that Migit can only reset entries that were made by Migit itself. Everything that was entered in the commit messages under “Origin commit data” is therefore removed.
### --branch-list=<'BRANCH1 BRANCH2 ...'>

Specifies one or more branches to be processed. By default, all branches from the source repository are rewritten.
### --replace-refs {delete-no-add, delete-and-add, update-no-add, update-or-add, update-and-add}

These options determine how replacement refs are handled after commits are edited:

`delete-no-add`: All existing replacement references will be deleted and no new ones will be added.
`delete-and-add`: Existing replacement references are deleted, but new ones are added for each commit rewrite.
`update-no-add`: Existing replacement references will be updated to point to the new commit hashes, but no new ones will be added.
`update-or-add`: New replacement references are added only for those commits that are not used to update an existing replacement reference. Existing ones are updated.
`update-and-add`: Existing replacement references are updated and new replacement references are added for each commit rewrite.

By default, update-and-add is used if $GIT_DIR/filter-repo/already_ran does not exist, otherwise update-or-add.
By default, this option, even if it is set to visible, usually ensures that references that point to other commits via their commit ID, for example in commit messages, are adjusted accordingly so that they do not point.
As an example, there might be a commit that is a revert of another commit. When reverting, Git usually always includes the commit ID of the reverted commit in the commit message.
This would also be adjusted so that the reference continues to point to the appropriate commit.
Already broken references, such as those created when cherry-picking commits that contain a commit ID, cannot be restored.
### --prune-empty {always, auto, never}

This option controls whether and how empty commits are removed:

`always`: Always removes all empty commits.

`auto`: (default): Only removes commits that become empty as a result of the rewrite (not those that were already empty in the original repo unless their parent commit was removed).

`ever`: Never removes empty commits.

When a commit's parent commit is removed, the first unremoved ancestor becomes the new parent commit.
### --prune-degenerate {always, auto, never}

This option specifically handles merge commits that might be "degenerated" by removing other commits:

`always`: Removes all degenerate merge commits.

`auto` : (Default): Only removes merge commits that were degenerated by editing (not those that were already degenerated originally).

`never`: Does not remove degenerate merge commits.

A merge commit is considered degenerate if it has fewer than two parents, a commit takes on both parent roles, or one parent is an ancestor of the other.
### --no-ff

This option affects the behavior of --prune-degenerate and is useful in projects that always use --no-ff (no fast-forward) merge commits. It prevents removal of the first parent commit even if it becomes an ancestor of another parent.
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

    Origin message was:
    ------------------
    - this is a commit message
```
### Extract a specific subdirectory of a repository specifying the source commit

```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1 --commit-suffix='Automatically migrated by Migit'
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

    Origin message was:
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
./migit-u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --exclude-subdir-list='subdir1 subdir2'
```
Commits are rewritten as in the previous example but all subdirectories except subdir1 and subdir2 are extracted.
### Extract subdirectories from deeper levels of a repository, specifying the source commit

```bash
./migit -u https://github.com/example/repository.git --pattern-source-url=https://github.com/example/repository/commit --subdir subdir1/nextdir/tool
```
Commits are rewritten as in the previous example but only the 'tool' subdirectory is extracted.

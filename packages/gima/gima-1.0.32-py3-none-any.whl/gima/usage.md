# `gima`, VERSION

`gima` is a Python software which simplifies managing many git repositories through the console. It stands for `gi`t `ma`nager.

## Available commands

`--summary` - prints summary

`--commit | -c` - interactively prepares a commit for all repos, or only the ones from the specified group (`--group` _group name_), or only from the given path (`--path` _path_):

&nbsp;Then, use interactivelly, following subcommands:

&nbsp;&nbsp;`a` _pattern_ - add file(s) by id (e.g. `1`), or by range of ids (`from-to`, e.g. `1-4`), or by using wildcard pattern (e.g. `*.pdf`)

&nbsp;&nbsp;`i` _pattern_ - ignore file(s) by id (e.g. `1`), or by range of ids (`from-to`, e.g. `1-4`), or by using wildcard pattern (e.g. `*.pdf`)

&nbsp;&nbsp;`c`         - commit

&nbsp;&nbsp;`cp`        - commit and then push

&nbsp;&nbsp;`push`      - push only

&nbsp;&nbsp;`pull`      - pull only

&nbsp;&nbsp;`n`         - go to the next repository

&nbsp;&nbsp;`q`         - quit
	
`--scan | -s [--path ...]` - scans for git repos in the current folder or in the folder specified with --param

`--group | -g` - manages groups for all the repos 

`--help | -h` - prints this help

## Important links:

&nbsp;&nbsp;Home page: `https://gitlab.com/ahypki/gima/`

&nbsp;&nbsp;Issues   : `https://gitlab.com/ahypki/gima/-/issues/`


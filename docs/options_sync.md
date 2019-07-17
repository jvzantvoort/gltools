# glt sync

Sync one GitLab group to another.


## Synopsis

```
glt sync [-g|--gitlab <gitlabsection>] [-q|--quiet] [-v|--verbose]
  [-G|--dest-gitlab <destgitlabsection>] <gitlabgroupname> <destgroupname>

```

## Options

- `-g, --gitlab GITLABSECTION`

  Which configuration section should be used (default: local)

- `-q, --quiet`

  Silence warnings

- `-v, --verbose`

  Enable verbose output

- `-G, --dest-gitlab <destgitlabsection>`

  which configuration section should be used as destination for sync
  (default: local)

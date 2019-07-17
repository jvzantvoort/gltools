# glt setup

Setup or update local clones of the group.

## Synopsis

```
glt setup [-g|--gitlab <gitlabsection>] [-q|--quiet] [-v|--verbose]
  [--http] [-e|--extended] [-w|--workdir <dirname>]
```

## Description

**glt groups**, list the groups visible to the user.

## Options

- `-g, --gitlab GITLABSECTION`

  Which configuration section should be used (default: local)

- `-q, --quiet`

  Silence warnings

- `-v, --verbose`

  Enable verbose output

- `--http`

  Use http urls instead of ssh in project sourcing.

- `-e, --extended`

  This overrides the ``mask`` filter and provides all visible
  projects in the listing.

- `-w, --workdir <dirname>`

  Where the group should be maintained
















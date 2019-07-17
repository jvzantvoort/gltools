# glt projects

List projects in the selected group.

## Synopsis

```
glt projects [-g|--gitlab <gitlabsection>] [-q|--quiet] [-v|--verbose]
  [--http] [-e|--extended] [-t|--terse] <gitlabgroupname>
```

## Description

**glt projects** lists the projects in ``gitlabgroupname`` as
visible to the user.

## Options

- `-g, --gitlab GITLABSECTION`

  Which configuration section should be used (default: local)

- `-q, --quiet`

  Silence warnings

- `-v, --verbose`

  Enable verbose output

- `--http`

  Use http urls i.s.o. ssh in project sourcing

- `-e, --extended`

  This overrides the ``mask`` filter and provides all visible
  projects in the listing.

- `-t, --terse`

  Terse output in command this provided an undecorated version of
  the projects useful in scripting.

# The `~/.gltools.cfg` configuration file

The `~/.gltools.cfg` is an optional yaml based configuration file
that allows for more control in the execution of various `glt`
related commands.

The basic structure is as follows:

```yaml
---
<section>:
  <groupname>:
    <option>: <value>
```

In this:

* **section** refers to a section in the ``~/.python-gitlab.cfg``
  file.
* **groupname** refers to a group name on the server referred to by
  the relevant **section** configuration.
* **option**/**value** refers to various options that can be set for
  the tool. The values are mostly singular strings with the
  exception of the ``mask`` option with takes a list argument.


| Option name  | Default       | Description                                   |
| ------------ | ------------- | --------------------------------------------- |
| `projectdir` | `~/Workspace` | Used by e.g. ``setup`` to build the project   |
|              |               | tree                                          |
| `exportdir`  | `~/exports`   | Used by e.g. ``export`` to write the output   |
|              |               | of the exports                                |
| `tempdir`    | `~/tmp`       | Used to overrule the temporary directory      |
| `protected`  | false         | Allows for a group to be marked read-only for |
|              |               | transactions.                                 |
| `mask`       |               | Patterns of projects that are omitted from    |
|              |               | output unless the ``-e`` or ``--extended``    |
|              |               | flag is set                                   |


## Example

```yaml
---
local:
  default:
    projectdir: /scratch/jvzantvoort
    exportdir: /scratch/jvzantvoort/exports
    tempdir: /scratch/jvzantvoort/temp
  ansible-common:
    protected: true
  client1:
    projectdir: /encrypted/client1
    exportdir: /encrypted/exports/client1
    tempdir: /encrypted/client1/temp
    mask:
      - "^role-.*$"
```


# Quickstart

## GitLab API Token

The tool requires a working GitLab API Access Token. 

In your gitlab page:

  * click on the upper right corner
  * select `Settings` 
  * In the left panel select `Access Tokens`

    * `Name`, enter a descriptive name
    * `Expires at`: leave it empty to omit expiration
    * `Scopes` -> `api` selected

  * Select `Create personal access token`

Make sure you save it - you won't be able to access it again.


## Get the package

Get the sources:

```
# git clone https://github.com/jvzantvoort/gltools.git
```

Build the package:
```
# cd gltools
# python setup.py bdist_rpm

- or - 

# make rpm
```

Install the package
```
# sudo yum install dist/gltools-0.X.X-1.noarch.rpm
```

## Configuration

To create the initial configuration use [glt init](options_init.md).
This creates the `~/.python-gitlab.cfg` configuration file.

The content of the file should look something like this

```ini
# cat ~/.python-gitlab.cfg

[global]
default = local
ssl_verify = false
timeout = 15

[local]
url = http://localhost
api_version = 4
private_token = FIXME
```

Update the parameters with the token your obtained and the url of
the gitlab server.

## Checkout the group

Use [glt setup](options_setup.md) to setup a workspace.

```
glt setup kitchen
cd ~/Workspace/kitchen/
```

Do the work including committing and pushing.

## Export the repositories for later use

Use [glt export](options_export.md) to export the code.

```
# glt export kitchen
INFO export_project:  export recipes, start
INFO export_project:  export recipes, end
```

Verify

```
# cd ~/exports/kitchen/
# ls -1
recipes
```

**NOTE**: unless the `--extended` option is provided certain patterns like
mentioned in the `mask` configuration are omitted (see:
[.gltools.cfg](gltools_cfg.md) for more information.

## Export the repositories to bundles

This is allows for backups, duplication or moving of projects.

```
# glt export -o ~/backups kitchen --extended --bundles kitchen
INFO export_project:  export role-cookiedough, start
INFO export_project:  export role-cookiedough, end
INFO export_project:  export recipes, start
INFO export_project:  export recipes, end
```

Verify:

```
# cd  ~/backups/kitchen/
# ls -1 *.bundle
recipes.bundle
role-cookiedough.bundle
```


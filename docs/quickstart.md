
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
git clone https://github.com/jvzantvoort/gltools.git
```

Build the package:
```
cd gltools
python setup.py bdist_rpm
```

Install the package
```
sudo yum install dist/gltools-0.X.X-1.noarch.rpm
```

## Configuration

When the tool is first run and no configuration is available a dummy
configuration is created in `~/.python-gitlab.cfg`.

```
# glt setup --groupname homenet
```

**FIXME**: horrible error message

The content of the file should look something like this
```
cat ~/.python-gitlab.cfg

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

```
[ansible@workstation ~]$ glt setup --groupname homenet
[ansible@workstation ~]$ cd ~/Workspace/homenet/
```

Do the work including committing.


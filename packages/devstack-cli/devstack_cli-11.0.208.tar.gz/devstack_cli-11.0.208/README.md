# DevStack CLI

The `devstack-cli` provides command-line access to Cloud Development Environments (CDEs) created by Cloudomation DevStack. Learn more about [Cloudomation DevStack](https://docs.cloudomation.com/devstack/docs/overview-and-concept).

## Installation

The following binaries must be installed to be able to use `devstack-cli`:

* `ssh`
* `ssh-keyscan`
* `rsync`
* `git`

On Debian/Ubuntu the packages can be installed with

```
apt install openssh-client rsync git
```

Then you can install `devstack-cli` by running

```
python -m pip install devstack-cli
```

## Usage

```
usage: cli.py [-h] [-c CONFIG_FILE] [--workspace-url WORKSPACE_URL] [-u USER_NAME] [--maximum-uptime-hours MAXIMUM_UPTIME_HOURS] [-n CDE_NAME] [-s] [--stop] [-w] [-o] [-p] [-f] [-l] [-t] [-q] [-v] [-V]

options:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        path to a devstack-cli configuration file
  --workspace-url WORKSPACE_URL
                        the URL of your Cloudomation workspace
  -u USER_NAME, --user-name USER_NAME
                        a user name to authenticate to the Cloudomation workspace
  --maximum-uptime-hours MAXIMUM_UPTIME_HOURS
                        the number of hours before an CDE is automatically stopped
  -n CDE_NAME, --cde-name CDE_NAME
                        the name of the CDE
  -s, --start           start CDE
  --stop                stop CDE
  -w, --wait-running    wait until CDE is running. implies "--start".
  -o, --connect         connect to CDE. implies "--start" and "--wait-running".
  -p, --port-forwarding
                        enable port-forwarding. implies "--start", "--wait-running", and "--connect".
  -f , --file-sync      enable file-sync implies "--start", "--wait-running", and "--connect".
  -l, --logs            enable following logs implies "--start", "--wait-running", and "--connect".
  -t, --terminal        open interactive terminal implies "--start", "--wait-running", and "--connect".
  -q, --quit            exit after processing command line arguments.
  -v, --verbose         enable debug logging
  -V, --version         show program's version number and exit
```

## Support

`devstack-cli` is part of Cloudomation DevStack and support is provided to you with an active subscription.

## Authors and acknowledgment

Cloudomation actively maintains the `devstack-cli` command line tool as part of Cloudomation DevStack

## License

Copyright (c) 2025 Starflows OG

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
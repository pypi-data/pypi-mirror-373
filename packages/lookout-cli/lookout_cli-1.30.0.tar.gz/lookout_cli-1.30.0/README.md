# Lookout CLI

Publicly available on [PyPi](https://pypi.org/project/lookout-cli/) for convenience but if you don't work at Greenroom Robotics, you probably don't want to use this.

## Install

* For development:
  * `pip install -e ./packages/lookout_config`
  * `pip install -e ./tools/lookout_cli`
* For production: `pip install lookout-cli`
* You may also need to `export PATH=$PATH:~/.local/bin` if you don't have `~/.local/bin` in your path
* Install autocomplete:
  * bash: `echo 'eval "$(_lookout_COMPLETE=bash_source lookout)"' >> ~/.bashrc`
  * zsh: `echo 'eval "$(_lookout_COMPLETE=zsh_source lookout)"' >> ~/.zshrc` (this is much nicer)

## Usage

* `lookout --help` to get help with the CLI

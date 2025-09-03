# Cadence CLI

## Install
```shell
pip install jetbrains-cadence
```

This will create a `cadence` script in your current environment.


## Completions
cadence CLI uses click for its command line interface. click can automatically generate completion files for bash, fish, and zsh which can either be generated and sourced each time your shell is started or, generated once, save to a file and sourced from there. The latter version is much more efficient.

To enable shell completions:
### bash
```bash
echo 'eval "$(_CADENCE_COMPLETE=bash_source cadence)"' >> ~/.bashrc
```
### zsh
```zsh
echo 'eval "$(_CADENCE_COMPLETE=zsh_source cadence)"' >> ~/.zshrc
```

```shell
echo 'eval (env _KHAL_COMPLETE=fish_source khal)"' >> ~/.config/fish/completions/khal.fish
```
---

## Getting Started

```shell
cadence login
```

#### Start the execution from YAML config
```shell
cadence execution start --preset path/to/config.yaml
```
This will print the ID of the started execution.


#### See the execution status
```shell
cadence execution status <YOUR-EXECUTION-ID>
```

#### Stop the execution
```shell
cadence execution stop <YOUR-EXECUTION-ID>
```

## More commands

#### Get information about the execution as a JSON
```shell
cadence execution info <YOUR-EXECUTION-ID>
```

#### List executions
```shell
cadence execution list
```
Options:
```
  --offset INTEGER  [default: 0]
  --count INTEGER   [default: 50]
  --all             List all executions. Count and offset are ignored
  --json / --table  Output format  [default: table]
```

## Workspace management
#### Display information about the current workspace:
```shell
cadence workspace
```

#### See available workspaces:
```shell
cadence workspace list
```

#### Set workspace:
```shell
cadence workspace set <YOUR-WORKSPACE-ID>
```


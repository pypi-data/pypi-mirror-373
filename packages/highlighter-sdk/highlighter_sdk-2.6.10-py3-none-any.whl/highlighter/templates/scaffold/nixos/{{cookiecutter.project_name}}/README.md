# {{ cookiecutter.title }}

{{ cookiecutter.short_description  }}

## Development

```shell
# If you're not already in a git repo
git init

# add files to git (required)
git add flake.nix python.nix

# Enter the nix shell. Need to say Yes a few times
# to use the nix build cache at https://cuda-maintainers.cachix.org:
nix develop
```

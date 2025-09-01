# vmaudit

## Contributing / Development Process

### Requirements

- [pipx](https://pipx.pypa.io/stable/installation/) is **required** for development.
- [just](https://github.com/casey/just) simplifies running development commands.
- [pre-commit](https://pre-commit.com/) is **required** for linting/formatting.
  - Install the tool globally: `pipx install pre-commit`
  - Activate the Git hooks in this repository: `pre-commit install`
- [Ruff for VSCode](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
  is highly recommended, and performs automatic code formatting in your editor.


### Running Locally

- Always run the code through `pipx` in "editable" mode, which allows live source
  code edits. The included `just` configuration simplifies that command, and also
  automatically passes your command-line arguments to the application. Example:

```sh
just run -h

# Or with root scanning privileges:
sudo just run -h
```

- After editing `pyproject.toml`, always erase the locally cached package
  metadata, so that subsequent package installations use the latest information.

```sh
just clean
```


### Committing Code

- Ensure that `pre-commit` is installed and hooked into your Git, so that all
  commits are verified. Alternatively, run the linting/formatting manually via the
  following command before every commit. Note that it only checks Git's tracked
  files (the repo's existing, modified or newly staged files).

```sh
just verify
```


---

This project is licensed under the GPLv2 License.
See the [LICENSE](LICENSE) file for details.

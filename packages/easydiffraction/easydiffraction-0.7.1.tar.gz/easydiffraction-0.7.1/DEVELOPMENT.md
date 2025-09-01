# Development

This is an example of a workflow that describes the development process.

## Installation and setup with Pixi

- Install Pixi by following the instructions on the
  [official Pixi Installation Guide](https://pixi.sh/latest/installation).
- Clone repositories with assets for building documentation
  ```bash
  git clone https://github.com/easyscience/assets-docs.git
  git clone https://github.com/easyscience/assets-branding.git
  ```
- Clone EasyDiffraction library repository
  ```bash
  git clone https://github.com/easyscience/diffraction-lib
  ```
- Go to the cloned directory
  ```bash
  cd diffraction-lib
  ```
- Create the environment defined in `pixi.toml` and install all necessary
  dependencies:
  ```bash
  pixi install
  ```
- Install Prettier for non-Python files formatting
  ```bash
  pixi run prettier-install
  ```

## Making changes

- Checkout/switch to the `develop` branch
  ```bash
  git checkout develop
  ```
- Create a new branch from the `develop` one
  ```bash
  git checkout -b new-feature
  ```
- Make changes in the code
  ```bash
  ...
  ```

## Checking code quality and testing

- Check and fix code quality (configuration is in `pyproject.toml` and
  `prettierrc.toml`)
  ```bash
  pixi run code-quality
  ```
- Run unit tests
  ```bash
  pixi run unit-tests
  ```
- Run functional tests
  ```bash
  pixi run func-tests
  ```
- Test tutorials as python scripts
  ```bash
  pixi run script-tests
  ```
- Convert tutorial scripts to notebooks
  ```bash
  pixi run notebook-prepare
  ```
- Test tutorials as notebooks
  ```bash
  pixi run notebook-tests
  ```

## Building and checking documentation with MkDocs

- Move notebooks to docs/tutorials
  ```bash
  pixi run docs-notebooks
  ```
- Add extra files to build documentation (from `../assets-docs/` and
  `../assets-branding/` directories)
  ```bash
  pixi run docs-assets
  ```
- Create mkdocs.yml file
  ```bash
  pixi run docs-config
  ```
- Build documentation
  ```bash
  pixi run docs-build
  ```
- Test the documentation locally (built in the `site/` directory). E.g., on
  macOS, open the site in the default browser via the terminal
  ```bash
  open http://127.0.0.1:8000
  ```
- Clean up after checking documentation
  ```bash
  pixi run docs-clean
  ```

## Committing and pushing changes

- Commit changes
  ```bash
  git add .
  git commit -m "Add new feature"
  ```
- Push the new branch to a remote repository
  ```bash
  git push -u origin new-feature
  ```
- Create a pull request on
  [EasyScience GitHub repository](https://github.com/easyscience/diffraction-lib/pulls)
  and request a review from team members

## Contributing

This section is meant for everyone working on developing the library and committing to the official repository. If you have an own fork of the library then this part does not affect you and might not work as explained below due to access restrictions.

### Development guide

For each new feature, bug fix, etc, please :

- make a new branch
- implement your solution
- make a `pull_request` to merge into `main`

To make sure that all of the commits are valid for pull requests the branch commit must pass all tests. 

The tests are divided into testing the code functionality and coding standard. These are run in the `run_tests` stage : 
- `tests` : runs the tests in `tests` dir
- `lint-type-tests` : checks if types are hinted with `mypy` and coding style with `flake8` (allowed to fail)

To make sure that everything is fine before committing make sure to go over the following checklist :

- run : `pytest` (existing tests must pass, try to cover most of new code)
- run : `flake8 pyCFS` (there shouldn't be any errors) 
  - if there are, run `black pyCFS/` and recheck with flake8
  - you might need to fix something manually
- run : `mypy pyCFS` (there shouldn't be any errors)

Only after making sure that these tests are ok locally commit the changes to your branch. This way you will make sure to catch any errors that might fail the tests.

### Documentation

Please make sure that you update the documentation along with the features that you implement. This will be checked in the code review.

The API documentation is generated automatically from the docstrings in the code. Therefore, make sure that all docstrings are updated and new features have docstrings in [Numpy style](https://numpydoc.readthedocs.io/en/latest/format.html).


### Commit messages

Please follow the guide here when writing commit messages. This will make it easier for everyone to follow along.

1. Specify type of commit 
2. Write commit message in lowercase
3. Use imperative mood 
4. First line max 50 characters, body max 72 characters

The commit message consists of several parts out of which some are optional.

```bash
<type>[optional scope]: <description>

[optional body]
```

- `feat` – a new feature is introduced with the changes
- `fix` – a bug fix has occurred
- `chore` – changes that do not relate to a fix or feature and don't modify src or test files (for example updating dependencies)
- `refactor` – refactored code that neither fixes a bug nor adds a feature
- `docs` – updates to documentation such as a the README or other markdown files
- `style` – changes that do not affect the meaning of the code, likely related to code formatting such as white-space, missing semi-colons, and so on.
- `test` – including new or correcting previous tests
- `perf` – performance improvements
- `ci` – continuous integration related
- `build` – changes that affect the build system or external dependencies
- `revert` – reverts a previous commit

Adapted from [this article](https://www.freecodecamp.org/news/how-to-write-better-git-commit-messages/).

### Publishing new versions

This part is managed automatically over GitLab CI. New versions of the library are published by pushing a tag to the `main` branch. 

:::{note}
This is only possible if you are a maintainer of the repository.
:::

A new version will be published when agreed upon by the maintainers of the library.
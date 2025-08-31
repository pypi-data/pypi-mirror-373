# Developing `talkgooder`

`talkgooder` is as simple as possible, given the complexities of language. It initially targets `en-US` rules, but can be easily extended for other locales. PRs welcome!

## Local development

VS Code is recommended. Install the recommended extensions and use the default Extension settings defined in the repo.

`talkgooder` has no dependencies for users, but you will need some things to develop locally. Create a venv using `requirements-dev.txt`.

### Use pytest early and often

Two rules:

1. All functionality must be in a function
1. All functions must have exhaustive tests

Create a new test file in `tests/` for each function you add. If you add a language conditional in a function, ensure your tests cover all corner cases.

### Lint your code

If you aren't using VS Code, configure Flake8 and Black to run with a line length of 100.

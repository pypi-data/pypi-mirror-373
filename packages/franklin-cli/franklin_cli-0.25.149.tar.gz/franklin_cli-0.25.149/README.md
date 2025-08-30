
# Franklin


## Use conventional commits

The Conventional Commits specification is a lightweight convention on top of commit messages. It provides an easy set of rules for creating an explicit commit history; which makes it easier to write automated tools on top of. This convention dovetails with SemVer, by describing the features, fixes, and breaking changes made in commit messages.

The commit message should be structured as follows:

    <type>[optional scope][!]: <description>

    [optional body]

    [[BREAKING CHANGE:] optional footer(s)]

The commit contains the following structural elements, to communicate intent to the consumers of your library:

**fix:** a commit of the type fix patches a bug in your codebase (this correlates with PATCH in Semantic Versioning).

**feat:** a commit of the type feat introduces a new feature to the codebase (this correlates with MINOR in Semantic Versioning).

BREAKING CHANGE: a commit that has a footer **BREAKING CHANGE:**, or appends a ! after the type/scope, introduces a breaking API change (correlating with MAJOR in Semantic Versioning). A BREAKING CHANGE can be part of commits of any type.

Types other than fix: and feat: are allowed, for example @commitlint/config-conventional (based on the Angular convention) recommends **build:**, **chore:**, **ci:**, **docs:**, **style:**, **refactor:**, **perf:**, **test:**, and others.

Footers other than BREAKING CHANGE: <description> may be provided and follow a convention similar to git trailer format.

Additional types are not mandated by the Conventional Commits specification, and have no implicit effect in Semantic Versioning (unless they include a BREAKING CHANGE). A scope may be provided to a commit’s type, to provide additional contextual information and is contained within parenthesis, e.g., feat(parser): add ability to parse arrays.

# Releases

Running `release-tag.sh` creates and pushes a version tag maching the version in the pushed `pyproject.toml`. This triggers Github actions that first amends the remote `CHANGELOG.md` and then builds and publishes a conda package for that version.


# Developer Notes

union of dependencies for franklin, franklin-educator and franklin-admin are included in requirements.txt to make conda package building work

For conda packages, franklin-admin depends on franklin-educator, which depends on franklin. This is to make it possible to install like this or each user group:

students:

    conda install munch-group::franklin

educators:

    conda install munch-group::franklin-educator

admin:

    conda install munch-group::franklin-admin


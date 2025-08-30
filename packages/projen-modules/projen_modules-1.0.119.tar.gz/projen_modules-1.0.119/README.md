# projen-modules

A collection of custom projen modules, that can be used to bootstrap and maintain consistent project configuration, tooling, dependencies, and builds.

## Getting Started

```sh
yarn install
npx projen build
```

This will:

* Install the dependencies
* Apply any projen changes
* Run tests
* Package project locally

Any files changed by projen should be committed to git.

Running the tests like this will update any snapshot files, this should be reviewed and committed to git.

## Testing

Types of testing:

* Snapshot - projen project outputs are stored as a snapshot in the corresponding `__snapshots__` directory. When the project changes then it is expected that these snapshots change too and should be reviewed committed alongside the project.
* Unit tests - these assert on specific functionality of the project and should be written for any new functionality added.

## Creating a New Project

```
npx projen new {project} --from projen-modules
```

Some projects may have required fields that need to be specified as part of this command, review any errors for details what needs to be specified.

### Project Types

| Project type                                   | Description                |
| ---------------------------------------------- | -------------------------- |
| [cdk-typescript-app](API.md#cdktypescriptapp-) | A typescript CDK app |
| [npm-package](API.md#npmpackage-)              | A typescript npm package   |
| [python-package](API.md#pythonpackage-)        | A python package           |
| [jsii-package](API.md#jsiiproject-)            | A typescript JSII package  |

## Project Structure

All source is located in `src` and is grouped by:

* `components` - these are common building blocks that can be used by projects to implement specific project functionality.
* `projects` - these are projects that can be built from this project (see #something)
* `utils` - these are helper functions that are often reused

`test` contains tests, and mirrors the `src` directory structure. Within here there are `__snapshots__` which contain snapshots of project tests (see #section).

r'''
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
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import projen as _projen_04054675
import projen.awscdk as _projen_awscdk_04054675
import projen.cdk as _projen_cdk_04054675
import projen.github as _projen_github_04054675
import projen.github.workflows as _projen_github_workflows_04054675
import projen.javascript as _projen_javascript_04054675
import projen.python as _projen_python_04054675
import projen.release as _projen_release_04054675
import projen.typescript as _projen_typescript_04054675


class CdkTypeScriptApp(
    _projen_awscdk_04054675.AwsCdkTypeScriptApp,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-modules.CdkTypeScriptApp",
):
    '''A CDK application in TypeScript.

    :pjid: cdk-typescript-app
    '''

    def __init__(
        self,
        *,
        cdk_version: builtins.str,
        code_owners: typing.Sequence[builtins.str],
        name: builtins.str,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        app: typing.Optional[builtins.str] = None,
        app_entrypoint: typing.Optional[builtins.str] = None,
        artifacts_directory: typing.Optional[builtins.str] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        biome: typing.Optional[builtins.bool] = None,
        biome_options: typing.Optional[typing.Union[_projen_javascript_04054675.BiomeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        build_command: typing.Optional[builtins.str] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_options: typing.Optional[typing.Union[_projen_javascript_04054675.BuildWorkflowOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        build_workflow_triggers: typing.Optional[typing.Union[_projen_github_workflows_04054675.Triggers, typing.Dict[builtins.str, typing.Any]]] = None,
        bump_package: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        bundler_options: typing.Optional[typing.Union[_projen_javascript_04054675.BundlerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bun_version: typing.Optional[builtins.str] = None,
        cdk_assert: typing.Optional[builtins.bool] = None,
        cdk_assertions: typing.Optional[builtins.bool] = None,
        cdk_cli_version: typing.Optional[builtins.str] = None,
        cdk_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_dependencies_as_deps: typing.Optional[builtins.bool] = None,
        cdkout: typing.Optional[builtins.str] = None,
        cdk_test_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_version_pinning: typing.Optional[builtins.bool] = None,
        check_licenses: typing.Optional[typing.Union[_projen_javascript_04054675.LicenseCheckerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        clobber: typing.Optional[builtins.bool] = None,
        code_artifact_options: typing.Optional[typing.Union[_projen_javascript_04054675.CodeArtifactOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        commit_generated: typing.Optional[builtins.bool] = None,
        constructs_version: typing.Optional[builtins.str] = None,
        context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        default_release_branch: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[typing.Union[_projen_github_04054675.DependabotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[typing.Union[_projen_javascript_04054675.UpgradeDependenciesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        disable_tsconfig_dev: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        edge_lambda_auto_discover: typing.Optional[builtins.bool] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[typing.Union[_projen_javascript_04054675.EslintOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        experimental_integ_runner: typing.Optional[builtins.bool] = None,
        feature_flags: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        homepage: typing.Optional[builtins.str] = None,
        integration_test_auto_discover: typing.Optional[builtins.bool] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[typing.Union[_projen_javascript_04054675.JestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        lambda_auto_discover: typing.Optional[builtins.bool] = None,
        lambda_extension_auto_discover: typing.Optional[builtins.bool] = None,
        lambda_options: typing.Optional[typing.Union[_projen_awscdk_04054675.LambdaFunctionCommonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        libdir: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        major_version: typing.Optional[jsii.Number] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        min_major_version: typing.Optional[jsii.Number] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        next_version_command: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[_projen_javascript_04054675.NpmAccess] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        npm_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        npm_provenance: typing.Optional[builtins.bool] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        outdir: typing.Optional[builtins.str] = None,
        package: typing.Optional[builtins.bool] = None,
        package_manager: typing.Optional[_projen_javascript_04054675.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        peer_dependency_options: typing.Optional[typing.Union[_projen_javascript_04054675.PeerDependencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pnpm_version: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[typing.Union[_projen_javascript_04054675.PrettierOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_type: typing.Optional[_projen_04054675.ProjectType] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        readme: typing.Optional[typing.Union["ReadmeOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        releasable_commits: typing.Optional[_projen_04054675.ReleasableCommits] = None,
        release: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, typing.Union[_projen_release_04054675.BranchOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_trigger: typing.Optional[_projen_release_04054675.ReleaseTrigger] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        require_approval: typing.Optional[_projen_awscdk_04054675.ApprovalLevel] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        scoped_packages_options: typing.Optional[typing.Sequence[typing.Union[_projen_javascript_04054675.ScopedPackagesOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        srcdir: typing.Optional[builtins.str] = None,
        stability: typing.Optional[builtins.str] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        ts_jest_options: typing.Optional[typing.Union[_projen_typescript_04054675.TsJestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        vscode: typing.Optional[builtins.bool] = None,
        watch_excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        watch_includes: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_git_identity: typing.Optional[typing.Union[_projen_github_04054675.GitIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        workflow_package_cache: typing.Optional[builtins.bool] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_runs_on_group: typing.Optional[typing.Union[_projen_04054675.GroupRunnerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        yarn_berry_options: typing.Optional[typing.Union[_projen_javascript_04054675.YarnBerryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cdk_version: (experimental) Minimum version of the AWS CDK to depend on. Default: "2.1.0"
        :param code_owners: List of teams used to generate the CODEOWNERS file.
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param app: (experimental) The command line to execute in order to synthesize the CDK application (language specific).
        :param app_entrypoint: (experimental) The CDK app's entrypoint (relative to the source directory, which is "src" by default). Default: "main.ts"
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Is the author an organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param biome: (experimental) Setup Biome. Default: false
        :param biome_options: (experimental) Biome options. Default: - default options
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param build_command: (experimental) A command to execute before synthesis. This command will be called when running ``cdk synth`` or when ``cdk watch`` identifies a change in your source code before redeployment. Default: - no build command
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_options: (experimental) Options for PR build workflow.
        :param build_workflow_triggers: (deprecated) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bump_package: (experimental) The ``commit-and-tag-version`` compatible package used to bump the package version, as a dependency string. This can be any compatible package version, including the deprecated ``standard-version@9``. Default: - A recent version of "commit-and-tag-version"
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param bun_version: (experimental) The version of Bun to use if using Bun as a package manager. Default: "latest"
        :param cdk_assert: (deprecated) Warning: NodeJS only. Install the Default: - will be included by default for AWS CDK >= 1.0.0 < 2.0.0
        :param cdk_assertions: (experimental) Install the assertions library? Only needed for CDK 1.x. If using CDK 2.x then assertions is already included in 'aws-cdk-lib' Default: - will be included by default for AWS CDK >= 1.111.0 < 2.0.0
        :param cdk_cli_version: (experimental) Version range of the AWS CDK CLI to depend on. Can be either a specific version, or an NPM version range. By default, the latest 2.x version will be installed; you can use this option to restrict it to a specific version or version range. Default: "^2"
        :param cdk_dependencies: (deprecated) Which AWS CDKv1 modules this project requires.
        :param cdk_dependencies_as_deps: (deprecated) If this is enabled (default), all modules declared in ``cdkDependencies`` will be also added as normal ``dependencies`` (as well as ``peerDependencies``). This is to ensure that downstream consumers actually have your CDK dependencies installed when using npm < 7 or yarn, where peer dependencies are not automatically installed. If this is disabled, ``cdkDependencies`` will be added to ``devDependencies`` to ensure they are present during development. Note: this setting only applies to construct library projects Default: true
        :param cdkout: (experimental) cdk.out directory. Default: "cdk.out"
        :param cdk_test_dependencies: (deprecated) AWS CDK modules required for testing.
        :param cdk_version_pinning: (experimental) Use pinned version instead of caret version for CDK. You can use this to prevent mixed versions for your CDK dependencies and to prevent auto-updates. If you use experimental features this will let you define the moment you include breaking changes.
        :param check_licenses: (experimental) Configure which licenses should be deemed acceptable for use by dependencies. This setting will cause the build to fail, if any prohibited or not allowed licenses ares encountered. Default: - no license checks are run during the build and all licenses will be accepted
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: - true, but false for subprojects
        :param code_artifact_options: (experimental) Options for npm packages using AWS CodeArtifact. This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact Default: - undefined
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v4 A secret is required for private repos. Configured with ``@codeCovTokenSecret``. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param constructs_version: (experimental) Minimum version of the ``constructs`` library to depend on. Default: - for CDK 1.x the default is "3.2.27", for CDK 2.x the default is "10.0.5".
        :param context: (experimental) Additional context to include in ``cdk.json``. Default: - no additional context
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param deps_upgrade: (experimental) Use tasks and github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for ``UpgradeDependencies``. Default: - default options
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param disable_tsconfig_dev: (experimental) Do not generate a ``tsconfig.dev.json`` file. Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param edge_lambda_auto_discover: (experimental) Automatically adds an ``cloudfront.experimental.EdgeFunction`` for each ``.edge-lambda.ts`` handler in your source tree. If this is disabled, you can manually add an ``awscdk.AutoDiscover`` component to your project. Default: true
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json. Default: "lib/index.js"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param experimental_integ_runner: (experimental) Enable experimental support for the AWS CDK integ-runner. Default: false
        :param feature_flags: (experimental) Include all feature flags in cdk.json. Default: true
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param homepage: (experimental) Package's Homepage / Website.
        :param integration_test_auto_discover: (experimental) Automatically discovers and creates integration tests for each ``.integ.ts`` file in under your test directory. Default: true
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param lambda_auto_discover: (experimental) Automatically adds an ``awscdk.LambdaFunction`` for each ``.lambda.ts`` handler in your source tree. If this is disabled, you can manually add an ``awscdk.AutoDiscover`` component to your project. Default: true
        :param lambda_extension_auto_discover: (experimental) Automatically adds an ``awscdk.LambdaExtension`` for each ``.lambda-extension.ts`` entrypoint in your source tree. If this is disabled, you can manually add an ``awscdk.AutoDiscover`` component to your project. Default: true
        :param lambda_options: (experimental) Common options for all AWS Lambda functions. Default: - default options
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param max_node_version: (experimental) The maximum node version supported by this package. Most projects should not use this option. The value indicates that the package is incompatible with any newer versions of node. This requirement is enforced via the engines field. You will normally not need to set this option. Consider this option only if your package is known to not function with newer versions of node. Default: - no maximum version is enforced
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param min_major_version: (experimental) Minimal Major version to release. This can be useful to set to 1, as breaking changes before the 1.x major release are not incrementing the major version number. Can not be set together with ``majorVersion``. Default: - No minimum version is being enforced
        :param min_node_version: (experimental) The minimum node version required by this package to function. Most projects should not use this option. The value indicates that the package is incompatible with any older versions of node. This requirement is enforced via the engines field. You will normally not need to set this option, even if your package is incompatible with EOL versions of node. Consider this option only if your package depends on a specific feature, that is not available in other LTS versions. Setting this option has very high impact on the consumers of your package, as package managers will actively prevent usage with node versions you have marked as incompatible. To change the node version of your CI/CD workflows, use ``workflowNodeVersion``. Default: - no minimum version is enforced
        :param mutable_build: (deprecated) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param next_version_command: (experimental) A shell command to control the next version to release. If present, this shell command will be run before the bump is executed, and it determines what version to release. It will be executed in the following environment: - Working directory: the project directory. - ``$VERSION``: the current version. Looks like ``1.2.3``. - ``$LATEST_TAG``: the most recent tag. Looks like ``prefix-v1.2.3``, or may be unset. - ``$SUGGESTED_BUMP``: the suggested bump action based on commits. One of ``major|minor|patch|none``. The command should print one of the following to ``stdout``: - Nothing: the next version number will be determined based on commit history. - ``x.y.z``: the next version number will be ``x.y.z``. - ``major|minor|patch``: the next version number will be the current version number with the indicated component bumped. This setting cannot be specified together with ``minMajorVersion``; the invoked script can be used to achieve the effects of ``minMajorVersion``. Default: - The next version will be determined based on the commit history and project settings.
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param npm_ignore_options: (experimental) Configuration options for .npmignore file.
        :param npm_provenance: (experimental) Should provenance statements be generated when the package is published. A supported package manager is required to publish a package with npm provenance statements and you will need to use a supported CI/CD provider. Note that the projen ``Release`` and ``Publisher`` components are using ``publib`` to publish packages, which is using npm internally and supports provenance statements independently of the package manager used. Default: - true for public packages, false otherwise
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other subprojects. Default: "."
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN_CLASSIC
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param pnpm_version: (experimental) The version of PNPM to use if using PNPM as a package manager. Default: "9"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: - true if not a subproject
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param readme: Configuration of the README.md file.
        :param releasable_commits: (experimental) Find commits that should be considered releasable Used to decide if a release is required. Default: ReleasableCommits.everyCommit()
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: "v"
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param require_approval: (experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them. Default: ApprovalLevel.BROADENING
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param scoped_packages_options: (experimental) Options for privately hosted scoped packages. Default: - fetch all scoped packages from the public npm registry
        :param scripts: (deprecated) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Also adds the script as a task. Default: {}
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param stability: (experimental) Package's Stability.
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param ts_jest_options: (experimental) Options for ts-jest.
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with commit-and-tag-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param watch_excludes: (experimental) Glob patterns to exclude from ``cdk watch``. Default: []
        :param watch_includes: (experimental) Glob patterns to include in ``cdk watch``. Default: []
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version used in GitHub Actions workflows. Always use this option if your GitHub Actions workflows require a specific to run. Default: - ``minNodeVersion`` if set, otherwise ``lts/*``.
        :param workflow_package_cache: (experimental) Enable Node.js package cache in GitHub workflows. Default: false
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param workflow_runs_on_group: (experimental) Github Runner Group selection options.
        :param yarn_berry_options: (experimental) Options for Yarn Berry. Default: - Yarn Berry v4 with all default options
        '''
        options = CdkTypeScriptAppOptions(
            cdk_version=cdk_version,
            code_owners=code_owners,
            name=name,
            allow_library_dependencies=allow_library_dependencies,
            app=app,
            app_entrypoint=app_entrypoint,
            artifacts_directory=artifacts_directory,
            author_email=author_email,
            author_name=author_name,
            author_organization=author_organization,
            author_url=author_url,
            auto_approve_options=auto_approve_options,
            auto_approve_upgrades=auto_approve_upgrades,
            auto_detect_bin=auto_detect_bin,
            auto_merge=auto_merge,
            auto_merge_options=auto_merge_options,
            bin=bin,
            biome=biome,
            biome_options=biome_options,
            bugs_email=bugs_email,
            bugs_url=bugs_url,
            build_command=build_command,
            build_workflow=build_workflow,
            build_workflow_options=build_workflow_options,
            build_workflow_triggers=build_workflow_triggers,
            bump_package=bump_package,
            bundled_deps=bundled_deps,
            bundler_options=bundler_options,
            bun_version=bun_version,
            cdk_assert=cdk_assert,
            cdk_assertions=cdk_assertions,
            cdk_cli_version=cdk_cli_version,
            cdk_dependencies=cdk_dependencies,
            cdk_dependencies_as_deps=cdk_dependencies_as_deps,
            cdkout=cdkout,
            cdk_test_dependencies=cdk_test_dependencies,
            cdk_version_pinning=cdk_version_pinning,
            check_licenses=check_licenses,
            clobber=clobber,
            code_artifact_options=code_artifact_options,
            code_cov=code_cov,
            code_cov_token_secret=code_cov_token_secret,
            commit_generated=commit_generated,
            constructs_version=constructs_version,
            context=context,
            copyright_owner=copyright_owner,
            copyright_period=copyright_period,
            default_release_branch=default_release_branch,
            dependabot=dependabot,
            dependabot_options=dependabot_options,
            deps=deps,
            deps_upgrade=deps_upgrade,
            deps_upgrade_options=deps_upgrade_options,
            description=description,
            dev_container=dev_container,
            dev_deps=dev_deps,
            disable_tsconfig=disable_tsconfig,
            disable_tsconfig_dev=disable_tsconfig_dev,
            docgen=docgen,
            docs_directory=docs_directory,
            edge_lambda_auto_discover=edge_lambda_auto_discover,
            entrypoint=entrypoint,
            entrypoint_types=entrypoint_types,
            eslint=eslint,
            eslint_options=eslint_options,
            experimental_integ_runner=experimental_integ_runner,
            feature_flags=feature_flags,
            github=github,
            github_options=github_options,
            gitignore=gitignore,
            git_ignore_options=git_ignore_options,
            git_options=git_options,
            gitpod=gitpod,
            homepage=homepage,
            integration_test_auto_discover=integration_test_auto_discover,
            jest=jest,
            jest_options=jest_options,
            jsii_release_version=jsii_release_version,
            keywords=keywords,
            lambda_auto_discover=lambda_auto_discover,
            lambda_extension_auto_discover=lambda_extension_auto_discover,
            lambda_options=lambda_options,
            libdir=libdir,
            license=license,
            licensed=licensed,
            logging=logging,
            major_version=major_version,
            max_node_version=max_node_version,
            mergify=mergify,
            mergify_options=mergify_options,
            min_major_version=min_major_version,
            min_node_version=min_node_version,
            mutable_build=mutable_build,
            next_version_command=next_version_command,
            npm_access=npm_access,
            npm_dist_tag=npm_dist_tag,
            npmignore=npmignore,
            npmignore_enabled=npmignore_enabled,
            npm_ignore_options=npm_ignore_options,
            npm_provenance=npm_provenance,
            npm_registry=npm_registry,
            npm_registry_url=npm_registry_url,
            npm_token_secret=npm_token_secret,
            outdir=outdir,
            package=package,
            package_manager=package_manager,
            package_name=package_name,
            parent=parent,
            peer_dependency_options=peer_dependency_options,
            peer_deps=peer_deps,
            pnpm_version=pnpm_version,
            post_build_steps=post_build_steps,
            prerelease=prerelease,
            prettier=prettier,
            prettier_options=prettier_options,
            project_type=project_type,
            projen_command=projen_command,
            projen_credentials=projen_credentials,
            projen_dev_dependency=projen_dev_dependency,
            projenrc_js=projenrc_js,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
            projenrc_js_options=projenrc_js_options,
            projenrc_ts=projenrc_ts,
            projenrc_ts_options=projenrc_ts_options,
            projen_token_secret=projen_token_secret,
            projen_version=projen_version,
            publish_dry_run=publish_dry_run,
            publish_tasks=publish_tasks,
            pull_request_template=pull_request_template,
            pull_request_template_contents=pull_request_template_contents,
            readme=readme,
            releasable_commits=releasable_commits,
            release=release,
            release_branches=release_branches,
            release_every_commit=release_every_commit,
            release_failure_issue=release_failure_issue,
            release_failure_issue_label=release_failure_issue_label,
            release_schedule=release_schedule,
            release_tag_prefix=release_tag_prefix,
            release_to_npm=release_to_npm,
            release_trigger=release_trigger,
            release_workflow=release_workflow,
            release_workflow_name=release_workflow_name,
            release_workflow_setup_steps=release_workflow_setup_steps,
            renovatebot=renovatebot,
            renovatebot_options=renovatebot_options,
            repository=repository,
            repository_directory=repository_directory,
            require_approval=require_approval,
            sample_code=sample_code,
            scoped_packages_options=scoped_packages_options,
            scripts=scripts,
            srcdir=srcdir,
            stability=stability,
            stale=stale,
            stale_options=stale_options,
            testdir=testdir,
            tsconfig=tsconfig,
            tsconfig_dev=tsconfig_dev,
            tsconfig_dev_file=tsconfig_dev_file,
            ts_jest_options=ts_jest_options,
            typescript_version=typescript_version,
            versionrc_options=versionrc_options,
            vscode=vscode,
            watch_excludes=watch_excludes,
            watch_includes=watch_includes,
            workflow_bootstrap_steps=workflow_bootstrap_steps,
            workflow_container_image=workflow_container_image,
            workflow_git_identity=workflow_git_identity,
            workflow_node_version=workflow_node_version,
            workflow_package_cache=workflow_package_cache,
            workflow_runs_on=workflow_runs_on,
            workflow_runs_on_group=workflow_runs_on_group,
            yarn_berry_options=yarn_berry_options,
        )

        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="readme")
    def readme(self) -> "Readme":
        return typing.cast("Readme", jsii.get(self, "readme"))

    @readme.setter
    def readme(self, value: "Readme") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a544530c4e440f72065d416ace5f306da46147589bc70a0f44ccba0553de9c78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readme", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="projen-modules.CdkTypeScriptAppOptions",
    jsii_struct_bases=[],
    name_mapping={
        "cdk_version": "cdkVersion",
        "code_owners": "codeOwners",
        "name": "name",
        "allow_library_dependencies": "allowLibraryDependencies",
        "app": "app",
        "app_entrypoint": "appEntrypoint",
        "artifacts_directory": "artifactsDirectory",
        "author_email": "authorEmail",
        "author_name": "authorName",
        "author_organization": "authorOrganization",
        "author_url": "authorUrl",
        "auto_approve_options": "autoApproveOptions",
        "auto_approve_upgrades": "autoApproveUpgrades",
        "auto_detect_bin": "autoDetectBin",
        "auto_merge": "autoMerge",
        "auto_merge_options": "autoMergeOptions",
        "bin": "bin",
        "biome": "biome",
        "biome_options": "biomeOptions",
        "bugs_email": "bugsEmail",
        "bugs_url": "bugsUrl",
        "build_command": "buildCommand",
        "build_workflow": "buildWorkflow",
        "build_workflow_options": "buildWorkflowOptions",
        "build_workflow_triggers": "buildWorkflowTriggers",
        "bump_package": "bumpPackage",
        "bundled_deps": "bundledDeps",
        "bundler_options": "bundlerOptions",
        "bun_version": "bunVersion",
        "cdk_assert": "cdkAssert",
        "cdk_assertions": "cdkAssertions",
        "cdk_cli_version": "cdkCliVersion",
        "cdk_dependencies": "cdkDependencies",
        "cdk_dependencies_as_deps": "cdkDependenciesAsDeps",
        "cdkout": "cdkout",
        "cdk_test_dependencies": "cdkTestDependencies",
        "cdk_version_pinning": "cdkVersionPinning",
        "check_licenses": "checkLicenses",
        "clobber": "clobber",
        "code_artifact_options": "codeArtifactOptions",
        "code_cov": "codeCov",
        "code_cov_token_secret": "codeCovTokenSecret",
        "commit_generated": "commitGenerated",
        "constructs_version": "constructsVersion",
        "context": "context",
        "copyright_owner": "copyrightOwner",
        "copyright_period": "copyrightPeriod",
        "default_release_branch": "defaultReleaseBranch",
        "dependabot": "dependabot",
        "dependabot_options": "dependabotOptions",
        "deps": "deps",
        "deps_upgrade": "depsUpgrade",
        "deps_upgrade_options": "depsUpgradeOptions",
        "description": "description",
        "dev_container": "devContainer",
        "dev_deps": "devDeps",
        "disable_tsconfig": "disableTsconfig",
        "disable_tsconfig_dev": "disableTsconfigDev",
        "docgen": "docgen",
        "docs_directory": "docsDirectory",
        "edge_lambda_auto_discover": "edgeLambdaAutoDiscover",
        "entrypoint": "entrypoint",
        "entrypoint_types": "entrypointTypes",
        "eslint": "eslint",
        "eslint_options": "eslintOptions",
        "experimental_integ_runner": "experimentalIntegRunner",
        "feature_flags": "featureFlags",
        "github": "github",
        "github_options": "githubOptions",
        "gitignore": "gitignore",
        "git_ignore_options": "gitIgnoreOptions",
        "git_options": "gitOptions",
        "gitpod": "gitpod",
        "homepage": "homepage",
        "integration_test_auto_discover": "integrationTestAutoDiscover",
        "jest": "jest",
        "jest_options": "jestOptions",
        "jsii_release_version": "jsiiReleaseVersion",
        "keywords": "keywords",
        "lambda_auto_discover": "lambdaAutoDiscover",
        "lambda_extension_auto_discover": "lambdaExtensionAutoDiscover",
        "lambda_options": "lambdaOptions",
        "libdir": "libdir",
        "license": "license",
        "licensed": "licensed",
        "logging": "logging",
        "major_version": "majorVersion",
        "max_node_version": "maxNodeVersion",
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "min_major_version": "minMajorVersion",
        "min_node_version": "minNodeVersion",
        "mutable_build": "mutableBuild",
        "next_version_command": "nextVersionCommand",
        "npm_access": "npmAccess",
        "npm_dist_tag": "npmDistTag",
        "npmignore": "npmignore",
        "npmignore_enabled": "npmignoreEnabled",
        "npm_ignore_options": "npmIgnoreOptions",
        "npm_provenance": "npmProvenance",
        "npm_registry": "npmRegistry",
        "npm_registry_url": "npmRegistryUrl",
        "npm_token_secret": "npmTokenSecret",
        "outdir": "outdir",
        "package": "package",
        "package_manager": "packageManager",
        "package_name": "packageName",
        "parent": "parent",
        "peer_dependency_options": "peerDependencyOptions",
        "peer_deps": "peerDeps",
        "pnpm_version": "pnpmVersion",
        "post_build_steps": "postBuildSteps",
        "prerelease": "prerelease",
        "prettier": "prettier",
        "prettier_options": "prettierOptions",
        "project_type": "projectType",
        "projen_command": "projenCommand",
        "projen_credentials": "projenCredentials",
        "projen_dev_dependency": "projenDevDependency",
        "projenrc_js": "projenrcJs",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "projenrc_js_options": "projenrcJsOptions",
        "projenrc_ts": "projenrcTs",
        "projenrc_ts_options": "projenrcTsOptions",
        "projen_token_secret": "projenTokenSecret",
        "projen_version": "projenVersion",
        "publish_dry_run": "publishDryRun",
        "publish_tasks": "publishTasks",
        "pull_request_template": "pullRequestTemplate",
        "pull_request_template_contents": "pullRequestTemplateContents",
        "readme": "readme",
        "releasable_commits": "releasableCommits",
        "release": "release",
        "release_branches": "releaseBranches",
        "release_every_commit": "releaseEveryCommit",
        "release_failure_issue": "releaseFailureIssue",
        "release_failure_issue_label": "releaseFailureIssueLabel",
        "release_schedule": "releaseSchedule",
        "release_tag_prefix": "releaseTagPrefix",
        "release_to_npm": "releaseToNpm",
        "release_trigger": "releaseTrigger",
        "release_workflow": "releaseWorkflow",
        "release_workflow_name": "releaseWorkflowName",
        "release_workflow_setup_steps": "releaseWorkflowSetupSteps",
        "renovatebot": "renovatebot",
        "renovatebot_options": "renovatebotOptions",
        "repository": "repository",
        "repository_directory": "repositoryDirectory",
        "require_approval": "requireApproval",
        "sample_code": "sampleCode",
        "scoped_packages_options": "scopedPackagesOptions",
        "scripts": "scripts",
        "srcdir": "srcdir",
        "stability": "stability",
        "stale": "stale",
        "stale_options": "staleOptions",
        "testdir": "testdir",
        "tsconfig": "tsconfig",
        "tsconfig_dev": "tsconfigDev",
        "tsconfig_dev_file": "tsconfigDevFile",
        "ts_jest_options": "tsJestOptions",
        "typescript_version": "typescriptVersion",
        "versionrc_options": "versionrcOptions",
        "vscode": "vscode",
        "watch_excludes": "watchExcludes",
        "watch_includes": "watchIncludes",
        "workflow_bootstrap_steps": "workflowBootstrapSteps",
        "workflow_container_image": "workflowContainerImage",
        "workflow_git_identity": "workflowGitIdentity",
        "workflow_node_version": "workflowNodeVersion",
        "workflow_package_cache": "workflowPackageCache",
        "workflow_runs_on": "workflowRunsOn",
        "workflow_runs_on_group": "workflowRunsOnGroup",
        "yarn_berry_options": "yarnBerryOptions",
    },
)
class CdkTypeScriptAppOptions:
    def __init__(
        self,
        *,
        cdk_version: builtins.str,
        code_owners: typing.Sequence[builtins.str],
        name: builtins.str,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        app: typing.Optional[builtins.str] = None,
        app_entrypoint: typing.Optional[builtins.str] = None,
        artifacts_directory: typing.Optional[builtins.str] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        biome: typing.Optional[builtins.bool] = None,
        biome_options: typing.Optional[typing.Union[_projen_javascript_04054675.BiomeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        build_command: typing.Optional[builtins.str] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_options: typing.Optional[typing.Union[_projen_javascript_04054675.BuildWorkflowOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        build_workflow_triggers: typing.Optional[typing.Union[_projen_github_workflows_04054675.Triggers, typing.Dict[builtins.str, typing.Any]]] = None,
        bump_package: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        bundler_options: typing.Optional[typing.Union[_projen_javascript_04054675.BundlerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bun_version: typing.Optional[builtins.str] = None,
        cdk_assert: typing.Optional[builtins.bool] = None,
        cdk_assertions: typing.Optional[builtins.bool] = None,
        cdk_cli_version: typing.Optional[builtins.str] = None,
        cdk_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_dependencies_as_deps: typing.Optional[builtins.bool] = None,
        cdkout: typing.Optional[builtins.str] = None,
        cdk_test_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_version_pinning: typing.Optional[builtins.bool] = None,
        check_licenses: typing.Optional[typing.Union[_projen_javascript_04054675.LicenseCheckerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        clobber: typing.Optional[builtins.bool] = None,
        code_artifact_options: typing.Optional[typing.Union[_projen_javascript_04054675.CodeArtifactOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        commit_generated: typing.Optional[builtins.bool] = None,
        constructs_version: typing.Optional[builtins.str] = None,
        context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        default_release_branch: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[typing.Union[_projen_github_04054675.DependabotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[typing.Union[_projen_javascript_04054675.UpgradeDependenciesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        disable_tsconfig_dev: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        edge_lambda_auto_discover: typing.Optional[builtins.bool] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[typing.Union[_projen_javascript_04054675.EslintOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        experimental_integ_runner: typing.Optional[builtins.bool] = None,
        feature_flags: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        homepage: typing.Optional[builtins.str] = None,
        integration_test_auto_discover: typing.Optional[builtins.bool] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[typing.Union[_projen_javascript_04054675.JestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        lambda_auto_discover: typing.Optional[builtins.bool] = None,
        lambda_extension_auto_discover: typing.Optional[builtins.bool] = None,
        lambda_options: typing.Optional[typing.Union[_projen_awscdk_04054675.LambdaFunctionCommonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        libdir: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        major_version: typing.Optional[jsii.Number] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        min_major_version: typing.Optional[jsii.Number] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        next_version_command: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[_projen_javascript_04054675.NpmAccess] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        npm_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        npm_provenance: typing.Optional[builtins.bool] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        outdir: typing.Optional[builtins.str] = None,
        package: typing.Optional[builtins.bool] = None,
        package_manager: typing.Optional[_projen_javascript_04054675.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        peer_dependency_options: typing.Optional[typing.Union[_projen_javascript_04054675.PeerDependencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pnpm_version: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[typing.Union[_projen_javascript_04054675.PrettierOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_type: typing.Optional[_projen_04054675.ProjectType] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        readme: typing.Optional[typing.Union["ReadmeOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        releasable_commits: typing.Optional[_projen_04054675.ReleasableCommits] = None,
        release: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, typing.Union[_projen_release_04054675.BranchOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_trigger: typing.Optional[_projen_release_04054675.ReleaseTrigger] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        require_approval: typing.Optional[_projen_awscdk_04054675.ApprovalLevel] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        scoped_packages_options: typing.Optional[typing.Sequence[typing.Union[_projen_javascript_04054675.ScopedPackagesOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        srcdir: typing.Optional[builtins.str] = None,
        stability: typing.Optional[builtins.str] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        ts_jest_options: typing.Optional[typing.Union[_projen_typescript_04054675.TsJestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        vscode: typing.Optional[builtins.bool] = None,
        watch_excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        watch_includes: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_git_identity: typing.Optional[typing.Union[_projen_github_04054675.GitIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        workflow_package_cache: typing.Optional[builtins.bool] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_runs_on_group: typing.Optional[typing.Union[_projen_04054675.GroupRunnerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        yarn_berry_options: typing.Optional[typing.Union[_projen_javascript_04054675.YarnBerryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''CdkTypeScriptAppOptions.

        :param cdk_version: (experimental) Minimum version of the AWS CDK to depend on. Default: "2.1.0"
        :param code_owners: List of teams used to generate the CODEOWNERS file.
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param app: (experimental) The command line to execute in order to synthesize the CDK application (language specific).
        :param app_entrypoint: (experimental) The CDK app's entrypoint (relative to the source directory, which is "src" by default). Default: "main.ts"
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Is the author an organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param biome: (experimental) Setup Biome. Default: false
        :param biome_options: (experimental) Biome options. Default: - default options
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param build_command: (experimental) A command to execute before synthesis. This command will be called when running ``cdk synth`` or when ``cdk watch`` identifies a change in your source code before redeployment. Default: - no build command
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_options: (experimental) Options for PR build workflow.
        :param build_workflow_triggers: (deprecated) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bump_package: (experimental) The ``commit-and-tag-version`` compatible package used to bump the package version, as a dependency string. This can be any compatible package version, including the deprecated ``standard-version@9``. Default: - A recent version of "commit-and-tag-version"
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param bun_version: (experimental) The version of Bun to use if using Bun as a package manager. Default: "latest"
        :param cdk_assert: (deprecated) Warning: NodeJS only. Install the Default: - will be included by default for AWS CDK >= 1.0.0 < 2.0.0
        :param cdk_assertions: (experimental) Install the assertions library? Only needed for CDK 1.x. If using CDK 2.x then assertions is already included in 'aws-cdk-lib' Default: - will be included by default for AWS CDK >= 1.111.0 < 2.0.0
        :param cdk_cli_version: (experimental) Version range of the AWS CDK CLI to depend on. Can be either a specific version, or an NPM version range. By default, the latest 2.x version will be installed; you can use this option to restrict it to a specific version or version range. Default: "^2"
        :param cdk_dependencies: (deprecated) Which AWS CDKv1 modules this project requires.
        :param cdk_dependencies_as_deps: (deprecated) If this is enabled (default), all modules declared in ``cdkDependencies`` will be also added as normal ``dependencies`` (as well as ``peerDependencies``). This is to ensure that downstream consumers actually have your CDK dependencies installed when using npm < 7 or yarn, where peer dependencies are not automatically installed. If this is disabled, ``cdkDependencies`` will be added to ``devDependencies`` to ensure they are present during development. Note: this setting only applies to construct library projects Default: true
        :param cdkout: (experimental) cdk.out directory. Default: "cdk.out"
        :param cdk_test_dependencies: (deprecated) AWS CDK modules required for testing.
        :param cdk_version_pinning: (experimental) Use pinned version instead of caret version for CDK. You can use this to prevent mixed versions for your CDK dependencies and to prevent auto-updates. If you use experimental features this will let you define the moment you include breaking changes.
        :param check_licenses: (experimental) Configure which licenses should be deemed acceptable for use by dependencies. This setting will cause the build to fail, if any prohibited or not allowed licenses ares encountered. Default: - no license checks are run during the build and all licenses will be accepted
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: - true, but false for subprojects
        :param code_artifact_options: (experimental) Options for npm packages using AWS CodeArtifact. This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact Default: - undefined
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v4 A secret is required for private repos. Configured with ``@codeCovTokenSecret``. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param constructs_version: (experimental) Minimum version of the ``constructs`` library to depend on. Default: - for CDK 1.x the default is "3.2.27", for CDK 2.x the default is "10.0.5".
        :param context: (experimental) Additional context to include in ``cdk.json``. Default: - no additional context
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param deps_upgrade: (experimental) Use tasks and github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for ``UpgradeDependencies``. Default: - default options
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param disable_tsconfig_dev: (experimental) Do not generate a ``tsconfig.dev.json`` file. Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param edge_lambda_auto_discover: (experimental) Automatically adds an ``cloudfront.experimental.EdgeFunction`` for each ``.edge-lambda.ts`` handler in your source tree. If this is disabled, you can manually add an ``awscdk.AutoDiscover`` component to your project. Default: true
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json. Default: "lib/index.js"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param experimental_integ_runner: (experimental) Enable experimental support for the AWS CDK integ-runner. Default: false
        :param feature_flags: (experimental) Include all feature flags in cdk.json. Default: true
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param homepage: (experimental) Package's Homepage / Website.
        :param integration_test_auto_discover: (experimental) Automatically discovers and creates integration tests for each ``.integ.ts`` file in under your test directory. Default: true
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param lambda_auto_discover: (experimental) Automatically adds an ``awscdk.LambdaFunction`` for each ``.lambda.ts`` handler in your source tree. If this is disabled, you can manually add an ``awscdk.AutoDiscover`` component to your project. Default: true
        :param lambda_extension_auto_discover: (experimental) Automatically adds an ``awscdk.LambdaExtension`` for each ``.lambda-extension.ts`` entrypoint in your source tree. If this is disabled, you can manually add an ``awscdk.AutoDiscover`` component to your project. Default: true
        :param lambda_options: (experimental) Common options for all AWS Lambda functions. Default: - default options
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param max_node_version: (experimental) The maximum node version supported by this package. Most projects should not use this option. The value indicates that the package is incompatible with any newer versions of node. This requirement is enforced via the engines field. You will normally not need to set this option. Consider this option only if your package is known to not function with newer versions of node. Default: - no maximum version is enforced
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param min_major_version: (experimental) Minimal Major version to release. This can be useful to set to 1, as breaking changes before the 1.x major release are not incrementing the major version number. Can not be set together with ``majorVersion``. Default: - No minimum version is being enforced
        :param min_node_version: (experimental) The minimum node version required by this package to function. Most projects should not use this option. The value indicates that the package is incompatible with any older versions of node. This requirement is enforced via the engines field. You will normally not need to set this option, even if your package is incompatible with EOL versions of node. Consider this option only if your package depends on a specific feature, that is not available in other LTS versions. Setting this option has very high impact on the consumers of your package, as package managers will actively prevent usage with node versions you have marked as incompatible. To change the node version of your CI/CD workflows, use ``workflowNodeVersion``. Default: - no minimum version is enforced
        :param mutable_build: (deprecated) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param next_version_command: (experimental) A shell command to control the next version to release. If present, this shell command will be run before the bump is executed, and it determines what version to release. It will be executed in the following environment: - Working directory: the project directory. - ``$VERSION``: the current version. Looks like ``1.2.3``. - ``$LATEST_TAG``: the most recent tag. Looks like ``prefix-v1.2.3``, or may be unset. - ``$SUGGESTED_BUMP``: the suggested bump action based on commits. One of ``major|minor|patch|none``. The command should print one of the following to ``stdout``: - Nothing: the next version number will be determined based on commit history. - ``x.y.z``: the next version number will be ``x.y.z``. - ``major|minor|patch``: the next version number will be the current version number with the indicated component bumped. This setting cannot be specified together with ``minMajorVersion``; the invoked script can be used to achieve the effects of ``minMajorVersion``. Default: - The next version will be determined based on the commit history and project settings.
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param npm_ignore_options: (experimental) Configuration options for .npmignore file.
        :param npm_provenance: (experimental) Should provenance statements be generated when the package is published. A supported package manager is required to publish a package with npm provenance statements and you will need to use a supported CI/CD provider. Note that the projen ``Release`` and ``Publisher`` components are using ``publib`` to publish packages, which is using npm internally and supports provenance statements independently of the package manager used. Default: - true for public packages, false otherwise
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other subprojects. Default: "."
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN_CLASSIC
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param pnpm_version: (experimental) The version of PNPM to use if using PNPM as a package manager. Default: "9"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: - true if not a subproject
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param readme: Configuration of the README.md file.
        :param releasable_commits: (experimental) Find commits that should be considered releasable Used to decide if a release is required. Default: ReleasableCommits.everyCommit()
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: "v"
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param require_approval: (experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them. Default: ApprovalLevel.BROADENING
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param scoped_packages_options: (experimental) Options for privately hosted scoped packages. Default: - fetch all scoped packages from the public npm registry
        :param scripts: (deprecated) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Also adds the script as a task. Default: {}
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param stability: (experimental) Package's Stability.
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param ts_jest_options: (experimental) Options for ts-jest.
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with commit-and-tag-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param watch_excludes: (experimental) Glob patterns to exclude from ``cdk watch``. Default: []
        :param watch_includes: (experimental) Glob patterns to include in ``cdk watch``. Default: []
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version used in GitHub Actions workflows. Always use this option if your GitHub Actions workflows require a specific to run. Default: - ``minNodeVersion`` if set, otherwise ``lts/*``.
        :param workflow_package_cache: (experimental) Enable Node.js package cache in GitHub workflows. Default: false
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param workflow_runs_on_group: (experimental) Github Runner Group selection options.
        :param yarn_berry_options: (experimental) Options for Yarn Berry. Default: - Yarn Berry v4 with all default options
        '''
        if isinstance(auto_approve_options, dict):
            auto_approve_options = _projen_github_04054675.AutoApproveOptions(**auto_approve_options)
        if isinstance(auto_merge_options, dict):
            auto_merge_options = _projen_github_04054675.AutoMergeOptions(**auto_merge_options)
        if isinstance(biome_options, dict):
            biome_options = _projen_javascript_04054675.BiomeOptions(**biome_options)
        if isinstance(build_workflow_options, dict):
            build_workflow_options = _projen_javascript_04054675.BuildWorkflowOptions(**build_workflow_options)
        if isinstance(build_workflow_triggers, dict):
            build_workflow_triggers = _projen_github_workflows_04054675.Triggers(**build_workflow_triggers)
        if isinstance(bundler_options, dict):
            bundler_options = _projen_javascript_04054675.BundlerOptions(**bundler_options)
        if isinstance(check_licenses, dict):
            check_licenses = _projen_javascript_04054675.LicenseCheckerOptions(**check_licenses)
        if isinstance(code_artifact_options, dict):
            code_artifact_options = _projen_javascript_04054675.CodeArtifactOptions(**code_artifact_options)
        if isinstance(dependabot_options, dict):
            dependabot_options = _projen_github_04054675.DependabotOptions(**dependabot_options)
        if isinstance(deps_upgrade_options, dict):
            deps_upgrade_options = _projen_javascript_04054675.UpgradeDependenciesOptions(**deps_upgrade_options)
        if isinstance(eslint_options, dict):
            eslint_options = _projen_javascript_04054675.EslintOptions(**eslint_options)
        if isinstance(github_options, dict):
            github_options = _projen_github_04054675.GitHubOptions(**github_options)
        if isinstance(git_ignore_options, dict):
            git_ignore_options = _projen_04054675.IgnoreFileOptions(**git_ignore_options)
        if isinstance(git_options, dict):
            git_options = _projen_04054675.GitOptions(**git_options)
        if isinstance(jest_options, dict):
            jest_options = _projen_javascript_04054675.JestOptions(**jest_options)
        if isinstance(lambda_options, dict):
            lambda_options = _projen_awscdk_04054675.LambdaFunctionCommonOptions(**lambda_options)
        if isinstance(logging, dict):
            logging = _projen_04054675.LoggerOptions(**logging)
        if isinstance(mergify_options, dict):
            mergify_options = _projen_github_04054675.MergifyOptions(**mergify_options)
        if isinstance(npm_ignore_options, dict):
            npm_ignore_options = _projen_04054675.IgnoreFileOptions(**npm_ignore_options)
        if isinstance(peer_dependency_options, dict):
            peer_dependency_options = _projen_javascript_04054675.PeerDependencyOptions(**peer_dependency_options)
        if isinstance(prettier_options, dict):
            prettier_options = _projen_javascript_04054675.PrettierOptions(**prettier_options)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = _projen_04054675.ProjenrcJsonOptions(**projenrc_json_options)
        if isinstance(projenrc_js_options, dict):
            projenrc_js_options = _projen_javascript_04054675.ProjenrcOptions(**projenrc_js_options)
        if isinstance(projenrc_ts_options, dict):
            projenrc_ts_options = _projen_typescript_04054675.ProjenrcOptions(**projenrc_ts_options)
        if isinstance(readme, dict):
            readme = ReadmeOptions(**readme)
        if isinstance(renovatebot_options, dict):
            renovatebot_options = _projen_04054675.RenovatebotOptions(**renovatebot_options)
        if isinstance(stale_options, dict):
            stale_options = _projen_github_04054675.StaleOptions(**stale_options)
        if isinstance(tsconfig, dict):
            tsconfig = _projen_javascript_04054675.TypescriptConfigOptions(**tsconfig)
        if isinstance(tsconfig_dev, dict):
            tsconfig_dev = _projen_javascript_04054675.TypescriptConfigOptions(**tsconfig_dev)
        if isinstance(ts_jest_options, dict):
            ts_jest_options = _projen_typescript_04054675.TsJestOptions(**ts_jest_options)
        if isinstance(workflow_git_identity, dict):
            workflow_git_identity = _projen_github_04054675.GitIdentity(**workflow_git_identity)
        if isinstance(workflow_runs_on_group, dict):
            workflow_runs_on_group = _projen_04054675.GroupRunnerOptions(**workflow_runs_on_group)
        if isinstance(yarn_berry_options, dict):
            yarn_berry_options = _projen_javascript_04054675.YarnBerryOptions(**yarn_berry_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a6354f4c0532263f309ca59025d89b070b95588f76bd5815340cc71a5341012)
            check_type(argname="argument cdk_version", value=cdk_version, expected_type=type_hints["cdk_version"])
            check_type(argname="argument code_owners", value=code_owners, expected_type=type_hints["code_owners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument allow_library_dependencies", value=allow_library_dependencies, expected_type=type_hints["allow_library_dependencies"])
            check_type(argname="argument app", value=app, expected_type=type_hints["app"])
            check_type(argname="argument app_entrypoint", value=app_entrypoint, expected_type=type_hints["app_entrypoint"])
            check_type(argname="argument artifacts_directory", value=artifacts_directory, expected_type=type_hints["artifacts_directory"])
            check_type(argname="argument author_email", value=author_email, expected_type=type_hints["author_email"])
            check_type(argname="argument author_name", value=author_name, expected_type=type_hints["author_name"])
            check_type(argname="argument author_organization", value=author_organization, expected_type=type_hints["author_organization"])
            check_type(argname="argument author_url", value=author_url, expected_type=type_hints["author_url"])
            check_type(argname="argument auto_approve_options", value=auto_approve_options, expected_type=type_hints["auto_approve_options"])
            check_type(argname="argument auto_approve_upgrades", value=auto_approve_upgrades, expected_type=type_hints["auto_approve_upgrades"])
            check_type(argname="argument auto_detect_bin", value=auto_detect_bin, expected_type=type_hints["auto_detect_bin"])
            check_type(argname="argument auto_merge", value=auto_merge, expected_type=type_hints["auto_merge"])
            check_type(argname="argument auto_merge_options", value=auto_merge_options, expected_type=type_hints["auto_merge_options"])
            check_type(argname="argument bin", value=bin, expected_type=type_hints["bin"])
            check_type(argname="argument biome", value=biome, expected_type=type_hints["biome"])
            check_type(argname="argument biome_options", value=biome_options, expected_type=type_hints["biome_options"])
            check_type(argname="argument bugs_email", value=bugs_email, expected_type=type_hints["bugs_email"])
            check_type(argname="argument bugs_url", value=bugs_url, expected_type=type_hints["bugs_url"])
            check_type(argname="argument build_command", value=build_command, expected_type=type_hints["build_command"])
            check_type(argname="argument build_workflow", value=build_workflow, expected_type=type_hints["build_workflow"])
            check_type(argname="argument build_workflow_options", value=build_workflow_options, expected_type=type_hints["build_workflow_options"])
            check_type(argname="argument build_workflow_triggers", value=build_workflow_triggers, expected_type=type_hints["build_workflow_triggers"])
            check_type(argname="argument bump_package", value=bump_package, expected_type=type_hints["bump_package"])
            check_type(argname="argument bundled_deps", value=bundled_deps, expected_type=type_hints["bundled_deps"])
            check_type(argname="argument bundler_options", value=bundler_options, expected_type=type_hints["bundler_options"])
            check_type(argname="argument bun_version", value=bun_version, expected_type=type_hints["bun_version"])
            check_type(argname="argument cdk_assert", value=cdk_assert, expected_type=type_hints["cdk_assert"])
            check_type(argname="argument cdk_assertions", value=cdk_assertions, expected_type=type_hints["cdk_assertions"])
            check_type(argname="argument cdk_cli_version", value=cdk_cli_version, expected_type=type_hints["cdk_cli_version"])
            check_type(argname="argument cdk_dependencies", value=cdk_dependencies, expected_type=type_hints["cdk_dependencies"])
            check_type(argname="argument cdk_dependencies_as_deps", value=cdk_dependencies_as_deps, expected_type=type_hints["cdk_dependencies_as_deps"])
            check_type(argname="argument cdkout", value=cdkout, expected_type=type_hints["cdkout"])
            check_type(argname="argument cdk_test_dependencies", value=cdk_test_dependencies, expected_type=type_hints["cdk_test_dependencies"])
            check_type(argname="argument cdk_version_pinning", value=cdk_version_pinning, expected_type=type_hints["cdk_version_pinning"])
            check_type(argname="argument check_licenses", value=check_licenses, expected_type=type_hints["check_licenses"])
            check_type(argname="argument clobber", value=clobber, expected_type=type_hints["clobber"])
            check_type(argname="argument code_artifact_options", value=code_artifact_options, expected_type=type_hints["code_artifact_options"])
            check_type(argname="argument code_cov", value=code_cov, expected_type=type_hints["code_cov"])
            check_type(argname="argument code_cov_token_secret", value=code_cov_token_secret, expected_type=type_hints["code_cov_token_secret"])
            check_type(argname="argument commit_generated", value=commit_generated, expected_type=type_hints["commit_generated"])
            check_type(argname="argument constructs_version", value=constructs_version, expected_type=type_hints["constructs_version"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
            check_type(argname="argument copyright_owner", value=copyright_owner, expected_type=type_hints["copyright_owner"])
            check_type(argname="argument copyright_period", value=copyright_period, expected_type=type_hints["copyright_period"])
            check_type(argname="argument default_release_branch", value=default_release_branch, expected_type=type_hints["default_release_branch"])
            check_type(argname="argument dependabot", value=dependabot, expected_type=type_hints["dependabot"])
            check_type(argname="argument dependabot_options", value=dependabot_options, expected_type=type_hints["dependabot_options"])
            check_type(argname="argument deps", value=deps, expected_type=type_hints["deps"])
            check_type(argname="argument deps_upgrade", value=deps_upgrade, expected_type=type_hints["deps_upgrade"])
            check_type(argname="argument deps_upgrade_options", value=deps_upgrade_options, expected_type=type_hints["deps_upgrade_options"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument dev_container", value=dev_container, expected_type=type_hints["dev_container"])
            check_type(argname="argument dev_deps", value=dev_deps, expected_type=type_hints["dev_deps"])
            check_type(argname="argument disable_tsconfig", value=disable_tsconfig, expected_type=type_hints["disable_tsconfig"])
            check_type(argname="argument disable_tsconfig_dev", value=disable_tsconfig_dev, expected_type=type_hints["disable_tsconfig_dev"])
            check_type(argname="argument docgen", value=docgen, expected_type=type_hints["docgen"])
            check_type(argname="argument docs_directory", value=docs_directory, expected_type=type_hints["docs_directory"])
            check_type(argname="argument edge_lambda_auto_discover", value=edge_lambda_auto_discover, expected_type=type_hints["edge_lambda_auto_discover"])
            check_type(argname="argument entrypoint", value=entrypoint, expected_type=type_hints["entrypoint"])
            check_type(argname="argument entrypoint_types", value=entrypoint_types, expected_type=type_hints["entrypoint_types"])
            check_type(argname="argument eslint", value=eslint, expected_type=type_hints["eslint"])
            check_type(argname="argument eslint_options", value=eslint_options, expected_type=type_hints["eslint_options"])
            check_type(argname="argument experimental_integ_runner", value=experimental_integ_runner, expected_type=type_hints["experimental_integ_runner"])
            check_type(argname="argument feature_flags", value=feature_flags, expected_type=type_hints["feature_flags"])
            check_type(argname="argument github", value=github, expected_type=type_hints["github"])
            check_type(argname="argument github_options", value=github_options, expected_type=type_hints["github_options"])
            check_type(argname="argument gitignore", value=gitignore, expected_type=type_hints["gitignore"])
            check_type(argname="argument git_ignore_options", value=git_ignore_options, expected_type=type_hints["git_ignore_options"])
            check_type(argname="argument git_options", value=git_options, expected_type=type_hints["git_options"])
            check_type(argname="argument gitpod", value=gitpod, expected_type=type_hints["gitpod"])
            check_type(argname="argument homepage", value=homepage, expected_type=type_hints["homepage"])
            check_type(argname="argument integration_test_auto_discover", value=integration_test_auto_discover, expected_type=type_hints["integration_test_auto_discover"])
            check_type(argname="argument jest", value=jest, expected_type=type_hints["jest"])
            check_type(argname="argument jest_options", value=jest_options, expected_type=type_hints["jest_options"])
            check_type(argname="argument jsii_release_version", value=jsii_release_version, expected_type=type_hints["jsii_release_version"])
            check_type(argname="argument keywords", value=keywords, expected_type=type_hints["keywords"])
            check_type(argname="argument lambda_auto_discover", value=lambda_auto_discover, expected_type=type_hints["lambda_auto_discover"])
            check_type(argname="argument lambda_extension_auto_discover", value=lambda_extension_auto_discover, expected_type=type_hints["lambda_extension_auto_discover"])
            check_type(argname="argument lambda_options", value=lambda_options, expected_type=type_hints["lambda_options"])
            check_type(argname="argument libdir", value=libdir, expected_type=type_hints["libdir"])
            check_type(argname="argument license", value=license, expected_type=type_hints["license"])
            check_type(argname="argument licensed", value=licensed, expected_type=type_hints["licensed"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument major_version", value=major_version, expected_type=type_hints["major_version"])
            check_type(argname="argument max_node_version", value=max_node_version, expected_type=type_hints["max_node_version"])
            check_type(argname="argument mergify", value=mergify, expected_type=type_hints["mergify"])
            check_type(argname="argument mergify_options", value=mergify_options, expected_type=type_hints["mergify_options"])
            check_type(argname="argument min_major_version", value=min_major_version, expected_type=type_hints["min_major_version"])
            check_type(argname="argument min_node_version", value=min_node_version, expected_type=type_hints["min_node_version"])
            check_type(argname="argument mutable_build", value=mutable_build, expected_type=type_hints["mutable_build"])
            check_type(argname="argument next_version_command", value=next_version_command, expected_type=type_hints["next_version_command"])
            check_type(argname="argument npm_access", value=npm_access, expected_type=type_hints["npm_access"])
            check_type(argname="argument npm_dist_tag", value=npm_dist_tag, expected_type=type_hints["npm_dist_tag"])
            check_type(argname="argument npmignore", value=npmignore, expected_type=type_hints["npmignore"])
            check_type(argname="argument npmignore_enabled", value=npmignore_enabled, expected_type=type_hints["npmignore_enabled"])
            check_type(argname="argument npm_ignore_options", value=npm_ignore_options, expected_type=type_hints["npm_ignore_options"])
            check_type(argname="argument npm_provenance", value=npm_provenance, expected_type=type_hints["npm_provenance"])
            check_type(argname="argument npm_registry", value=npm_registry, expected_type=type_hints["npm_registry"])
            check_type(argname="argument npm_registry_url", value=npm_registry_url, expected_type=type_hints["npm_registry_url"])
            check_type(argname="argument npm_token_secret", value=npm_token_secret, expected_type=type_hints["npm_token_secret"])
            check_type(argname="argument outdir", value=outdir, expected_type=type_hints["outdir"])
            check_type(argname="argument package", value=package, expected_type=type_hints["package"])
            check_type(argname="argument package_manager", value=package_manager, expected_type=type_hints["package_manager"])
            check_type(argname="argument package_name", value=package_name, expected_type=type_hints["package_name"])
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument peer_dependency_options", value=peer_dependency_options, expected_type=type_hints["peer_dependency_options"])
            check_type(argname="argument peer_deps", value=peer_deps, expected_type=type_hints["peer_deps"])
            check_type(argname="argument pnpm_version", value=pnpm_version, expected_type=type_hints["pnpm_version"])
            check_type(argname="argument post_build_steps", value=post_build_steps, expected_type=type_hints["post_build_steps"])
            check_type(argname="argument prerelease", value=prerelease, expected_type=type_hints["prerelease"])
            check_type(argname="argument prettier", value=prettier, expected_type=type_hints["prettier"])
            check_type(argname="argument prettier_options", value=prettier_options, expected_type=type_hints["prettier_options"])
            check_type(argname="argument project_type", value=project_type, expected_type=type_hints["project_type"])
            check_type(argname="argument projen_command", value=projen_command, expected_type=type_hints["projen_command"])
            check_type(argname="argument projen_credentials", value=projen_credentials, expected_type=type_hints["projen_credentials"])
            check_type(argname="argument projen_dev_dependency", value=projen_dev_dependency, expected_type=type_hints["projen_dev_dependency"])
            check_type(argname="argument projenrc_js", value=projenrc_js, expected_type=type_hints["projenrc_js"])
            check_type(argname="argument projenrc_json", value=projenrc_json, expected_type=type_hints["projenrc_json"])
            check_type(argname="argument projenrc_json_options", value=projenrc_json_options, expected_type=type_hints["projenrc_json_options"])
            check_type(argname="argument projenrc_js_options", value=projenrc_js_options, expected_type=type_hints["projenrc_js_options"])
            check_type(argname="argument projenrc_ts", value=projenrc_ts, expected_type=type_hints["projenrc_ts"])
            check_type(argname="argument projenrc_ts_options", value=projenrc_ts_options, expected_type=type_hints["projenrc_ts_options"])
            check_type(argname="argument projen_token_secret", value=projen_token_secret, expected_type=type_hints["projen_token_secret"])
            check_type(argname="argument projen_version", value=projen_version, expected_type=type_hints["projen_version"])
            check_type(argname="argument publish_dry_run", value=publish_dry_run, expected_type=type_hints["publish_dry_run"])
            check_type(argname="argument publish_tasks", value=publish_tasks, expected_type=type_hints["publish_tasks"])
            check_type(argname="argument pull_request_template", value=pull_request_template, expected_type=type_hints["pull_request_template"])
            check_type(argname="argument pull_request_template_contents", value=pull_request_template_contents, expected_type=type_hints["pull_request_template_contents"])
            check_type(argname="argument readme", value=readme, expected_type=type_hints["readme"])
            check_type(argname="argument releasable_commits", value=releasable_commits, expected_type=type_hints["releasable_commits"])
            check_type(argname="argument release", value=release, expected_type=type_hints["release"])
            check_type(argname="argument release_branches", value=release_branches, expected_type=type_hints["release_branches"])
            check_type(argname="argument release_every_commit", value=release_every_commit, expected_type=type_hints["release_every_commit"])
            check_type(argname="argument release_failure_issue", value=release_failure_issue, expected_type=type_hints["release_failure_issue"])
            check_type(argname="argument release_failure_issue_label", value=release_failure_issue_label, expected_type=type_hints["release_failure_issue_label"])
            check_type(argname="argument release_schedule", value=release_schedule, expected_type=type_hints["release_schedule"])
            check_type(argname="argument release_tag_prefix", value=release_tag_prefix, expected_type=type_hints["release_tag_prefix"])
            check_type(argname="argument release_to_npm", value=release_to_npm, expected_type=type_hints["release_to_npm"])
            check_type(argname="argument release_trigger", value=release_trigger, expected_type=type_hints["release_trigger"])
            check_type(argname="argument release_workflow", value=release_workflow, expected_type=type_hints["release_workflow"])
            check_type(argname="argument release_workflow_name", value=release_workflow_name, expected_type=type_hints["release_workflow_name"])
            check_type(argname="argument release_workflow_setup_steps", value=release_workflow_setup_steps, expected_type=type_hints["release_workflow_setup_steps"])
            check_type(argname="argument renovatebot", value=renovatebot, expected_type=type_hints["renovatebot"])
            check_type(argname="argument renovatebot_options", value=renovatebot_options, expected_type=type_hints["renovatebot_options"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument repository_directory", value=repository_directory, expected_type=type_hints["repository_directory"])
            check_type(argname="argument require_approval", value=require_approval, expected_type=type_hints["require_approval"])
            check_type(argname="argument sample_code", value=sample_code, expected_type=type_hints["sample_code"])
            check_type(argname="argument scoped_packages_options", value=scoped_packages_options, expected_type=type_hints["scoped_packages_options"])
            check_type(argname="argument scripts", value=scripts, expected_type=type_hints["scripts"])
            check_type(argname="argument srcdir", value=srcdir, expected_type=type_hints["srcdir"])
            check_type(argname="argument stability", value=stability, expected_type=type_hints["stability"])
            check_type(argname="argument stale", value=stale, expected_type=type_hints["stale"])
            check_type(argname="argument stale_options", value=stale_options, expected_type=type_hints["stale_options"])
            check_type(argname="argument testdir", value=testdir, expected_type=type_hints["testdir"])
            check_type(argname="argument tsconfig", value=tsconfig, expected_type=type_hints["tsconfig"])
            check_type(argname="argument tsconfig_dev", value=tsconfig_dev, expected_type=type_hints["tsconfig_dev"])
            check_type(argname="argument tsconfig_dev_file", value=tsconfig_dev_file, expected_type=type_hints["tsconfig_dev_file"])
            check_type(argname="argument ts_jest_options", value=ts_jest_options, expected_type=type_hints["ts_jest_options"])
            check_type(argname="argument typescript_version", value=typescript_version, expected_type=type_hints["typescript_version"])
            check_type(argname="argument versionrc_options", value=versionrc_options, expected_type=type_hints["versionrc_options"])
            check_type(argname="argument vscode", value=vscode, expected_type=type_hints["vscode"])
            check_type(argname="argument watch_excludes", value=watch_excludes, expected_type=type_hints["watch_excludes"])
            check_type(argname="argument watch_includes", value=watch_includes, expected_type=type_hints["watch_includes"])
            check_type(argname="argument workflow_bootstrap_steps", value=workflow_bootstrap_steps, expected_type=type_hints["workflow_bootstrap_steps"])
            check_type(argname="argument workflow_container_image", value=workflow_container_image, expected_type=type_hints["workflow_container_image"])
            check_type(argname="argument workflow_git_identity", value=workflow_git_identity, expected_type=type_hints["workflow_git_identity"])
            check_type(argname="argument workflow_node_version", value=workflow_node_version, expected_type=type_hints["workflow_node_version"])
            check_type(argname="argument workflow_package_cache", value=workflow_package_cache, expected_type=type_hints["workflow_package_cache"])
            check_type(argname="argument workflow_runs_on", value=workflow_runs_on, expected_type=type_hints["workflow_runs_on"])
            check_type(argname="argument workflow_runs_on_group", value=workflow_runs_on_group, expected_type=type_hints["workflow_runs_on_group"])
            check_type(argname="argument yarn_berry_options", value=yarn_berry_options, expected_type=type_hints["yarn_berry_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cdk_version": cdk_version,
            "code_owners": code_owners,
            "name": name,
        }
        if allow_library_dependencies is not None:
            self._values["allow_library_dependencies"] = allow_library_dependencies
        if app is not None:
            self._values["app"] = app
        if app_entrypoint is not None:
            self._values["app_entrypoint"] = app_entrypoint
        if artifacts_directory is not None:
            self._values["artifacts_directory"] = artifacts_directory
        if author_email is not None:
            self._values["author_email"] = author_email
        if author_name is not None:
            self._values["author_name"] = author_name
        if author_organization is not None:
            self._values["author_organization"] = author_organization
        if author_url is not None:
            self._values["author_url"] = author_url
        if auto_approve_options is not None:
            self._values["auto_approve_options"] = auto_approve_options
        if auto_approve_upgrades is not None:
            self._values["auto_approve_upgrades"] = auto_approve_upgrades
        if auto_detect_bin is not None:
            self._values["auto_detect_bin"] = auto_detect_bin
        if auto_merge is not None:
            self._values["auto_merge"] = auto_merge
        if auto_merge_options is not None:
            self._values["auto_merge_options"] = auto_merge_options
        if bin is not None:
            self._values["bin"] = bin
        if biome is not None:
            self._values["biome"] = biome
        if biome_options is not None:
            self._values["biome_options"] = biome_options
        if bugs_email is not None:
            self._values["bugs_email"] = bugs_email
        if bugs_url is not None:
            self._values["bugs_url"] = bugs_url
        if build_command is not None:
            self._values["build_command"] = build_command
        if build_workflow is not None:
            self._values["build_workflow"] = build_workflow
        if build_workflow_options is not None:
            self._values["build_workflow_options"] = build_workflow_options
        if build_workflow_triggers is not None:
            self._values["build_workflow_triggers"] = build_workflow_triggers
        if bump_package is not None:
            self._values["bump_package"] = bump_package
        if bundled_deps is not None:
            self._values["bundled_deps"] = bundled_deps
        if bundler_options is not None:
            self._values["bundler_options"] = bundler_options
        if bun_version is not None:
            self._values["bun_version"] = bun_version
        if cdk_assert is not None:
            self._values["cdk_assert"] = cdk_assert
        if cdk_assertions is not None:
            self._values["cdk_assertions"] = cdk_assertions
        if cdk_cli_version is not None:
            self._values["cdk_cli_version"] = cdk_cli_version
        if cdk_dependencies is not None:
            self._values["cdk_dependencies"] = cdk_dependencies
        if cdk_dependencies_as_deps is not None:
            self._values["cdk_dependencies_as_deps"] = cdk_dependencies_as_deps
        if cdkout is not None:
            self._values["cdkout"] = cdkout
        if cdk_test_dependencies is not None:
            self._values["cdk_test_dependencies"] = cdk_test_dependencies
        if cdk_version_pinning is not None:
            self._values["cdk_version_pinning"] = cdk_version_pinning
        if check_licenses is not None:
            self._values["check_licenses"] = check_licenses
        if clobber is not None:
            self._values["clobber"] = clobber
        if code_artifact_options is not None:
            self._values["code_artifact_options"] = code_artifact_options
        if code_cov is not None:
            self._values["code_cov"] = code_cov
        if code_cov_token_secret is not None:
            self._values["code_cov_token_secret"] = code_cov_token_secret
        if commit_generated is not None:
            self._values["commit_generated"] = commit_generated
        if constructs_version is not None:
            self._values["constructs_version"] = constructs_version
        if context is not None:
            self._values["context"] = context
        if copyright_owner is not None:
            self._values["copyright_owner"] = copyright_owner
        if copyright_period is not None:
            self._values["copyright_period"] = copyright_period
        if default_release_branch is not None:
            self._values["default_release_branch"] = default_release_branch
        if dependabot is not None:
            self._values["dependabot"] = dependabot
        if dependabot_options is not None:
            self._values["dependabot_options"] = dependabot_options
        if deps is not None:
            self._values["deps"] = deps
        if deps_upgrade is not None:
            self._values["deps_upgrade"] = deps_upgrade
        if deps_upgrade_options is not None:
            self._values["deps_upgrade_options"] = deps_upgrade_options
        if description is not None:
            self._values["description"] = description
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if dev_deps is not None:
            self._values["dev_deps"] = dev_deps
        if disable_tsconfig is not None:
            self._values["disable_tsconfig"] = disable_tsconfig
        if disable_tsconfig_dev is not None:
            self._values["disable_tsconfig_dev"] = disable_tsconfig_dev
        if docgen is not None:
            self._values["docgen"] = docgen
        if docs_directory is not None:
            self._values["docs_directory"] = docs_directory
        if edge_lambda_auto_discover is not None:
            self._values["edge_lambda_auto_discover"] = edge_lambda_auto_discover
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint
        if entrypoint_types is not None:
            self._values["entrypoint_types"] = entrypoint_types
        if eslint is not None:
            self._values["eslint"] = eslint
        if eslint_options is not None:
            self._values["eslint_options"] = eslint_options
        if experimental_integ_runner is not None:
            self._values["experimental_integ_runner"] = experimental_integ_runner
        if feature_flags is not None:
            self._values["feature_flags"] = feature_flags
        if github is not None:
            self._values["github"] = github
        if github_options is not None:
            self._values["github_options"] = github_options
        if gitignore is not None:
            self._values["gitignore"] = gitignore
        if git_ignore_options is not None:
            self._values["git_ignore_options"] = git_ignore_options
        if git_options is not None:
            self._values["git_options"] = git_options
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if homepage is not None:
            self._values["homepage"] = homepage
        if integration_test_auto_discover is not None:
            self._values["integration_test_auto_discover"] = integration_test_auto_discover
        if jest is not None:
            self._values["jest"] = jest
        if jest_options is not None:
            self._values["jest_options"] = jest_options
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version
        if keywords is not None:
            self._values["keywords"] = keywords
        if lambda_auto_discover is not None:
            self._values["lambda_auto_discover"] = lambda_auto_discover
        if lambda_extension_auto_discover is not None:
            self._values["lambda_extension_auto_discover"] = lambda_extension_auto_discover
        if lambda_options is not None:
            self._values["lambda_options"] = lambda_options
        if libdir is not None:
            self._values["libdir"] = libdir
        if license is not None:
            self._values["license"] = license
        if licensed is not None:
            self._values["licensed"] = licensed
        if logging is not None:
            self._values["logging"] = logging
        if major_version is not None:
            self._values["major_version"] = major_version
        if max_node_version is not None:
            self._values["max_node_version"] = max_node_version
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if min_major_version is not None:
            self._values["min_major_version"] = min_major_version
        if min_node_version is not None:
            self._values["min_node_version"] = min_node_version
        if mutable_build is not None:
            self._values["mutable_build"] = mutable_build
        if next_version_command is not None:
            self._values["next_version_command"] = next_version_command
        if npm_access is not None:
            self._values["npm_access"] = npm_access
        if npm_dist_tag is not None:
            self._values["npm_dist_tag"] = npm_dist_tag
        if npmignore is not None:
            self._values["npmignore"] = npmignore
        if npmignore_enabled is not None:
            self._values["npmignore_enabled"] = npmignore_enabled
        if npm_ignore_options is not None:
            self._values["npm_ignore_options"] = npm_ignore_options
        if npm_provenance is not None:
            self._values["npm_provenance"] = npm_provenance
        if npm_registry is not None:
            self._values["npm_registry"] = npm_registry
        if npm_registry_url is not None:
            self._values["npm_registry_url"] = npm_registry_url
        if npm_token_secret is not None:
            self._values["npm_token_secret"] = npm_token_secret
        if outdir is not None:
            self._values["outdir"] = outdir
        if package is not None:
            self._values["package"] = package
        if package_manager is not None:
            self._values["package_manager"] = package_manager
        if package_name is not None:
            self._values["package_name"] = package_name
        if parent is not None:
            self._values["parent"] = parent
        if peer_dependency_options is not None:
            self._values["peer_dependency_options"] = peer_dependency_options
        if peer_deps is not None:
            self._values["peer_deps"] = peer_deps
        if pnpm_version is not None:
            self._values["pnpm_version"] = pnpm_version
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if prerelease is not None:
            self._values["prerelease"] = prerelease
        if prettier is not None:
            self._values["prettier"] = prettier
        if prettier_options is not None:
            self._values["prettier_options"] = prettier_options
        if project_type is not None:
            self._values["project_type"] = project_type
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projen_credentials is not None:
            self._values["projen_credentials"] = projen_credentials
        if projen_dev_dependency is not None:
            self._values["projen_dev_dependency"] = projen_dev_dependency
        if projenrc_js is not None:
            self._values["projenrc_js"] = projenrc_js
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if projenrc_js_options is not None:
            self._values["projenrc_js_options"] = projenrc_js_options
        if projenrc_ts is not None:
            self._values["projenrc_ts"] = projenrc_ts
        if projenrc_ts_options is not None:
            self._values["projenrc_ts_options"] = projenrc_ts_options
        if projen_token_secret is not None:
            self._values["projen_token_secret"] = projen_token_secret
        if projen_version is not None:
            self._values["projen_version"] = projen_version
        if publish_dry_run is not None:
            self._values["publish_dry_run"] = publish_dry_run
        if publish_tasks is not None:
            self._values["publish_tasks"] = publish_tasks
        if pull_request_template is not None:
            self._values["pull_request_template"] = pull_request_template
        if pull_request_template_contents is not None:
            self._values["pull_request_template_contents"] = pull_request_template_contents
        if readme is not None:
            self._values["readme"] = readme
        if releasable_commits is not None:
            self._values["releasable_commits"] = releasable_commits
        if release is not None:
            self._values["release"] = release
        if release_branches is not None:
            self._values["release_branches"] = release_branches
        if release_every_commit is not None:
            self._values["release_every_commit"] = release_every_commit
        if release_failure_issue is not None:
            self._values["release_failure_issue"] = release_failure_issue
        if release_failure_issue_label is not None:
            self._values["release_failure_issue_label"] = release_failure_issue_label
        if release_schedule is not None:
            self._values["release_schedule"] = release_schedule
        if release_tag_prefix is not None:
            self._values["release_tag_prefix"] = release_tag_prefix
        if release_to_npm is not None:
            self._values["release_to_npm"] = release_to_npm
        if release_trigger is not None:
            self._values["release_trigger"] = release_trigger
        if release_workflow is not None:
            self._values["release_workflow"] = release_workflow
        if release_workflow_name is not None:
            self._values["release_workflow_name"] = release_workflow_name
        if release_workflow_setup_steps is not None:
            self._values["release_workflow_setup_steps"] = release_workflow_setup_steps
        if renovatebot is not None:
            self._values["renovatebot"] = renovatebot
        if renovatebot_options is not None:
            self._values["renovatebot_options"] = renovatebot_options
        if repository is not None:
            self._values["repository"] = repository
        if repository_directory is not None:
            self._values["repository_directory"] = repository_directory
        if require_approval is not None:
            self._values["require_approval"] = require_approval
        if sample_code is not None:
            self._values["sample_code"] = sample_code
        if scoped_packages_options is not None:
            self._values["scoped_packages_options"] = scoped_packages_options
        if scripts is not None:
            self._values["scripts"] = scripts
        if srcdir is not None:
            self._values["srcdir"] = srcdir
        if stability is not None:
            self._values["stability"] = stability
        if stale is not None:
            self._values["stale"] = stale
        if stale_options is not None:
            self._values["stale_options"] = stale_options
        if testdir is not None:
            self._values["testdir"] = testdir
        if tsconfig is not None:
            self._values["tsconfig"] = tsconfig
        if tsconfig_dev is not None:
            self._values["tsconfig_dev"] = tsconfig_dev
        if tsconfig_dev_file is not None:
            self._values["tsconfig_dev_file"] = tsconfig_dev_file
        if ts_jest_options is not None:
            self._values["ts_jest_options"] = ts_jest_options
        if typescript_version is not None:
            self._values["typescript_version"] = typescript_version
        if versionrc_options is not None:
            self._values["versionrc_options"] = versionrc_options
        if vscode is not None:
            self._values["vscode"] = vscode
        if watch_excludes is not None:
            self._values["watch_excludes"] = watch_excludes
        if watch_includes is not None:
            self._values["watch_includes"] = watch_includes
        if workflow_bootstrap_steps is not None:
            self._values["workflow_bootstrap_steps"] = workflow_bootstrap_steps
        if workflow_container_image is not None:
            self._values["workflow_container_image"] = workflow_container_image
        if workflow_git_identity is not None:
            self._values["workflow_git_identity"] = workflow_git_identity
        if workflow_node_version is not None:
            self._values["workflow_node_version"] = workflow_node_version
        if workflow_package_cache is not None:
            self._values["workflow_package_cache"] = workflow_package_cache
        if workflow_runs_on is not None:
            self._values["workflow_runs_on"] = workflow_runs_on
        if workflow_runs_on_group is not None:
            self._values["workflow_runs_on_group"] = workflow_runs_on_group
        if yarn_berry_options is not None:
            self._values["yarn_berry_options"] = yarn_berry_options

    @builtins.property
    def cdk_version(self) -> builtins.str:
        '''(experimental) Minimum version of the AWS CDK to depend on.

        :default: "2.1.0"

        :stability: experimental
        '''
        result = self._values.get("cdk_version")
        assert result is not None, "Required property 'cdk_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code_owners(self) -> typing.List[builtins.str]:
        '''List of teams used to generate the CODEOWNERS file.'''
        result = self._values.get("code_owners")
        assert result is not None, "Required property 'code_owners' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_library_dependencies(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``.

        This is normally only allowed for libraries. For apps, there's no meaning
        for specifying these.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("allow_library_dependencies")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def app(self) -> typing.Optional[builtins.str]:
        '''(experimental) The command line to execute in order to synthesize the CDK application (language specific).

        :stability: experimental
        '''
        result = self._values.get("app")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def app_entrypoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) The CDK app's entrypoint (relative to the source directory, which is "src" by default).

        :default: "main.ts"

        :stability: experimental
        '''
        result = self._values.get("app_entrypoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def artifacts_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) A directory which will contain build artifacts.

        :default: "dist"

        :stability: experimental
        '''
        result = self._values.get("artifacts_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's e-mail.

        :stability: experimental
        '''
        result = self._values.get("author_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's name.

        :stability: experimental
        '''
        result = self._values.get("author_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_organization(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Is the author an organization.

        :stability: experimental
        '''
        result = self._values.get("author_organization")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's URL / Website.

        :stability: experimental
        '''
        result = self._values.get("author_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_approve_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.AutoApproveOptions]:
        '''(experimental) Enable and configure the 'auto approve' workflow.

        :default: - auto approve is disabled

        :stability: experimental
        '''
        result = self._values.get("auto_approve_options")
        return typing.cast(typing.Optional[_projen_github_04054675.AutoApproveOptions], result)

    @builtins.property
    def auto_approve_upgrades(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued).

        Throw if set to true but ``autoApproveOptions`` are not defined.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("auto_approve_upgrades")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_detect_bin(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_detect_bin")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_merge(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable automatic merging on GitHub.

        Has no effect if ``github.mergify``
        is set to false.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_merge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_merge_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.AutoMergeOptions]:
        '''(experimental) Configure options for automatic merging on GitHub.

        Has no effect if
        ``github.mergify`` or ``autoMerge`` is set to false.

        :default: - see defaults in ``AutoMergeOptions``

        :stability: experimental
        '''
        result = self._values.get("auto_merge_options")
        return typing.cast(typing.Optional[_projen_github_04054675.AutoMergeOptions], result)

    @builtins.property
    def bin(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Binary programs vended with your module.

        You can use this option to add/customize how binaries are represented in
        your ``package.json``, but unless ``autoDetectBin`` is ``false``, every
        executable file under ``bin`` will automatically be added to this section.

        :stability: experimental
        '''
        result = self._values.get("bin")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def biome(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup Biome.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("biome")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def biome_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.BiomeOptions]:
        '''(experimental) Biome options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("biome_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.BiomeOptions], result)

    @builtins.property
    def bugs_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) The email address to which issues should be reported.

        :stability: experimental
        '''
        result = self._values.get("bugs_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bugs_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The url to your project's issue tracker.

        :stability: experimental
        '''
        result = self._values.get("bugs_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) A command to execute before synthesis.

        This command will be called when
        running ``cdk synth`` or when ``cdk watch`` identifies a change in your source
        code before redeployment.

        :default: - no build command

        :stability: experimental
        '''
        result = self._values.get("build_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_workflow(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow for building PRs.

        :default: - true if not a subproject

        :stability: experimental
        '''
        result = self._values.get("build_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_workflow_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.BuildWorkflowOptions]:
        '''(experimental) Options for PR build workflow.

        :stability: experimental
        '''
        result = self._values.get("build_workflow_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.BuildWorkflowOptions], result)

    @builtins.property
    def build_workflow_triggers(
        self,
    ) -> typing.Optional[_projen_github_workflows_04054675.Triggers]:
        '''(deprecated) Build workflow triggers.

        :default: "{ pullRequest: {}, workflowDispatch: {} }"

        :deprecated: - Use ``buildWorkflowOptions.workflowTriggers``

        :stability: deprecated
        '''
        result = self._values.get("build_workflow_triggers")
        return typing.cast(typing.Optional[_projen_github_workflows_04054675.Triggers], result)

    @builtins.property
    def bump_package(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ``commit-and-tag-version`` compatible package used to bump the package version, as a dependency string.

        This can be any compatible package version, including the deprecated ``standard-version@9``.

        :default: - A recent version of "commit-and-tag-version"

        :stability: experimental
        '''
        result = self._values.get("bump_package")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bundled_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of dependencies to bundle into this module.

        These modules will be
        added both to the ``dependencies`` section and ``bundledDependencies`` section of
        your ``package.json``.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :stability: experimental
        '''
        result = self._values.get("bundled_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bundler_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.BundlerOptions]:
        '''(experimental) Options for ``Bundler``.

        :stability: experimental
        '''
        result = self._values.get("bundler_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.BundlerOptions], result)

    @builtins.property
    def bun_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of Bun to use if using Bun as a package manager.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("bun_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cdk_assert(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Warning: NodeJS only.

        Install the

        :default: - will be included by default for AWS CDK >= 1.0.0 < 2.0.0

        :deprecated: The

        :stability: deprecated
        :aws-cdk: /assertions (in V1) and included in ``aws-cdk-lib`` for V2.
        '''
        result = self._values.get("cdk_assert")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cdk_assertions(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Install the assertions library?

        Only needed for CDK 1.x. If using CDK 2.x then
        assertions is already included in 'aws-cdk-lib'

        :default: - will be included by default for AWS CDK >= 1.111.0 < 2.0.0

        :stability: experimental
        '''
        result = self._values.get("cdk_assertions")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cdk_cli_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version range of the AWS CDK CLI to depend on.

        Can be either a specific version, or an NPM version range.

        By default, the latest 2.x version will be installed; you can use this
        option to restrict it to a specific version or version range.

        :default: "^2"

        :stability: experimental
        '''
        result = self._values.get("cdk_cli_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cdk_dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) Which AWS CDKv1 modules this project requires.

        :deprecated: For CDK 2.x use "deps" instead. (or "peerDeps" if you're building a library)

        :stability: deprecated
        '''
        result = self._values.get("cdk_dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cdk_dependencies_as_deps(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) If this is enabled (default), all modules declared in ``cdkDependencies`` will be also added as normal ``dependencies`` (as well as ``peerDependencies``).

        This is to ensure that downstream consumers actually have your CDK dependencies installed
        when using npm < 7 or yarn, where peer dependencies are not automatically installed.
        If this is disabled, ``cdkDependencies`` will be added to ``devDependencies`` to ensure
        they are present during development.

        Note: this setting only applies to construct library projects

        :default: true

        :deprecated: Not supported in CDK v2.

        :stability: deprecated
        '''
        result = self._values.get("cdk_dependencies_as_deps")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cdkout(self) -> typing.Optional[builtins.str]:
        '''(experimental) cdk.out directory.

        :default: "cdk.out"

        :stability: experimental
        '''
        result = self._values.get("cdkout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cdk_test_dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) AWS CDK modules required for testing.

        :deprecated: For CDK 2.x use 'devDeps' (in node.js projects) or 'testDeps' (in java projects) instead

        :stability: deprecated
        '''
        result = self._values.get("cdk_test_dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cdk_version_pinning(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use pinned version instead of caret version for CDK.

        You can use this to prevent mixed versions for your CDK dependencies and to prevent auto-updates.
        If you use experimental features this will let you define the moment you include breaking changes.

        :stability: experimental
        '''
        result = self._values.get("cdk_version_pinning")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def check_licenses(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.LicenseCheckerOptions]:
        '''(experimental) Configure which licenses should be deemed acceptable for use by dependencies.

        This setting will cause the build to fail, if any prohibited or not allowed licenses ares encountered.

        :default: - no license checks are run during the build and all licenses will be accepted

        :stability: experimental
        '''
        result = self._values.get("check_licenses")
        return typing.cast(typing.Optional[_projen_javascript_04054675.LicenseCheckerOptions], result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: - true, but false for subprojects

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_artifact_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.CodeArtifactOptions]:
        '''(experimental) Options for npm packages using AWS CodeArtifact.

        This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("code_artifact_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.CodeArtifactOptions], result)

    @builtins.property
    def code_cov(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v4 A secret is required for private repos. Configured with ``@codeCovTokenSecret``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("code_cov")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_cov_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories.

        :default: - if this option is not specified, only public repositories are supported

        :stability: experimental
        '''
        result = self._values.get("code_cov_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def commit_generated(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to commit the managed files by default.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("commit_generated")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def constructs_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Minimum version of the ``constructs`` library to depend on.

        :default:

        - for CDK 1.x the default is "3.2.27", for CDK 2.x the default is
        "10.0.5".

        :stability: experimental
        '''
        result = self._values.get("constructs_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional context to include in ``cdk.json``.

        :default: - no additional context

        :stability: experimental
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def copyright_owner(self) -> typing.Optional[builtins.str]:
        '''(experimental) License copyright owner.

        :default: - defaults to the value of authorName or "" if ``authorName`` is undefined.

        :stability: experimental
        '''
        result = self._values.get("copyright_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copyright_period(self) -> typing.Optional[builtins.str]:
        '''(experimental) The copyright years to put in the LICENSE file.

        :default: - current year

        :stability: experimental
        '''
        result = self._values.get("copyright_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_release_branch(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the main release branch.

        :default: "main"

        :stability: experimental
        '''
        result = self._values.get("default_release_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependabot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use dependabot to handle dependency upgrades.

        Cannot be used in conjunction with ``depsUpgrade``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dependabot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dependabot_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.DependabotOptions]:
        '''(experimental) Options for dependabot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("dependabot_options")
        return typing.cast(typing.Optional[_projen_github_04054675.DependabotOptions], result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Runtime dependencies of this module.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deps_upgrade(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use tasks and github workflows to handle dependency upgrades.

        Cannot be used in conjunction with ``dependabot``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deps_upgrade_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.UpgradeDependenciesOptions]:
        '''(experimental) Options for ``UpgradeDependencies``.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.UpgradeDependenciesOptions], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description is just a string that helps people understand the purpose of the package.

        It can be used when searching for packages in a package manager as well.
        See https://classic.yarnpkg.com/en/docs/package-json/#toc-description

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Build dependencies for this module.

        These dependencies will only be
        available in your build environment but will not be fetched when this
        module is consumed.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("dev_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def disable_tsconfig(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("disable_tsconfig")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def disable_tsconfig_dev(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Do not generate a ``tsconfig.dev.json`` file.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("disable_tsconfig_dev")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docgen(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Docgen by Typedoc.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("docgen")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docs_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) Docs directory.

        :default: "docs"

        :stability: experimental
        '''
        result = self._values.get("docs_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def edge_lambda_auto_discover(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically adds an ``cloudfront.experimental.EdgeFunction`` for each ``.edge-lambda.ts`` handler in your source tree. If this is disabled, you can manually add an ``awscdk.AutoDiscover`` component to your project.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("edge_lambda_auto_discover")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def entrypoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json.

        :default: "lib/index.js"

        :stability: experimental
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint_types(self) -> typing.Optional[builtins.str]:
        '''(experimental) The .d.ts file that includes the type declarations for this module.

        :default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)

        :stability: experimental
        '''
        result = self._values.get("entrypoint_types")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eslint(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup eslint.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("eslint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def eslint_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.EslintOptions]:
        '''(experimental) Eslint options.

        :default: - opinionated default options

        :stability: experimental
        '''
        result = self._values.get("eslint_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.EslintOptions], result)

    @builtins.property
    def experimental_integ_runner(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable experimental support for the AWS CDK integ-runner.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("experimental_integ_runner")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def feature_flags(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include all feature flags in cdk.json.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("feature_flags")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable GitHub integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github_options(self) -> typing.Optional[_projen_github_04054675.GitHubOptions]:
        '''(experimental) Options for GitHub integration.

        :default: - see GitHubOptions

        :stability: experimental
        '''
        result = self._values.get("github_options")
        return typing.cast(typing.Optional[_projen_github_04054675.GitHubOptions], result)

    @builtins.property
    def gitignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional entries to .gitignore.

        :stability: experimental
        '''
        result = self._values.get("gitignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def git_ignore_options(self) -> typing.Optional[_projen_04054675.IgnoreFileOptions]:
        '''(experimental) Configuration options for .gitignore file.

        :stability: experimental
        '''
        result = self._values.get("git_ignore_options")
        return typing.cast(typing.Optional[_projen_04054675.IgnoreFileOptions], result)

    @builtins.property
    def git_options(self) -> typing.Optional[_projen_04054675.GitOptions]:
        '''(experimental) Configuration options for git.

        :stability: experimental
        '''
        result = self._values.get("git_options")
        return typing.cast(typing.Optional[_projen_04054675.GitOptions], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Homepage / Website.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_test_auto_discover(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically discovers and creates integration tests for each ``.integ.ts`` file in under your test directory.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("integration_test_auto_discover")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def jest(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup jest unit tests.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("jest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def jest_options(self) -> typing.Optional[_projen_javascript_04054675.JestOptions]:
        '''(experimental) Jest options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("jest_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.JestOptions], result)

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement of ``publib`` which is used to publish modules to npm.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Keywords to include in ``package.json``.

        :stability: experimental
        '''
        result = self._values.get("keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def lambda_auto_discover(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically adds an ``awscdk.LambdaFunction`` for each ``.lambda.ts`` handler in your source tree. If this is disabled, you can manually add an ``awscdk.AutoDiscover`` component to your project.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("lambda_auto_discover")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lambda_extension_auto_discover(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically adds an ``awscdk.LambdaExtension`` for each ``.lambda-extension.ts`` entrypoint in your source tree. If this is disabled, you can manually add an ``awscdk.AutoDiscover`` component to your project.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("lambda_extension_auto_discover")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lambda_options(
        self,
    ) -> typing.Optional[_projen_awscdk_04054675.LambdaFunctionCommonOptions]:
        '''(experimental) Common options for all AWS Lambda functions.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("lambda_options")
        return typing.cast(typing.Optional[_projen_awscdk_04054675.LambdaFunctionCommonOptions], result)

    @builtins.property
    def libdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript  artifacts output directory.

        :default: "lib"

        :stability: experimental
        '''
        result = self._values.get("libdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License's SPDX identifier.

        See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses.
        Use the ``licensed`` option if you want to no license to be specified.

        :default: "Apache-2.0"

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def licensed(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates if a license should be added.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("licensed")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def logging(self) -> typing.Optional[_projen_04054675.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[_projen_04054675.LoggerOptions], result)

    @builtins.property
    def major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Major version to release from the default branch.

        If this is specified, we bump the latest version of this major version line.
        If not specified, we bump the global latest version.

        :default: - Major version is not enforced.

        :stability: experimental
        '''
        result = self._values.get("major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The maximum node version supported by this package.

        Most projects should not use this option.
        The value indicates that the package is incompatible with any newer versions of node.
        This requirement is enforced via the engines field.

        You will normally not need to set this option.
        Consider this option only if your package is known to not function with newer versions of node.

        :default: - no maximum version is enforced

        :stability: experimental
        '''
        result = self._values.get("max_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether mergify should be enabled on this repository or not.

        :default: true

        :deprecated: use ``githubOptions.mergify`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.MergifyOptions]:
        '''(deprecated) Options for mergify.

        :default: - default options

        :deprecated: use ``githubOptions.mergifyOptions`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional[_projen_github_04054675.MergifyOptions], result)

    @builtins.property
    def min_major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Minimal Major version to release.

        This can be useful to set to 1, as breaking changes before the 1.x major
        release are not incrementing the major version number.

        Can not be set together with ``majorVersion``.

        :default: - No minimum version is being enforced

        :stability: experimental
        '''
        result = self._values.get("min_major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The minimum node version required by this package to function.

        Most projects should not use this option.
        The value indicates that the package is incompatible with any older versions of node.
        This requirement is enforced via the engines field.

        You will normally not need to set this option, even if your package is incompatible with EOL versions of node.
        Consider this option only if your package depends on a specific feature, that is not available in other LTS versions.
        Setting this option has very high impact on the consumers of your package,
        as package managers will actively prevent usage with node versions you have marked as incompatible.

        To change the node version of your CI/CD workflows, use ``workflowNodeVersion``.

        :default: - no minimum version is enforced

        :stability: experimental
        '''
        result = self._values.get("min_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mutable_build(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically update files modified during builds to pull-request branches.

        This means
        that any files synthesized by projen or e.g. test snapshots will always be up-to-date
        before a PR is merged.

        Implies that PR builds do not have anti-tamper checks.

        :default: true

        :deprecated: - Use ``buildWorkflowOptions.mutableBuild``

        :stability: deprecated
        '''
        result = self._values.get("mutable_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def next_version_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) A shell command to control the next version to release.

        If present, this shell command will be run before the bump is executed, and
        it determines what version to release. It will be executed in the following
        environment:

        - Working directory: the project directory.
        - ``$VERSION``: the current version. Looks like ``1.2.3``.
        - ``$LATEST_TAG``: the most recent tag. Looks like ``prefix-v1.2.3``, or may be unset.
        - ``$SUGGESTED_BUMP``: the suggested bump action based on commits. One of ``major|minor|patch|none``.

        The command should print one of the following to ``stdout``:

        - Nothing: the next version number will be determined based on commit history.
        - ``x.y.z``: the next version number will be ``x.y.z``.
        - ``major|minor|patch``: the next version number will be the current version number
          with the indicated component bumped.

        This setting cannot be specified together with ``minMajorVersion``; the invoked
        script can be used to achieve the effects of ``minMajorVersion``.

        :default: - The next version will be determined based on the commit history and project settings.

        :stability: experimental
        '''
        result = self._values.get("next_version_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_access(self) -> typing.Optional[_projen_javascript_04054675.NpmAccess]:
        '''(experimental) Access level of the npm package.

        :default:

        - for scoped packages (e.g. ``foo@bar``), the default is
        ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is
        ``NpmAccess.PUBLIC``.

        :stability: experimental
        '''
        result = self._values.get("npm_access")
        return typing.cast(typing.Optional[_projen_javascript_04054675.NpmAccess], result)

    @builtins.property
    def npm_dist_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) The npmDistTag to use when publishing from the default branch.

        To set the npm dist-tag for release branches, set the ``npmDistTag`` property
        for each branch.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("npm_dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npmignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) Additional entries to .npmignore.

        :deprecated: - use ``project.addPackageIgnore``

        :stability: deprecated
        '''
        result = self._values.get("npmignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def npmignore_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("npmignore_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def npm_ignore_options(self) -> typing.Optional[_projen_04054675.IgnoreFileOptions]:
        '''(experimental) Configuration options for .npmignore file.

        :stability: experimental
        '''
        result = self._values.get("npm_ignore_options")
        return typing.cast(typing.Optional[_projen_04054675.IgnoreFileOptions], result)

    @builtins.property
    def npm_provenance(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Should provenance statements be generated when the package is published.

        A supported package manager is required to publish a package with npm provenance statements and
        you will need to use a supported CI/CD provider.

        Note that the projen ``Release`` and ``Publisher`` components are using ``publib`` to publish packages,
        which is using npm internally and supports provenance statements independently of the package manager used.

        :default: - true for public packages, false otherwise

        :stability: experimental
        '''
        result = self._values.get("npm_provenance")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def npm_registry(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The host name of the npm registry to publish to.

        Cannot be set together with ``npmRegistryUrl``.

        :deprecated: use ``npmRegistryUrl`` instead

        :stability: deprecated
        '''
        result = self._values.get("npm_registry")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_registry_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The base URL of the npm package registry.

        Must be a URL (e.g. start with "https://" or "http://")

        :default: "https://registry.npmjs.org"

        :stability: experimental
        '''
        result = self._values.get("npm_registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the NPM token to use when publishing packages.

        :default: "NPM_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("npm_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project. Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        subprojects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def package(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``).

        :default: true

        :stability: experimental
        '''
        result = self._values.get("package")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def package_manager(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.NodePackageManager]:
        '''(experimental) The Node Package Manager used to execute scripts.

        :default: NodePackageManager.YARN_CLASSIC

        :stability: experimental
        '''
        result = self._values.get("package_manager")
        return typing.cast(typing.Optional[_projen_javascript_04054675.NodePackageManager], result)

    @builtins.property
    def package_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The "name" in package.json.

        :default: - defaults to project name

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("package_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[_projen_04054675.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[_projen_04054675.Project], result)

    @builtins.property
    def peer_dependency_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.PeerDependencyOptions]:
        '''(experimental) Options for ``peerDeps``.

        :stability: experimental
        '''
        result = self._values.get("peer_dependency_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.PeerDependencyOptions], result)

    @builtins.property
    def peer_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Peer dependencies for this module.

        Dependencies listed here are required to
        be installed (and satisfied) by the *consumer* of this library. Using peer
        dependencies allows you to ensure that only a single module of a certain
        library exists in the ``node_modules`` tree of your consumers.

        Note that prior to npm@7, peer dependencies are *not* automatically
        installed, which means that adding peer dependencies to a library will be a
        breaking change for your customers.

        Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is
        enabled by default), projen will automatically add a dev dependency with a
        pinned version for each peer dependency. This will ensure that you build &
        test your module against the lowest peer version required.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("peer_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pnpm_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of PNPM to use if using PNPM as a package manager.

        :default: "9"

        :stability: experimental
        '''
        result = self._values.get("pnpm_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_build_steps(
        self,
    ) -> typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]]:
        '''(experimental) Steps to execute after build as part of the release workflow.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]], result)

    @builtins.property
    def prerelease(self) -> typing.Optional[builtins.str]:
        '''(experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre").

        :default: - normal semantic versions

        :stability: experimental
        '''
        result = self._values.get("prerelease")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prettier(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup prettier.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("prettier")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def prettier_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.PrettierOptions]:
        '''(experimental) Prettier options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("prettier_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.PrettierOptions], result)

    @builtins.property
    def project_type(self) -> typing.Optional[_projen_04054675.ProjectType]:
        '''(deprecated) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :deprecated: no longer supported at the base project level

        :stability: deprecated
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[_projen_04054675.ProjectType], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_credentials(
        self,
    ) -> typing.Optional[_projen_github_04054675.GithubCredentials]:
        '''(experimental) Choose a method of providing GitHub API access for projen workflows.

        :default: - use a personal access token named PROJEN_GITHUB_TOKEN

        :stability: experimental
        '''
        result = self._values.get("projen_credentials")
        return typing.cast(typing.Optional[_projen_github_04054675.GithubCredentials], result)

    @builtins.property
    def projen_dev_dependency(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates of "projen" should be installed as a devDependency.

        :default: - true if not a subproject

        :stability: experimental
        '''
        result = self._values.get("projen_dev_dependency")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation.

        :default: - true if projenrcJson is false

        :stability: experimental
        '''
        result = self._values.get("projenrc_js")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(
        self,
    ) -> typing.Optional[_projen_04054675.ProjenrcJsonOptions]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[_projen_04054675.ProjenrcJsonOptions], result)

    @builtins.property
    def projenrc_js_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.js.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_js_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.ProjenrcOptions], result)

    @builtins.property
    def projenrc_ts(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use TypeScript for your projenrc file (``.projenrc.ts``).

        :default: false

        :stability: experimental
        :pjnew: true
        '''
        result = self._values.get("projenrc_ts")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_ts_options(
        self,
    ) -> typing.Optional[_projen_typescript_04054675.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.ts.

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts_options")
        return typing.cast(typing.Optional[_projen_typescript_04054675.ProjenrcOptions], result)

    @builtins.property
    def projen_token_secret(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows.

        This token needs to have the ``repo``, ``workflows``
        and ``packages`` scope.

        :default: "PROJEN_GITHUB_TOKEN"

        :deprecated: use ``projenCredentials``

        :stability: deprecated
        '''
        result = self._values.get("projen_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of projen to install.

        :default: - Defaults to the latest version.

        :stability: experimental
        '''
        result = self._values.get("projen_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_dry_run(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Instead of actually publishing to package managers, just print the publishing command.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_dry_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_tasks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define publishing tasks that can be executed manually as well as workflows.

        Normally, publishing only happens within automated workflows. Enable this
        in order to create a publishing task for each publishing activity.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_tasks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_request_template(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include a GitHub pull request template.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("pull_request_template")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_request_template_contents(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The contents of the pull request template.

        :default: - default content

        :stability: experimental
        '''
        result = self._values.get("pull_request_template_contents")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def readme(self) -> typing.Optional["ReadmeOptions"]:
        '''Configuration of the README.md file.'''
        result = self._values.get("readme")
        return typing.cast(typing.Optional["ReadmeOptions"], result)

    @builtins.property
    def releasable_commits(self) -> typing.Optional[_projen_04054675.ReleasableCommits]:
        '''(experimental) Find commits that should be considered releasable Used to decide if a release is required.

        :default: ReleasableCommits.everyCommit()

        :stability: experimental
        '''
        result = self._values.get("releasable_commits")
        return typing.cast(typing.Optional[_projen_04054675.ReleasableCommits], result)

    @builtins.property
    def release(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add release management to this project.

        :default: - true (false for subprojects)

        :stability: experimental
        '''
        result = self._values.get("release")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_branches(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _projen_release_04054675.BranchOptions]]:
        '''(experimental) Defines additional release branches.

        A workflow will be created for each
        release branch which will publish releases from commits in this branch.
        Each release branch *must* be assigned a major version number which is used
        to enforce that versions published from that branch always use that major
        version. If multiple branches are used, the ``majorVersion`` field must also
        be provided for the default branch.

        :default:

        - no additional branches are used for release. you can use
        ``addBranch()`` to add additional branches.

        :stability: experimental
        '''
        result = self._values.get("release_branches")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _projen_release_04054675.BranchOptions]], result)

    @builtins.property
    def release_every_commit(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``.

        :default: true

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.continuous()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_every_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create a github issue on every failed publishing task.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The label to apply to issues indicating publish failures.

        Only applies if ``releaseFailureIssue`` is true.

        :default: "failed-release"

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_schedule(self) -> typing.Optional[builtins.str]:
        '''(deprecated) CRON schedule to trigger new releases.

        :default: - no scheduled releases

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.scheduled()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_tag_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Automatically add the given prefix to release tags.

        Useful if you are releasing on multiple branches with overlapping version numbers.
        Note: this prefix is used to detect the latest tagged version
        when bumping, so if you change this on a project with an existing version
        history, you may need to manually tag your latest release
        with the new prefix.

        :default: "v"

        :stability: experimental
        '''
        result = self._values.get("release_tag_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_to_npm(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically release to npm when new versions are introduced.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_to_npm")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_trigger(
        self,
    ) -> typing.Optional[_projen_release_04054675.ReleaseTrigger]:
        '''(experimental) The release trigger to use.

        :default: - Continuous releases (``ReleaseTrigger.continuous()``)

        :stability: experimental
        '''
        result = self._values.get("release_trigger")
        return typing.cast(typing.Optional[_projen_release_04054675.ReleaseTrigger], result)

    @builtins.property
    def release_workflow(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) DEPRECATED: renamed to ``release``.

        :default: - true if not a subproject

        :deprecated: see ``release``.

        :stability: deprecated
        '''
        result = self._values.get("release_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_workflow_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the default release workflow.

        :default: "release"

        :stability: experimental
        '''
        result = self._values.get("release_workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_workflow_setup_steps(
        self,
    ) -> typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]]:
        '''(experimental) A set of workflow steps to execute in order to setup the workflow container.

        :stability: experimental
        '''
        result = self._values.get("release_workflow_setup_steps")
        return typing.cast(typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]], result)

    @builtins.property
    def renovatebot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use renovatebot to handle dependency upgrades.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("renovatebot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def renovatebot_options(
        self,
    ) -> typing.Optional[_projen_04054675.RenovatebotOptions]:
        '''(experimental) Options for renovatebot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("renovatebot_options")
        return typing.cast(typing.Optional[_projen_04054675.RenovatebotOptions], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) The repository is the location where the actual code for your package lives.

        See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.

        :stability: experimental
        '''
        result = self._values.get("repository_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def require_approval(
        self,
    ) -> typing.Optional[_projen_awscdk_04054675.ApprovalLevel]:
        '''(experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them.

        :default: ApprovalLevel.BROADENING

        :stability: experimental
        '''
        result = self._values.get("require_approval")
        return typing.cast(typing.Optional[_projen_awscdk_04054675.ApprovalLevel], result)

    @builtins.property
    def sample_code(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sample_code")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def scoped_packages_options(
        self,
    ) -> typing.Optional[typing.List[_projen_javascript_04054675.ScopedPackagesOptions]]:
        '''(experimental) Options for privately hosted scoped packages.

        :default: - fetch all scoped packages from the public npm registry

        :stability: experimental
        '''
        result = self._values.get("scoped_packages_options")
        return typing.cast(typing.Optional[typing.List[_projen_javascript_04054675.ScopedPackagesOptions]], result)

    @builtins.property
    def scripts(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(deprecated) npm scripts to include.

        If a script has the same name as a standard script,
        the standard script will be overwritten.
        Also adds the script as a task.

        :default: {}

        :deprecated: use ``project.addTask()`` or ``package.setScript()``

        :stability: deprecated
        '''
        result = self._values.get("scripts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def srcdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript sources directory.

        :default: "src"

        :stability: experimental
        '''
        result = self._values.get("srcdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stability(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Stability.

        :stability: experimental
        '''
        result = self._values.get("stability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stale(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto-close of stale issues and pull request.

        See ``staleOptions`` for options.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("stale")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_options(self) -> typing.Optional[_projen_github_04054675.StaleOptions]:
        '''(experimental) Auto-close stale issues and pull requests.

        To disable set ``stale`` to ``false``.

        :default: - see defaults in ``StaleOptions``

        :stability: experimental
        '''
        result = self._values.get("stale_options")
        return typing.cast(typing.Optional[_projen_github_04054675.StaleOptions], result)

    @builtins.property
    def testdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Jest tests directory.

        Tests files should be named ``xxx.test.ts``.
        If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``),
        then tests are going to be compiled into ``lib/`` and executed as javascript.
        If the test directory is outside of ``src``, then we configure jest to
        compile the code in-memory.

        :default: "test"

        :stability: experimental
        '''
        result = self._values.get("testdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tsconfig(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions]:
        '''(experimental) Custom TSConfig.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("tsconfig")
        return typing.cast(typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions]:
        '''(experimental) Custom tsconfig options for the development tsconfig.json file (used for testing).

        :default: - use the production tsconfig options

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev")
        return typing.cast(typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev_file(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the development tsconfig.json file.

        :default: "tsconfig.dev.json"

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ts_jest_options(
        self,
    ) -> typing.Optional[_projen_typescript_04054675.TsJestOptions]:
        '''(experimental) Options for ts-jest.

        :stability: experimental
        '''
        result = self._values.get("ts_jest_options")
        return typing.cast(typing.Optional[_projen_typescript_04054675.TsJestOptions], result)

    @builtins.property
    def typescript_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) TypeScript version to use.

        NOTE: Typescript is not semantically versioned and should remain on the
        same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``).

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("typescript_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def versionrc_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Custom configuration used when creating changelog with commit-and-tag-version package.

        Given values either append to default configuration or overwrite values in it.

        :default: - standard configuration applicable for GitHub repositories

        :stability: experimental
        '''
        result = self._values.get("versionrc_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def vscode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable VSCode integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("vscode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def watch_excludes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Glob patterns to exclude from ``cdk watch``.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("watch_excludes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def watch_includes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Glob patterns to include in ``cdk watch``.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("watch_includes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def workflow_bootstrap_steps(
        self,
    ) -> typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]]:
        '''(experimental) Workflow steps to use in order to bootstrap this repo.

        :default: "yarn install --frozen-lockfile && yarn projen"

        :stability: experimental
        '''
        result = self._values.get("workflow_bootstrap_steps")
        return typing.cast(typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]], result)

    @builtins.property
    def workflow_container_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Container image to use for GitHub workflows.

        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("workflow_container_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_git_identity(
        self,
    ) -> typing.Optional[_projen_github_04054675.GitIdentity]:
        '''(experimental) The git identity to use in workflows.

        :default: - GitHub Actions

        :stability: experimental
        '''
        result = self._values.get("workflow_git_identity")
        return typing.cast(typing.Optional[_projen_github_04054675.GitIdentity], result)

    @builtins.property
    def workflow_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The node version used in GitHub Actions workflows.

        Always use this option if your GitHub Actions workflows require a specific to run.

        :default: - ``minNodeVersion`` if set, otherwise ``lts/*``.

        :stability: experimental
        '''
        result = self._values.get("workflow_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_package_cache(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable Node.js package cache in GitHub workflows.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("workflow_package_cache")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def workflow_runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        :description: Defines a target Runner by labels
        :throws: {Error} if both ``runsOn`` and ``runsOnGroup`` are specified
        '''
        result = self._values.get("workflow_runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def workflow_runs_on_group(
        self,
    ) -> typing.Optional[_projen_04054675.GroupRunnerOptions]:
        '''(experimental) Github Runner Group selection options.

        :stability: experimental
        :description: Defines a target Runner Group by name and/or labels
        :throws: {Error} if both ``runsOn`` and ``runsOnGroup`` are specified
        '''
        result = self._values.get("workflow_runs_on_group")
        return typing.cast(typing.Optional[_projen_04054675.GroupRunnerOptions], result)

    @builtins.property
    def yarn_berry_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.YarnBerryOptions]:
        '''(experimental) Options for Yarn Berry.

        :default: - Yarn Berry v4 with all default options

        :stability: experimental
        '''
        result = self._values.get("yarn_berry_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.YarnBerryOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdkTypeScriptAppOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="projen-modules.ISectionOptions")
class ISectionOptions(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        ...

    @body.setter
    def body(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        ...

    @title.setter
    def title(self, value: builtins.str) -> None:
        ...


class _ISectionOptionsProxy:
    __jsii_type__: typing.ClassVar[str] = "projen-modules.ISectionOptions"

    @builtins.property
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "body"))

    @body.setter
    def body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23029d204b6d2d942365c98cdf1ae37497306087c242e282bc4760de997efd13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "body", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae35859c3728359fce2cd5f37ce86da906192904c18d529b6c42fb7cd911ad9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "title", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISectionOptions).__jsii_proxy_class__ = lambda : _ISectionOptionsProxy


class JsiiProject(
    _projen_cdk_04054675.JsiiProject,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-modules.JsiiProject",
):
    '''A JSII project in TypeScript.

    :pjid: jsii-project
    '''

    def __init__(
        self,
        *,
        author: builtins.str,
        author_address: builtins.str,
        code_owners: typing.Sequence[builtins.str],
        name: builtins.str,
        repository_url: builtins.str,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        artifacts_directory: typing.Optional[builtins.str] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        biome: typing.Optional[builtins.bool] = None,
        biome_options: typing.Optional[typing.Union[_projen_javascript_04054675.BiomeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_options: typing.Optional[typing.Union[_projen_javascript_04054675.BuildWorkflowOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        build_workflow_triggers: typing.Optional[typing.Union[_projen_github_workflows_04054675.Triggers, typing.Dict[builtins.str, typing.Any]]] = None,
        bump_package: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        bundler_options: typing.Optional[typing.Union[_projen_javascript_04054675.BundlerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bun_version: typing.Optional[builtins.str] = None,
        check_licenses: typing.Optional[typing.Union[_projen_javascript_04054675.LicenseCheckerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        clobber: typing.Optional[builtins.bool] = None,
        code_artifact_options: typing.Optional[typing.Union[_projen_javascript_04054675.CodeArtifactOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        commit_generated: typing.Optional[builtins.bool] = None,
        compat: typing.Optional[builtins.bool] = None,
        compat_ignore: typing.Optional[builtins.str] = None,
        compress_assembly: typing.Optional[builtins.bool] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        default_release_branch: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[typing.Union[_projen_github_04054675.DependabotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[typing.Union[_projen_javascript_04054675.UpgradeDependenciesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        disable_tsconfig_dev: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docgen_file_path: typing.Optional[builtins.str] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        dotnet: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiDotNetTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[typing.Union[_projen_javascript_04054675.EslintOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        exclude_typescript: typing.Optional[typing.Sequence[builtins.str]] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        homepage: typing.Optional[builtins.str] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[typing.Union[_projen_javascript_04054675.JestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        jsii_version: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        libdir: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        major_version: typing.Optional[jsii.Number] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        min_major_version: typing.Optional[jsii.Number] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        next_version_command: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[_projen_javascript_04054675.NpmAccess] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        npm_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        npm_provenance: typing.Optional[builtins.bool] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        outdir: typing.Optional[builtins.str] = None,
        package: typing.Optional[builtins.bool] = None,
        package_manager: typing.Optional[_projen_javascript_04054675.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        peer_dependency_options: typing.Optional[typing.Union[_projen_javascript_04054675.PeerDependencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pnpm_version: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[typing.Union[_projen_javascript_04054675.PrettierOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_type: typing.Optional[_projen_04054675.ProjectType] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        publish_to_go: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiGoTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        publish_to_maven: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiJavaTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        publish_to_nuget: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiDotNetTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        publish_to_pypi: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiPythonTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        python: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiPythonTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        readme: typing.Optional[typing.Union["ReadmeOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        releasable_commits: typing.Optional[_projen_04054675.ReleasableCommits] = None,
        release: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, typing.Union[_projen_release_04054675.BranchOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_trigger: typing.Optional[_projen_release_04054675.ReleaseTrigger] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        rootdir: typing.Optional[builtins.str] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        scoped_packages_options: typing.Optional[typing.Sequence[typing.Union[_projen_javascript_04054675.ScopedPackagesOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        srcdir: typing.Optional[builtins.str] = None,
        stability: typing.Optional[builtins.str] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        ts_jest_options: typing.Optional[typing.Union[_projen_typescript_04054675.TsJestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        vscode: typing.Optional[builtins.bool] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_git_identity: typing.Optional[typing.Union[_projen_github_04054675.GitIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        workflow_package_cache: typing.Optional[builtins.bool] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_runs_on_group: typing.Optional[typing.Union[_projen_04054675.GroupRunnerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        yarn_berry_options: typing.Optional[typing.Union[_projen_javascript_04054675.YarnBerryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param author: (experimental) The name of the library author. Default: $GIT_USER_NAME
        :param author_address: (experimental) Email or URL of the library author. Default: $GIT_USER_EMAIL
        :param code_owners: List of teams used to generate the CODEOWNERS file.
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param repository_url: (experimental) Git repository URL. Default: $GIT_REMOTE
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Is the author an organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param biome: (experimental) Setup Biome. Default: false
        :param biome_options: (experimental) Biome options. Default: - default options
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_options: (experimental) Options for PR build workflow.
        :param build_workflow_triggers: (deprecated) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bump_package: (experimental) The ``commit-and-tag-version`` compatible package used to bump the package version, as a dependency string. This can be any compatible package version, including the deprecated ``standard-version@9``. Default: - A recent version of "commit-and-tag-version"
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param bun_version: (experimental) The version of Bun to use if using Bun as a package manager. Default: "latest"
        :param check_licenses: (experimental) Configure which licenses should be deemed acceptable for use by dependencies. This setting will cause the build to fail, if any prohibited or not allowed licenses ares encountered. Default: - no license checks are run during the build and all licenses will be accepted
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: - true, but false for subprojects
        :param code_artifact_options: (experimental) Options for npm packages using AWS CodeArtifact. This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact Default: - undefined
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v4 A secret is required for private repos. Configured with ``@codeCovTokenSecret``. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param compat: (experimental) Automatically run API compatibility test against the latest version published to npm after compilation. - You can manually run compatibility tests using ``yarn compat`` if this feature is disabled. - You can ignore compatibility failures by adding lines to a ".compatignore" file. Default: false
        :param compat_ignore: (experimental) Name of the ignore file for API compatibility tests. Default: ".compatignore"
        :param compress_assembly: (experimental) Emit a compressed version of the assembly. Default: false
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param deps_upgrade: (experimental) Use tasks and github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for ``UpgradeDependencies``. Default: - default options
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param disable_tsconfig_dev: (experimental) Do not generate a ``tsconfig.dev.json`` file. Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docgen_file_path: (experimental) File path for generated docs. Default: "API.md"
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param dotnet: 
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json. Default: "lib/index.js"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param exclude_typescript: (experimental) Accepts a list of glob patterns. Files matching any of those patterns will be excluded from the TypeScript compiler input. By default, jsii will include all *.ts files (except .d.ts files) in the TypeScript compiler input. This can be problematic for example when the package's build or test procedure generates .ts files that cannot be compiled with jsii's compiler settings.
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param homepage: (experimental) Package's Homepage / Website.
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param jsii_version: (experimental) Version of the jsii compiler to use. Set to "*" if you want to manually manage the version of jsii in your project by managing updates to ``package.json`` on your own. NOTE: The jsii compiler releases since 5.0.0 are not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~5.0.0``). Default: "~5.6.0"
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param max_node_version: (experimental) The maximum node version supported by this package. Most projects should not use this option. The value indicates that the package is incompatible with any newer versions of node. This requirement is enforced via the engines field. You will normally not need to set this option. Consider this option only if your package is known to not function with newer versions of node. Default: - no maximum version is enforced
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param min_major_version: (experimental) Minimal Major version to release. This can be useful to set to 1, as breaking changes before the 1.x major release are not incrementing the major version number. Can not be set together with ``majorVersion``. Default: - No minimum version is being enforced
        :param min_node_version: (experimental) The minimum node version required by this package to function. Most projects should not use this option. The value indicates that the package is incompatible with any older versions of node. This requirement is enforced via the engines field. You will normally not need to set this option, even if your package is incompatible with EOL versions of node. Consider this option only if your package depends on a specific feature, that is not available in other LTS versions. Setting this option has very high impact on the consumers of your package, as package managers will actively prevent usage with node versions you have marked as incompatible. To change the node version of your CI/CD workflows, use ``workflowNodeVersion``. Default: - no minimum version is enforced
        :param mutable_build: (deprecated) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param next_version_command: (experimental) A shell command to control the next version to release. If present, this shell command will be run before the bump is executed, and it determines what version to release. It will be executed in the following environment: - Working directory: the project directory. - ``$VERSION``: the current version. Looks like ``1.2.3``. - ``$LATEST_TAG``: the most recent tag. Looks like ``prefix-v1.2.3``, or may be unset. - ``$SUGGESTED_BUMP``: the suggested bump action based on commits. One of ``major|minor|patch|none``. The command should print one of the following to ``stdout``: - Nothing: the next version number will be determined based on commit history. - ``x.y.z``: the next version number will be ``x.y.z``. - ``major|minor|patch``: the next version number will be the current version number with the indicated component bumped. This setting cannot be specified together with ``minMajorVersion``; the invoked script can be used to achieve the effects of ``minMajorVersion``. Default: - The next version will be determined based on the commit history and project settings.
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param npm_ignore_options: (experimental) Configuration options for .npmignore file.
        :param npm_provenance: (experimental) Should provenance statements be generated when the package is published. A supported package manager is required to publish a package with npm provenance statements and you will need to use a supported CI/CD provider. Note that the projen ``Release`` and ``Publisher`` components are using ``publib`` to publish packages, which is using npm internally and supports provenance statements independently of the package manager used. Default: - true for public packages, false otherwise
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other subprojects. Default: "."
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN_CLASSIC
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param pnpm_version: (experimental) The version of PNPM to use if using PNPM as a package manager. Default: "9"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: - true if not a subproject
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param publish_to_go: (experimental) Publish Go bindings to a git repository. Default: - no publishing
        :param publish_to_maven: (experimental) Publish to maven. Default: - no publishing
        :param publish_to_nuget: (experimental) Publish to NuGet. Default: - no publishing
        :param publish_to_pypi: (experimental) Publish to pypi. Default: - no publishing
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param python: 
        :param readme: Configuration of the README.md file.
        :param releasable_commits: (experimental) Find commits that should be considered releasable Used to decide if a release is required. Default: ReleasableCommits.everyCommit()
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: "v"
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param rootdir: Default: "."
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param scoped_packages_options: (experimental) Options for privately hosted scoped packages. Default: - fetch all scoped packages from the public npm registry
        :param scripts: (deprecated) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Also adds the script as a task. Default: {}
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param stability: (experimental) Package's Stability.
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param ts_jest_options: (experimental) Options for ts-jest.
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with commit-and-tag-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version used in GitHub Actions workflows. Always use this option if your GitHub Actions workflows require a specific to run. Default: - ``minNodeVersion`` if set, otherwise ``lts/*``.
        :param workflow_package_cache: (experimental) Enable Node.js package cache in GitHub workflows. Default: false
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param workflow_runs_on_group: (experimental) Github Runner Group selection options.
        :param yarn_berry_options: (experimental) Options for Yarn Berry. Default: - Yarn Berry v4 with all default options
        '''
        options = JsiiProjectOptions(
            author=author,
            author_address=author_address,
            code_owners=code_owners,
            name=name,
            repository_url=repository_url,
            allow_library_dependencies=allow_library_dependencies,
            artifacts_directory=artifacts_directory,
            author_email=author_email,
            author_name=author_name,
            author_organization=author_organization,
            author_url=author_url,
            auto_approve_options=auto_approve_options,
            auto_approve_upgrades=auto_approve_upgrades,
            auto_detect_bin=auto_detect_bin,
            auto_merge=auto_merge,
            auto_merge_options=auto_merge_options,
            bin=bin,
            biome=biome,
            biome_options=biome_options,
            bugs_email=bugs_email,
            bugs_url=bugs_url,
            build_workflow=build_workflow,
            build_workflow_options=build_workflow_options,
            build_workflow_triggers=build_workflow_triggers,
            bump_package=bump_package,
            bundled_deps=bundled_deps,
            bundler_options=bundler_options,
            bun_version=bun_version,
            check_licenses=check_licenses,
            clobber=clobber,
            code_artifact_options=code_artifact_options,
            code_cov=code_cov,
            code_cov_token_secret=code_cov_token_secret,
            commit_generated=commit_generated,
            compat=compat,
            compat_ignore=compat_ignore,
            compress_assembly=compress_assembly,
            copyright_owner=copyright_owner,
            copyright_period=copyright_period,
            default_release_branch=default_release_branch,
            dependabot=dependabot,
            dependabot_options=dependabot_options,
            deps=deps,
            deps_upgrade=deps_upgrade,
            deps_upgrade_options=deps_upgrade_options,
            description=description,
            dev_container=dev_container,
            dev_deps=dev_deps,
            disable_tsconfig=disable_tsconfig,
            disable_tsconfig_dev=disable_tsconfig_dev,
            docgen=docgen,
            docgen_file_path=docgen_file_path,
            docs_directory=docs_directory,
            dotnet=dotnet,
            entrypoint=entrypoint,
            entrypoint_types=entrypoint_types,
            eslint=eslint,
            eslint_options=eslint_options,
            exclude_typescript=exclude_typescript,
            github=github,
            github_options=github_options,
            gitignore=gitignore,
            git_ignore_options=git_ignore_options,
            git_options=git_options,
            gitpod=gitpod,
            homepage=homepage,
            jest=jest,
            jest_options=jest_options,
            jsii_release_version=jsii_release_version,
            jsii_version=jsii_version,
            keywords=keywords,
            libdir=libdir,
            license=license,
            licensed=licensed,
            logging=logging,
            major_version=major_version,
            max_node_version=max_node_version,
            mergify=mergify,
            mergify_options=mergify_options,
            min_major_version=min_major_version,
            min_node_version=min_node_version,
            mutable_build=mutable_build,
            next_version_command=next_version_command,
            npm_access=npm_access,
            npm_dist_tag=npm_dist_tag,
            npmignore=npmignore,
            npmignore_enabled=npmignore_enabled,
            npm_ignore_options=npm_ignore_options,
            npm_provenance=npm_provenance,
            npm_registry=npm_registry,
            npm_registry_url=npm_registry_url,
            npm_token_secret=npm_token_secret,
            outdir=outdir,
            package=package,
            package_manager=package_manager,
            package_name=package_name,
            parent=parent,
            peer_dependency_options=peer_dependency_options,
            peer_deps=peer_deps,
            pnpm_version=pnpm_version,
            post_build_steps=post_build_steps,
            prerelease=prerelease,
            prettier=prettier,
            prettier_options=prettier_options,
            project_type=project_type,
            projen_command=projen_command,
            projen_credentials=projen_credentials,
            projen_dev_dependency=projen_dev_dependency,
            projenrc_js=projenrc_js,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
            projenrc_js_options=projenrc_js_options,
            projenrc_ts=projenrc_ts,
            projenrc_ts_options=projenrc_ts_options,
            projen_token_secret=projen_token_secret,
            projen_version=projen_version,
            publish_dry_run=publish_dry_run,
            publish_tasks=publish_tasks,
            publish_to_go=publish_to_go,
            publish_to_maven=publish_to_maven,
            publish_to_nuget=publish_to_nuget,
            publish_to_pypi=publish_to_pypi,
            pull_request_template=pull_request_template,
            pull_request_template_contents=pull_request_template_contents,
            python=python,
            readme=readme,
            releasable_commits=releasable_commits,
            release=release,
            release_branches=release_branches,
            release_every_commit=release_every_commit,
            release_failure_issue=release_failure_issue,
            release_failure_issue_label=release_failure_issue_label,
            release_schedule=release_schedule,
            release_tag_prefix=release_tag_prefix,
            release_to_npm=release_to_npm,
            release_trigger=release_trigger,
            release_workflow=release_workflow,
            release_workflow_name=release_workflow_name,
            release_workflow_setup_steps=release_workflow_setup_steps,
            renovatebot=renovatebot,
            renovatebot_options=renovatebot_options,
            repository=repository,
            repository_directory=repository_directory,
            rootdir=rootdir,
            sample_code=sample_code,
            scoped_packages_options=scoped_packages_options,
            scripts=scripts,
            srcdir=srcdir,
            stability=stability,
            stale=stale,
            stale_options=stale_options,
            testdir=testdir,
            tsconfig=tsconfig,
            tsconfig_dev=tsconfig_dev,
            tsconfig_dev_file=tsconfig_dev_file,
            ts_jest_options=ts_jest_options,
            typescript_version=typescript_version,
            versionrc_options=versionrc_options,
            vscode=vscode,
            workflow_bootstrap_steps=workflow_bootstrap_steps,
            workflow_container_image=workflow_container_image,
            workflow_git_identity=workflow_git_identity,
            workflow_node_version=workflow_node_version,
            workflow_package_cache=workflow_package_cache,
            workflow_runs_on=workflow_runs_on,
            workflow_runs_on_group=workflow_runs_on_group,
            yarn_berry_options=yarn_berry_options,
        )

        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="readme")
    def readme(self) -> "Readme":
        return typing.cast("Readme", jsii.get(self, "readme"))

    @readme.setter
    def readme(self, value: "Readme") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6f448692015be891a4fa1b5c76f220188ba4be73e94a65360a4338352b1ea99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readme", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="projen-modules.JsiiProjectOptions",
    jsii_struct_bases=[],
    name_mapping={
        "author": "author",
        "author_address": "authorAddress",
        "code_owners": "codeOwners",
        "name": "name",
        "repository_url": "repositoryUrl",
        "allow_library_dependencies": "allowLibraryDependencies",
        "artifacts_directory": "artifactsDirectory",
        "author_email": "authorEmail",
        "author_name": "authorName",
        "author_organization": "authorOrganization",
        "author_url": "authorUrl",
        "auto_approve_options": "autoApproveOptions",
        "auto_approve_upgrades": "autoApproveUpgrades",
        "auto_detect_bin": "autoDetectBin",
        "auto_merge": "autoMerge",
        "auto_merge_options": "autoMergeOptions",
        "bin": "bin",
        "biome": "biome",
        "biome_options": "biomeOptions",
        "bugs_email": "bugsEmail",
        "bugs_url": "bugsUrl",
        "build_workflow": "buildWorkflow",
        "build_workflow_options": "buildWorkflowOptions",
        "build_workflow_triggers": "buildWorkflowTriggers",
        "bump_package": "bumpPackage",
        "bundled_deps": "bundledDeps",
        "bundler_options": "bundlerOptions",
        "bun_version": "bunVersion",
        "check_licenses": "checkLicenses",
        "clobber": "clobber",
        "code_artifact_options": "codeArtifactOptions",
        "code_cov": "codeCov",
        "code_cov_token_secret": "codeCovTokenSecret",
        "commit_generated": "commitGenerated",
        "compat": "compat",
        "compat_ignore": "compatIgnore",
        "compress_assembly": "compressAssembly",
        "copyright_owner": "copyrightOwner",
        "copyright_period": "copyrightPeriod",
        "default_release_branch": "defaultReleaseBranch",
        "dependabot": "dependabot",
        "dependabot_options": "dependabotOptions",
        "deps": "deps",
        "deps_upgrade": "depsUpgrade",
        "deps_upgrade_options": "depsUpgradeOptions",
        "description": "description",
        "dev_container": "devContainer",
        "dev_deps": "devDeps",
        "disable_tsconfig": "disableTsconfig",
        "disable_tsconfig_dev": "disableTsconfigDev",
        "docgen": "docgen",
        "docgen_file_path": "docgenFilePath",
        "docs_directory": "docsDirectory",
        "dotnet": "dotnet",
        "entrypoint": "entrypoint",
        "entrypoint_types": "entrypointTypes",
        "eslint": "eslint",
        "eslint_options": "eslintOptions",
        "exclude_typescript": "excludeTypescript",
        "github": "github",
        "github_options": "githubOptions",
        "gitignore": "gitignore",
        "git_ignore_options": "gitIgnoreOptions",
        "git_options": "gitOptions",
        "gitpod": "gitpod",
        "homepage": "homepage",
        "jest": "jest",
        "jest_options": "jestOptions",
        "jsii_release_version": "jsiiReleaseVersion",
        "jsii_version": "jsiiVersion",
        "keywords": "keywords",
        "libdir": "libdir",
        "license": "license",
        "licensed": "licensed",
        "logging": "logging",
        "major_version": "majorVersion",
        "max_node_version": "maxNodeVersion",
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "min_major_version": "minMajorVersion",
        "min_node_version": "minNodeVersion",
        "mutable_build": "mutableBuild",
        "next_version_command": "nextVersionCommand",
        "npm_access": "npmAccess",
        "npm_dist_tag": "npmDistTag",
        "npmignore": "npmignore",
        "npmignore_enabled": "npmignoreEnabled",
        "npm_ignore_options": "npmIgnoreOptions",
        "npm_provenance": "npmProvenance",
        "npm_registry": "npmRegistry",
        "npm_registry_url": "npmRegistryUrl",
        "npm_token_secret": "npmTokenSecret",
        "outdir": "outdir",
        "package": "package",
        "package_manager": "packageManager",
        "package_name": "packageName",
        "parent": "parent",
        "peer_dependency_options": "peerDependencyOptions",
        "peer_deps": "peerDeps",
        "pnpm_version": "pnpmVersion",
        "post_build_steps": "postBuildSteps",
        "prerelease": "prerelease",
        "prettier": "prettier",
        "prettier_options": "prettierOptions",
        "project_type": "projectType",
        "projen_command": "projenCommand",
        "projen_credentials": "projenCredentials",
        "projen_dev_dependency": "projenDevDependency",
        "projenrc_js": "projenrcJs",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "projenrc_js_options": "projenrcJsOptions",
        "projenrc_ts": "projenrcTs",
        "projenrc_ts_options": "projenrcTsOptions",
        "projen_token_secret": "projenTokenSecret",
        "projen_version": "projenVersion",
        "publish_dry_run": "publishDryRun",
        "publish_tasks": "publishTasks",
        "publish_to_go": "publishToGo",
        "publish_to_maven": "publishToMaven",
        "publish_to_nuget": "publishToNuget",
        "publish_to_pypi": "publishToPypi",
        "pull_request_template": "pullRequestTemplate",
        "pull_request_template_contents": "pullRequestTemplateContents",
        "python": "python",
        "readme": "readme",
        "releasable_commits": "releasableCommits",
        "release": "release",
        "release_branches": "releaseBranches",
        "release_every_commit": "releaseEveryCommit",
        "release_failure_issue": "releaseFailureIssue",
        "release_failure_issue_label": "releaseFailureIssueLabel",
        "release_schedule": "releaseSchedule",
        "release_tag_prefix": "releaseTagPrefix",
        "release_to_npm": "releaseToNpm",
        "release_trigger": "releaseTrigger",
        "release_workflow": "releaseWorkflow",
        "release_workflow_name": "releaseWorkflowName",
        "release_workflow_setup_steps": "releaseWorkflowSetupSteps",
        "renovatebot": "renovatebot",
        "renovatebot_options": "renovatebotOptions",
        "repository": "repository",
        "repository_directory": "repositoryDirectory",
        "rootdir": "rootdir",
        "sample_code": "sampleCode",
        "scoped_packages_options": "scopedPackagesOptions",
        "scripts": "scripts",
        "srcdir": "srcdir",
        "stability": "stability",
        "stale": "stale",
        "stale_options": "staleOptions",
        "testdir": "testdir",
        "tsconfig": "tsconfig",
        "tsconfig_dev": "tsconfigDev",
        "tsconfig_dev_file": "tsconfigDevFile",
        "ts_jest_options": "tsJestOptions",
        "typescript_version": "typescriptVersion",
        "versionrc_options": "versionrcOptions",
        "vscode": "vscode",
        "workflow_bootstrap_steps": "workflowBootstrapSteps",
        "workflow_container_image": "workflowContainerImage",
        "workflow_git_identity": "workflowGitIdentity",
        "workflow_node_version": "workflowNodeVersion",
        "workflow_package_cache": "workflowPackageCache",
        "workflow_runs_on": "workflowRunsOn",
        "workflow_runs_on_group": "workflowRunsOnGroup",
        "yarn_berry_options": "yarnBerryOptions",
    },
)
class JsiiProjectOptions:
    def __init__(
        self,
        *,
        author: builtins.str,
        author_address: builtins.str,
        code_owners: typing.Sequence[builtins.str],
        name: builtins.str,
        repository_url: builtins.str,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        artifacts_directory: typing.Optional[builtins.str] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        biome: typing.Optional[builtins.bool] = None,
        biome_options: typing.Optional[typing.Union[_projen_javascript_04054675.BiomeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_options: typing.Optional[typing.Union[_projen_javascript_04054675.BuildWorkflowOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        build_workflow_triggers: typing.Optional[typing.Union[_projen_github_workflows_04054675.Triggers, typing.Dict[builtins.str, typing.Any]]] = None,
        bump_package: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        bundler_options: typing.Optional[typing.Union[_projen_javascript_04054675.BundlerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bun_version: typing.Optional[builtins.str] = None,
        check_licenses: typing.Optional[typing.Union[_projen_javascript_04054675.LicenseCheckerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        clobber: typing.Optional[builtins.bool] = None,
        code_artifact_options: typing.Optional[typing.Union[_projen_javascript_04054675.CodeArtifactOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        commit_generated: typing.Optional[builtins.bool] = None,
        compat: typing.Optional[builtins.bool] = None,
        compat_ignore: typing.Optional[builtins.str] = None,
        compress_assembly: typing.Optional[builtins.bool] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        default_release_branch: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[typing.Union[_projen_github_04054675.DependabotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[typing.Union[_projen_javascript_04054675.UpgradeDependenciesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        disable_tsconfig_dev: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docgen_file_path: typing.Optional[builtins.str] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        dotnet: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiDotNetTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[typing.Union[_projen_javascript_04054675.EslintOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        exclude_typescript: typing.Optional[typing.Sequence[builtins.str]] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        homepage: typing.Optional[builtins.str] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[typing.Union[_projen_javascript_04054675.JestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        jsii_version: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        libdir: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        major_version: typing.Optional[jsii.Number] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        min_major_version: typing.Optional[jsii.Number] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        next_version_command: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[_projen_javascript_04054675.NpmAccess] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        npm_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        npm_provenance: typing.Optional[builtins.bool] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        outdir: typing.Optional[builtins.str] = None,
        package: typing.Optional[builtins.bool] = None,
        package_manager: typing.Optional[_projen_javascript_04054675.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        peer_dependency_options: typing.Optional[typing.Union[_projen_javascript_04054675.PeerDependencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pnpm_version: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[typing.Union[_projen_javascript_04054675.PrettierOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_type: typing.Optional[_projen_04054675.ProjectType] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        publish_to_go: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiGoTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        publish_to_maven: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiJavaTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        publish_to_nuget: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiDotNetTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        publish_to_pypi: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiPythonTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        python: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiPythonTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        readme: typing.Optional[typing.Union["ReadmeOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        releasable_commits: typing.Optional[_projen_04054675.ReleasableCommits] = None,
        release: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, typing.Union[_projen_release_04054675.BranchOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_trigger: typing.Optional[_projen_release_04054675.ReleaseTrigger] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        rootdir: typing.Optional[builtins.str] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        scoped_packages_options: typing.Optional[typing.Sequence[typing.Union[_projen_javascript_04054675.ScopedPackagesOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        srcdir: typing.Optional[builtins.str] = None,
        stability: typing.Optional[builtins.str] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        ts_jest_options: typing.Optional[typing.Union[_projen_typescript_04054675.TsJestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        vscode: typing.Optional[builtins.bool] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_git_identity: typing.Optional[typing.Union[_projen_github_04054675.GitIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        workflow_package_cache: typing.Optional[builtins.bool] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_runs_on_group: typing.Optional[typing.Union[_projen_04054675.GroupRunnerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        yarn_berry_options: typing.Optional[typing.Union[_projen_javascript_04054675.YarnBerryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''JsiiProjectOptions.

        :param author: (experimental) The name of the library author. Default: $GIT_USER_NAME
        :param author_address: (experimental) Email or URL of the library author. Default: $GIT_USER_EMAIL
        :param code_owners: List of teams used to generate the CODEOWNERS file.
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param repository_url: (experimental) Git repository URL. Default: $GIT_REMOTE
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Is the author an organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param biome: (experimental) Setup Biome. Default: false
        :param biome_options: (experimental) Biome options. Default: - default options
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_options: (experimental) Options for PR build workflow.
        :param build_workflow_triggers: (deprecated) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bump_package: (experimental) The ``commit-and-tag-version`` compatible package used to bump the package version, as a dependency string. This can be any compatible package version, including the deprecated ``standard-version@9``. Default: - A recent version of "commit-and-tag-version"
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param bun_version: (experimental) The version of Bun to use if using Bun as a package manager. Default: "latest"
        :param check_licenses: (experimental) Configure which licenses should be deemed acceptable for use by dependencies. This setting will cause the build to fail, if any prohibited or not allowed licenses ares encountered. Default: - no license checks are run during the build and all licenses will be accepted
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: - true, but false for subprojects
        :param code_artifact_options: (experimental) Options for npm packages using AWS CodeArtifact. This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact Default: - undefined
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v4 A secret is required for private repos. Configured with ``@codeCovTokenSecret``. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param compat: (experimental) Automatically run API compatibility test against the latest version published to npm after compilation. - You can manually run compatibility tests using ``yarn compat`` if this feature is disabled. - You can ignore compatibility failures by adding lines to a ".compatignore" file. Default: false
        :param compat_ignore: (experimental) Name of the ignore file for API compatibility tests. Default: ".compatignore"
        :param compress_assembly: (experimental) Emit a compressed version of the assembly. Default: false
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param deps_upgrade: (experimental) Use tasks and github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for ``UpgradeDependencies``. Default: - default options
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param disable_tsconfig_dev: (experimental) Do not generate a ``tsconfig.dev.json`` file. Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docgen_file_path: (experimental) File path for generated docs. Default: "API.md"
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param dotnet: 
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json. Default: "lib/index.js"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param exclude_typescript: (experimental) Accepts a list of glob patterns. Files matching any of those patterns will be excluded from the TypeScript compiler input. By default, jsii will include all *.ts files (except .d.ts files) in the TypeScript compiler input. This can be problematic for example when the package's build or test procedure generates .ts files that cannot be compiled with jsii's compiler settings.
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param homepage: (experimental) Package's Homepage / Website.
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param jsii_version: (experimental) Version of the jsii compiler to use. Set to "*" if you want to manually manage the version of jsii in your project by managing updates to ``package.json`` on your own. NOTE: The jsii compiler releases since 5.0.0 are not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~5.0.0``). Default: "~5.6.0"
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param max_node_version: (experimental) The maximum node version supported by this package. Most projects should not use this option. The value indicates that the package is incompatible with any newer versions of node. This requirement is enforced via the engines field. You will normally not need to set this option. Consider this option only if your package is known to not function with newer versions of node. Default: - no maximum version is enforced
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param min_major_version: (experimental) Minimal Major version to release. This can be useful to set to 1, as breaking changes before the 1.x major release are not incrementing the major version number. Can not be set together with ``majorVersion``. Default: - No minimum version is being enforced
        :param min_node_version: (experimental) The minimum node version required by this package to function. Most projects should not use this option. The value indicates that the package is incompatible with any older versions of node. This requirement is enforced via the engines field. You will normally not need to set this option, even if your package is incompatible with EOL versions of node. Consider this option only if your package depends on a specific feature, that is not available in other LTS versions. Setting this option has very high impact on the consumers of your package, as package managers will actively prevent usage with node versions you have marked as incompatible. To change the node version of your CI/CD workflows, use ``workflowNodeVersion``. Default: - no minimum version is enforced
        :param mutable_build: (deprecated) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param next_version_command: (experimental) A shell command to control the next version to release. If present, this shell command will be run before the bump is executed, and it determines what version to release. It will be executed in the following environment: - Working directory: the project directory. - ``$VERSION``: the current version. Looks like ``1.2.3``. - ``$LATEST_TAG``: the most recent tag. Looks like ``prefix-v1.2.3``, or may be unset. - ``$SUGGESTED_BUMP``: the suggested bump action based on commits. One of ``major|minor|patch|none``. The command should print one of the following to ``stdout``: - Nothing: the next version number will be determined based on commit history. - ``x.y.z``: the next version number will be ``x.y.z``. - ``major|minor|patch``: the next version number will be the current version number with the indicated component bumped. This setting cannot be specified together with ``minMajorVersion``; the invoked script can be used to achieve the effects of ``minMajorVersion``. Default: - The next version will be determined based on the commit history and project settings.
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param npm_ignore_options: (experimental) Configuration options for .npmignore file.
        :param npm_provenance: (experimental) Should provenance statements be generated when the package is published. A supported package manager is required to publish a package with npm provenance statements and you will need to use a supported CI/CD provider. Note that the projen ``Release`` and ``Publisher`` components are using ``publib`` to publish packages, which is using npm internally and supports provenance statements independently of the package manager used. Default: - true for public packages, false otherwise
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other subprojects. Default: "."
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN_CLASSIC
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param pnpm_version: (experimental) The version of PNPM to use if using PNPM as a package manager. Default: "9"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: - true if not a subproject
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param publish_to_go: (experimental) Publish Go bindings to a git repository. Default: - no publishing
        :param publish_to_maven: (experimental) Publish to maven. Default: - no publishing
        :param publish_to_nuget: (experimental) Publish to NuGet. Default: - no publishing
        :param publish_to_pypi: (experimental) Publish to pypi. Default: - no publishing
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param python: 
        :param readme: Configuration of the README.md file.
        :param releasable_commits: (experimental) Find commits that should be considered releasable Used to decide if a release is required. Default: ReleasableCommits.everyCommit()
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: "v"
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param rootdir: Default: "."
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param scoped_packages_options: (experimental) Options for privately hosted scoped packages. Default: - fetch all scoped packages from the public npm registry
        :param scripts: (deprecated) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Also adds the script as a task. Default: {}
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param stability: (experimental) Package's Stability.
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param ts_jest_options: (experimental) Options for ts-jest.
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with commit-and-tag-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version used in GitHub Actions workflows. Always use this option if your GitHub Actions workflows require a specific to run. Default: - ``minNodeVersion`` if set, otherwise ``lts/*``.
        :param workflow_package_cache: (experimental) Enable Node.js package cache in GitHub workflows. Default: false
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param workflow_runs_on_group: (experimental) Github Runner Group selection options.
        :param yarn_berry_options: (experimental) Options for Yarn Berry. Default: - Yarn Berry v4 with all default options
        '''
        if isinstance(auto_approve_options, dict):
            auto_approve_options = _projen_github_04054675.AutoApproveOptions(**auto_approve_options)
        if isinstance(auto_merge_options, dict):
            auto_merge_options = _projen_github_04054675.AutoMergeOptions(**auto_merge_options)
        if isinstance(biome_options, dict):
            biome_options = _projen_javascript_04054675.BiomeOptions(**biome_options)
        if isinstance(build_workflow_options, dict):
            build_workflow_options = _projen_javascript_04054675.BuildWorkflowOptions(**build_workflow_options)
        if isinstance(build_workflow_triggers, dict):
            build_workflow_triggers = _projen_github_workflows_04054675.Triggers(**build_workflow_triggers)
        if isinstance(bundler_options, dict):
            bundler_options = _projen_javascript_04054675.BundlerOptions(**bundler_options)
        if isinstance(check_licenses, dict):
            check_licenses = _projen_javascript_04054675.LicenseCheckerOptions(**check_licenses)
        if isinstance(code_artifact_options, dict):
            code_artifact_options = _projen_javascript_04054675.CodeArtifactOptions(**code_artifact_options)
        if isinstance(dependabot_options, dict):
            dependabot_options = _projen_github_04054675.DependabotOptions(**dependabot_options)
        if isinstance(deps_upgrade_options, dict):
            deps_upgrade_options = _projen_javascript_04054675.UpgradeDependenciesOptions(**deps_upgrade_options)
        if isinstance(dotnet, dict):
            dotnet = _projen_cdk_04054675.JsiiDotNetTarget(**dotnet)
        if isinstance(eslint_options, dict):
            eslint_options = _projen_javascript_04054675.EslintOptions(**eslint_options)
        if isinstance(github_options, dict):
            github_options = _projen_github_04054675.GitHubOptions(**github_options)
        if isinstance(git_ignore_options, dict):
            git_ignore_options = _projen_04054675.IgnoreFileOptions(**git_ignore_options)
        if isinstance(git_options, dict):
            git_options = _projen_04054675.GitOptions(**git_options)
        if isinstance(jest_options, dict):
            jest_options = _projen_javascript_04054675.JestOptions(**jest_options)
        if isinstance(logging, dict):
            logging = _projen_04054675.LoggerOptions(**logging)
        if isinstance(mergify_options, dict):
            mergify_options = _projen_github_04054675.MergifyOptions(**mergify_options)
        if isinstance(npm_ignore_options, dict):
            npm_ignore_options = _projen_04054675.IgnoreFileOptions(**npm_ignore_options)
        if isinstance(peer_dependency_options, dict):
            peer_dependency_options = _projen_javascript_04054675.PeerDependencyOptions(**peer_dependency_options)
        if isinstance(prettier_options, dict):
            prettier_options = _projen_javascript_04054675.PrettierOptions(**prettier_options)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = _projen_04054675.ProjenrcJsonOptions(**projenrc_json_options)
        if isinstance(projenrc_js_options, dict):
            projenrc_js_options = _projen_javascript_04054675.ProjenrcOptions(**projenrc_js_options)
        if isinstance(projenrc_ts_options, dict):
            projenrc_ts_options = _projen_typescript_04054675.ProjenrcOptions(**projenrc_ts_options)
        if isinstance(publish_to_go, dict):
            publish_to_go = _projen_cdk_04054675.JsiiGoTarget(**publish_to_go)
        if isinstance(publish_to_maven, dict):
            publish_to_maven = _projen_cdk_04054675.JsiiJavaTarget(**publish_to_maven)
        if isinstance(publish_to_nuget, dict):
            publish_to_nuget = _projen_cdk_04054675.JsiiDotNetTarget(**publish_to_nuget)
        if isinstance(publish_to_pypi, dict):
            publish_to_pypi = _projen_cdk_04054675.JsiiPythonTarget(**publish_to_pypi)
        if isinstance(python, dict):
            python = _projen_cdk_04054675.JsiiPythonTarget(**python)
        if isinstance(readme, dict):
            readme = ReadmeOptions(**readme)
        if isinstance(renovatebot_options, dict):
            renovatebot_options = _projen_04054675.RenovatebotOptions(**renovatebot_options)
        if isinstance(stale_options, dict):
            stale_options = _projen_github_04054675.StaleOptions(**stale_options)
        if isinstance(tsconfig, dict):
            tsconfig = _projen_javascript_04054675.TypescriptConfigOptions(**tsconfig)
        if isinstance(tsconfig_dev, dict):
            tsconfig_dev = _projen_javascript_04054675.TypescriptConfigOptions(**tsconfig_dev)
        if isinstance(ts_jest_options, dict):
            ts_jest_options = _projen_typescript_04054675.TsJestOptions(**ts_jest_options)
        if isinstance(workflow_git_identity, dict):
            workflow_git_identity = _projen_github_04054675.GitIdentity(**workflow_git_identity)
        if isinstance(workflow_runs_on_group, dict):
            workflow_runs_on_group = _projen_04054675.GroupRunnerOptions(**workflow_runs_on_group)
        if isinstance(yarn_berry_options, dict):
            yarn_berry_options = _projen_javascript_04054675.YarnBerryOptions(**yarn_berry_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcc0f0f3d874afabc142961b7ca192083fcad906385166f2e47f7e7399ce16bc)
            check_type(argname="argument author", value=author, expected_type=type_hints["author"])
            check_type(argname="argument author_address", value=author_address, expected_type=type_hints["author_address"])
            check_type(argname="argument code_owners", value=code_owners, expected_type=type_hints["code_owners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument repository_url", value=repository_url, expected_type=type_hints["repository_url"])
            check_type(argname="argument allow_library_dependencies", value=allow_library_dependencies, expected_type=type_hints["allow_library_dependencies"])
            check_type(argname="argument artifacts_directory", value=artifacts_directory, expected_type=type_hints["artifacts_directory"])
            check_type(argname="argument author_email", value=author_email, expected_type=type_hints["author_email"])
            check_type(argname="argument author_name", value=author_name, expected_type=type_hints["author_name"])
            check_type(argname="argument author_organization", value=author_organization, expected_type=type_hints["author_organization"])
            check_type(argname="argument author_url", value=author_url, expected_type=type_hints["author_url"])
            check_type(argname="argument auto_approve_options", value=auto_approve_options, expected_type=type_hints["auto_approve_options"])
            check_type(argname="argument auto_approve_upgrades", value=auto_approve_upgrades, expected_type=type_hints["auto_approve_upgrades"])
            check_type(argname="argument auto_detect_bin", value=auto_detect_bin, expected_type=type_hints["auto_detect_bin"])
            check_type(argname="argument auto_merge", value=auto_merge, expected_type=type_hints["auto_merge"])
            check_type(argname="argument auto_merge_options", value=auto_merge_options, expected_type=type_hints["auto_merge_options"])
            check_type(argname="argument bin", value=bin, expected_type=type_hints["bin"])
            check_type(argname="argument biome", value=biome, expected_type=type_hints["biome"])
            check_type(argname="argument biome_options", value=biome_options, expected_type=type_hints["biome_options"])
            check_type(argname="argument bugs_email", value=bugs_email, expected_type=type_hints["bugs_email"])
            check_type(argname="argument bugs_url", value=bugs_url, expected_type=type_hints["bugs_url"])
            check_type(argname="argument build_workflow", value=build_workflow, expected_type=type_hints["build_workflow"])
            check_type(argname="argument build_workflow_options", value=build_workflow_options, expected_type=type_hints["build_workflow_options"])
            check_type(argname="argument build_workflow_triggers", value=build_workflow_triggers, expected_type=type_hints["build_workflow_triggers"])
            check_type(argname="argument bump_package", value=bump_package, expected_type=type_hints["bump_package"])
            check_type(argname="argument bundled_deps", value=bundled_deps, expected_type=type_hints["bundled_deps"])
            check_type(argname="argument bundler_options", value=bundler_options, expected_type=type_hints["bundler_options"])
            check_type(argname="argument bun_version", value=bun_version, expected_type=type_hints["bun_version"])
            check_type(argname="argument check_licenses", value=check_licenses, expected_type=type_hints["check_licenses"])
            check_type(argname="argument clobber", value=clobber, expected_type=type_hints["clobber"])
            check_type(argname="argument code_artifact_options", value=code_artifact_options, expected_type=type_hints["code_artifact_options"])
            check_type(argname="argument code_cov", value=code_cov, expected_type=type_hints["code_cov"])
            check_type(argname="argument code_cov_token_secret", value=code_cov_token_secret, expected_type=type_hints["code_cov_token_secret"])
            check_type(argname="argument commit_generated", value=commit_generated, expected_type=type_hints["commit_generated"])
            check_type(argname="argument compat", value=compat, expected_type=type_hints["compat"])
            check_type(argname="argument compat_ignore", value=compat_ignore, expected_type=type_hints["compat_ignore"])
            check_type(argname="argument compress_assembly", value=compress_assembly, expected_type=type_hints["compress_assembly"])
            check_type(argname="argument copyright_owner", value=copyright_owner, expected_type=type_hints["copyright_owner"])
            check_type(argname="argument copyright_period", value=copyright_period, expected_type=type_hints["copyright_period"])
            check_type(argname="argument default_release_branch", value=default_release_branch, expected_type=type_hints["default_release_branch"])
            check_type(argname="argument dependabot", value=dependabot, expected_type=type_hints["dependabot"])
            check_type(argname="argument dependabot_options", value=dependabot_options, expected_type=type_hints["dependabot_options"])
            check_type(argname="argument deps", value=deps, expected_type=type_hints["deps"])
            check_type(argname="argument deps_upgrade", value=deps_upgrade, expected_type=type_hints["deps_upgrade"])
            check_type(argname="argument deps_upgrade_options", value=deps_upgrade_options, expected_type=type_hints["deps_upgrade_options"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument dev_container", value=dev_container, expected_type=type_hints["dev_container"])
            check_type(argname="argument dev_deps", value=dev_deps, expected_type=type_hints["dev_deps"])
            check_type(argname="argument disable_tsconfig", value=disable_tsconfig, expected_type=type_hints["disable_tsconfig"])
            check_type(argname="argument disable_tsconfig_dev", value=disable_tsconfig_dev, expected_type=type_hints["disable_tsconfig_dev"])
            check_type(argname="argument docgen", value=docgen, expected_type=type_hints["docgen"])
            check_type(argname="argument docgen_file_path", value=docgen_file_path, expected_type=type_hints["docgen_file_path"])
            check_type(argname="argument docs_directory", value=docs_directory, expected_type=type_hints["docs_directory"])
            check_type(argname="argument dotnet", value=dotnet, expected_type=type_hints["dotnet"])
            check_type(argname="argument entrypoint", value=entrypoint, expected_type=type_hints["entrypoint"])
            check_type(argname="argument entrypoint_types", value=entrypoint_types, expected_type=type_hints["entrypoint_types"])
            check_type(argname="argument eslint", value=eslint, expected_type=type_hints["eslint"])
            check_type(argname="argument eslint_options", value=eslint_options, expected_type=type_hints["eslint_options"])
            check_type(argname="argument exclude_typescript", value=exclude_typescript, expected_type=type_hints["exclude_typescript"])
            check_type(argname="argument github", value=github, expected_type=type_hints["github"])
            check_type(argname="argument github_options", value=github_options, expected_type=type_hints["github_options"])
            check_type(argname="argument gitignore", value=gitignore, expected_type=type_hints["gitignore"])
            check_type(argname="argument git_ignore_options", value=git_ignore_options, expected_type=type_hints["git_ignore_options"])
            check_type(argname="argument git_options", value=git_options, expected_type=type_hints["git_options"])
            check_type(argname="argument gitpod", value=gitpod, expected_type=type_hints["gitpod"])
            check_type(argname="argument homepage", value=homepage, expected_type=type_hints["homepage"])
            check_type(argname="argument jest", value=jest, expected_type=type_hints["jest"])
            check_type(argname="argument jest_options", value=jest_options, expected_type=type_hints["jest_options"])
            check_type(argname="argument jsii_release_version", value=jsii_release_version, expected_type=type_hints["jsii_release_version"])
            check_type(argname="argument jsii_version", value=jsii_version, expected_type=type_hints["jsii_version"])
            check_type(argname="argument keywords", value=keywords, expected_type=type_hints["keywords"])
            check_type(argname="argument libdir", value=libdir, expected_type=type_hints["libdir"])
            check_type(argname="argument license", value=license, expected_type=type_hints["license"])
            check_type(argname="argument licensed", value=licensed, expected_type=type_hints["licensed"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument major_version", value=major_version, expected_type=type_hints["major_version"])
            check_type(argname="argument max_node_version", value=max_node_version, expected_type=type_hints["max_node_version"])
            check_type(argname="argument mergify", value=mergify, expected_type=type_hints["mergify"])
            check_type(argname="argument mergify_options", value=mergify_options, expected_type=type_hints["mergify_options"])
            check_type(argname="argument min_major_version", value=min_major_version, expected_type=type_hints["min_major_version"])
            check_type(argname="argument min_node_version", value=min_node_version, expected_type=type_hints["min_node_version"])
            check_type(argname="argument mutable_build", value=mutable_build, expected_type=type_hints["mutable_build"])
            check_type(argname="argument next_version_command", value=next_version_command, expected_type=type_hints["next_version_command"])
            check_type(argname="argument npm_access", value=npm_access, expected_type=type_hints["npm_access"])
            check_type(argname="argument npm_dist_tag", value=npm_dist_tag, expected_type=type_hints["npm_dist_tag"])
            check_type(argname="argument npmignore", value=npmignore, expected_type=type_hints["npmignore"])
            check_type(argname="argument npmignore_enabled", value=npmignore_enabled, expected_type=type_hints["npmignore_enabled"])
            check_type(argname="argument npm_ignore_options", value=npm_ignore_options, expected_type=type_hints["npm_ignore_options"])
            check_type(argname="argument npm_provenance", value=npm_provenance, expected_type=type_hints["npm_provenance"])
            check_type(argname="argument npm_registry", value=npm_registry, expected_type=type_hints["npm_registry"])
            check_type(argname="argument npm_registry_url", value=npm_registry_url, expected_type=type_hints["npm_registry_url"])
            check_type(argname="argument npm_token_secret", value=npm_token_secret, expected_type=type_hints["npm_token_secret"])
            check_type(argname="argument outdir", value=outdir, expected_type=type_hints["outdir"])
            check_type(argname="argument package", value=package, expected_type=type_hints["package"])
            check_type(argname="argument package_manager", value=package_manager, expected_type=type_hints["package_manager"])
            check_type(argname="argument package_name", value=package_name, expected_type=type_hints["package_name"])
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument peer_dependency_options", value=peer_dependency_options, expected_type=type_hints["peer_dependency_options"])
            check_type(argname="argument peer_deps", value=peer_deps, expected_type=type_hints["peer_deps"])
            check_type(argname="argument pnpm_version", value=pnpm_version, expected_type=type_hints["pnpm_version"])
            check_type(argname="argument post_build_steps", value=post_build_steps, expected_type=type_hints["post_build_steps"])
            check_type(argname="argument prerelease", value=prerelease, expected_type=type_hints["prerelease"])
            check_type(argname="argument prettier", value=prettier, expected_type=type_hints["prettier"])
            check_type(argname="argument prettier_options", value=prettier_options, expected_type=type_hints["prettier_options"])
            check_type(argname="argument project_type", value=project_type, expected_type=type_hints["project_type"])
            check_type(argname="argument projen_command", value=projen_command, expected_type=type_hints["projen_command"])
            check_type(argname="argument projen_credentials", value=projen_credentials, expected_type=type_hints["projen_credentials"])
            check_type(argname="argument projen_dev_dependency", value=projen_dev_dependency, expected_type=type_hints["projen_dev_dependency"])
            check_type(argname="argument projenrc_js", value=projenrc_js, expected_type=type_hints["projenrc_js"])
            check_type(argname="argument projenrc_json", value=projenrc_json, expected_type=type_hints["projenrc_json"])
            check_type(argname="argument projenrc_json_options", value=projenrc_json_options, expected_type=type_hints["projenrc_json_options"])
            check_type(argname="argument projenrc_js_options", value=projenrc_js_options, expected_type=type_hints["projenrc_js_options"])
            check_type(argname="argument projenrc_ts", value=projenrc_ts, expected_type=type_hints["projenrc_ts"])
            check_type(argname="argument projenrc_ts_options", value=projenrc_ts_options, expected_type=type_hints["projenrc_ts_options"])
            check_type(argname="argument projen_token_secret", value=projen_token_secret, expected_type=type_hints["projen_token_secret"])
            check_type(argname="argument projen_version", value=projen_version, expected_type=type_hints["projen_version"])
            check_type(argname="argument publish_dry_run", value=publish_dry_run, expected_type=type_hints["publish_dry_run"])
            check_type(argname="argument publish_tasks", value=publish_tasks, expected_type=type_hints["publish_tasks"])
            check_type(argname="argument publish_to_go", value=publish_to_go, expected_type=type_hints["publish_to_go"])
            check_type(argname="argument publish_to_maven", value=publish_to_maven, expected_type=type_hints["publish_to_maven"])
            check_type(argname="argument publish_to_nuget", value=publish_to_nuget, expected_type=type_hints["publish_to_nuget"])
            check_type(argname="argument publish_to_pypi", value=publish_to_pypi, expected_type=type_hints["publish_to_pypi"])
            check_type(argname="argument pull_request_template", value=pull_request_template, expected_type=type_hints["pull_request_template"])
            check_type(argname="argument pull_request_template_contents", value=pull_request_template_contents, expected_type=type_hints["pull_request_template_contents"])
            check_type(argname="argument python", value=python, expected_type=type_hints["python"])
            check_type(argname="argument readme", value=readme, expected_type=type_hints["readme"])
            check_type(argname="argument releasable_commits", value=releasable_commits, expected_type=type_hints["releasable_commits"])
            check_type(argname="argument release", value=release, expected_type=type_hints["release"])
            check_type(argname="argument release_branches", value=release_branches, expected_type=type_hints["release_branches"])
            check_type(argname="argument release_every_commit", value=release_every_commit, expected_type=type_hints["release_every_commit"])
            check_type(argname="argument release_failure_issue", value=release_failure_issue, expected_type=type_hints["release_failure_issue"])
            check_type(argname="argument release_failure_issue_label", value=release_failure_issue_label, expected_type=type_hints["release_failure_issue_label"])
            check_type(argname="argument release_schedule", value=release_schedule, expected_type=type_hints["release_schedule"])
            check_type(argname="argument release_tag_prefix", value=release_tag_prefix, expected_type=type_hints["release_tag_prefix"])
            check_type(argname="argument release_to_npm", value=release_to_npm, expected_type=type_hints["release_to_npm"])
            check_type(argname="argument release_trigger", value=release_trigger, expected_type=type_hints["release_trigger"])
            check_type(argname="argument release_workflow", value=release_workflow, expected_type=type_hints["release_workflow"])
            check_type(argname="argument release_workflow_name", value=release_workflow_name, expected_type=type_hints["release_workflow_name"])
            check_type(argname="argument release_workflow_setup_steps", value=release_workflow_setup_steps, expected_type=type_hints["release_workflow_setup_steps"])
            check_type(argname="argument renovatebot", value=renovatebot, expected_type=type_hints["renovatebot"])
            check_type(argname="argument renovatebot_options", value=renovatebot_options, expected_type=type_hints["renovatebot_options"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument repository_directory", value=repository_directory, expected_type=type_hints["repository_directory"])
            check_type(argname="argument rootdir", value=rootdir, expected_type=type_hints["rootdir"])
            check_type(argname="argument sample_code", value=sample_code, expected_type=type_hints["sample_code"])
            check_type(argname="argument scoped_packages_options", value=scoped_packages_options, expected_type=type_hints["scoped_packages_options"])
            check_type(argname="argument scripts", value=scripts, expected_type=type_hints["scripts"])
            check_type(argname="argument srcdir", value=srcdir, expected_type=type_hints["srcdir"])
            check_type(argname="argument stability", value=stability, expected_type=type_hints["stability"])
            check_type(argname="argument stale", value=stale, expected_type=type_hints["stale"])
            check_type(argname="argument stale_options", value=stale_options, expected_type=type_hints["stale_options"])
            check_type(argname="argument testdir", value=testdir, expected_type=type_hints["testdir"])
            check_type(argname="argument tsconfig", value=tsconfig, expected_type=type_hints["tsconfig"])
            check_type(argname="argument tsconfig_dev", value=tsconfig_dev, expected_type=type_hints["tsconfig_dev"])
            check_type(argname="argument tsconfig_dev_file", value=tsconfig_dev_file, expected_type=type_hints["tsconfig_dev_file"])
            check_type(argname="argument ts_jest_options", value=ts_jest_options, expected_type=type_hints["ts_jest_options"])
            check_type(argname="argument typescript_version", value=typescript_version, expected_type=type_hints["typescript_version"])
            check_type(argname="argument versionrc_options", value=versionrc_options, expected_type=type_hints["versionrc_options"])
            check_type(argname="argument vscode", value=vscode, expected_type=type_hints["vscode"])
            check_type(argname="argument workflow_bootstrap_steps", value=workflow_bootstrap_steps, expected_type=type_hints["workflow_bootstrap_steps"])
            check_type(argname="argument workflow_container_image", value=workflow_container_image, expected_type=type_hints["workflow_container_image"])
            check_type(argname="argument workflow_git_identity", value=workflow_git_identity, expected_type=type_hints["workflow_git_identity"])
            check_type(argname="argument workflow_node_version", value=workflow_node_version, expected_type=type_hints["workflow_node_version"])
            check_type(argname="argument workflow_package_cache", value=workflow_package_cache, expected_type=type_hints["workflow_package_cache"])
            check_type(argname="argument workflow_runs_on", value=workflow_runs_on, expected_type=type_hints["workflow_runs_on"])
            check_type(argname="argument workflow_runs_on_group", value=workflow_runs_on_group, expected_type=type_hints["workflow_runs_on_group"])
            check_type(argname="argument yarn_berry_options", value=yarn_berry_options, expected_type=type_hints["yarn_berry_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "author": author,
            "author_address": author_address,
            "code_owners": code_owners,
            "name": name,
            "repository_url": repository_url,
        }
        if allow_library_dependencies is not None:
            self._values["allow_library_dependencies"] = allow_library_dependencies
        if artifacts_directory is not None:
            self._values["artifacts_directory"] = artifacts_directory
        if author_email is not None:
            self._values["author_email"] = author_email
        if author_name is not None:
            self._values["author_name"] = author_name
        if author_organization is not None:
            self._values["author_organization"] = author_organization
        if author_url is not None:
            self._values["author_url"] = author_url
        if auto_approve_options is not None:
            self._values["auto_approve_options"] = auto_approve_options
        if auto_approve_upgrades is not None:
            self._values["auto_approve_upgrades"] = auto_approve_upgrades
        if auto_detect_bin is not None:
            self._values["auto_detect_bin"] = auto_detect_bin
        if auto_merge is not None:
            self._values["auto_merge"] = auto_merge
        if auto_merge_options is not None:
            self._values["auto_merge_options"] = auto_merge_options
        if bin is not None:
            self._values["bin"] = bin
        if biome is not None:
            self._values["biome"] = biome
        if biome_options is not None:
            self._values["biome_options"] = biome_options
        if bugs_email is not None:
            self._values["bugs_email"] = bugs_email
        if bugs_url is not None:
            self._values["bugs_url"] = bugs_url
        if build_workflow is not None:
            self._values["build_workflow"] = build_workflow
        if build_workflow_options is not None:
            self._values["build_workflow_options"] = build_workflow_options
        if build_workflow_triggers is not None:
            self._values["build_workflow_triggers"] = build_workflow_triggers
        if bump_package is not None:
            self._values["bump_package"] = bump_package
        if bundled_deps is not None:
            self._values["bundled_deps"] = bundled_deps
        if bundler_options is not None:
            self._values["bundler_options"] = bundler_options
        if bun_version is not None:
            self._values["bun_version"] = bun_version
        if check_licenses is not None:
            self._values["check_licenses"] = check_licenses
        if clobber is not None:
            self._values["clobber"] = clobber
        if code_artifact_options is not None:
            self._values["code_artifact_options"] = code_artifact_options
        if code_cov is not None:
            self._values["code_cov"] = code_cov
        if code_cov_token_secret is not None:
            self._values["code_cov_token_secret"] = code_cov_token_secret
        if commit_generated is not None:
            self._values["commit_generated"] = commit_generated
        if compat is not None:
            self._values["compat"] = compat
        if compat_ignore is not None:
            self._values["compat_ignore"] = compat_ignore
        if compress_assembly is not None:
            self._values["compress_assembly"] = compress_assembly
        if copyright_owner is not None:
            self._values["copyright_owner"] = copyright_owner
        if copyright_period is not None:
            self._values["copyright_period"] = copyright_period
        if default_release_branch is not None:
            self._values["default_release_branch"] = default_release_branch
        if dependabot is not None:
            self._values["dependabot"] = dependabot
        if dependabot_options is not None:
            self._values["dependabot_options"] = dependabot_options
        if deps is not None:
            self._values["deps"] = deps
        if deps_upgrade is not None:
            self._values["deps_upgrade"] = deps_upgrade
        if deps_upgrade_options is not None:
            self._values["deps_upgrade_options"] = deps_upgrade_options
        if description is not None:
            self._values["description"] = description
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if dev_deps is not None:
            self._values["dev_deps"] = dev_deps
        if disable_tsconfig is not None:
            self._values["disable_tsconfig"] = disable_tsconfig
        if disable_tsconfig_dev is not None:
            self._values["disable_tsconfig_dev"] = disable_tsconfig_dev
        if docgen is not None:
            self._values["docgen"] = docgen
        if docgen_file_path is not None:
            self._values["docgen_file_path"] = docgen_file_path
        if docs_directory is not None:
            self._values["docs_directory"] = docs_directory
        if dotnet is not None:
            self._values["dotnet"] = dotnet
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint
        if entrypoint_types is not None:
            self._values["entrypoint_types"] = entrypoint_types
        if eslint is not None:
            self._values["eslint"] = eslint
        if eslint_options is not None:
            self._values["eslint_options"] = eslint_options
        if exclude_typescript is not None:
            self._values["exclude_typescript"] = exclude_typescript
        if github is not None:
            self._values["github"] = github
        if github_options is not None:
            self._values["github_options"] = github_options
        if gitignore is not None:
            self._values["gitignore"] = gitignore
        if git_ignore_options is not None:
            self._values["git_ignore_options"] = git_ignore_options
        if git_options is not None:
            self._values["git_options"] = git_options
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if homepage is not None:
            self._values["homepage"] = homepage
        if jest is not None:
            self._values["jest"] = jest
        if jest_options is not None:
            self._values["jest_options"] = jest_options
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version
        if jsii_version is not None:
            self._values["jsii_version"] = jsii_version
        if keywords is not None:
            self._values["keywords"] = keywords
        if libdir is not None:
            self._values["libdir"] = libdir
        if license is not None:
            self._values["license"] = license
        if licensed is not None:
            self._values["licensed"] = licensed
        if logging is not None:
            self._values["logging"] = logging
        if major_version is not None:
            self._values["major_version"] = major_version
        if max_node_version is not None:
            self._values["max_node_version"] = max_node_version
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if min_major_version is not None:
            self._values["min_major_version"] = min_major_version
        if min_node_version is not None:
            self._values["min_node_version"] = min_node_version
        if mutable_build is not None:
            self._values["mutable_build"] = mutable_build
        if next_version_command is not None:
            self._values["next_version_command"] = next_version_command
        if npm_access is not None:
            self._values["npm_access"] = npm_access
        if npm_dist_tag is not None:
            self._values["npm_dist_tag"] = npm_dist_tag
        if npmignore is not None:
            self._values["npmignore"] = npmignore
        if npmignore_enabled is not None:
            self._values["npmignore_enabled"] = npmignore_enabled
        if npm_ignore_options is not None:
            self._values["npm_ignore_options"] = npm_ignore_options
        if npm_provenance is not None:
            self._values["npm_provenance"] = npm_provenance
        if npm_registry is not None:
            self._values["npm_registry"] = npm_registry
        if npm_registry_url is not None:
            self._values["npm_registry_url"] = npm_registry_url
        if npm_token_secret is not None:
            self._values["npm_token_secret"] = npm_token_secret
        if outdir is not None:
            self._values["outdir"] = outdir
        if package is not None:
            self._values["package"] = package
        if package_manager is not None:
            self._values["package_manager"] = package_manager
        if package_name is not None:
            self._values["package_name"] = package_name
        if parent is not None:
            self._values["parent"] = parent
        if peer_dependency_options is not None:
            self._values["peer_dependency_options"] = peer_dependency_options
        if peer_deps is not None:
            self._values["peer_deps"] = peer_deps
        if pnpm_version is not None:
            self._values["pnpm_version"] = pnpm_version
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if prerelease is not None:
            self._values["prerelease"] = prerelease
        if prettier is not None:
            self._values["prettier"] = prettier
        if prettier_options is not None:
            self._values["prettier_options"] = prettier_options
        if project_type is not None:
            self._values["project_type"] = project_type
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projen_credentials is not None:
            self._values["projen_credentials"] = projen_credentials
        if projen_dev_dependency is not None:
            self._values["projen_dev_dependency"] = projen_dev_dependency
        if projenrc_js is not None:
            self._values["projenrc_js"] = projenrc_js
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if projenrc_js_options is not None:
            self._values["projenrc_js_options"] = projenrc_js_options
        if projenrc_ts is not None:
            self._values["projenrc_ts"] = projenrc_ts
        if projenrc_ts_options is not None:
            self._values["projenrc_ts_options"] = projenrc_ts_options
        if projen_token_secret is not None:
            self._values["projen_token_secret"] = projen_token_secret
        if projen_version is not None:
            self._values["projen_version"] = projen_version
        if publish_dry_run is not None:
            self._values["publish_dry_run"] = publish_dry_run
        if publish_tasks is not None:
            self._values["publish_tasks"] = publish_tasks
        if publish_to_go is not None:
            self._values["publish_to_go"] = publish_to_go
        if publish_to_maven is not None:
            self._values["publish_to_maven"] = publish_to_maven
        if publish_to_nuget is not None:
            self._values["publish_to_nuget"] = publish_to_nuget
        if publish_to_pypi is not None:
            self._values["publish_to_pypi"] = publish_to_pypi
        if pull_request_template is not None:
            self._values["pull_request_template"] = pull_request_template
        if pull_request_template_contents is not None:
            self._values["pull_request_template_contents"] = pull_request_template_contents
        if python is not None:
            self._values["python"] = python
        if readme is not None:
            self._values["readme"] = readme
        if releasable_commits is not None:
            self._values["releasable_commits"] = releasable_commits
        if release is not None:
            self._values["release"] = release
        if release_branches is not None:
            self._values["release_branches"] = release_branches
        if release_every_commit is not None:
            self._values["release_every_commit"] = release_every_commit
        if release_failure_issue is not None:
            self._values["release_failure_issue"] = release_failure_issue
        if release_failure_issue_label is not None:
            self._values["release_failure_issue_label"] = release_failure_issue_label
        if release_schedule is not None:
            self._values["release_schedule"] = release_schedule
        if release_tag_prefix is not None:
            self._values["release_tag_prefix"] = release_tag_prefix
        if release_to_npm is not None:
            self._values["release_to_npm"] = release_to_npm
        if release_trigger is not None:
            self._values["release_trigger"] = release_trigger
        if release_workflow is not None:
            self._values["release_workflow"] = release_workflow
        if release_workflow_name is not None:
            self._values["release_workflow_name"] = release_workflow_name
        if release_workflow_setup_steps is not None:
            self._values["release_workflow_setup_steps"] = release_workflow_setup_steps
        if renovatebot is not None:
            self._values["renovatebot"] = renovatebot
        if renovatebot_options is not None:
            self._values["renovatebot_options"] = renovatebot_options
        if repository is not None:
            self._values["repository"] = repository
        if repository_directory is not None:
            self._values["repository_directory"] = repository_directory
        if rootdir is not None:
            self._values["rootdir"] = rootdir
        if sample_code is not None:
            self._values["sample_code"] = sample_code
        if scoped_packages_options is not None:
            self._values["scoped_packages_options"] = scoped_packages_options
        if scripts is not None:
            self._values["scripts"] = scripts
        if srcdir is not None:
            self._values["srcdir"] = srcdir
        if stability is not None:
            self._values["stability"] = stability
        if stale is not None:
            self._values["stale"] = stale
        if stale_options is not None:
            self._values["stale_options"] = stale_options
        if testdir is not None:
            self._values["testdir"] = testdir
        if tsconfig is not None:
            self._values["tsconfig"] = tsconfig
        if tsconfig_dev is not None:
            self._values["tsconfig_dev"] = tsconfig_dev
        if tsconfig_dev_file is not None:
            self._values["tsconfig_dev_file"] = tsconfig_dev_file
        if ts_jest_options is not None:
            self._values["ts_jest_options"] = ts_jest_options
        if typescript_version is not None:
            self._values["typescript_version"] = typescript_version
        if versionrc_options is not None:
            self._values["versionrc_options"] = versionrc_options
        if vscode is not None:
            self._values["vscode"] = vscode
        if workflow_bootstrap_steps is not None:
            self._values["workflow_bootstrap_steps"] = workflow_bootstrap_steps
        if workflow_container_image is not None:
            self._values["workflow_container_image"] = workflow_container_image
        if workflow_git_identity is not None:
            self._values["workflow_git_identity"] = workflow_git_identity
        if workflow_node_version is not None:
            self._values["workflow_node_version"] = workflow_node_version
        if workflow_package_cache is not None:
            self._values["workflow_package_cache"] = workflow_package_cache
        if workflow_runs_on is not None:
            self._values["workflow_runs_on"] = workflow_runs_on
        if workflow_runs_on_group is not None:
            self._values["workflow_runs_on_group"] = workflow_runs_on_group
        if yarn_berry_options is not None:
            self._values["yarn_berry_options"] = yarn_berry_options

    @builtins.property
    def author(self) -> builtins.str:
        '''(experimental) The name of the library author.

        :default: $GIT_USER_NAME

        :stability: experimental
        '''
        result = self._values.get("author")
        assert result is not None, "Required property 'author' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def author_address(self) -> builtins.str:
        '''(experimental) Email or URL of the library author.

        :default: $GIT_USER_EMAIL

        :stability: experimental
        '''
        result = self._values.get("author_address")
        assert result is not None, "Required property 'author_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code_owners(self) -> typing.List[builtins.str]:
        '''List of teams used to generate the CODEOWNERS file.'''
        result = self._values.get("code_owners")
        assert result is not None, "Required property 'code_owners' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_url(self) -> builtins.str:
        '''(experimental) Git repository URL.

        :default: $GIT_REMOTE

        :stability: experimental
        '''
        result = self._values.get("repository_url")
        assert result is not None, "Required property 'repository_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_library_dependencies(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``.

        This is normally only allowed for libraries. For apps, there's no meaning
        for specifying these.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("allow_library_dependencies")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def artifacts_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) A directory which will contain build artifacts.

        :default: "dist"

        :stability: experimental
        '''
        result = self._values.get("artifacts_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's e-mail.

        :stability: experimental
        '''
        result = self._values.get("author_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's name.

        :stability: experimental
        '''
        result = self._values.get("author_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_organization(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Is the author an organization.

        :stability: experimental
        '''
        result = self._values.get("author_organization")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's URL / Website.

        :stability: experimental
        '''
        result = self._values.get("author_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_approve_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.AutoApproveOptions]:
        '''(experimental) Enable and configure the 'auto approve' workflow.

        :default: - auto approve is disabled

        :stability: experimental
        '''
        result = self._values.get("auto_approve_options")
        return typing.cast(typing.Optional[_projen_github_04054675.AutoApproveOptions], result)

    @builtins.property
    def auto_approve_upgrades(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued).

        Throw if set to true but ``autoApproveOptions`` are not defined.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("auto_approve_upgrades")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_detect_bin(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_detect_bin")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_merge(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable automatic merging on GitHub.

        Has no effect if ``github.mergify``
        is set to false.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_merge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_merge_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.AutoMergeOptions]:
        '''(experimental) Configure options for automatic merging on GitHub.

        Has no effect if
        ``github.mergify`` or ``autoMerge`` is set to false.

        :default: - see defaults in ``AutoMergeOptions``

        :stability: experimental
        '''
        result = self._values.get("auto_merge_options")
        return typing.cast(typing.Optional[_projen_github_04054675.AutoMergeOptions], result)

    @builtins.property
    def bin(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Binary programs vended with your module.

        You can use this option to add/customize how binaries are represented in
        your ``package.json``, but unless ``autoDetectBin`` is ``false``, every
        executable file under ``bin`` will automatically be added to this section.

        :stability: experimental
        '''
        result = self._values.get("bin")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def biome(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup Biome.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("biome")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def biome_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.BiomeOptions]:
        '''(experimental) Biome options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("biome_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.BiomeOptions], result)

    @builtins.property
    def bugs_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) The email address to which issues should be reported.

        :stability: experimental
        '''
        result = self._values.get("bugs_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bugs_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The url to your project's issue tracker.

        :stability: experimental
        '''
        result = self._values.get("bugs_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_workflow(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow for building PRs.

        :default: - true if not a subproject

        :stability: experimental
        '''
        result = self._values.get("build_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_workflow_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.BuildWorkflowOptions]:
        '''(experimental) Options for PR build workflow.

        :stability: experimental
        '''
        result = self._values.get("build_workflow_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.BuildWorkflowOptions], result)

    @builtins.property
    def build_workflow_triggers(
        self,
    ) -> typing.Optional[_projen_github_workflows_04054675.Triggers]:
        '''(deprecated) Build workflow triggers.

        :default: "{ pullRequest: {}, workflowDispatch: {} }"

        :deprecated: - Use ``buildWorkflowOptions.workflowTriggers``

        :stability: deprecated
        '''
        result = self._values.get("build_workflow_triggers")
        return typing.cast(typing.Optional[_projen_github_workflows_04054675.Triggers], result)

    @builtins.property
    def bump_package(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ``commit-and-tag-version`` compatible package used to bump the package version, as a dependency string.

        This can be any compatible package version, including the deprecated ``standard-version@9``.

        :default: - A recent version of "commit-and-tag-version"

        :stability: experimental
        '''
        result = self._values.get("bump_package")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bundled_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of dependencies to bundle into this module.

        These modules will be
        added both to the ``dependencies`` section and ``bundledDependencies`` section of
        your ``package.json``.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :stability: experimental
        '''
        result = self._values.get("bundled_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bundler_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.BundlerOptions]:
        '''(experimental) Options for ``Bundler``.

        :stability: experimental
        '''
        result = self._values.get("bundler_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.BundlerOptions], result)

    @builtins.property
    def bun_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of Bun to use if using Bun as a package manager.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("bun_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def check_licenses(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.LicenseCheckerOptions]:
        '''(experimental) Configure which licenses should be deemed acceptable for use by dependencies.

        This setting will cause the build to fail, if any prohibited or not allowed licenses ares encountered.

        :default: - no license checks are run during the build and all licenses will be accepted

        :stability: experimental
        '''
        result = self._values.get("check_licenses")
        return typing.cast(typing.Optional[_projen_javascript_04054675.LicenseCheckerOptions], result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: - true, but false for subprojects

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_artifact_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.CodeArtifactOptions]:
        '''(experimental) Options for npm packages using AWS CodeArtifact.

        This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("code_artifact_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.CodeArtifactOptions], result)

    @builtins.property
    def code_cov(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v4 A secret is required for private repos. Configured with ``@codeCovTokenSecret``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("code_cov")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_cov_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories.

        :default: - if this option is not specified, only public repositories are supported

        :stability: experimental
        '''
        result = self._values.get("code_cov_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def commit_generated(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to commit the managed files by default.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("commit_generated")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def compat(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically run API compatibility test against the latest version published to npm after compilation.

        - You can manually run compatibility tests using ``yarn compat`` if this feature is disabled.
        - You can ignore compatibility failures by adding lines to a ".compatignore" file.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("compat")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def compat_ignore(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the ignore file for API compatibility tests.

        :default: ".compatignore"

        :stability: experimental
        '''
        result = self._values.get("compat_ignore")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compress_assembly(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Emit a compressed version of the assembly.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("compress_assembly")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def copyright_owner(self) -> typing.Optional[builtins.str]:
        '''(experimental) License copyright owner.

        :default: - defaults to the value of authorName or "" if ``authorName`` is undefined.

        :stability: experimental
        '''
        result = self._values.get("copyright_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copyright_period(self) -> typing.Optional[builtins.str]:
        '''(experimental) The copyright years to put in the LICENSE file.

        :default: - current year

        :stability: experimental
        '''
        result = self._values.get("copyright_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_release_branch(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the main release branch.

        :default: "main"

        :stability: experimental
        '''
        result = self._values.get("default_release_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependabot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use dependabot to handle dependency upgrades.

        Cannot be used in conjunction with ``depsUpgrade``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dependabot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dependabot_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.DependabotOptions]:
        '''(experimental) Options for dependabot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("dependabot_options")
        return typing.cast(typing.Optional[_projen_github_04054675.DependabotOptions], result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Runtime dependencies of this module.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deps_upgrade(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use tasks and github workflows to handle dependency upgrades.

        Cannot be used in conjunction with ``dependabot``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deps_upgrade_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.UpgradeDependenciesOptions]:
        '''(experimental) Options for ``UpgradeDependencies``.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.UpgradeDependenciesOptions], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description is just a string that helps people understand the purpose of the package.

        It can be used when searching for packages in a package manager as well.
        See https://classic.yarnpkg.com/en/docs/package-json/#toc-description

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Build dependencies for this module.

        These dependencies will only be
        available in your build environment but will not be fetched when this
        module is consumed.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("dev_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def disable_tsconfig(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("disable_tsconfig")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def disable_tsconfig_dev(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Do not generate a ``tsconfig.dev.json`` file.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("disable_tsconfig_dev")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docgen(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Docgen by Typedoc.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("docgen")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docgen_file_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) File path for generated docs.

        :default: "API.md"

        :stability: experimental
        '''
        result = self._values.get("docgen_file_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def docs_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) Docs directory.

        :default: "docs"

        :stability: experimental
        '''
        result = self._values.get("docs_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dotnet(self) -> typing.Optional[_projen_cdk_04054675.JsiiDotNetTarget]:
        '''
        :deprecated: use ``publishToNuget``

        :stability: deprecated
        '''
        result = self._values.get("dotnet")
        return typing.cast(typing.Optional[_projen_cdk_04054675.JsiiDotNetTarget], result)

    @builtins.property
    def entrypoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json.

        :default: "lib/index.js"

        :stability: experimental
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint_types(self) -> typing.Optional[builtins.str]:
        '''(experimental) The .d.ts file that includes the type declarations for this module.

        :default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)

        :stability: experimental
        '''
        result = self._values.get("entrypoint_types")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eslint(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup eslint.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("eslint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def eslint_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.EslintOptions]:
        '''(experimental) Eslint options.

        :default: - opinionated default options

        :stability: experimental
        '''
        result = self._values.get("eslint_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.EslintOptions], result)

    @builtins.property
    def exclude_typescript(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Accepts a list of glob patterns. Files matching any of those patterns will be excluded from the TypeScript compiler input.

        By default, jsii will include all *.ts files (except .d.ts files) in the TypeScript compiler input.
        This can be problematic for example when the package's build or test procedure generates .ts files
        that cannot be compiled with jsii's compiler settings.

        :stability: experimental
        '''
        result = self._values.get("exclude_typescript")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def github(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable GitHub integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github_options(self) -> typing.Optional[_projen_github_04054675.GitHubOptions]:
        '''(experimental) Options for GitHub integration.

        :default: - see GitHubOptions

        :stability: experimental
        '''
        result = self._values.get("github_options")
        return typing.cast(typing.Optional[_projen_github_04054675.GitHubOptions], result)

    @builtins.property
    def gitignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional entries to .gitignore.

        :stability: experimental
        '''
        result = self._values.get("gitignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def git_ignore_options(self) -> typing.Optional[_projen_04054675.IgnoreFileOptions]:
        '''(experimental) Configuration options for .gitignore file.

        :stability: experimental
        '''
        result = self._values.get("git_ignore_options")
        return typing.cast(typing.Optional[_projen_04054675.IgnoreFileOptions], result)

    @builtins.property
    def git_options(self) -> typing.Optional[_projen_04054675.GitOptions]:
        '''(experimental) Configuration options for git.

        :stability: experimental
        '''
        result = self._values.get("git_options")
        return typing.cast(typing.Optional[_projen_04054675.GitOptions], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Homepage / Website.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jest(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup jest unit tests.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("jest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def jest_options(self) -> typing.Optional[_projen_javascript_04054675.JestOptions]:
        '''(experimental) Jest options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("jest_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.JestOptions], result)

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement of ``publib`` which is used to publish modules to npm.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jsii_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of the jsii compiler to use.

        Set to "*" if you want to manually manage the version of jsii in your
        project by managing updates to ``package.json`` on your own.

        NOTE: The jsii compiler releases since 5.0.0 are not semantically versioned
        and should remain on the same minor, so we recommend using a ``~`` dependency
        (e.g. ``~5.0.0``).

        :default: "~5.6.0"

        :stability: experimental
        :pjnew: "~5.8.0"
        '''
        result = self._values.get("jsii_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Keywords to include in ``package.json``.

        :stability: experimental
        '''
        result = self._values.get("keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def libdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript  artifacts output directory.

        :default: "lib"

        :stability: experimental
        '''
        result = self._values.get("libdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License's SPDX identifier.

        See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses.
        Use the ``licensed`` option if you want to no license to be specified.

        :default: "Apache-2.0"

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def licensed(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates if a license should be added.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("licensed")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def logging(self) -> typing.Optional[_projen_04054675.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[_projen_04054675.LoggerOptions], result)

    @builtins.property
    def major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Major version to release from the default branch.

        If this is specified, we bump the latest version of this major version line.
        If not specified, we bump the global latest version.

        :default: - Major version is not enforced.

        :stability: experimental
        '''
        result = self._values.get("major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The maximum node version supported by this package.

        Most projects should not use this option.
        The value indicates that the package is incompatible with any newer versions of node.
        This requirement is enforced via the engines field.

        You will normally not need to set this option.
        Consider this option only if your package is known to not function with newer versions of node.

        :default: - no maximum version is enforced

        :stability: experimental
        '''
        result = self._values.get("max_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether mergify should be enabled on this repository or not.

        :default: true

        :deprecated: use ``githubOptions.mergify`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.MergifyOptions]:
        '''(deprecated) Options for mergify.

        :default: - default options

        :deprecated: use ``githubOptions.mergifyOptions`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional[_projen_github_04054675.MergifyOptions], result)

    @builtins.property
    def min_major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Minimal Major version to release.

        This can be useful to set to 1, as breaking changes before the 1.x major
        release are not incrementing the major version number.

        Can not be set together with ``majorVersion``.

        :default: - No minimum version is being enforced

        :stability: experimental
        '''
        result = self._values.get("min_major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The minimum node version required by this package to function.

        Most projects should not use this option.
        The value indicates that the package is incompatible with any older versions of node.
        This requirement is enforced via the engines field.

        You will normally not need to set this option, even if your package is incompatible with EOL versions of node.
        Consider this option only if your package depends on a specific feature, that is not available in other LTS versions.
        Setting this option has very high impact on the consumers of your package,
        as package managers will actively prevent usage with node versions you have marked as incompatible.

        To change the node version of your CI/CD workflows, use ``workflowNodeVersion``.

        :default: - no minimum version is enforced

        :stability: experimental
        '''
        result = self._values.get("min_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mutable_build(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically update files modified during builds to pull-request branches.

        This means
        that any files synthesized by projen or e.g. test snapshots will always be up-to-date
        before a PR is merged.

        Implies that PR builds do not have anti-tamper checks.

        :default: true

        :deprecated: - Use ``buildWorkflowOptions.mutableBuild``

        :stability: deprecated
        '''
        result = self._values.get("mutable_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def next_version_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) A shell command to control the next version to release.

        If present, this shell command will be run before the bump is executed, and
        it determines what version to release. It will be executed in the following
        environment:

        - Working directory: the project directory.
        - ``$VERSION``: the current version. Looks like ``1.2.3``.
        - ``$LATEST_TAG``: the most recent tag. Looks like ``prefix-v1.2.3``, or may be unset.
        - ``$SUGGESTED_BUMP``: the suggested bump action based on commits. One of ``major|minor|patch|none``.

        The command should print one of the following to ``stdout``:

        - Nothing: the next version number will be determined based on commit history.
        - ``x.y.z``: the next version number will be ``x.y.z``.
        - ``major|minor|patch``: the next version number will be the current version number
          with the indicated component bumped.

        This setting cannot be specified together with ``minMajorVersion``; the invoked
        script can be used to achieve the effects of ``minMajorVersion``.

        :default: - The next version will be determined based on the commit history and project settings.

        :stability: experimental
        '''
        result = self._values.get("next_version_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_access(self) -> typing.Optional[_projen_javascript_04054675.NpmAccess]:
        '''(experimental) Access level of the npm package.

        :default:

        - for scoped packages (e.g. ``foo@bar``), the default is
        ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is
        ``NpmAccess.PUBLIC``.

        :stability: experimental
        '''
        result = self._values.get("npm_access")
        return typing.cast(typing.Optional[_projen_javascript_04054675.NpmAccess], result)

    @builtins.property
    def npm_dist_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) The npmDistTag to use when publishing from the default branch.

        To set the npm dist-tag for release branches, set the ``npmDistTag`` property
        for each branch.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("npm_dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npmignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) Additional entries to .npmignore.

        :deprecated: - use ``project.addPackageIgnore``

        :stability: deprecated
        '''
        result = self._values.get("npmignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def npmignore_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("npmignore_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def npm_ignore_options(self) -> typing.Optional[_projen_04054675.IgnoreFileOptions]:
        '''(experimental) Configuration options for .npmignore file.

        :stability: experimental
        '''
        result = self._values.get("npm_ignore_options")
        return typing.cast(typing.Optional[_projen_04054675.IgnoreFileOptions], result)

    @builtins.property
    def npm_provenance(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Should provenance statements be generated when the package is published.

        A supported package manager is required to publish a package with npm provenance statements and
        you will need to use a supported CI/CD provider.

        Note that the projen ``Release`` and ``Publisher`` components are using ``publib`` to publish packages,
        which is using npm internally and supports provenance statements independently of the package manager used.

        :default: - true for public packages, false otherwise

        :stability: experimental
        '''
        result = self._values.get("npm_provenance")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def npm_registry(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The host name of the npm registry to publish to.

        Cannot be set together with ``npmRegistryUrl``.

        :deprecated: use ``npmRegistryUrl`` instead

        :stability: deprecated
        '''
        result = self._values.get("npm_registry")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_registry_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The base URL of the npm package registry.

        Must be a URL (e.g. start with "https://" or "http://")

        :default: "https://registry.npmjs.org"

        :stability: experimental
        '''
        result = self._values.get("npm_registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the NPM token to use when publishing packages.

        :default: "NPM_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("npm_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project. Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        subprojects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def package(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``).

        :default: true

        :stability: experimental
        '''
        result = self._values.get("package")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def package_manager(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.NodePackageManager]:
        '''(experimental) The Node Package Manager used to execute scripts.

        :default: NodePackageManager.YARN_CLASSIC

        :stability: experimental
        '''
        result = self._values.get("package_manager")
        return typing.cast(typing.Optional[_projen_javascript_04054675.NodePackageManager], result)

    @builtins.property
    def package_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The "name" in package.json.

        :default: - defaults to project name

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("package_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[_projen_04054675.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[_projen_04054675.Project], result)

    @builtins.property
    def peer_dependency_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.PeerDependencyOptions]:
        '''(experimental) Options for ``peerDeps``.

        :stability: experimental
        '''
        result = self._values.get("peer_dependency_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.PeerDependencyOptions], result)

    @builtins.property
    def peer_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Peer dependencies for this module.

        Dependencies listed here are required to
        be installed (and satisfied) by the *consumer* of this library. Using peer
        dependencies allows you to ensure that only a single module of a certain
        library exists in the ``node_modules`` tree of your consumers.

        Note that prior to npm@7, peer dependencies are *not* automatically
        installed, which means that adding peer dependencies to a library will be a
        breaking change for your customers.

        Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is
        enabled by default), projen will automatically add a dev dependency with a
        pinned version for each peer dependency. This will ensure that you build &
        test your module against the lowest peer version required.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("peer_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pnpm_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of PNPM to use if using PNPM as a package manager.

        :default: "9"

        :stability: experimental
        '''
        result = self._values.get("pnpm_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_build_steps(
        self,
    ) -> typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]]:
        '''(experimental) Steps to execute after build as part of the release workflow.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]], result)

    @builtins.property
    def prerelease(self) -> typing.Optional[builtins.str]:
        '''(experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre").

        :default: - normal semantic versions

        :stability: experimental
        '''
        result = self._values.get("prerelease")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prettier(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup prettier.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("prettier")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def prettier_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.PrettierOptions]:
        '''(experimental) Prettier options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("prettier_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.PrettierOptions], result)

    @builtins.property
    def project_type(self) -> typing.Optional[_projen_04054675.ProjectType]:
        '''(deprecated) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :deprecated: no longer supported at the base project level

        :stability: deprecated
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[_projen_04054675.ProjectType], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_credentials(
        self,
    ) -> typing.Optional[_projen_github_04054675.GithubCredentials]:
        '''(experimental) Choose a method of providing GitHub API access for projen workflows.

        :default: - use a personal access token named PROJEN_GITHUB_TOKEN

        :stability: experimental
        '''
        result = self._values.get("projen_credentials")
        return typing.cast(typing.Optional[_projen_github_04054675.GithubCredentials], result)

    @builtins.property
    def projen_dev_dependency(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates of "projen" should be installed as a devDependency.

        :default: - true if not a subproject

        :stability: experimental
        '''
        result = self._values.get("projen_dev_dependency")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation.

        :default: - true if projenrcJson is false

        :stability: experimental
        '''
        result = self._values.get("projenrc_js")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(
        self,
    ) -> typing.Optional[_projen_04054675.ProjenrcJsonOptions]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[_projen_04054675.ProjenrcJsonOptions], result)

    @builtins.property
    def projenrc_js_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.js.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_js_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.ProjenrcOptions], result)

    @builtins.property
    def projenrc_ts(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use TypeScript for your projenrc file (``.projenrc.ts``).

        :default: false

        :stability: experimental
        :pjnew: true
        '''
        result = self._values.get("projenrc_ts")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_ts_options(
        self,
    ) -> typing.Optional[_projen_typescript_04054675.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.ts.

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts_options")
        return typing.cast(typing.Optional[_projen_typescript_04054675.ProjenrcOptions], result)

    @builtins.property
    def projen_token_secret(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows.

        This token needs to have the ``repo``, ``workflows``
        and ``packages`` scope.

        :default: "PROJEN_GITHUB_TOKEN"

        :deprecated: use ``projenCredentials``

        :stability: deprecated
        '''
        result = self._values.get("projen_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of projen to install.

        :default: - Defaults to the latest version.

        :stability: experimental
        '''
        result = self._values.get("projen_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_dry_run(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Instead of actually publishing to package managers, just print the publishing command.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_dry_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_tasks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define publishing tasks that can be executed manually as well as workflows.

        Normally, publishing only happens within automated workflows. Enable this
        in order to create a publishing task for each publishing activity.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_tasks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_to_go(self) -> typing.Optional[_projen_cdk_04054675.JsiiGoTarget]:
        '''(experimental) Publish Go bindings to a git repository.

        :default: - no publishing

        :stability: experimental
        '''
        result = self._values.get("publish_to_go")
        return typing.cast(typing.Optional[_projen_cdk_04054675.JsiiGoTarget], result)

    @builtins.property
    def publish_to_maven(self) -> typing.Optional[_projen_cdk_04054675.JsiiJavaTarget]:
        '''(experimental) Publish to maven.

        :default: - no publishing

        :stability: experimental
        '''
        result = self._values.get("publish_to_maven")
        return typing.cast(typing.Optional[_projen_cdk_04054675.JsiiJavaTarget], result)

    @builtins.property
    def publish_to_nuget(
        self,
    ) -> typing.Optional[_projen_cdk_04054675.JsiiDotNetTarget]:
        '''(experimental) Publish to NuGet.

        :default: - no publishing

        :stability: experimental
        '''
        result = self._values.get("publish_to_nuget")
        return typing.cast(typing.Optional[_projen_cdk_04054675.JsiiDotNetTarget], result)

    @builtins.property
    def publish_to_pypi(self) -> typing.Optional[_projen_cdk_04054675.JsiiPythonTarget]:
        '''(experimental) Publish to pypi.

        :default: - no publishing

        :stability: experimental
        '''
        result = self._values.get("publish_to_pypi")
        return typing.cast(typing.Optional[_projen_cdk_04054675.JsiiPythonTarget], result)

    @builtins.property
    def pull_request_template(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include a GitHub pull request template.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("pull_request_template")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_request_template_contents(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The contents of the pull request template.

        :default: - default content

        :stability: experimental
        '''
        result = self._values.get("pull_request_template_contents")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def python(self) -> typing.Optional[_projen_cdk_04054675.JsiiPythonTarget]:
        '''
        :deprecated: use ``publishToPyPi``

        :stability: deprecated
        '''
        result = self._values.get("python")
        return typing.cast(typing.Optional[_projen_cdk_04054675.JsiiPythonTarget], result)

    @builtins.property
    def readme(self) -> typing.Optional["ReadmeOptions"]:
        '''Configuration of the README.md file.'''
        result = self._values.get("readme")
        return typing.cast(typing.Optional["ReadmeOptions"], result)

    @builtins.property
    def releasable_commits(self) -> typing.Optional[_projen_04054675.ReleasableCommits]:
        '''(experimental) Find commits that should be considered releasable Used to decide if a release is required.

        :default: ReleasableCommits.everyCommit()

        :stability: experimental
        '''
        result = self._values.get("releasable_commits")
        return typing.cast(typing.Optional[_projen_04054675.ReleasableCommits], result)

    @builtins.property
    def release(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add release management to this project.

        :default: - true (false for subprojects)

        :stability: experimental
        '''
        result = self._values.get("release")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_branches(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _projen_release_04054675.BranchOptions]]:
        '''(experimental) Defines additional release branches.

        A workflow will be created for each
        release branch which will publish releases from commits in this branch.
        Each release branch *must* be assigned a major version number which is used
        to enforce that versions published from that branch always use that major
        version. If multiple branches are used, the ``majorVersion`` field must also
        be provided for the default branch.

        :default:

        - no additional branches are used for release. you can use
        ``addBranch()`` to add additional branches.

        :stability: experimental
        '''
        result = self._values.get("release_branches")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _projen_release_04054675.BranchOptions]], result)

    @builtins.property
    def release_every_commit(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``.

        :default: true

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.continuous()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_every_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create a github issue on every failed publishing task.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The label to apply to issues indicating publish failures.

        Only applies if ``releaseFailureIssue`` is true.

        :default: "failed-release"

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_schedule(self) -> typing.Optional[builtins.str]:
        '''(deprecated) CRON schedule to trigger new releases.

        :default: - no scheduled releases

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.scheduled()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_tag_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Automatically add the given prefix to release tags.

        Useful if you are releasing on multiple branches with overlapping version numbers.
        Note: this prefix is used to detect the latest tagged version
        when bumping, so if you change this on a project with an existing version
        history, you may need to manually tag your latest release
        with the new prefix.

        :default: "v"

        :stability: experimental
        '''
        result = self._values.get("release_tag_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_to_npm(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically release to npm when new versions are introduced.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_to_npm")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_trigger(
        self,
    ) -> typing.Optional[_projen_release_04054675.ReleaseTrigger]:
        '''(experimental) The release trigger to use.

        :default: - Continuous releases (``ReleaseTrigger.continuous()``)

        :stability: experimental
        '''
        result = self._values.get("release_trigger")
        return typing.cast(typing.Optional[_projen_release_04054675.ReleaseTrigger], result)

    @builtins.property
    def release_workflow(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) DEPRECATED: renamed to ``release``.

        :default: - true if not a subproject

        :deprecated: see ``release``.

        :stability: deprecated
        '''
        result = self._values.get("release_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_workflow_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the default release workflow.

        :default: "release"

        :stability: experimental
        '''
        result = self._values.get("release_workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_workflow_setup_steps(
        self,
    ) -> typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]]:
        '''(experimental) A set of workflow steps to execute in order to setup the workflow container.

        :stability: experimental
        '''
        result = self._values.get("release_workflow_setup_steps")
        return typing.cast(typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]], result)

    @builtins.property
    def renovatebot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use renovatebot to handle dependency upgrades.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("renovatebot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def renovatebot_options(
        self,
    ) -> typing.Optional[_projen_04054675.RenovatebotOptions]:
        '''(experimental) Options for renovatebot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("renovatebot_options")
        return typing.cast(typing.Optional[_projen_04054675.RenovatebotOptions], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) The repository is the location where the actual code for your package lives.

        See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.

        :stability: experimental
        '''
        result = self._values.get("repository_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rootdir(self) -> typing.Optional[builtins.str]:
        '''
        :default: "."

        :stability: experimental
        '''
        result = self._values.get("rootdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sample_code(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sample_code")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def scoped_packages_options(
        self,
    ) -> typing.Optional[typing.List[_projen_javascript_04054675.ScopedPackagesOptions]]:
        '''(experimental) Options for privately hosted scoped packages.

        :default: - fetch all scoped packages from the public npm registry

        :stability: experimental
        '''
        result = self._values.get("scoped_packages_options")
        return typing.cast(typing.Optional[typing.List[_projen_javascript_04054675.ScopedPackagesOptions]], result)

    @builtins.property
    def scripts(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(deprecated) npm scripts to include.

        If a script has the same name as a standard script,
        the standard script will be overwritten.
        Also adds the script as a task.

        :default: {}

        :deprecated: use ``project.addTask()`` or ``package.setScript()``

        :stability: deprecated
        '''
        result = self._values.get("scripts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def srcdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript sources directory.

        :default: "src"

        :stability: experimental
        '''
        result = self._values.get("srcdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stability(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Stability.

        :stability: experimental
        '''
        result = self._values.get("stability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stale(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto-close of stale issues and pull request.

        See ``staleOptions`` for options.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("stale")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_options(self) -> typing.Optional[_projen_github_04054675.StaleOptions]:
        '''(experimental) Auto-close stale issues and pull requests.

        To disable set ``stale`` to ``false``.

        :default: - see defaults in ``StaleOptions``

        :stability: experimental
        '''
        result = self._values.get("stale_options")
        return typing.cast(typing.Optional[_projen_github_04054675.StaleOptions], result)

    @builtins.property
    def testdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Jest tests directory.

        Tests files should be named ``xxx.test.ts``.
        If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``),
        then tests are going to be compiled into ``lib/`` and executed as javascript.
        If the test directory is outside of ``src``, then we configure jest to
        compile the code in-memory.

        :default: "test"

        :stability: experimental
        '''
        result = self._values.get("testdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tsconfig(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions]:
        '''(experimental) Custom TSConfig.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("tsconfig")
        return typing.cast(typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions]:
        '''(experimental) Custom tsconfig options for the development tsconfig.json file (used for testing).

        :default: - use the production tsconfig options

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev")
        return typing.cast(typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev_file(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the development tsconfig.json file.

        :default: "tsconfig.dev.json"

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ts_jest_options(
        self,
    ) -> typing.Optional[_projen_typescript_04054675.TsJestOptions]:
        '''(experimental) Options for ts-jest.

        :stability: experimental
        '''
        result = self._values.get("ts_jest_options")
        return typing.cast(typing.Optional[_projen_typescript_04054675.TsJestOptions], result)

    @builtins.property
    def typescript_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) TypeScript version to use.

        NOTE: Typescript is not semantically versioned and should remain on the
        same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``).

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("typescript_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def versionrc_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Custom configuration used when creating changelog with commit-and-tag-version package.

        Given values either append to default configuration or overwrite values in it.

        :default: - standard configuration applicable for GitHub repositories

        :stability: experimental
        '''
        result = self._values.get("versionrc_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def vscode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable VSCode integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("vscode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def workflow_bootstrap_steps(
        self,
    ) -> typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]]:
        '''(experimental) Workflow steps to use in order to bootstrap this repo.

        :default: "yarn install --frozen-lockfile && yarn projen"

        :stability: experimental
        '''
        result = self._values.get("workflow_bootstrap_steps")
        return typing.cast(typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]], result)

    @builtins.property
    def workflow_container_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Container image to use for GitHub workflows.

        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("workflow_container_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_git_identity(
        self,
    ) -> typing.Optional[_projen_github_04054675.GitIdentity]:
        '''(experimental) The git identity to use in workflows.

        :default: - GitHub Actions

        :stability: experimental
        '''
        result = self._values.get("workflow_git_identity")
        return typing.cast(typing.Optional[_projen_github_04054675.GitIdentity], result)

    @builtins.property
    def workflow_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The node version used in GitHub Actions workflows.

        Always use this option if your GitHub Actions workflows require a specific to run.

        :default: - ``minNodeVersion`` if set, otherwise ``lts/*``.

        :stability: experimental
        '''
        result = self._values.get("workflow_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_package_cache(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable Node.js package cache in GitHub workflows.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("workflow_package_cache")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def workflow_runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        :description: Defines a target Runner by labels
        :throws: {Error} if both ``runsOn`` and ``runsOnGroup`` are specified
        '''
        result = self._values.get("workflow_runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def workflow_runs_on_group(
        self,
    ) -> typing.Optional[_projen_04054675.GroupRunnerOptions]:
        '''(experimental) Github Runner Group selection options.

        :stability: experimental
        :description: Defines a target Runner Group by name and/or labels
        :throws: {Error} if both ``runsOn`` and ``runsOnGroup`` are specified
        '''
        result = self._values.get("workflow_runs_on_group")
        return typing.cast(typing.Optional[_projen_04054675.GroupRunnerOptions], result)

    @builtins.property
    def yarn_berry_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.YarnBerryOptions]:
        '''(experimental) Options for Yarn Berry.

        :default: - Yarn Berry v4 with all default options

        :stability: experimental
        '''
        result = self._values.get("yarn_berry_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.YarnBerryOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JsiiProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NpmPackage(
    _projen_typescript_04054675.TypeScriptProject,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-modules.NpmPackage",
):
    '''A NPM/node package in TypeScript.

    :pjid: npm-package
    '''

    def __init__(
        self,
        *,
        code_owners: typing.Sequence[builtins.str],
        name: builtins.str,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        artifacts_directory: typing.Optional[builtins.str] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        biome: typing.Optional[builtins.bool] = None,
        biome_options: typing.Optional[typing.Union[_projen_javascript_04054675.BiomeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_options: typing.Optional[typing.Union[_projen_javascript_04054675.BuildWorkflowOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        build_workflow_triggers: typing.Optional[typing.Union[_projen_github_workflows_04054675.Triggers, typing.Dict[builtins.str, typing.Any]]] = None,
        bump_package: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        bundler_options: typing.Optional[typing.Union[_projen_javascript_04054675.BundlerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bun_version: typing.Optional[builtins.str] = None,
        check_licenses: typing.Optional[typing.Union[_projen_javascript_04054675.LicenseCheckerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        clobber: typing.Optional[builtins.bool] = None,
        code_artifact_options: typing.Optional[typing.Union[_projen_javascript_04054675.CodeArtifactOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        commit_generated: typing.Optional[builtins.bool] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        default_release_branch: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[typing.Union[_projen_github_04054675.DependabotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[typing.Union[_projen_javascript_04054675.UpgradeDependenciesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        disable_tsconfig_dev: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[typing.Union[_projen_javascript_04054675.EslintOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        homepage: typing.Optional[builtins.str] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[typing.Union[_projen_javascript_04054675.JestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        libdir: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        major_version: typing.Optional[jsii.Number] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        min_major_version: typing.Optional[jsii.Number] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        next_version_command: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[_projen_javascript_04054675.NpmAccess] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        npm_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        npm_provenance: typing.Optional[builtins.bool] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        outdir: typing.Optional[builtins.str] = None,
        package: typing.Optional[builtins.bool] = None,
        package_manager: typing.Optional[_projen_javascript_04054675.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        peer_dependency_options: typing.Optional[typing.Union[_projen_javascript_04054675.PeerDependencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pnpm_version: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[typing.Union[_projen_javascript_04054675.PrettierOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_type: typing.Optional[_projen_04054675.ProjectType] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        readme: typing.Optional[typing.Union["ReadmeOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        releasable_commits: typing.Optional[_projen_04054675.ReleasableCommits] = None,
        release: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, typing.Union[_projen_release_04054675.BranchOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_trigger: typing.Optional[_projen_release_04054675.ReleaseTrigger] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        scoped_packages_options: typing.Optional[typing.Sequence[typing.Union[_projen_javascript_04054675.ScopedPackagesOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        srcdir: typing.Optional[builtins.str] = None,
        stability: typing.Optional[builtins.str] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        ts_jest_options: typing.Optional[typing.Union[_projen_typescript_04054675.TsJestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        vscode: typing.Optional[builtins.bool] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_git_identity: typing.Optional[typing.Union[_projen_github_04054675.GitIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        workflow_package_cache: typing.Optional[builtins.bool] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_runs_on_group: typing.Optional[typing.Union[_projen_04054675.GroupRunnerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        yarn_berry_options: typing.Optional[typing.Union[_projen_javascript_04054675.YarnBerryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param code_owners: List of teams used to generate the CODEOWNERS file.
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Is the author an organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param biome: (experimental) Setup Biome. Default: false
        :param biome_options: (experimental) Biome options. Default: - default options
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_options: (experimental) Options for PR build workflow.
        :param build_workflow_triggers: (deprecated) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bump_package: (experimental) The ``commit-and-tag-version`` compatible package used to bump the package version, as a dependency string. This can be any compatible package version, including the deprecated ``standard-version@9``. Default: - A recent version of "commit-and-tag-version"
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param bun_version: (experimental) The version of Bun to use if using Bun as a package manager. Default: "latest"
        :param check_licenses: (experimental) Configure which licenses should be deemed acceptable for use by dependencies. This setting will cause the build to fail, if any prohibited or not allowed licenses ares encountered. Default: - no license checks are run during the build and all licenses will be accepted
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: - true, but false for subprojects
        :param code_artifact_options: (experimental) Options for npm packages using AWS CodeArtifact. This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact Default: - undefined
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v4 A secret is required for private repos. Configured with ``@codeCovTokenSecret``. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param deps_upgrade: (experimental) Use tasks and github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for ``UpgradeDependencies``. Default: - default options
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param disable_tsconfig_dev: (experimental) Do not generate a ``tsconfig.dev.json`` file. Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json. Default: "lib/index.js"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param homepage: (experimental) Package's Homepage / Website.
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param max_node_version: (experimental) The maximum node version supported by this package. Most projects should not use this option. The value indicates that the package is incompatible with any newer versions of node. This requirement is enforced via the engines field. You will normally not need to set this option. Consider this option only if your package is known to not function with newer versions of node. Default: - no maximum version is enforced
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param min_major_version: (experimental) Minimal Major version to release. This can be useful to set to 1, as breaking changes before the 1.x major release are not incrementing the major version number. Can not be set together with ``majorVersion``. Default: - No minimum version is being enforced
        :param min_node_version: (experimental) The minimum node version required by this package to function. Most projects should not use this option. The value indicates that the package is incompatible with any older versions of node. This requirement is enforced via the engines field. You will normally not need to set this option, even if your package is incompatible with EOL versions of node. Consider this option only if your package depends on a specific feature, that is not available in other LTS versions. Setting this option has very high impact on the consumers of your package, as package managers will actively prevent usage with node versions you have marked as incompatible. To change the node version of your CI/CD workflows, use ``workflowNodeVersion``. Default: - no minimum version is enforced
        :param mutable_build: (deprecated) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param next_version_command: (experimental) A shell command to control the next version to release. If present, this shell command will be run before the bump is executed, and it determines what version to release. It will be executed in the following environment: - Working directory: the project directory. - ``$VERSION``: the current version. Looks like ``1.2.3``. - ``$LATEST_TAG``: the most recent tag. Looks like ``prefix-v1.2.3``, or may be unset. - ``$SUGGESTED_BUMP``: the suggested bump action based on commits. One of ``major|minor|patch|none``. The command should print one of the following to ``stdout``: - Nothing: the next version number will be determined based on commit history. - ``x.y.z``: the next version number will be ``x.y.z``. - ``major|minor|patch``: the next version number will be the current version number with the indicated component bumped. This setting cannot be specified together with ``minMajorVersion``; the invoked script can be used to achieve the effects of ``minMajorVersion``. Default: - The next version will be determined based on the commit history and project settings.
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param npm_ignore_options: (experimental) Configuration options for .npmignore file.
        :param npm_provenance: (experimental) Should provenance statements be generated when the package is published. A supported package manager is required to publish a package with npm provenance statements and you will need to use a supported CI/CD provider. Note that the projen ``Release`` and ``Publisher`` components are using ``publib`` to publish packages, which is using npm internally and supports provenance statements independently of the package manager used. Default: - true for public packages, false otherwise
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other subprojects. Default: "."
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN_CLASSIC
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param pnpm_version: (experimental) The version of PNPM to use if using PNPM as a package manager. Default: "9"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: - true if not a subproject
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param readme: Configuration of the README.md file.
        :param releasable_commits: (experimental) Find commits that should be considered releasable Used to decide if a release is required. Default: ReleasableCommits.everyCommit()
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: "v"
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param scoped_packages_options: (experimental) Options for privately hosted scoped packages. Default: - fetch all scoped packages from the public npm registry
        :param scripts: (deprecated) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Also adds the script as a task. Default: {}
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param stability: (experimental) Package's Stability.
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param ts_jest_options: (experimental) Options for ts-jest.
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with commit-and-tag-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version used in GitHub Actions workflows. Always use this option if your GitHub Actions workflows require a specific to run. Default: - ``minNodeVersion`` if set, otherwise ``lts/*``.
        :param workflow_package_cache: (experimental) Enable Node.js package cache in GitHub workflows. Default: false
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param workflow_runs_on_group: (experimental) Github Runner Group selection options.
        :param yarn_berry_options: (experimental) Options for Yarn Berry. Default: - Yarn Berry v4 with all default options
        '''
        options = NpmPackageOptions(
            code_owners=code_owners,
            name=name,
            allow_library_dependencies=allow_library_dependencies,
            artifacts_directory=artifacts_directory,
            author_email=author_email,
            author_name=author_name,
            author_organization=author_organization,
            author_url=author_url,
            auto_approve_options=auto_approve_options,
            auto_approve_upgrades=auto_approve_upgrades,
            auto_detect_bin=auto_detect_bin,
            auto_merge=auto_merge,
            auto_merge_options=auto_merge_options,
            bin=bin,
            biome=biome,
            biome_options=biome_options,
            bugs_email=bugs_email,
            bugs_url=bugs_url,
            build_workflow=build_workflow,
            build_workflow_options=build_workflow_options,
            build_workflow_triggers=build_workflow_triggers,
            bump_package=bump_package,
            bundled_deps=bundled_deps,
            bundler_options=bundler_options,
            bun_version=bun_version,
            check_licenses=check_licenses,
            clobber=clobber,
            code_artifact_options=code_artifact_options,
            code_cov=code_cov,
            code_cov_token_secret=code_cov_token_secret,
            commit_generated=commit_generated,
            copyright_owner=copyright_owner,
            copyright_period=copyright_period,
            default_release_branch=default_release_branch,
            dependabot=dependabot,
            dependabot_options=dependabot_options,
            deps=deps,
            deps_upgrade=deps_upgrade,
            deps_upgrade_options=deps_upgrade_options,
            description=description,
            dev_container=dev_container,
            dev_deps=dev_deps,
            disable_tsconfig=disable_tsconfig,
            disable_tsconfig_dev=disable_tsconfig_dev,
            docgen=docgen,
            docs_directory=docs_directory,
            entrypoint=entrypoint,
            entrypoint_types=entrypoint_types,
            eslint=eslint,
            eslint_options=eslint_options,
            github=github,
            github_options=github_options,
            gitignore=gitignore,
            git_ignore_options=git_ignore_options,
            git_options=git_options,
            gitpod=gitpod,
            homepage=homepage,
            jest=jest,
            jest_options=jest_options,
            jsii_release_version=jsii_release_version,
            keywords=keywords,
            libdir=libdir,
            license=license,
            licensed=licensed,
            logging=logging,
            major_version=major_version,
            max_node_version=max_node_version,
            mergify=mergify,
            mergify_options=mergify_options,
            min_major_version=min_major_version,
            min_node_version=min_node_version,
            mutable_build=mutable_build,
            next_version_command=next_version_command,
            npm_access=npm_access,
            npm_dist_tag=npm_dist_tag,
            npmignore=npmignore,
            npmignore_enabled=npmignore_enabled,
            npm_ignore_options=npm_ignore_options,
            npm_provenance=npm_provenance,
            npm_registry=npm_registry,
            npm_registry_url=npm_registry_url,
            npm_token_secret=npm_token_secret,
            outdir=outdir,
            package=package,
            package_manager=package_manager,
            package_name=package_name,
            parent=parent,
            peer_dependency_options=peer_dependency_options,
            peer_deps=peer_deps,
            pnpm_version=pnpm_version,
            post_build_steps=post_build_steps,
            prerelease=prerelease,
            prettier=prettier,
            prettier_options=prettier_options,
            project_type=project_type,
            projen_command=projen_command,
            projen_credentials=projen_credentials,
            projen_dev_dependency=projen_dev_dependency,
            projenrc_js=projenrc_js,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
            projenrc_js_options=projenrc_js_options,
            projenrc_ts=projenrc_ts,
            projenrc_ts_options=projenrc_ts_options,
            projen_token_secret=projen_token_secret,
            projen_version=projen_version,
            publish_dry_run=publish_dry_run,
            publish_tasks=publish_tasks,
            pull_request_template=pull_request_template,
            pull_request_template_contents=pull_request_template_contents,
            readme=readme,
            releasable_commits=releasable_commits,
            release=release,
            release_branches=release_branches,
            release_every_commit=release_every_commit,
            release_failure_issue=release_failure_issue,
            release_failure_issue_label=release_failure_issue_label,
            release_schedule=release_schedule,
            release_tag_prefix=release_tag_prefix,
            release_to_npm=release_to_npm,
            release_trigger=release_trigger,
            release_workflow=release_workflow,
            release_workflow_name=release_workflow_name,
            release_workflow_setup_steps=release_workflow_setup_steps,
            renovatebot=renovatebot,
            renovatebot_options=renovatebot_options,
            repository=repository,
            repository_directory=repository_directory,
            sample_code=sample_code,
            scoped_packages_options=scoped_packages_options,
            scripts=scripts,
            srcdir=srcdir,
            stability=stability,
            stale=stale,
            stale_options=stale_options,
            testdir=testdir,
            tsconfig=tsconfig,
            tsconfig_dev=tsconfig_dev,
            tsconfig_dev_file=tsconfig_dev_file,
            ts_jest_options=ts_jest_options,
            typescript_version=typescript_version,
            versionrc_options=versionrc_options,
            vscode=vscode,
            workflow_bootstrap_steps=workflow_bootstrap_steps,
            workflow_container_image=workflow_container_image,
            workflow_git_identity=workflow_git_identity,
            workflow_node_version=workflow_node_version,
            workflow_package_cache=workflow_package_cache,
            workflow_runs_on=workflow_runs_on,
            workflow_runs_on_group=workflow_runs_on_group,
            yarn_berry_options=yarn_berry_options,
        )

        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="readme")
    def readme(self) -> "Readme":
        return typing.cast("Readme", jsii.get(self, "readme"))

    @readme.setter
    def readme(self, value: "Readme") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cb7da275ba82f1b6bb477c4c22f7721642ea0759b39a4fc1874a92b34daa7eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readme", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="projen-modules.NpmPackageOptions",
    jsii_struct_bases=[],
    name_mapping={
        "code_owners": "codeOwners",
        "name": "name",
        "allow_library_dependencies": "allowLibraryDependencies",
        "artifacts_directory": "artifactsDirectory",
        "author_email": "authorEmail",
        "author_name": "authorName",
        "author_organization": "authorOrganization",
        "author_url": "authorUrl",
        "auto_approve_options": "autoApproveOptions",
        "auto_approve_upgrades": "autoApproveUpgrades",
        "auto_detect_bin": "autoDetectBin",
        "auto_merge": "autoMerge",
        "auto_merge_options": "autoMergeOptions",
        "bin": "bin",
        "biome": "biome",
        "biome_options": "biomeOptions",
        "bugs_email": "bugsEmail",
        "bugs_url": "bugsUrl",
        "build_workflow": "buildWorkflow",
        "build_workflow_options": "buildWorkflowOptions",
        "build_workflow_triggers": "buildWorkflowTriggers",
        "bump_package": "bumpPackage",
        "bundled_deps": "bundledDeps",
        "bundler_options": "bundlerOptions",
        "bun_version": "bunVersion",
        "check_licenses": "checkLicenses",
        "clobber": "clobber",
        "code_artifact_options": "codeArtifactOptions",
        "code_cov": "codeCov",
        "code_cov_token_secret": "codeCovTokenSecret",
        "commit_generated": "commitGenerated",
        "copyright_owner": "copyrightOwner",
        "copyright_period": "copyrightPeriod",
        "default_release_branch": "defaultReleaseBranch",
        "dependabot": "dependabot",
        "dependabot_options": "dependabotOptions",
        "deps": "deps",
        "deps_upgrade": "depsUpgrade",
        "deps_upgrade_options": "depsUpgradeOptions",
        "description": "description",
        "dev_container": "devContainer",
        "dev_deps": "devDeps",
        "disable_tsconfig": "disableTsconfig",
        "disable_tsconfig_dev": "disableTsconfigDev",
        "docgen": "docgen",
        "docs_directory": "docsDirectory",
        "entrypoint": "entrypoint",
        "entrypoint_types": "entrypointTypes",
        "eslint": "eslint",
        "eslint_options": "eslintOptions",
        "github": "github",
        "github_options": "githubOptions",
        "gitignore": "gitignore",
        "git_ignore_options": "gitIgnoreOptions",
        "git_options": "gitOptions",
        "gitpod": "gitpod",
        "homepage": "homepage",
        "jest": "jest",
        "jest_options": "jestOptions",
        "jsii_release_version": "jsiiReleaseVersion",
        "keywords": "keywords",
        "libdir": "libdir",
        "license": "license",
        "licensed": "licensed",
        "logging": "logging",
        "major_version": "majorVersion",
        "max_node_version": "maxNodeVersion",
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "min_major_version": "minMajorVersion",
        "min_node_version": "minNodeVersion",
        "mutable_build": "mutableBuild",
        "next_version_command": "nextVersionCommand",
        "npm_access": "npmAccess",
        "npm_dist_tag": "npmDistTag",
        "npmignore": "npmignore",
        "npmignore_enabled": "npmignoreEnabled",
        "npm_ignore_options": "npmIgnoreOptions",
        "npm_provenance": "npmProvenance",
        "npm_registry": "npmRegistry",
        "npm_registry_url": "npmRegistryUrl",
        "npm_token_secret": "npmTokenSecret",
        "outdir": "outdir",
        "package": "package",
        "package_manager": "packageManager",
        "package_name": "packageName",
        "parent": "parent",
        "peer_dependency_options": "peerDependencyOptions",
        "peer_deps": "peerDeps",
        "pnpm_version": "pnpmVersion",
        "post_build_steps": "postBuildSteps",
        "prerelease": "prerelease",
        "prettier": "prettier",
        "prettier_options": "prettierOptions",
        "project_type": "projectType",
        "projen_command": "projenCommand",
        "projen_credentials": "projenCredentials",
        "projen_dev_dependency": "projenDevDependency",
        "projenrc_js": "projenrcJs",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "projenrc_js_options": "projenrcJsOptions",
        "projenrc_ts": "projenrcTs",
        "projenrc_ts_options": "projenrcTsOptions",
        "projen_token_secret": "projenTokenSecret",
        "projen_version": "projenVersion",
        "publish_dry_run": "publishDryRun",
        "publish_tasks": "publishTasks",
        "pull_request_template": "pullRequestTemplate",
        "pull_request_template_contents": "pullRequestTemplateContents",
        "readme": "readme",
        "releasable_commits": "releasableCommits",
        "release": "release",
        "release_branches": "releaseBranches",
        "release_every_commit": "releaseEveryCommit",
        "release_failure_issue": "releaseFailureIssue",
        "release_failure_issue_label": "releaseFailureIssueLabel",
        "release_schedule": "releaseSchedule",
        "release_tag_prefix": "releaseTagPrefix",
        "release_to_npm": "releaseToNpm",
        "release_trigger": "releaseTrigger",
        "release_workflow": "releaseWorkflow",
        "release_workflow_name": "releaseWorkflowName",
        "release_workflow_setup_steps": "releaseWorkflowSetupSteps",
        "renovatebot": "renovatebot",
        "renovatebot_options": "renovatebotOptions",
        "repository": "repository",
        "repository_directory": "repositoryDirectory",
        "sample_code": "sampleCode",
        "scoped_packages_options": "scopedPackagesOptions",
        "scripts": "scripts",
        "srcdir": "srcdir",
        "stability": "stability",
        "stale": "stale",
        "stale_options": "staleOptions",
        "testdir": "testdir",
        "tsconfig": "tsconfig",
        "tsconfig_dev": "tsconfigDev",
        "tsconfig_dev_file": "tsconfigDevFile",
        "ts_jest_options": "tsJestOptions",
        "typescript_version": "typescriptVersion",
        "versionrc_options": "versionrcOptions",
        "vscode": "vscode",
        "workflow_bootstrap_steps": "workflowBootstrapSteps",
        "workflow_container_image": "workflowContainerImage",
        "workflow_git_identity": "workflowGitIdentity",
        "workflow_node_version": "workflowNodeVersion",
        "workflow_package_cache": "workflowPackageCache",
        "workflow_runs_on": "workflowRunsOn",
        "workflow_runs_on_group": "workflowRunsOnGroup",
        "yarn_berry_options": "yarnBerryOptions",
    },
)
class NpmPackageOptions:
    def __init__(
        self,
        *,
        code_owners: typing.Sequence[builtins.str],
        name: builtins.str,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        artifacts_directory: typing.Optional[builtins.str] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        biome: typing.Optional[builtins.bool] = None,
        biome_options: typing.Optional[typing.Union[_projen_javascript_04054675.BiomeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_options: typing.Optional[typing.Union[_projen_javascript_04054675.BuildWorkflowOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        build_workflow_triggers: typing.Optional[typing.Union[_projen_github_workflows_04054675.Triggers, typing.Dict[builtins.str, typing.Any]]] = None,
        bump_package: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        bundler_options: typing.Optional[typing.Union[_projen_javascript_04054675.BundlerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        bun_version: typing.Optional[builtins.str] = None,
        check_licenses: typing.Optional[typing.Union[_projen_javascript_04054675.LicenseCheckerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        clobber: typing.Optional[builtins.bool] = None,
        code_artifact_options: typing.Optional[typing.Union[_projen_javascript_04054675.CodeArtifactOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        commit_generated: typing.Optional[builtins.bool] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        default_release_branch: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[typing.Union[_projen_github_04054675.DependabotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[typing.Union[_projen_javascript_04054675.UpgradeDependenciesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        disable_tsconfig_dev: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[typing.Union[_projen_javascript_04054675.EslintOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        homepage: typing.Optional[builtins.str] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[typing.Union[_projen_javascript_04054675.JestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        libdir: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        major_version: typing.Optional[jsii.Number] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        min_major_version: typing.Optional[jsii.Number] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        next_version_command: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[_projen_javascript_04054675.NpmAccess] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        npm_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        npm_provenance: typing.Optional[builtins.bool] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        outdir: typing.Optional[builtins.str] = None,
        package: typing.Optional[builtins.bool] = None,
        package_manager: typing.Optional[_projen_javascript_04054675.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        peer_dependency_options: typing.Optional[typing.Union[_projen_javascript_04054675.PeerDependencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pnpm_version: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[typing.Union[_projen_javascript_04054675.PrettierOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_type: typing.Optional[_projen_04054675.ProjectType] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        readme: typing.Optional[typing.Union["ReadmeOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        releasable_commits: typing.Optional[_projen_04054675.ReleasableCommits] = None,
        release: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, typing.Union[_projen_release_04054675.BranchOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_trigger: typing.Optional[_projen_release_04054675.ReleaseTrigger] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        scoped_packages_options: typing.Optional[typing.Sequence[typing.Union[_projen_javascript_04054675.ScopedPackagesOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        srcdir: typing.Optional[builtins.str] = None,
        stability: typing.Optional[builtins.str] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        ts_jest_options: typing.Optional[typing.Union[_projen_typescript_04054675.TsJestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        vscode: typing.Optional[builtins.bool] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_git_identity: typing.Optional[typing.Union[_projen_github_04054675.GitIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        workflow_package_cache: typing.Optional[builtins.bool] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_runs_on_group: typing.Optional[typing.Union[_projen_04054675.GroupRunnerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        yarn_berry_options: typing.Optional[typing.Union[_projen_javascript_04054675.YarnBerryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''NpmPackageOptions.

        :param code_owners: List of teams used to generate the CODEOWNERS file.
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Is the author an organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param biome: (experimental) Setup Biome. Default: false
        :param biome_options: (experimental) Biome options. Default: - default options
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_options: (experimental) Options for PR build workflow.
        :param build_workflow_triggers: (deprecated) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bump_package: (experimental) The ``commit-and-tag-version`` compatible package used to bump the package version, as a dependency string. This can be any compatible package version, including the deprecated ``standard-version@9``. Default: - A recent version of "commit-and-tag-version"
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param bun_version: (experimental) The version of Bun to use if using Bun as a package manager. Default: "latest"
        :param check_licenses: (experimental) Configure which licenses should be deemed acceptable for use by dependencies. This setting will cause the build to fail, if any prohibited or not allowed licenses ares encountered. Default: - no license checks are run during the build and all licenses will be accepted
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: - true, but false for subprojects
        :param code_artifact_options: (experimental) Options for npm packages using AWS CodeArtifact. This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact Default: - undefined
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v4 A secret is required for private repos. Configured with ``@codeCovTokenSecret``. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param deps_upgrade: (experimental) Use tasks and github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for ``UpgradeDependencies``. Default: - default options
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param disable_tsconfig_dev: (experimental) Do not generate a ``tsconfig.dev.json`` file. Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json. Default: "lib/index.js"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param homepage: (experimental) Package's Homepage / Website.
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param max_node_version: (experimental) The maximum node version supported by this package. Most projects should not use this option. The value indicates that the package is incompatible with any newer versions of node. This requirement is enforced via the engines field. You will normally not need to set this option. Consider this option only if your package is known to not function with newer versions of node. Default: - no maximum version is enforced
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param min_major_version: (experimental) Minimal Major version to release. This can be useful to set to 1, as breaking changes before the 1.x major release are not incrementing the major version number. Can not be set together with ``majorVersion``. Default: - No minimum version is being enforced
        :param min_node_version: (experimental) The minimum node version required by this package to function. Most projects should not use this option. The value indicates that the package is incompatible with any older versions of node. This requirement is enforced via the engines field. You will normally not need to set this option, even if your package is incompatible with EOL versions of node. Consider this option only if your package depends on a specific feature, that is not available in other LTS versions. Setting this option has very high impact on the consumers of your package, as package managers will actively prevent usage with node versions you have marked as incompatible. To change the node version of your CI/CD workflows, use ``workflowNodeVersion``. Default: - no minimum version is enforced
        :param mutable_build: (deprecated) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param next_version_command: (experimental) A shell command to control the next version to release. If present, this shell command will be run before the bump is executed, and it determines what version to release. It will be executed in the following environment: - Working directory: the project directory. - ``$VERSION``: the current version. Looks like ``1.2.3``. - ``$LATEST_TAG``: the most recent tag. Looks like ``prefix-v1.2.3``, or may be unset. - ``$SUGGESTED_BUMP``: the suggested bump action based on commits. One of ``major|minor|patch|none``. The command should print one of the following to ``stdout``: - Nothing: the next version number will be determined based on commit history. - ``x.y.z``: the next version number will be ``x.y.z``. - ``major|minor|patch``: the next version number will be the current version number with the indicated component bumped. This setting cannot be specified together with ``minMajorVersion``; the invoked script can be used to achieve the effects of ``minMajorVersion``. Default: - The next version will be determined based on the commit history and project settings.
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param npm_ignore_options: (experimental) Configuration options for .npmignore file.
        :param npm_provenance: (experimental) Should provenance statements be generated when the package is published. A supported package manager is required to publish a package with npm provenance statements and you will need to use a supported CI/CD provider. Note that the projen ``Release`` and ``Publisher`` components are using ``publib`` to publish packages, which is using npm internally and supports provenance statements independently of the package manager used. Default: - true for public packages, false otherwise
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other subprojects. Default: "."
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN_CLASSIC
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param pnpm_version: (experimental) The version of PNPM to use if using PNPM as a package manager. Default: "9"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: - true if not a subproject
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param readme: Configuration of the README.md file.
        :param releasable_commits: (experimental) Find commits that should be considered releasable Used to decide if a release is required. Default: ReleasableCommits.everyCommit()
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: "v"
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param scoped_packages_options: (experimental) Options for privately hosted scoped packages. Default: - fetch all scoped packages from the public npm registry
        :param scripts: (deprecated) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Also adds the script as a task. Default: {}
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param stability: (experimental) Package's Stability.
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param ts_jest_options: (experimental) Options for ts-jest.
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with commit-and-tag-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version used in GitHub Actions workflows. Always use this option if your GitHub Actions workflows require a specific to run. Default: - ``minNodeVersion`` if set, otherwise ``lts/*``.
        :param workflow_package_cache: (experimental) Enable Node.js package cache in GitHub workflows. Default: false
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param workflow_runs_on_group: (experimental) Github Runner Group selection options.
        :param yarn_berry_options: (experimental) Options for Yarn Berry. Default: - Yarn Berry v4 with all default options
        '''
        if isinstance(auto_approve_options, dict):
            auto_approve_options = _projen_github_04054675.AutoApproveOptions(**auto_approve_options)
        if isinstance(auto_merge_options, dict):
            auto_merge_options = _projen_github_04054675.AutoMergeOptions(**auto_merge_options)
        if isinstance(biome_options, dict):
            biome_options = _projen_javascript_04054675.BiomeOptions(**biome_options)
        if isinstance(build_workflow_options, dict):
            build_workflow_options = _projen_javascript_04054675.BuildWorkflowOptions(**build_workflow_options)
        if isinstance(build_workflow_triggers, dict):
            build_workflow_triggers = _projen_github_workflows_04054675.Triggers(**build_workflow_triggers)
        if isinstance(bundler_options, dict):
            bundler_options = _projen_javascript_04054675.BundlerOptions(**bundler_options)
        if isinstance(check_licenses, dict):
            check_licenses = _projen_javascript_04054675.LicenseCheckerOptions(**check_licenses)
        if isinstance(code_artifact_options, dict):
            code_artifact_options = _projen_javascript_04054675.CodeArtifactOptions(**code_artifact_options)
        if isinstance(dependabot_options, dict):
            dependabot_options = _projen_github_04054675.DependabotOptions(**dependabot_options)
        if isinstance(deps_upgrade_options, dict):
            deps_upgrade_options = _projen_javascript_04054675.UpgradeDependenciesOptions(**deps_upgrade_options)
        if isinstance(eslint_options, dict):
            eslint_options = _projen_javascript_04054675.EslintOptions(**eslint_options)
        if isinstance(github_options, dict):
            github_options = _projen_github_04054675.GitHubOptions(**github_options)
        if isinstance(git_ignore_options, dict):
            git_ignore_options = _projen_04054675.IgnoreFileOptions(**git_ignore_options)
        if isinstance(git_options, dict):
            git_options = _projen_04054675.GitOptions(**git_options)
        if isinstance(jest_options, dict):
            jest_options = _projen_javascript_04054675.JestOptions(**jest_options)
        if isinstance(logging, dict):
            logging = _projen_04054675.LoggerOptions(**logging)
        if isinstance(mergify_options, dict):
            mergify_options = _projen_github_04054675.MergifyOptions(**mergify_options)
        if isinstance(npm_ignore_options, dict):
            npm_ignore_options = _projen_04054675.IgnoreFileOptions(**npm_ignore_options)
        if isinstance(peer_dependency_options, dict):
            peer_dependency_options = _projen_javascript_04054675.PeerDependencyOptions(**peer_dependency_options)
        if isinstance(prettier_options, dict):
            prettier_options = _projen_javascript_04054675.PrettierOptions(**prettier_options)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = _projen_04054675.ProjenrcJsonOptions(**projenrc_json_options)
        if isinstance(projenrc_js_options, dict):
            projenrc_js_options = _projen_javascript_04054675.ProjenrcOptions(**projenrc_js_options)
        if isinstance(projenrc_ts_options, dict):
            projenrc_ts_options = _projen_typescript_04054675.ProjenrcOptions(**projenrc_ts_options)
        if isinstance(readme, dict):
            readme = ReadmeOptions(**readme)
        if isinstance(renovatebot_options, dict):
            renovatebot_options = _projen_04054675.RenovatebotOptions(**renovatebot_options)
        if isinstance(stale_options, dict):
            stale_options = _projen_github_04054675.StaleOptions(**stale_options)
        if isinstance(tsconfig, dict):
            tsconfig = _projen_javascript_04054675.TypescriptConfigOptions(**tsconfig)
        if isinstance(tsconfig_dev, dict):
            tsconfig_dev = _projen_javascript_04054675.TypescriptConfigOptions(**tsconfig_dev)
        if isinstance(ts_jest_options, dict):
            ts_jest_options = _projen_typescript_04054675.TsJestOptions(**ts_jest_options)
        if isinstance(workflow_git_identity, dict):
            workflow_git_identity = _projen_github_04054675.GitIdentity(**workflow_git_identity)
        if isinstance(workflow_runs_on_group, dict):
            workflow_runs_on_group = _projen_04054675.GroupRunnerOptions(**workflow_runs_on_group)
        if isinstance(yarn_berry_options, dict):
            yarn_berry_options = _projen_javascript_04054675.YarnBerryOptions(**yarn_berry_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b17dce6f2f04ceb519c781a818d66bcf4fef528d5b613028b126fd373e7b4048)
            check_type(argname="argument code_owners", value=code_owners, expected_type=type_hints["code_owners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument allow_library_dependencies", value=allow_library_dependencies, expected_type=type_hints["allow_library_dependencies"])
            check_type(argname="argument artifacts_directory", value=artifacts_directory, expected_type=type_hints["artifacts_directory"])
            check_type(argname="argument author_email", value=author_email, expected_type=type_hints["author_email"])
            check_type(argname="argument author_name", value=author_name, expected_type=type_hints["author_name"])
            check_type(argname="argument author_organization", value=author_organization, expected_type=type_hints["author_organization"])
            check_type(argname="argument author_url", value=author_url, expected_type=type_hints["author_url"])
            check_type(argname="argument auto_approve_options", value=auto_approve_options, expected_type=type_hints["auto_approve_options"])
            check_type(argname="argument auto_approve_upgrades", value=auto_approve_upgrades, expected_type=type_hints["auto_approve_upgrades"])
            check_type(argname="argument auto_detect_bin", value=auto_detect_bin, expected_type=type_hints["auto_detect_bin"])
            check_type(argname="argument auto_merge", value=auto_merge, expected_type=type_hints["auto_merge"])
            check_type(argname="argument auto_merge_options", value=auto_merge_options, expected_type=type_hints["auto_merge_options"])
            check_type(argname="argument bin", value=bin, expected_type=type_hints["bin"])
            check_type(argname="argument biome", value=biome, expected_type=type_hints["biome"])
            check_type(argname="argument biome_options", value=biome_options, expected_type=type_hints["biome_options"])
            check_type(argname="argument bugs_email", value=bugs_email, expected_type=type_hints["bugs_email"])
            check_type(argname="argument bugs_url", value=bugs_url, expected_type=type_hints["bugs_url"])
            check_type(argname="argument build_workflow", value=build_workflow, expected_type=type_hints["build_workflow"])
            check_type(argname="argument build_workflow_options", value=build_workflow_options, expected_type=type_hints["build_workflow_options"])
            check_type(argname="argument build_workflow_triggers", value=build_workflow_triggers, expected_type=type_hints["build_workflow_triggers"])
            check_type(argname="argument bump_package", value=bump_package, expected_type=type_hints["bump_package"])
            check_type(argname="argument bundled_deps", value=bundled_deps, expected_type=type_hints["bundled_deps"])
            check_type(argname="argument bundler_options", value=bundler_options, expected_type=type_hints["bundler_options"])
            check_type(argname="argument bun_version", value=bun_version, expected_type=type_hints["bun_version"])
            check_type(argname="argument check_licenses", value=check_licenses, expected_type=type_hints["check_licenses"])
            check_type(argname="argument clobber", value=clobber, expected_type=type_hints["clobber"])
            check_type(argname="argument code_artifact_options", value=code_artifact_options, expected_type=type_hints["code_artifact_options"])
            check_type(argname="argument code_cov", value=code_cov, expected_type=type_hints["code_cov"])
            check_type(argname="argument code_cov_token_secret", value=code_cov_token_secret, expected_type=type_hints["code_cov_token_secret"])
            check_type(argname="argument commit_generated", value=commit_generated, expected_type=type_hints["commit_generated"])
            check_type(argname="argument copyright_owner", value=copyright_owner, expected_type=type_hints["copyright_owner"])
            check_type(argname="argument copyright_period", value=copyright_period, expected_type=type_hints["copyright_period"])
            check_type(argname="argument default_release_branch", value=default_release_branch, expected_type=type_hints["default_release_branch"])
            check_type(argname="argument dependabot", value=dependabot, expected_type=type_hints["dependabot"])
            check_type(argname="argument dependabot_options", value=dependabot_options, expected_type=type_hints["dependabot_options"])
            check_type(argname="argument deps", value=deps, expected_type=type_hints["deps"])
            check_type(argname="argument deps_upgrade", value=deps_upgrade, expected_type=type_hints["deps_upgrade"])
            check_type(argname="argument deps_upgrade_options", value=deps_upgrade_options, expected_type=type_hints["deps_upgrade_options"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument dev_container", value=dev_container, expected_type=type_hints["dev_container"])
            check_type(argname="argument dev_deps", value=dev_deps, expected_type=type_hints["dev_deps"])
            check_type(argname="argument disable_tsconfig", value=disable_tsconfig, expected_type=type_hints["disable_tsconfig"])
            check_type(argname="argument disable_tsconfig_dev", value=disable_tsconfig_dev, expected_type=type_hints["disable_tsconfig_dev"])
            check_type(argname="argument docgen", value=docgen, expected_type=type_hints["docgen"])
            check_type(argname="argument docs_directory", value=docs_directory, expected_type=type_hints["docs_directory"])
            check_type(argname="argument entrypoint", value=entrypoint, expected_type=type_hints["entrypoint"])
            check_type(argname="argument entrypoint_types", value=entrypoint_types, expected_type=type_hints["entrypoint_types"])
            check_type(argname="argument eslint", value=eslint, expected_type=type_hints["eslint"])
            check_type(argname="argument eslint_options", value=eslint_options, expected_type=type_hints["eslint_options"])
            check_type(argname="argument github", value=github, expected_type=type_hints["github"])
            check_type(argname="argument github_options", value=github_options, expected_type=type_hints["github_options"])
            check_type(argname="argument gitignore", value=gitignore, expected_type=type_hints["gitignore"])
            check_type(argname="argument git_ignore_options", value=git_ignore_options, expected_type=type_hints["git_ignore_options"])
            check_type(argname="argument git_options", value=git_options, expected_type=type_hints["git_options"])
            check_type(argname="argument gitpod", value=gitpod, expected_type=type_hints["gitpod"])
            check_type(argname="argument homepage", value=homepage, expected_type=type_hints["homepage"])
            check_type(argname="argument jest", value=jest, expected_type=type_hints["jest"])
            check_type(argname="argument jest_options", value=jest_options, expected_type=type_hints["jest_options"])
            check_type(argname="argument jsii_release_version", value=jsii_release_version, expected_type=type_hints["jsii_release_version"])
            check_type(argname="argument keywords", value=keywords, expected_type=type_hints["keywords"])
            check_type(argname="argument libdir", value=libdir, expected_type=type_hints["libdir"])
            check_type(argname="argument license", value=license, expected_type=type_hints["license"])
            check_type(argname="argument licensed", value=licensed, expected_type=type_hints["licensed"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument major_version", value=major_version, expected_type=type_hints["major_version"])
            check_type(argname="argument max_node_version", value=max_node_version, expected_type=type_hints["max_node_version"])
            check_type(argname="argument mergify", value=mergify, expected_type=type_hints["mergify"])
            check_type(argname="argument mergify_options", value=mergify_options, expected_type=type_hints["mergify_options"])
            check_type(argname="argument min_major_version", value=min_major_version, expected_type=type_hints["min_major_version"])
            check_type(argname="argument min_node_version", value=min_node_version, expected_type=type_hints["min_node_version"])
            check_type(argname="argument mutable_build", value=mutable_build, expected_type=type_hints["mutable_build"])
            check_type(argname="argument next_version_command", value=next_version_command, expected_type=type_hints["next_version_command"])
            check_type(argname="argument npm_access", value=npm_access, expected_type=type_hints["npm_access"])
            check_type(argname="argument npm_dist_tag", value=npm_dist_tag, expected_type=type_hints["npm_dist_tag"])
            check_type(argname="argument npmignore", value=npmignore, expected_type=type_hints["npmignore"])
            check_type(argname="argument npmignore_enabled", value=npmignore_enabled, expected_type=type_hints["npmignore_enabled"])
            check_type(argname="argument npm_ignore_options", value=npm_ignore_options, expected_type=type_hints["npm_ignore_options"])
            check_type(argname="argument npm_provenance", value=npm_provenance, expected_type=type_hints["npm_provenance"])
            check_type(argname="argument npm_registry", value=npm_registry, expected_type=type_hints["npm_registry"])
            check_type(argname="argument npm_registry_url", value=npm_registry_url, expected_type=type_hints["npm_registry_url"])
            check_type(argname="argument npm_token_secret", value=npm_token_secret, expected_type=type_hints["npm_token_secret"])
            check_type(argname="argument outdir", value=outdir, expected_type=type_hints["outdir"])
            check_type(argname="argument package", value=package, expected_type=type_hints["package"])
            check_type(argname="argument package_manager", value=package_manager, expected_type=type_hints["package_manager"])
            check_type(argname="argument package_name", value=package_name, expected_type=type_hints["package_name"])
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument peer_dependency_options", value=peer_dependency_options, expected_type=type_hints["peer_dependency_options"])
            check_type(argname="argument peer_deps", value=peer_deps, expected_type=type_hints["peer_deps"])
            check_type(argname="argument pnpm_version", value=pnpm_version, expected_type=type_hints["pnpm_version"])
            check_type(argname="argument post_build_steps", value=post_build_steps, expected_type=type_hints["post_build_steps"])
            check_type(argname="argument prerelease", value=prerelease, expected_type=type_hints["prerelease"])
            check_type(argname="argument prettier", value=prettier, expected_type=type_hints["prettier"])
            check_type(argname="argument prettier_options", value=prettier_options, expected_type=type_hints["prettier_options"])
            check_type(argname="argument project_type", value=project_type, expected_type=type_hints["project_type"])
            check_type(argname="argument projen_command", value=projen_command, expected_type=type_hints["projen_command"])
            check_type(argname="argument projen_credentials", value=projen_credentials, expected_type=type_hints["projen_credentials"])
            check_type(argname="argument projen_dev_dependency", value=projen_dev_dependency, expected_type=type_hints["projen_dev_dependency"])
            check_type(argname="argument projenrc_js", value=projenrc_js, expected_type=type_hints["projenrc_js"])
            check_type(argname="argument projenrc_json", value=projenrc_json, expected_type=type_hints["projenrc_json"])
            check_type(argname="argument projenrc_json_options", value=projenrc_json_options, expected_type=type_hints["projenrc_json_options"])
            check_type(argname="argument projenrc_js_options", value=projenrc_js_options, expected_type=type_hints["projenrc_js_options"])
            check_type(argname="argument projenrc_ts", value=projenrc_ts, expected_type=type_hints["projenrc_ts"])
            check_type(argname="argument projenrc_ts_options", value=projenrc_ts_options, expected_type=type_hints["projenrc_ts_options"])
            check_type(argname="argument projen_token_secret", value=projen_token_secret, expected_type=type_hints["projen_token_secret"])
            check_type(argname="argument projen_version", value=projen_version, expected_type=type_hints["projen_version"])
            check_type(argname="argument publish_dry_run", value=publish_dry_run, expected_type=type_hints["publish_dry_run"])
            check_type(argname="argument publish_tasks", value=publish_tasks, expected_type=type_hints["publish_tasks"])
            check_type(argname="argument pull_request_template", value=pull_request_template, expected_type=type_hints["pull_request_template"])
            check_type(argname="argument pull_request_template_contents", value=pull_request_template_contents, expected_type=type_hints["pull_request_template_contents"])
            check_type(argname="argument readme", value=readme, expected_type=type_hints["readme"])
            check_type(argname="argument releasable_commits", value=releasable_commits, expected_type=type_hints["releasable_commits"])
            check_type(argname="argument release", value=release, expected_type=type_hints["release"])
            check_type(argname="argument release_branches", value=release_branches, expected_type=type_hints["release_branches"])
            check_type(argname="argument release_every_commit", value=release_every_commit, expected_type=type_hints["release_every_commit"])
            check_type(argname="argument release_failure_issue", value=release_failure_issue, expected_type=type_hints["release_failure_issue"])
            check_type(argname="argument release_failure_issue_label", value=release_failure_issue_label, expected_type=type_hints["release_failure_issue_label"])
            check_type(argname="argument release_schedule", value=release_schedule, expected_type=type_hints["release_schedule"])
            check_type(argname="argument release_tag_prefix", value=release_tag_prefix, expected_type=type_hints["release_tag_prefix"])
            check_type(argname="argument release_to_npm", value=release_to_npm, expected_type=type_hints["release_to_npm"])
            check_type(argname="argument release_trigger", value=release_trigger, expected_type=type_hints["release_trigger"])
            check_type(argname="argument release_workflow", value=release_workflow, expected_type=type_hints["release_workflow"])
            check_type(argname="argument release_workflow_name", value=release_workflow_name, expected_type=type_hints["release_workflow_name"])
            check_type(argname="argument release_workflow_setup_steps", value=release_workflow_setup_steps, expected_type=type_hints["release_workflow_setup_steps"])
            check_type(argname="argument renovatebot", value=renovatebot, expected_type=type_hints["renovatebot"])
            check_type(argname="argument renovatebot_options", value=renovatebot_options, expected_type=type_hints["renovatebot_options"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument repository_directory", value=repository_directory, expected_type=type_hints["repository_directory"])
            check_type(argname="argument sample_code", value=sample_code, expected_type=type_hints["sample_code"])
            check_type(argname="argument scoped_packages_options", value=scoped_packages_options, expected_type=type_hints["scoped_packages_options"])
            check_type(argname="argument scripts", value=scripts, expected_type=type_hints["scripts"])
            check_type(argname="argument srcdir", value=srcdir, expected_type=type_hints["srcdir"])
            check_type(argname="argument stability", value=stability, expected_type=type_hints["stability"])
            check_type(argname="argument stale", value=stale, expected_type=type_hints["stale"])
            check_type(argname="argument stale_options", value=stale_options, expected_type=type_hints["stale_options"])
            check_type(argname="argument testdir", value=testdir, expected_type=type_hints["testdir"])
            check_type(argname="argument tsconfig", value=tsconfig, expected_type=type_hints["tsconfig"])
            check_type(argname="argument tsconfig_dev", value=tsconfig_dev, expected_type=type_hints["tsconfig_dev"])
            check_type(argname="argument tsconfig_dev_file", value=tsconfig_dev_file, expected_type=type_hints["tsconfig_dev_file"])
            check_type(argname="argument ts_jest_options", value=ts_jest_options, expected_type=type_hints["ts_jest_options"])
            check_type(argname="argument typescript_version", value=typescript_version, expected_type=type_hints["typescript_version"])
            check_type(argname="argument versionrc_options", value=versionrc_options, expected_type=type_hints["versionrc_options"])
            check_type(argname="argument vscode", value=vscode, expected_type=type_hints["vscode"])
            check_type(argname="argument workflow_bootstrap_steps", value=workflow_bootstrap_steps, expected_type=type_hints["workflow_bootstrap_steps"])
            check_type(argname="argument workflow_container_image", value=workflow_container_image, expected_type=type_hints["workflow_container_image"])
            check_type(argname="argument workflow_git_identity", value=workflow_git_identity, expected_type=type_hints["workflow_git_identity"])
            check_type(argname="argument workflow_node_version", value=workflow_node_version, expected_type=type_hints["workflow_node_version"])
            check_type(argname="argument workflow_package_cache", value=workflow_package_cache, expected_type=type_hints["workflow_package_cache"])
            check_type(argname="argument workflow_runs_on", value=workflow_runs_on, expected_type=type_hints["workflow_runs_on"])
            check_type(argname="argument workflow_runs_on_group", value=workflow_runs_on_group, expected_type=type_hints["workflow_runs_on_group"])
            check_type(argname="argument yarn_berry_options", value=yarn_berry_options, expected_type=type_hints["yarn_berry_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "code_owners": code_owners,
            "name": name,
        }
        if allow_library_dependencies is not None:
            self._values["allow_library_dependencies"] = allow_library_dependencies
        if artifacts_directory is not None:
            self._values["artifacts_directory"] = artifacts_directory
        if author_email is not None:
            self._values["author_email"] = author_email
        if author_name is not None:
            self._values["author_name"] = author_name
        if author_organization is not None:
            self._values["author_organization"] = author_organization
        if author_url is not None:
            self._values["author_url"] = author_url
        if auto_approve_options is not None:
            self._values["auto_approve_options"] = auto_approve_options
        if auto_approve_upgrades is not None:
            self._values["auto_approve_upgrades"] = auto_approve_upgrades
        if auto_detect_bin is not None:
            self._values["auto_detect_bin"] = auto_detect_bin
        if auto_merge is not None:
            self._values["auto_merge"] = auto_merge
        if auto_merge_options is not None:
            self._values["auto_merge_options"] = auto_merge_options
        if bin is not None:
            self._values["bin"] = bin
        if biome is not None:
            self._values["biome"] = biome
        if biome_options is not None:
            self._values["biome_options"] = biome_options
        if bugs_email is not None:
            self._values["bugs_email"] = bugs_email
        if bugs_url is not None:
            self._values["bugs_url"] = bugs_url
        if build_workflow is not None:
            self._values["build_workflow"] = build_workflow
        if build_workflow_options is not None:
            self._values["build_workflow_options"] = build_workflow_options
        if build_workflow_triggers is not None:
            self._values["build_workflow_triggers"] = build_workflow_triggers
        if bump_package is not None:
            self._values["bump_package"] = bump_package
        if bundled_deps is not None:
            self._values["bundled_deps"] = bundled_deps
        if bundler_options is not None:
            self._values["bundler_options"] = bundler_options
        if bun_version is not None:
            self._values["bun_version"] = bun_version
        if check_licenses is not None:
            self._values["check_licenses"] = check_licenses
        if clobber is not None:
            self._values["clobber"] = clobber
        if code_artifact_options is not None:
            self._values["code_artifact_options"] = code_artifact_options
        if code_cov is not None:
            self._values["code_cov"] = code_cov
        if code_cov_token_secret is not None:
            self._values["code_cov_token_secret"] = code_cov_token_secret
        if commit_generated is not None:
            self._values["commit_generated"] = commit_generated
        if copyright_owner is not None:
            self._values["copyright_owner"] = copyright_owner
        if copyright_period is not None:
            self._values["copyright_period"] = copyright_period
        if default_release_branch is not None:
            self._values["default_release_branch"] = default_release_branch
        if dependabot is not None:
            self._values["dependabot"] = dependabot
        if dependabot_options is not None:
            self._values["dependabot_options"] = dependabot_options
        if deps is not None:
            self._values["deps"] = deps
        if deps_upgrade is not None:
            self._values["deps_upgrade"] = deps_upgrade
        if deps_upgrade_options is not None:
            self._values["deps_upgrade_options"] = deps_upgrade_options
        if description is not None:
            self._values["description"] = description
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if dev_deps is not None:
            self._values["dev_deps"] = dev_deps
        if disable_tsconfig is not None:
            self._values["disable_tsconfig"] = disable_tsconfig
        if disable_tsconfig_dev is not None:
            self._values["disable_tsconfig_dev"] = disable_tsconfig_dev
        if docgen is not None:
            self._values["docgen"] = docgen
        if docs_directory is not None:
            self._values["docs_directory"] = docs_directory
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint
        if entrypoint_types is not None:
            self._values["entrypoint_types"] = entrypoint_types
        if eslint is not None:
            self._values["eslint"] = eslint
        if eslint_options is not None:
            self._values["eslint_options"] = eslint_options
        if github is not None:
            self._values["github"] = github
        if github_options is not None:
            self._values["github_options"] = github_options
        if gitignore is not None:
            self._values["gitignore"] = gitignore
        if git_ignore_options is not None:
            self._values["git_ignore_options"] = git_ignore_options
        if git_options is not None:
            self._values["git_options"] = git_options
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if homepage is not None:
            self._values["homepage"] = homepage
        if jest is not None:
            self._values["jest"] = jest
        if jest_options is not None:
            self._values["jest_options"] = jest_options
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version
        if keywords is not None:
            self._values["keywords"] = keywords
        if libdir is not None:
            self._values["libdir"] = libdir
        if license is not None:
            self._values["license"] = license
        if licensed is not None:
            self._values["licensed"] = licensed
        if logging is not None:
            self._values["logging"] = logging
        if major_version is not None:
            self._values["major_version"] = major_version
        if max_node_version is not None:
            self._values["max_node_version"] = max_node_version
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if min_major_version is not None:
            self._values["min_major_version"] = min_major_version
        if min_node_version is not None:
            self._values["min_node_version"] = min_node_version
        if mutable_build is not None:
            self._values["mutable_build"] = mutable_build
        if next_version_command is not None:
            self._values["next_version_command"] = next_version_command
        if npm_access is not None:
            self._values["npm_access"] = npm_access
        if npm_dist_tag is not None:
            self._values["npm_dist_tag"] = npm_dist_tag
        if npmignore is not None:
            self._values["npmignore"] = npmignore
        if npmignore_enabled is not None:
            self._values["npmignore_enabled"] = npmignore_enabled
        if npm_ignore_options is not None:
            self._values["npm_ignore_options"] = npm_ignore_options
        if npm_provenance is not None:
            self._values["npm_provenance"] = npm_provenance
        if npm_registry is not None:
            self._values["npm_registry"] = npm_registry
        if npm_registry_url is not None:
            self._values["npm_registry_url"] = npm_registry_url
        if npm_token_secret is not None:
            self._values["npm_token_secret"] = npm_token_secret
        if outdir is not None:
            self._values["outdir"] = outdir
        if package is not None:
            self._values["package"] = package
        if package_manager is not None:
            self._values["package_manager"] = package_manager
        if package_name is not None:
            self._values["package_name"] = package_name
        if parent is not None:
            self._values["parent"] = parent
        if peer_dependency_options is not None:
            self._values["peer_dependency_options"] = peer_dependency_options
        if peer_deps is not None:
            self._values["peer_deps"] = peer_deps
        if pnpm_version is not None:
            self._values["pnpm_version"] = pnpm_version
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if prerelease is not None:
            self._values["prerelease"] = prerelease
        if prettier is not None:
            self._values["prettier"] = prettier
        if prettier_options is not None:
            self._values["prettier_options"] = prettier_options
        if project_type is not None:
            self._values["project_type"] = project_type
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projen_credentials is not None:
            self._values["projen_credentials"] = projen_credentials
        if projen_dev_dependency is not None:
            self._values["projen_dev_dependency"] = projen_dev_dependency
        if projenrc_js is not None:
            self._values["projenrc_js"] = projenrc_js
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if projenrc_js_options is not None:
            self._values["projenrc_js_options"] = projenrc_js_options
        if projenrc_ts is not None:
            self._values["projenrc_ts"] = projenrc_ts
        if projenrc_ts_options is not None:
            self._values["projenrc_ts_options"] = projenrc_ts_options
        if projen_token_secret is not None:
            self._values["projen_token_secret"] = projen_token_secret
        if projen_version is not None:
            self._values["projen_version"] = projen_version
        if publish_dry_run is not None:
            self._values["publish_dry_run"] = publish_dry_run
        if publish_tasks is not None:
            self._values["publish_tasks"] = publish_tasks
        if pull_request_template is not None:
            self._values["pull_request_template"] = pull_request_template
        if pull_request_template_contents is not None:
            self._values["pull_request_template_contents"] = pull_request_template_contents
        if readme is not None:
            self._values["readme"] = readme
        if releasable_commits is not None:
            self._values["releasable_commits"] = releasable_commits
        if release is not None:
            self._values["release"] = release
        if release_branches is not None:
            self._values["release_branches"] = release_branches
        if release_every_commit is not None:
            self._values["release_every_commit"] = release_every_commit
        if release_failure_issue is not None:
            self._values["release_failure_issue"] = release_failure_issue
        if release_failure_issue_label is not None:
            self._values["release_failure_issue_label"] = release_failure_issue_label
        if release_schedule is not None:
            self._values["release_schedule"] = release_schedule
        if release_tag_prefix is not None:
            self._values["release_tag_prefix"] = release_tag_prefix
        if release_to_npm is not None:
            self._values["release_to_npm"] = release_to_npm
        if release_trigger is not None:
            self._values["release_trigger"] = release_trigger
        if release_workflow is not None:
            self._values["release_workflow"] = release_workflow
        if release_workflow_name is not None:
            self._values["release_workflow_name"] = release_workflow_name
        if release_workflow_setup_steps is not None:
            self._values["release_workflow_setup_steps"] = release_workflow_setup_steps
        if renovatebot is not None:
            self._values["renovatebot"] = renovatebot
        if renovatebot_options is not None:
            self._values["renovatebot_options"] = renovatebot_options
        if repository is not None:
            self._values["repository"] = repository
        if repository_directory is not None:
            self._values["repository_directory"] = repository_directory
        if sample_code is not None:
            self._values["sample_code"] = sample_code
        if scoped_packages_options is not None:
            self._values["scoped_packages_options"] = scoped_packages_options
        if scripts is not None:
            self._values["scripts"] = scripts
        if srcdir is not None:
            self._values["srcdir"] = srcdir
        if stability is not None:
            self._values["stability"] = stability
        if stale is not None:
            self._values["stale"] = stale
        if stale_options is not None:
            self._values["stale_options"] = stale_options
        if testdir is not None:
            self._values["testdir"] = testdir
        if tsconfig is not None:
            self._values["tsconfig"] = tsconfig
        if tsconfig_dev is not None:
            self._values["tsconfig_dev"] = tsconfig_dev
        if tsconfig_dev_file is not None:
            self._values["tsconfig_dev_file"] = tsconfig_dev_file
        if ts_jest_options is not None:
            self._values["ts_jest_options"] = ts_jest_options
        if typescript_version is not None:
            self._values["typescript_version"] = typescript_version
        if versionrc_options is not None:
            self._values["versionrc_options"] = versionrc_options
        if vscode is not None:
            self._values["vscode"] = vscode
        if workflow_bootstrap_steps is not None:
            self._values["workflow_bootstrap_steps"] = workflow_bootstrap_steps
        if workflow_container_image is not None:
            self._values["workflow_container_image"] = workflow_container_image
        if workflow_git_identity is not None:
            self._values["workflow_git_identity"] = workflow_git_identity
        if workflow_node_version is not None:
            self._values["workflow_node_version"] = workflow_node_version
        if workflow_package_cache is not None:
            self._values["workflow_package_cache"] = workflow_package_cache
        if workflow_runs_on is not None:
            self._values["workflow_runs_on"] = workflow_runs_on
        if workflow_runs_on_group is not None:
            self._values["workflow_runs_on_group"] = workflow_runs_on_group
        if yarn_berry_options is not None:
            self._values["yarn_berry_options"] = yarn_berry_options

    @builtins.property
    def code_owners(self) -> typing.List[builtins.str]:
        '''List of teams used to generate the CODEOWNERS file.'''
        result = self._values.get("code_owners")
        assert result is not None, "Required property 'code_owners' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_library_dependencies(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``.

        This is normally only allowed for libraries. For apps, there's no meaning
        for specifying these.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("allow_library_dependencies")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def artifacts_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) A directory which will contain build artifacts.

        :default: "dist"

        :stability: experimental
        '''
        result = self._values.get("artifacts_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's e-mail.

        :stability: experimental
        '''
        result = self._values.get("author_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's name.

        :stability: experimental
        '''
        result = self._values.get("author_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_organization(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Is the author an organization.

        :stability: experimental
        '''
        result = self._values.get("author_organization")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's URL / Website.

        :stability: experimental
        '''
        result = self._values.get("author_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_approve_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.AutoApproveOptions]:
        '''(experimental) Enable and configure the 'auto approve' workflow.

        :default: - auto approve is disabled

        :stability: experimental
        '''
        result = self._values.get("auto_approve_options")
        return typing.cast(typing.Optional[_projen_github_04054675.AutoApproveOptions], result)

    @builtins.property
    def auto_approve_upgrades(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued).

        Throw if set to true but ``autoApproveOptions`` are not defined.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("auto_approve_upgrades")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_detect_bin(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_detect_bin")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_merge(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable automatic merging on GitHub.

        Has no effect if ``github.mergify``
        is set to false.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_merge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_merge_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.AutoMergeOptions]:
        '''(experimental) Configure options for automatic merging on GitHub.

        Has no effect if
        ``github.mergify`` or ``autoMerge`` is set to false.

        :default: - see defaults in ``AutoMergeOptions``

        :stability: experimental
        '''
        result = self._values.get("auto_merge_options")
        return typing.cast(typing.Optional[_projen_github_04054675.AutoMergeOptions], result)

    @builtins.property
    def bin(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Binary programs vended with your module.

        You can use this option to add/customize how binaries are represented in
        your ``package.json``, but unless ``autoDetectBin`` is ``false``, every
        executable file under ``bin`` will automatically be added to this section.

        :stability: experimental
        '''
        result = self._values.get("bin")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def biome(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup Biome.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("biome")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def biome_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.BiomeOptions]:
        '''(experimental) Biome options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("biome_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.BiomeOptions], result)

    @builtins.property
    def bugs_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) The email address to which issues should be reported.

        :stability: experimental
        '''
        result = self._values.get("bugs_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bugs_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The url to your project's issue tracker.

        :stability: experimental
        '''
        result = self._values.get("bugs_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_workflow(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow for building PRs.

        :default: - true if not a subproject

        :stability: experimental
        '''
        result = self._values.get("build_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_workflow_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.BuildWorkflowOptions]:
        '''(experimental) Options for PR build workflow.

        :stability: experimental
        '''
        result = self._values.get("build_workflow_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.BuildWorkflowOptions], result)

    @builtins.property
    def build_workflow_triggers(
        self,
    ) -> typing.Optional[_projen_github_workflows_04054675.Triggers]:
        '''(deprecated) Build workflow triggers.

        :default: "{ pullRequest: {}, workflowDispatch: {} }"

        :deprecated: - Use ``buildWorkflowOptions.workflowTriggers``

        :stability: deprecated
        '''
        result = self._values.get("build_workflow_triggers")
        return typing.cast(typing.Optional[_projen_github_workflows_04054675.Triggers], result)

    @builtins.property
    def bump_package(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ``commit-and-tag-version`` compatible package used to bump the package version, as a dependency string.

        This can be any compatible package version, including the deprecated ``standard-version@9``.

        :default: - A recent version of "commit-and-tag-version"

        :stability: experimental
        '''
        result = self._values.get("bump_package")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bundled_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of dependencies to bundle into this module.

        These modules will be
        added both to the ``dependencies`` section and ``bundledDependencies`` section of
        your ``package.json``.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :stability: experimental
        '''
        result = self._values.get("bundled_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bundler_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.BundlerOptions]:
        '''(experimental) Options for ``Bundler``.

        :stability: experimental
        '''
        result = self._values.get("bundler_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.BundlerOptions], result)

    @builtins.property
    def bun_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of Bun to use if using Bun as a package manager.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("bun_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def check_licenses(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.LicenseCheckerOptions]:
        '''(experimental) Configure which licenses should be deemed acceptable for use by dependencies.

        This setting will cause the build to fail, if any prohibited or not allowed licenses ares encountered.

        :default: - no license checks are run during the build and all licenses will be accepted

        :stability: experimental
        '''
        result = self._values.get("check_licenses")
        return typing.cast(typing.Optional[_projen_javascript_04054675.LicenseCheckerOptions], result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: - true, but false for subprojects

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_artifact_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.CodeArtifactOptions]:
        '''(experimental) Options for npm packages using AWS CodeArtifact.

        This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("code_artifact_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.CodeArtifactOptions], result)

    @builtins.property
    def code_cov(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v4 A secret is required for private repos. Configured with ``@codeCovTokenSecret``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("code_cov")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_cov_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories.

        :default: - if this option is not specified, only public repositories are supported

        :stability: experimental
        '''
        result = self._values.get("code_cov_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def commit_generated(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to commit the managed files by default.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("commit_generated")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def copyright_owner(self) -> typing.Optional[builtins.str]:
        '''(experimental) License copyright owner.

        :default: - defaults to the value of authorName or "" if ``authorName`` is undefined.

        :stability: experimental
        '''
        result = self._values.get("copyright_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copyright_period(self) -> typing.Optional[builtins.str]:
        '''(experimental) The copyright years to put in the LICENSE file.

        :default: - current year

        :stability: experimental
        '''
        result = self._values.get("copyright_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_release_branch(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the main release branch.

        :default: "main"

        :stability: experimental
        '''
        result = self._values.get("default_release_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependabot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use dependabot to handle dependency upgrades.

        Cannot be used in conjunction with ``depsUpgrade``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dependabot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dependabot_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.DependabotOptions]:
        '''(experimental) Options for dependabot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("dependabot_options")
        return typing.cast(typing.Optional[_projen_github_04054675.DependabotOptions], result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Runtime dependencies of this module.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deps_upgrade(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use tasks and github workflows to handle dependency upgrades.

        Cannot be used in conjunction with ``dependabot``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deps_upgrade_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.UpgradeDependenciesOptions]:
        '''(experimental) Options for ``UpgradeDependencies``.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.UpgradeDependenciesOptions], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description is just a string that helps people understand the purpose of the package.

        It can be used when searching for packages in a package manager as well.
        See https://classic.yarnpkg.com/en/docs/package-json/#toc-description

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Build dependencies for this module.

        These dependencies will only be
        available in your build environment but will not be fetched when this
        module is consumed.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("dev_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def disable_tsconfig(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("disable_tsconfig")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def disable_tsconfig_dev(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Do not generate a ``tsconfig.dev.json`` file.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("disable_tsconfig_dev")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docgen(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Docgen by Typedoc.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("docgen")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docs_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) Docs directory.

        :default: "docs"

        :stability: experimental
        '''
        result = self._values.get("docs_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json.

        :default: "lib/index.js"

        :stability: experimental
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint_types(self) -> typing.Optional[builtins.str]:
        '''(experimental) The .d.ts file that includes the type declarations for this module.

        :default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)

        :stability: experimental
        '''
        result = self._values.get("entrypoint_types")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eslint(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup eslint.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("eslint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def eslint_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.EslintOptions]:
        '''(experimental) Eslint options.

        :default: - opinionated default options

        :stability: experimental
        '''
        result = self._values.get("eslint_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.EslintOptions], result)

    @builtins.property
    def github(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable GitHub integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github_options(self) -> typing.Optional[_projen_github_04054675.GitHubOptions]:
        '''(experimental) Options for GitHub integration.

        :default: - see GitHubOptions

        :stability: experimental
        '''
        result = self._values.get("github_options")
        return typing.cast(typing.Optional[_projen_github_04054675.GitHubOptions], result)

    @builtins.property
    def gitignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional entries to .gitignore.

        :stability: experimental
        '''
        result = self._values.get("gitignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def git_ignore_options(self) -> typing.Optional[_projen_04054675.IgnoreFileOptions]:
        '''(experimental) Configuration options for .gitignore file.

        :stability: experimental
        '''
        result = self._values.get("git_ignore_options")
        return typing.cast(typing.Optional[_projen_04054675.IgnoreFileOptions], result)

    @builtins.property
    def git_options(self) -> typing.Optional[_projen_04054675.GitOptions]:
        '''(experimental) Configuration options for git.

        :stability: experimental
        '''
        result = self._values.get("git_options")
        return typing.cast(typing.Optional[_projen_04054675.GitOptions], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Homepage / Website.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jest(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup jest unit tests.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("jest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def jest_options(self) -> typing.Optional[_projen_javascript_04054675.JestOptions]:
        '''(experimental) Jest options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("jest_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.JestOptions], result)

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement of ``publib`` which is used to publish modules to npm.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Keywords to include in ``package.json``.

        :stability: experimental
        '''
        result = self._values.get("keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def libdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript  artifacts output directory.

        :default: "lib"

        :stability: experimental
        '''
        result = self._values.get("libdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License's SPDX identifier.

        See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses.
        Use the ``licensed`` option if you want to no license to be specified.

        :default: "Apache-2.0"

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def licensed(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates if a license should be added.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("licensed")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def logging(self) -> typing.Optional[_projen_04054675.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[_projen_04054675.LoggerOptions], result)

    @builtins.property
    def major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Major version to release from the default branch.

        If this is specified, we bump the latest version of this major version line.
        If not specified, we bump the global latest version.

        :default: - Major version is not enforced.

        :stability: experimental
        '''
        result = self._values.get("major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The maximum node version supported by this package.

        Most projects should not use this option.
        The value indicates that the package is incompatible with any newer versions of node.
        This requirement is enforced via the engines field.

        You will normally not need to set this option.
        Consider this option only if your package is known to not function with newer versions of node.

        :default: - no maximum version is enforced

        :stability: experimental
        '''
        result = self._values.get("max_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether mergify should be enabled on this repository or not.

        :default: true

        :deprecated: use ``githubOptions.mergify`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.MergifyOptions]:
        '''(deprecated) Options for mergify.

        :default: - default options

        :deprecated: use ``githubOptions.mergifyOptions`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional[_projen_github_04054675.MergifyOptions], result)

    @builtins.property
    def min_major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Minimal Major version to release.

        This can be useful to set to 1, as breaking changes before the 1.x major
        release are not incrementing the major version number.

        Can not be set together with ``majorVersion``.

        :default: - No minimum version is being enforced

        :stability: experimental
        '''
        result = self._values.get("min_major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The minimum node version required by this package to function.

        Most projects should not use this option.
        The value indicates that the package is incompatible with any older versions of node.
        This requirement is enforced via the engines field.

        You will normally not need to set this option, even if your package is incompatible with EOL versions of node.
        Consider this option only if your package depends on a specific feature, that is not available in other LTS versions.
        Setting this option has very high impact on the consumers of your package,
        as package managers will actively prevent usage with node versions you have marked as incompatible.

        To change the node version of your CI/CD workflows, use ``workflowNodeVersion``.

        :default: - no minimum version is enforced

        :stability: experimental
        '''
        result = self._values.get("min_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mutable_build(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically update files modified during builds to pull-request branches.

        This means
        that any files synthesized by projen or e.g. test snapshots will always be up-to-date
        before a PR is merged.

        Implies that PR builds do not have anti-tamper checks.

        :default: true

        :deprecated: - Use ``buildWorkflowOptions.mutableBuild``

        :stability: deprecated
        '''
        result = self._values.get("mutable_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def next_version_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) A shell command to control the next version to release.

        If present, this shell command will be run before the bump is executed, and
        it determines what version to release. It will be executed in the following
        environment:

        - Working directory: the project directory.
        - ``$VERSION``: the current version. Looks like ``1.2.3``.
        - ``$LATEST_TAG``: the most recent tag. Looks like ``prefix-v1.2.3``, or may be unset.
        - ``$SUGGESTED_BUMP``: the suggested bump action based on commits. One of ``major|minor|patch|none``.

        The command should print one of the following to ``stdout``:

        - Nothing: the next version number will be determined based on commit history.
        - ``x.y.z``: the next version number will be ``x.y.z``.
        - ``major|minor|patch``: the next version number will be the current version number
          with the indicated component bumped.

        This setting cannot be specified together with ``minMajorVersion``; the invoked
        script can be used to achieve the effects of ``minMajorVersion``.

        :default: - The next version will be determined based on the commit history and project settings.

        :stability: experimental
        '''
        result = self._values.get("next_version_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_access(self) -> typing.Optional[_projen_javascript_04054675.NpmAccess]:
        '''(experimental) Access level of the npm package.

        :default:

        - for scoped packages (e.g. ``foo@bar``), the default is
        ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is
        ``NpmAccess.PUBLIC``.

        :stability: experimental
        '''
        result = self._values.get("npm_access")
        return typing.cast(typing.Optional[_projen_javascript_04054675.NpmAccess], result)

    @builtins.property
    def npm_dist_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) The npmDistTag to use when publishing from the default branch.

        To set the npm dist-tag for release branches, set the ``npmDistTag`` property
        for each branch.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("npm_dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npmignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) Additional entries to .npmignore.

        :deprecated: - use ``project.addPackageIgnore``

        :stability: deprecated
        '''
        result = self._values.get("npmignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def npmignore_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("npmignore_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def npm_ignore_options(self) -> typing.Optional[_projen_04054675.IgnoreFileOptions]:
        '''(experimental) Configuration options for .npmignore file.

        :stability: experimental
        '''
        result = self._values.get("npm_ignore_options")
        return typing.cast(typing.Optional[_projen_04054675.IgnoreFileOptions], result)

    @builtins.property
    def npm_provenance(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Should provenance statements be generated when the package is published.

        A supported package manager is required to publish a package with npm provenance statements and
        you will need to use a supported CI/CD provider.

        Note that the projen ``Release`` and ``Publisher`` components are using ``publib`` to publish packages,
        which is using npm internally and supports provenance statements independently of the package manager used.

        :default: - true for public packages, false otherwise

        :stability: experimental
        '''
        result = self._values.get("npm_provenance")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def npm_registry(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The host name of the npm registry to publish to.

        Cannot be set together with ``npmRegistryUrl``.

        :deprecated: use ``npmRegistryUrl`` instead

        :stability: deprecated
        '''
        result = self._values.get("npm_registry")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_registry_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The base URL of the npm package registry.

        Must be a URL (e.g. start with "https://" or "http://")

        :default: "https://registry.npmjs.org"

        :stability: experimental
        '''
        result = self._values.get("npm_registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the NPM token to use when publishing packages.

        :default: "NPM_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("npm_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project. Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        subprojects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def package(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``).

        :default: true

        :stability: experimental
        '''
        result = self._values.get("package")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def package_manager(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.NodePackageManager]:
        '''(experimental) The Node Package Manager used to execute scripts.

        :default: NodePackageManager.YARN_CLASSIC

        :stability: experimental
        '''
        result = self._values.get("package_manager")
        return typing.cast(typing.Optional[_projen_javascript_04054675.NodePackageManager], result)

    @builtins.property
    def package_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The "name" in package.json.

        :default: - defaults to project name

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("package_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[_projen_04054675.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[_projen_04054675.Project], result)

    @builtins.property
    def peer_dependency_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.PeerDependencyOptions]:
        '''(experimental) Options for ``peerDeps``.

        :stability: experimental
        '''
        result = self._values.get("peer_dependency_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.PeerDependencyOptions], result)

    @builtins.property
    def peer_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Peer dependencies for this module.

        Dependencies listed here are required to
        be installed (and satisfied) by the *consumer* of this library. Using peer
        dependencies allows you to ensure that only a single module of a certain
        library exists in the ``node_modules`` tree of your consumers.

        Note that prior to npm@7, peer dependencies are *not* automatically
        installed, which means that adding peer dependencies to a library will be a
        breaking change for your customers.

        Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is
        enabled by default), projen will automatically add a dev dependency with a
        pinned version for each peer dependency. This will ensure that you build &
        test your module against the lowest peer version required.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("peer_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pnpm_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of PNPM to use if using PNPM as a package manager.

        :default: "9"

        :stability: experimental
        '''
        result = self._values.get("pnpm_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_build_steps(
        self,
    ) -> typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]]:
        '''(experimental) Steps to execute after build as part of the release workflow.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]], result)

    @builtins.property
    def prerelease(self) -> typing.Optional[builtins.str]:
        '''(experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre").

        :default: - normal semantic versions

        :stability: experimental
        '''
        result = self._values.get("prerelease")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prettier(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup prettier.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("prettier")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def prettier_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.PrettierOptions]:
        '''(experimental) Prettier options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("prettier_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.PrettierOptions], result)

    @builtins.property
    def project_type(self) -> typing.Optional[_projen_04054675.ProjectType]:
        '''(deprecated) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :deprecated: no longer supported at the base project level

        :stability: deprecated
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[_projen_04054675.ProjectType], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_credentials(
        self,
    ) -> typing.Optional[_projen_github_04054675.GithubCredentials]:
        '''(experimental) Choose a method of providing GitHub API access for projen workflows.

        :default: - use a personal access token named PROJEN_GITHUB_TOKEN

        :stability: experimental
        '''
        result = self._values.get("projen_credentials")
        return typing.cast(typing.Optional[_projen_github_04054675.GithubCredentials], result)

    @builtins.property
    def projen_dev_dependency(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates of "projen" should be installed as a devDependency.

        :default: - true if not a subproject

        :stability: experimental
        '''
        result = self._values.get("projen_dev_dependency")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation.

        :default: - true if projenrcJson is false

        :stability: experimental
        '''
        result = self._values.get("projenrc_js")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(
        self,
    ) -> typing.Optional[_projen_04054675.ProjenrcJsonOptions]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[_projen_04054675.ProjenrcJsonOptions], result)

    @builtins.property
    def projenrc_js_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.js.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_js_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.ProjenrcOptions], result)

    @builtins.property
    def projenrc_ts(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use TypeScript for your projenrc file (``.projenrc.ts``).

        :default: false

        :stability: experimental
        :pjnew: true
        '''
        result = self._values.get("projenrc_ts")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_ts_options(
        self,
    ) -> typing.Optional[_projen_typescript_04054675.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.ts.

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts_options")
        return typing.cast(typing.Optional[_projen_typescript_04054675.ProjenrcOptions], result)

    @builtins.property
    def projen_token_secret(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows.

        This token needs to have the ``repo``, ``workflows``
        and ``packages`` scope.

        :default: "PROJEN_GITHUB_TOKEN"

        :deprecated: use ``projenCredentials``

        :stability: deprecated
        '''
        result = self._values.get("projen_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of projen to install.

        :default: - Defaults to the latest version.

        :stability: experimental
        '''
        result = self._values.get("projen_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_dry_run(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Instead of actually publishing to package managers, just print the publishing command.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_dry_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_tasks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define publishing tasks that can be executed manually as well as workflows.

        Normally, publishing only happens within automated workflows. Enable this
        in order to create a publishing task for each publishing activity.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_tasks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_request_template(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include a GitHub pull request template.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("pull_request_template")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_request_template_contents(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The contents of the pull request template.

        :default: - default content

        :stability: experimental
        '''
        result = self._values.get("pull_request_template_contents")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def readme(self) -> typing.Optional["ReadmeOptions"]:
        '''Configuration of the README.md file.'''
        result = self._values.get("readme")
        return typing.cast(typing.Optional["ReadmeOptions"], result)

    @builtins.property
    def releasable_commits(self) -> typing.Optional[_projen_04054675.ReleasableCommits]:
        '''(experimental) Find commits that should be considered releasable Used to decide if a release is required.

        :default: ReleasableCommits.everyCommit()

        :stability: experimental
        '''
        result = self._values.get("releasable_commits")
        return typing.cast(typing.Optional[_projen_04054675.ReleasableCommits], result)

    @builtins.property
    def release(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add release management to this project.

        :default: - true (false for subprojects)

        :stability: experimental
        '''
        result = self._values.get("release")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_branches(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _projen_release_04054675.BranchOptions]]:
        '''(experimental) Defines additional release branches.

        A workflow will be created for each
        release branch which will publish releases from commits in this branch.
        Each release branch *must* be assigned a major version number which is used
        to enforce that versions published from that branch always use that major
        version. If multiple branches are used, the ``majorVersion`` field must also
        be provided for the default branch.

        :default:

        - no additional branches are used for release. you can use
        ``addBranch()`` to add additional branches.

        :stability: experimental
        '''
        result = self._values.get("release_branches")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _projen_release_04054675.BranchOptions]], result)

    @builtins.property
    def release_every_commit(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``.

        :default: true

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.continuous()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_every_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create a github issue on every failed publishing task.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The label to apply to issues indicating publish failures.

        Only applies if ``releaseFailureIssue`` is true.

        :default: "failed-release"

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_schedule(self) -> typing.Optional[builtins.str]:
        '''(deprecated) CRON schedule to trigger new releases.

        :default: - no scheduled releases

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.scheduled()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_tag_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Automatically add the given prefix to release tags.

        Useful if you are releasing on multiple branches with overlapping version numbers.
        Note: this prefix is used to detect the latest tagged version
        when bumping, so if you change this on a project with an existing version
        history, you may need to manually tag your latest release
        with the new prefix.

        :default: "v"

        :stability: experimental
        '''
        result = self._values.get("release_tag_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_to_npm(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically release to npm when new versions are introduced.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_to_npm")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_trigger(
        self,
    ) -> typing.Optional[_projen_release_04054675.ReleaseTrigger]:
        '''(experimental) The release trigger to use.

        :default: - Continuous releases (``ReleaseTrigger.continuous()``)

        :stability: experimental
        '''
        result = self._values.get("release_trigger")
        return typing.cast(typing.Optional[_projen_release_04054675.ReleaseTrigger], result)

    @builtins.property
    def release_workflow(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) DEPRECATED: renamed to ``release``.

        :default: - true if not a subproject

        :deprecated: see ``release``.

        :stability: deprecated
        '''
        result = self._values.get("release_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_workflow_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the default release workflow.

        :default: "release"

        :stability: experimental
        '''
        result = self._values.get("release_workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_workflow_setup_steps(
        self,
    ) -> typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]]:
        '''(experimental) A set of workflow steps to execute in order to setup the workflow container.

        :stability: experimental
        '''
        result = self._values.get("release_workflow_setup_steps")
        return typing.cast(typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]], result)

    @builtins.property
    def renovatebot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use renovatebot to handle dependency upgrades.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("renovatebot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def renovatebot_options(
        self,
    ) -> typing.Optional[_projen_04054675.RenovatebotOptions]:
        '''(experimental) Options for renovatebot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("renovatebot_options")
        return typing.cast(typing.Optional[_projen_04054675.RenovatebotOptions], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) The repository is the location where the actual code for your package lives.

        See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.

        :stability: experimental
        '''
        result = self._values.get("repository_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sample_code(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sample_code")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def scoped_packages_options(
        self,
    ) -> typing.Optional[typing.List[_projen_javascript_04054675.ScopedPackagesOptions]]:
        '''(experimental) Options for privately hosted scoped packages.

        :default: - fetch all scoped packages from the public npm registry

        :stability: experimental
        '''
        result = self._values.get("scoped_packages_options")
        return typing.cast(typing.Optional[typing.List[_projen_javascript_04054675.ScopedPackagesOptions]], result)

    @builtins.property
    def scripts(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(deprecated) npm scripts to include.

        If a script has the same name as a standard script,
        the standard script will be overwritten.
        Also adds the script as a task.

        :default: {}

        :deprecated: use ``project.addTask()`` or ``package.setScript()``

        :stability: deprecated
        '''
        result = self._values.get("scripts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def srcdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript sources directory.

        :default: "src"

        :stability: experimental
        '''
        result = self._values.get("srcdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stability(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Stability.

        :stability: experimental
        '''
        result = self._values.get("stability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stale(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto-close of stale issues and pull request.

        See ``staleOptions`` for options.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("stale")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_options(self) -> typing.Optional[_projen_github_04054675.StaleOptions]:
        '''(experimental) Auto-close stale issues and pull requests.

        To disable set ``stale`` to ``false``.

        :default: - see defaults in ``StaleOptions``

        :stability: experimental
        '''
        result = self._values.get("stale_options")
        return typing.cast(typing.Optional[_projen_github_04054675.StaleOptions], result)

    @builtins.property
    def testdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Jest tests directory.

        Tests files should be named ``xxx.test.ts``.
        If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``),
        then tests are going to be compiled into ``lib/`` and executed as javascript.
        If the test directory is outside of ``src``, then we configure jest to
        compile the code in-memory.

        :default: "test"

        :stability: experimental
        '''
        result = self._values.get("testdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tsconfig(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions]:
        '''(experimental) Custom TSConfig.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("tsconfig")
        return typing.cast(typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions]:
        '''(experimental) Custom tsconfig options for the development tsconfig.json file (used for testing).

        :default: - use the production tsconfig options

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev")
        return typing.cast(typing.Optional[_projen_javascript_04054675.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev_file(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the development tsconfig.json file.

        :default: "tsconfig.dev.json"

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ts_jest_options(
        self,
    ) -> typing.Optional[_projen_typescript_04054675.TsJestOptions]:
        '''(experimental) Options for ts-jest.

        :stability: experimental
        '''
        result = self._values.get("ts_jest_options")
        return typing.cast(typing.Optional[_projen_typescript_04054675.TsJestOptions], result)

    @builtins.property
    def typescript_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) TypeScript version to use.

        NOTE: Typescript is not semantically versioned and should remain on the
        same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``).

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("typescript_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def versionrc_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Custom configuration used when creating changelog with commit-and-tag-version package.

        Given values either append to default configuration or overwrite values in it.

        :default: - standard configuration applicable for GitHub repositories

        :stability: experimental
        '''
        result = self._values.get("versionrc_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def vscode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable VSCode integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("vscode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def workflow_bootstrap_steps(
        self,
    ) -> typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]]:
        '''(experimental) Workflow steps to use in order to bootstrap this repo.

        :default: "yarn install --frozen-lockfile && yarn projen"

        :stability: experimental
        '''
        result = self._values.get("workflow_bootstrap_steps")
        return typing.cast(typing.Optional[typing.List[_projen_github_workflows_04054675.JobStep]], result)

    @builtins.property
    def workflow_container_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Container image to use for GitHub workflows.

        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("workflow_container_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_git_identity(
        self,
    ) -> typing.Optional[_projen_github_04054675.GitIdentity]:
        '''(experimental) The git identity to use in workflows.

        :default: - GitHub Actions

        :stability: experimental
        '''
        result = self._values.get("workflow_git_identity")
        return typing.cast(typing.Optional[_projen_github_04054675.GitIdentity], result)

    @builtins.property
    def workflow_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The node version used in GitHub Actions workflows.

        Always use this option if your GitHub Actions workflows require a specific to run.

        :default: - ``minNodeVersion`` if set, otherwise ``lts/*``.

        :stability: experimental
        '''
        result = self._values.get("workflow_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_package_cache(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable Node.js package cache in GitHub workflows.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("workflow_package_cache")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def workflow_runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        :description: Defines a target Runner by labels
        :throws: {Error} if both ``runsOn`` and ``runsOnGroup`` are specified
        '''
        result = self._values.get("workflow_runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def workflow_runs_on_group(
        self,
    ) -> typing.Optional[_projen_04054675.GroupRunnerOptions]:
        '''(experimental) Github Runner Group selection options.

        :stability: experimental
        :description: Defines a target Runner Group by name and/or labels
        :throws: {Error} if both ``runsOn`` and ``runsOnGroup`` are specified
        '''
        result = self._values.get("workflow_runs_on_group")
        return typing.cast(typing.Optional[_projen_04054675.GroupRunnerOptions], result)

    @builtins.property
    def yarn_berry_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.YarnBerryOptions]:
        '''(experimental) Options for Yarn Berry.

        :default: - Yarn Berry v4 with all default options

        :stability: experimental
        '''
        result = self._values.get("yarn_berry_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.YarnBerryOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NpmPackageOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PythonPackage(
    _projen_python_04054675.PythonProject,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-modules.PythonPackage",
):
    '''A Python package.

    :pjid: python-package
    '''

    def __init__(
        self,
        *,
        author_email: builtins.str,
        author_name: builtins.str,
        code_owners: typing.Sequence[builtins.str],
        module_name: builtins.str,
        name: builtins.str,
        version: builtins.str,
        auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        clobber: typing.Optional[builtins.bool] = None,
        commit_generated: typing.Optional[builtins.bool] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        homepage: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        package_name: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        pip: typing.Optional[builtins.bool] = None,
        poetry: typing.Optional[builtins.bool] = None,
        poetry_options: typing.Optional[typing.Union[_projen_python_04054675.PoetryPyprojectOptionsWithoutDeps, typing.Dict[builtins.str, typing.Any]]] = None,
        project_type: typing.Optional[_projen_04054675.ProjectType] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_python: typing.Optional[builtins.bool] = None,
        projenrc_python_options: typing.Optional[typing.Union[_projen_python_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcTsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        pytest: typing.Optional[builtins.bool] = None,
        pytest_options: typing.Optional[typing.Union[_projen_python_04054675.PytestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        python_exec: typing.Optional[builtins.str] = None,
        readme: typing.Optional[typing.Union["ReadmeOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        sample: typing.Optional[builtins.bool] = None,
        sample_testdir: typing.Optional[builtins.str] = None,
        setup_config: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        setuptools: typing.Optional[builtins.bool] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        venv: typing.Optional[builtins.bool] = None,
        venv_options: typing.Optional[typing.Union[_projen_python_04054675.VenvOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vscode: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param author_email: (experimental) Author's e-mail. Default: $GIT_USER_EMAIL
        :param author_name: (experimental) Author's name. Default: $GIT_USER_NAME
        :param code_owners: List of teams used to generate the CODEOWNERS file.
        :param module_name: (experimental) Name of the python package as used in imports and filenames. Must only consist of alphanumeric characters and underscores. Default: $PYTHON_MODULE_NAME
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param version: (experimental) Version of the package. Default: "0.1.0"
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: - true, but false for subprojects
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param deps: (experimental) List of runtime dependencies for this project. Dependencies use the format: ``<module>@<semver>``. Additional dependencies can be added via ``project.addDependency()``. Default: []
        :param description: (experimental) A short description of the package.
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param dev_deps: (experimental) List of dev dependencies for this project. Dependencies use the format: ``<module>@<semver>``. Additional dependencies can be added via ``project.addDevDependency()``. Default: []
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param homepage: (experimental) A URL to the website of the project.
        :param license: (experimental) License of this package as an SPDX identifier.
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other subprojects. Default: "."
        :param package_name: (experimental) Package name.
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param pip: (experimental) Use pip with a requirements.txt file to track project dependencies. Default: - true, unless poetry is true, then false
        :param poetry: (experimental) Use poetry to manage your project dependencies, virtual environment, and (optional) packaging/publishing. This feature is incompatible with pip, setuptools, or venv. If you set this option to ``true``, then pip, setuptools, and venv must be set to ``false``. Default: false
        :param poetry_options: (experimental) Additional options to set for poetry if using poetry.
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projenrc_js: (experimental) Use projenrc in javascript. This will install ``projen`` as a JavaScript dependency and add a ``synth`` task which will run ``.projenrc.js``. Default: false
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param projenrc_js_options: (experimental) Options related to projenrc in JavaScript. Default: - default options
        :param projenrc_python: (experimental) Use projenrc in Python. This will install ``projen`` as a Python dependency and add a ``synth`` task which will run ``.projenrc.py``. Default: true
        :param projenrc_python_options: (experimental) Options related to projenrc in python. Default: - default options
        :param projenrc_ts: (experimental) Use projenrc in TypeScript. This will create a tsconfig file (default: ``tsconfig.projen.json``) and use ``ts-node`` in the default task to parse the project source files. Default: false
        :param projenrc_ts_options: (experimental) Options related to projenrc in TypeScript. Default: - default options
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param pull_request_template: Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: The contents of the pull request template. Default: default content
        :param pytest: (experimental) Include pytest tests. Default: true
        :param pytest_options: (experimental) pytest options. Default: - defaults
        :param python_exec: (experimental) Path to the python executable to use. Default: "python"
        :param readme: Configuration of the README.md file.
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param sample: (experimental) Include sample code and test if the relevant directories don't exist. Default: true
        :param sample_testdir: (experimental) Location of sample tests. Typically the same directory where project tests will be located. Default: "tests"
        :param setup_config: (experimental) Additional fields to pass in the setup() function if using setuptools.
        :param setuptools: (experimental) Use setuptools with a setup.py script for packaging and publishing. Default: - true, unless poetry is true, then false
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param venv: (experimental) Use venv to manage a virtual environment for installing dependencies inside. Default: - true, unless poetry is true, then false
        :param venv_options: (experimental) Venv options. Default: - defaults
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        '''
        options = PythonPackageOptions(
            author_email=author_email,
            author_name=author_name,
            code_owners=code_owners,
            module_name=module_name,
            name=name,
            version=version,
            auto_approve_options=auto_approve_options,
            auto_merge=auto_merge,
            auto_merge_options=auto_merge_options,
            classifiers=classifiers,
            clobber=clobber,
            commit_generated=commit_generated,
            deps=deps,
            description=description,
            dev_container=dev_container,
            dev_deps=dev_deps,
            github=github,
            github_options=github_options,
            git_ignore_options=git_ignore_options,
            git_options=git_options,
            gitpod=gitpod,
            homepage=homepage,
            license=license,
            logging=logging,
            mergify=mergify,
            mergify_options=mergify_options,
            outdir=outdir,
            package_name=package_name,
            parent=parent,
            pip=pip,
            poetry=poetry,
            poetry_options=poetry_options,
            project_type=project_type,
            projen_command=projen_command,
            projen_credentials=projen_credentials,
            projenrc_js=projenrc_js,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
            projenrc_js_options=projenrc_js_options,
            projenrc_python=projenrc_python,
            projenrc_python_options=projenrc_python_options,
            projenrc_ts=projenrc_ts,
            projenrc_ts_options=projenrc_ts_options,
            projen_token_secret=projen_token_secret,
            pull_request_template=pull_request_template,
            pull_request_template_contents=pull_request_template_contents,
            pytest=pytest,
            pytest_options=pytest_options,
            python_exec=python_exec,
            readme=readme,
            renovatebot=renovatebot,
            renovatebot_options=renovatebot_options,
            sample=sample,
            sample_testdir=sample_testdir,
            setup_config=setup_config,
            setuptools=setuptools,
            stale=stale,
            stale_options=stale_options,
            venv=venv,
            venv_options=venv_options,
            vscode=vscode,
        )

        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="readme")
    def readme(self) -> "Readme":
        return typing.cast("Readme", jsii.get(self, "readme"))

    @readme.setter
    def readme(self, value: "Readme") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a456e663d7da59de9fd68ca5bb5f5bc98971d99102fdb04adfe975c14215095)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readme", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="projen-modules.PythonPackageOptions",
    jsii_struct_bases=[],
    name_mapping={
        "author_email": "authorEmail",
        "author_name": "authorName",
        "code_owners": "codeOwners",
        "module_name": "moduleName",
        "name": "name",
        "version": "version",
        "auto_approve_options": "autoApproveOptions",
        "auto_merge": "autoMerge",
        "auto_merge_options": "autoMergeOptions",
        "classifiers": "classifiers",
        "clobber": "clobber",
        "commit_generated": "commitGenerated",
        "deps": "deps",
        "description": "description",
        "dev_container": "devContainer",
        "dev_deps": "devDeps",
        "github": "github",
        "github_options": "githubOptions",
        "git_ignore_options": "gitIgnoreOptions",
        "git_options": "gitOptions",
        "gitpod": "gitpod",
        "homepage": "homepage",
        "license": "license",
        "logging": "logging",
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "outdir": "outdir",
        "package_name": "packageName",
        "parent": "parent",
        "pip": "pip",
        "poetry": "poetry",
        "poetry_options": "poetryOptions",
        "project_type": "projectType",
        "projen_command": "projenCommand",
        "projen_credentials": "projenCredentials",
        "projenrc_js": "projenrcJs",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "projenrc_js_options": "projenrcJsOptions",
        "projenrc_python": "projenrcPython",
        "projenrc_python_options": "projenrcPythonOptions",
        "projenrc_ts": "projenrcTs",
        "projenrc_ts_options": "projenrcTsOptions",
        "projen_token_secret": "projenTokenSecret",
        "pull_request_template": "pullRequestTemplate",
        "pull_request_template_contents": "pullRequestTemplateContents",
        "pytest": "pytest",
        "pytest_options": "pytestOptions",
        "python_exec": "pythonExec",
        "readme": "readme",
        "renovatebot": "renovatebot",
        "renovatebot_options": "renovatebotOptions",
        "sample": "sample",
        "sample_testdir": "sampleTestdir",
        "setup_config": "setupConfig",
        "setuptools": "setuptools",
        "stale": "stale",
        "stale_options": "staleOptions",
        "venv": "venv",
        "venv_options": "venvOptions",
        "vscode": "vscode",
    },
)
class PythonPackageOptions:
    def __init__(
        self,
        *,
        author_email: builtins.str,
        author_name: builtins.str,
        code_owners: typing.Sequence[builtins.str],
        module_name: builtins.str,
        name: builtins.str,
        version: builtins.str,
        auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        clobber: typing.Optional[builtins.bool] = None,
        commit_generated: typing.Optional[builtins.bool] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        homepage: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        package_name: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        pip: typing.Optional[builtins.bool] = None,
        poetry: typing.Optional[builtins.bool] = None,
        poetry_options: typing.Optional[typing.Union[_projen_python_04054675.PoetryPyprojectOptionsWithoutDeps, typing.Dict[builtins.str, typing.Any]]] = None,
        project_type: typing.Optional[_projen_04054675.ProjectType] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_python: typing.Optional[builtins.bool] = None,
        projenrc_python_options: typing.Optional[typing.Union[_projen_python_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcTsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        pytest: typing.Optional[builtins.bool] = None,
        pytest_options: typing.Optional[typing.Union[_projen_python_04054675.PytestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        python_exec: typing.Optional[builtins.str] = None,
        readme: typing.Optional[typing.Union["ReadmeOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        sample: typing.Optional[builtins.bool] = None,
        sample_testdir: typing.Optional[builtins.str] = None,
        setup_config: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        setuptools: typing.Optional[builtins.bool] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        venv: typing.Optional[builtins.bool] = None,
        venv_options: typing.Optional[typing.Union[_projen_python_04054675.VenvOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vscode: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''PythonPackageOptions.

        :param author_email: (experimental) Author's e-mail. Default: $GIT_USER_EMAIL
        :param author_name: (experimental) Author's name. Default: $GIT_USER_NAME
        :param code_owners: List of teams used to generate the CODEOWNERS file.
        :param module_name: (experimental) Name of the python package as used in imports and filenames. Must only consist of alphanumeric characters and underscores. Default: $PYTHON_MODULE_NAME
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param version: (experimental) Version of the package. Default: "0.1.0"
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: - true, but false for subprojects
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param deps: (experimental) List of runtime dependencies for this project. Dependencies use the format: ``<module>@<semver>``. Additional dependencies can be added via ``project.addDependency()``. Default: []
        :param description: (experimental) A short description of the package.
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param dev_deps: (experimental) List of dev dependencies for this project. Dependencies use the format: ``<module>@<semver>``. Additional dependencies can be added via ``project.addDevDependency()``. Default: []
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param homepage: (experimental) A URL to the website of the project.
        :param license: (experimental) License of this package as an SPDX identifier.
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other subprojects. Default: "."
        :param package_name: (experimental) Package name.
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param pip: (experimental) Use pip with a requirements.txt file to track project dependencies. Default: - true, unless poetry is true, then false
        :param poetry: (experimental) Use poetry to manage your project dependencies, virtual environment, and (optional) packaging/publishing. This feature is incompatible with pip, setuptools, or venv. If you set this option to ``true``, then pip, setuptools, and venv must be set to ``false``. Default: false
        :param poetry_options: (experimental) Additional options to set for poetry if using poetry.
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projenrc_js: (experimental) Use projenrc in javascript. This will install ``projen`` as a JavaScript dependency and add a ``synth`` task which will run ``.projenrc.js``. Default: false
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param projenrc_js_options: (experimental) Options related to projenrc in JavaScript. Default: - default options
        :param projenrc_python: (experimental) Use projenrc in Python. This will install ``projen`` as a Python dependency and add a ``synth`` task which will run ``.projenrc.py``. Default: true
        :param projenrc_python_options: (experimental) Options related to projenrc in python. Default: - default options
        :param projenrc_ts: (experimental) Use projenrc in TypeScript. This will create a tsconfig file (default: ``tsconfig.projen.json``) and use ``ts-node`` in the default task to parse the project source files. Default: false
        :param projenrc_ts_options: (experimental) Options related to projenrc in TypeScript. Default: - default options
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param pull_request_template: Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: The contents of the pull request template. Default: default content
        :param pytest: (experimental) Include pytest tests. Default: true
        :param pytest_options: (experimental) pytest options. Default: - defaults
        :param python_exec: (experimental) Path to the python executable to use. Default: "python"
        :param readme: Configuration of the README.md file.
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param sample: (experimental) Include sample code and test if the relevant directories don't exist. Default: true
        :param sample_testdir: (experimental) Location of sample tests. Typically the same directory where project tests will be located. Default: "tests"
        :param setup_config: (experimental) Additional fields to pass in the setup() function if using setuptools.
        :param setuptools: (experimental) Use setuptools with a setup.py script for packaging and publishing. Default: - true, unless poetry is true, then false
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param venv: (experimental) Use venv to manage a virtual environment for installing dependencies inside. Default: - true, unless poetry is true, then false
        :param venv_options: (experimental) Venv options. Default: - defaults
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        '''
        if isinstance(auto_approve_options, dict):
            auto_approve_options = _projen_github_04054675.AutoApproveOptions(**auto_approve_options)
        if isinstance(auto_merge_options, dict):
            auto_merge_options = _projen_github_04054675.AutoMergeOptions(**auto_merge_options)
        if isinstance(github_options, dict):
            github_options = _projen_github_04054675.GitHubOptions(**github_options)
        if isinstance(git_ignore_options, dict):
            git_ignore_options = _projen_04054675.IgnoreFileOptions(**git_ignore_options)
        if isinstance(git_options, dict):
            git_options = _projen_04054675.GitOptions(**git_options)
        if isinstance(logging, dict):
            logging = _projen_04054675.LoggerOptions(**logging)
        if isinstance(mergify_options, dict):
            mergify_options = _projen_github_04054675.MergifyOptions(**mergify_options)
        if isinstance(poetry_options, dict):
            poetry_options = _projen_python_04054675.PoetryPyprojectOptionsWithoutDeps(**poetry_options)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = _projen_04054675.ProjenrcJsonOptions(**projenrc_json_options)
        if isinstance(projenrc_js_options, dict):
            projenrc_js_options = _projen_javascript_04054675.ProjenrcOptions(**projenrc_js_options)
        if isinstance(projenrc_python_options, dict):
            projenrc_python_options = _projen_python_04054675.ProjenrcOptions(**projenrc_python_options)
        if isinstance(projenrc_ts_options, dict):
            projenrc_ts_options = _projen_typescript_04054675.ProjenrcTsOptions(**projenrc_ts_options)
        if isinstance(pytest_options, dict):
            pytest_options = _projen_python_04054675.PytestOptions(**pytest_options)
        if isinstance(readme, dict):
            readme = ReadmeOptions(**readme)
        if isinstance(renovatebot_options, dict):
            renovatebot_options = _projen_04054675.RenovatebotOptions(**renovatebot_options)
        if isinstance(stale_options, dict):
            stale_options = _projen_github_04054675.StaleOptions(**stale_options)
        if isinstance(venv_options, dict):
            venv_options = _projen_python_04054675.VenvOptions(**venv_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__882525f8fb69251a060fbbe97c2383313ea4b9c0269874cb1d13172a5420010c)
            check_type(argname="argument author_email", value=author_email, expected_type=type_hints["author_email"])
            check_type(argname="argument author_name", value=author_name, expected_type=type_hints["author_name"])
            check_type(argname="argument code_owners", value=code_owners, expected_type=type_hints["code_owners"])
            check_type(argname="argument module_name", value=module_name, expected_type=type_hints["module_name"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument auto_approve_options", value=auto_approve_options, expected_type=type_hints["auto_approve_options"])
            check_type(argname="argument auto_merge", value=auto_merge, expected_type=type_hints["auto_merge"])
            check_type(argname="argument auto_merge_options", value=auto_merge_options, expected_type=type_hints["auto_merge_options"])
            check_type(argname="argument classifiers", value=classifiers, expected_type=type_hints["classifiers"])
            check_type(argname="argument clobber", value=clobber, expected_type=type_hints["clobber"])
            check_type(argname="argument commit_generated", value=commit_generated, expected_type=type_hints["commit_generated"])
            check_type(argname="argument deps", value=deps, expected_type=type_hints["deps"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument dev_container", value=dev_container, expected_type=type_hints["dev_container"])
            check_type(argname="argument dev_deps", value=dev_deps, expected_type=type_hints["dev_deps"])
            check_type(argname="argument github", value=github, expected_type=type_hints["github"])
            check_type(argname="argument github_options", value=github_options, expected_type=type_hints["github_options"])
            check_type(argname="argument git_ignore_options", value=git_ignore_options, expected_type=type_hints["git_ignore_options"])
            check_type(argname="argument git_options", value=git_options, expected_type=type_hints["git_options"])
            check_type(argname="argument gitpod", value=gitpod, expected_type=type_hints["gitpod"])
            check_type(argname="argument homepage", value=homepage, expected_type=type_hints["homepage"])
            check_type(argname="argument license", value=license, expected_type=type_hints["license"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument mergify", value=mergify, expected_type=type_hints["mergify"])
            check_type(argname="argument mergify_options", value=mergify_options, expected_type=type_hints["mergify_options"])
            check_type(argname="argument outdir", value=outdir, expected_type=type_hints["outdir"])
            check_type(argname="argument package_name", value=package_name, expected_type=type_hints["package_name"])
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument pip", value=pip, expected_type=type_hints["pip"])
            check_type(argname="argument poetry", value=poetry, expected_type=type_hints["poetry"])
            check_type(argname="argument poetry_options", value=poetry_options, expected_type=type_hints["poetry_options"])
            check_type(argname="argument project_type", value=project_type, expected_type=type_hints["project_type"])
            check_type(argname="argument projen_command", value=projen_command, expected_type=type_hints["projen_command"])
            check_type(argname="argument projen_credentials", value=projen_credentials, expected_type=type_hints["projen_credentials"])
            check_type(argname="argument projenrc_js", value=projenrc_js, expected_type=type_hints["projenrc_js"])
            check_type(argname="argument projenrc_json", value=projenrc_json, expected_type=type_hints["projenrc_json"])
            check_type(argname="argument projenrc_json_options", value=projenrc_json_options, expected_type=type_hints["projenrc_json_options"])
            check_type(argname="argument projenrc_js_options", value=projenrc_js_options, expected_type=type_hints["projenrc_js_options"])
            check_type(argname="argument projenrc_python", value=projenrc_python, expected_type=type_hints["projenrc_python"])
            check_type(argname="argument projenrc_python_options", value=projenrc_python_options, expected_type=type_hints["projenrc_python_options"])
            check_type(argname="argument projenrc_ts", value=projenrc_ts, expected_type=type_hints["projenrc_ts"])
            check_type(argname="argument projenrc_ts_options", value=projenrc_ts_options, expected_type=type_hints["projenrc_ts_options"])
            check_type(argname="argument projen_token_secret", value=projen_token_secret, expected_type=type_hints["projen_token_secret"])
            check_type(argname="argument pull_request_template", value=pull_request_template, expected_type=type_hints["pull_request_template"])
            check_type(argname="argument pull_request_template_contents", value=pull_request_template_contents, expected_type=type_hints["pull_request_template_contents"])
            check_type(argname="argument pytest", value=pytest, expected_type=type_hints["pytest"])
            check_type(argname="argument pytest_options", value=pytest_options, expected_type=type_hints["pytest_options"])
            check_type(argname="argument python_exec", value=python_exec, expected_type=type_hints["python_exec"])
            check_type(argname="argument readme", value=readme, expected_type=type_hints["readme"])
            check_type(argname="argument renovatebot", value=renovatebot, expected_type=type_hints["renovatebot"])
            check_type(argname="argument renovatebot_options", value=renovatebot_options, expected_type=type_hints["renovatebot_options"])
            check_type(argname="argument sample", value=sample, expected_type=type_hints["sample"])
            check_type(argname="argument sample_testdir", value=sample_testdir, expected_type=type_hints["sample_testdir"])
            check_type(argname="argument setup_config", value=setup_config, expected_type=type_hints["setup_config"])
            check_type(argname="argument setuptools", value=setuptools, expected_type=type_hints["setuptools"])
            check_type(argname="argument stale", value=stale, expected_type=type_hints["stale"])
            check_type(argname="argument stale_options", value=stale_options, expected_type=type_hints["stale_options"])
            check_type(argname="argument venv", value=venv, expected_type=type_hints["venv"])
            check_type(argname="argument venv_options", value=venv_options, expected_type=type_hints["venv_options"])
            check_type(argname="argument vscode", value=vscode, expected_type=type_hints["vscode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "author_email": author_email,
            "author_name": author_name,
            "code_owners": code_owners,
            "module_name": module_name,
            "name": name,
            "version": version,
        }
        if auto_approve_options is not None:
            self._values["auto_approve_options"] = auto_approve_options
        if auto_merge is not None:
            self._values["auto_merge"] = auto_merge
        if auto_merge_options is not None:
            self._values["auto_merge_options"] = auto_merge_options
        if classifiers is not None:
            self._values["classifiers"] = classifiers
        if clobber is not None:
            self._values["clobber"] = clobber
        if commit_generated is not None:
            self._values["commit_generated"] = commit_generated
        if deps is not None:
            self._values["deps"] = deps
        if description is not None:
            self._values["description"] = description
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if dev_deps is not None:
            self._values["dev_deps"] = dev_deps
        if github is not None:
            self._values["github"] = github
        if github_options is not None:
            self._values["github_options"] = github_options
        if git_ignore_options is not None:
            self._values["git_ignore_options"] = git_ignore_options
        if git_options is not None:
            self._values["git_options"] = git_options
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if homepage is not None:
            self._values["homepage"] = homepage
        if license is not None:
            self._values["license"] = license
        if logging is not None:
            self._values["logging"] = logging
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if outdir is not None:
            self._values["outdir"] = outdir
        if package_name is not None:
            self._values["package_name"] = package_name
        if parent is not None:
            self._values["parent"] = parent
        if pip is not None:
            self._values["pip"] = pip
        if poetry is not None:
            self._values["poetry"] = poetry
        if poetry_options is not None:
            self._values["poetry_options"] = poetry_options
        if project_type is not None:
            self._values["project_type"] = project_type
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projen_credentials is not None:
            self._values["projen_credentials"] = projen_credentials
        if projenrc_js is not None:
            self._values["projenrc_js"] = projenrc_js
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if projenrc_js_options is not None:
            self._values["projenrc_js_options"] = projenrc_js_options
        if projenrc_python is not None:
            self._values["projenrc_python"] = projenrc_python
        if projenrc_python_options is not None:
            self._values["projenrc_python_options"] = projenrc_python_options
        if projenrc_ts is not None:
            self._values["projenrc_ts"] = projenrc_ts
        if projenrc_ts_options is not None:
            self._values["projenrc_ts_options"] = projenrc_ts_options
        if projen_token_secret is not None:
            self._values["projen_token_secret"] = projen_token_secret
        if pull_request_template is not None:
            self._values["pull_request_template"] = pull_request_template
        if pull_request_template_contents is not None:
            self._values["pull_request_template_contents"] = pull_request_template_contents
        if pytest is not None:
            self._values["pytest"] = pytest
        if pytest_options is not None:
            self._values["pytest_options"] = pytest_options
        if python_exec is not None:
            self._values["python_exec"] = python_exec
        if readme is not None:
            self._values["readme"] = readme
        if renovatebot is not None:
            self._values["renovatebot"] = renovatebot
        if renovatebot_options is not None:
            self._values["renovatebot_options"] = renovatebot_options
        if sample is not None:
            self._values["sample"] = sample
        if sample_testdir is not None:
            self._values["sample_testdir"] = sample_testdir
        if setup_config is not None:
            self._values["setup_config"] = setup_config
        if setuptools is not None:
            self._values["setuptools"] = setuptools
        if stale is not None:
            self._values["stale"] = stale
        if stale_options is not None:
            self._values["stale_options"] = stale_options
        if venv is not None:
            self._values["venv"] = venv
        if venv_options is not None:
            self._values["venv_options"] = venv_options
        if vscode is not None:
            self._values["vscode"] = vscode

    @builtins.property
    def author_email(self) -> builtins.str:
        '''(experimental) Author's e-mail.

        :default: $GIT_USER_EMAIL

        :stability: experimental
        '''
        result = self._values.get("author_email")
        assert result is not None, "Required property 'author_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def author_name(self) -> builtins.str:
        '''(experimental) Author's name.

        :default: $GIT_USER_NAME

        :stability: experimental
        '''
        result = self._values.get("author_name")
        assert result is not None, "Required property 'author_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code_owners(self) -> typing.List[builtins.str]:
        '''List of teams used to generate the CODEOWNERS file.'''
        result = self._values.get("code_owners")
        assert result is not None, "Required property 'code_owners' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def module_name(self) -> builtins.str:
        '''(experimental) Name of the python package as used in imports and filenames.

        Must only consist of alphanumeric characters and underscores.

        :default: $PYTHON_MODULE_NAME

        :stability: experimental
        '''
        result = self._values.get("module_name")
        assert result is not None, "Required property 'module_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) Version of the package.

        :default: "0.1.0"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_approve_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.AutoApproveOptions]:
        '''(experimental) Enable and configure the 'auto approve' workflow.

        :default: - auto approve is disabled

        :stability: experimental
        '''
        result = self._values.get("auto_approve_options")
        return typing.cast(typing.Optional[_projen_github_04054675.AutoApproveOptions], result)

    @builtins.property
    def auto_merge(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable automatic merging on GitHub.

        Has no effect if ``github.mergify``
        is set to false.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_merge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_merge_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.AutoMergeOptions]:
        '''(experimental) Configure options for automatic merging on GitHub.

        Has no effect if
        ``github.mergify`` or ``autoMerge`` is set to false.

        :default: - see defaults in ``AutoMergeOptions``

        :stability: experimental
        '''
        result = self._values.get("auto_merge_options")
        return typing.cast(typing.Optional[_projen_github_04054675.AutoMergeOptions], result)

    @builtins.property
    def classifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of PyPI trove classifiers that describe the project.

        :stability: experimental
        '''
        result = self._values.get("classifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: - true, but false for subprojects

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def commit_generated(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to commit the managed files by default.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("commit_generated")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of runtime dependencies for this project. Dependencies use the format: ``<module>@<semver>``.

        Additional dependencies can be added via ``project.addDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A short description of the package.

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of dev dependencies for this project. Dependencies use the format: ``<module>@<semver>``.

        Additional dependencies can be added via ``project.addDevDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("dev_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def github(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable GitHub integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github_options(self) -> typing.Optional[_projen_github_04054675.GitHubOptions]:
        '''(experimental) Options for GitHub integration.

        :default: - see GitHubOptions

        :stability: experimental
        '''
        result = self._values.get("github_options")
        return typing.cast(typing.Optional[_projen_github_04054675.GitHubOptions], result)

    @builtins.property
    def git_ignore_options(self) -> typing.Optional[_projen_04054675.IgnoreFileOptions]:
        '''(experimental) Configuration options for .gitignore file.

        :stability: experimental
        '''
        result = self._values.get("git_ignore_options")
        return typing.cast(typing.Optional[_projen_04054675.IgnoreFileOptions], result)

    @builtins.property
    def git_options(self) -> typing.Optional[_projen_04054675.GitOptions]:
        '''(experimental) Configuration options for git.

        :stability: experimental
        '''
        result = self._values.get("git_options")
        return typing.cast(typing.Optional[_projen_04054675.GitOptions], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) A URL to the website of the project.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License of this package as an SPDX identifier.

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging(self) -> typing.Optional[_projen_04054675.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[_projen_04054675.LoggerOptions], result)

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether mergify should be enabled on this repository or not.

        :default: true

        :deprecated: use ``githubOptions.mergify`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(
        self,
    ) -> typing.Optional[_projen_github_04054675.MergifyOptions]:
        '''(deprecated) Options for mergify.

        :default: - default options

        :deprecated: use ``githubOptions.mergifyOptions`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional[_projen_github_04054675.MergifyOptions], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project. Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        subprojects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def package_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package name.

        :stability: experimental
        '''
        result = self._values.get("package_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[_projen_04054675.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[_projen_04054675.Project], result)

    @builtins.property
    def pip(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use pip with a requirements.txt file to track project dependencies.

        :default: - true, unless poetry is true, then false

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("pip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def poetry(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use poetry to manage your project dependencies, virtual environment, and (optional) packaging/publishing.

        This feature is incompatible with pip, setuptools, or venv.
        If you set this option to ``true``, then pip, setuptools, and venv must be set to ``false``.

        :default: false

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("poetry")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def poetry_options(
        self,
    ) -> typing.Optional[_projen_python_04054675.PoetryPyprojectOptionsWithoutDeps]:
        '''(experimental) Additional options to set for poetry if using poetry.

        :stability: experimental
        '''
        result = self._values.get("poetry_options")
        return typing.cast(typing.Optional[_projen_python_04054675.PoetryPyprojectOptionsWithoutDeps], result)

    @builtins.property
    def project_type(self) -> typing.Optional[_projen_04054675.ProjectType]:
        '''(deprecated) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :deprecated: no longer supported at the base project level

        :stability: deprecated
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[_projen_04054675.ProjectType], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_credentials(
        self,
    ) -> typing.Optional[_projen_github_04054675.GithubCredentials]:
        '''(experimental) Choose a method of providing GitHub API access for projen workflows.

        :default: - use a personal access token named PROJEN_GITHUB_TOKEN

        :stability: experimental
        '''
        result = self._values.get("projen_credentials")
        return typing.cast(typing.Optional[_projen_github_04054675.GithubCredentials], result)

    @builtins.property
    def projenrc_js(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use projenrc in javascript.

        This will install ``projen`` as a JavaScript dependency and add a ``synth``
        task which will run ``.projenrc.js``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_js")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(
        self,
    ) -> typing.Optional[_projen_04054675.ProjenrcJsonOptions]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[_projen_04054675.ProjenrcJsonOptions], result)

    @builtins.property
    def projenrc_js_options(
        self,
    ) -> typing.Optional[_projen_javascript_04054675.ProjenrcOptions]:
        '''(experimental) Options related to projenrc in JavaScript.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_js_options")
        return typing.cast(typing.Optional[_projen_javascript_04054675.ProjenrcOptions], result)

    @builtins.property
    def projenrc_python(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use projenrc in Python.

        This will install ``projen`` as a Python dependency and add a ``synth``
        task which will run ``.projenrc.py``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projenrc_python")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_python_options(
        self,
    ) -> typing.Optional[_projen_python_04054675.ProjenrcOptions]:
        '''(experimental) Options related to projenrc in python.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_python_options")
        return typing.cast(typing.Optional[_projen_python_04054675.ProjenrcOptions], result)

    @builtins.property
    def projenrc_ts(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use projenrc in TypeScript.

        This will create a tsconfig file (default: ``tsconfig.projen.json``)
        and use ``ts-node`` in the default task to parse the project source files.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_ts_options(
        self,
    ) -> typing.Optional[_projen_typescript_04054675.ProjenrcTsOptions]:
        '''(experimental) Options related to projenrc in TypeScript.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts_options")
        return typing.cast(typing.Optional[_projen_typescript_04054675.ProjenrcTsOptions], result)

    @builtins.property
    def projen_token_secret(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows.

        This token needs to have the ``repo``, ``workflows``
        and ``packages`` scope.

        :default: "PROJEN_GITHUB_TOKEN"

        :deprecated: use ``projenCredentials``

        :stability: deprecated
        '''
        result = self._values.get("projen_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_request_template(self) -> typing.Optional[builtins.bool]:
        '''Include a GitHub pull request template.

        :default: true
        '''
        result = self._values.get("pull_request_template")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_request_template_contents(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''The contents of the pull request template.

        :default: default content
        '''
        result = self._values.get("pull_request_template_contents")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pytest(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include pytest tests.

        :default: true

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("pytest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pytest_options(self) -> typing.Optional[_projen_python_04054675.PytestOptions]:
        '''(experimental) pytest options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("pytest_options")
        return typing.cast(typing.Optional[_projen_python_04054675.PytestOptions], result)

    @builtins.property
    def python_exec(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path to the python executable to use.

        :default: "python"

        :stability: experimental
        '''
        result = self._values.get("python_exec")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readme(self) -> typing.Optional["ReadmeOptions"]:
        '''Configuration of the README.md file.'''
        result = self._values.get("readme")
        return typing.cast(typing.Optional["ReadmeOptions"], result)

    @builtins.property
    def renovatebot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use renovatebot to handle dependency upgrades.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("renovatebot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def renovatebot_options(
        self,
    ) -> typing.Optional[_projen_04054675.RenovatebotOptions]:
        '''(experimental) Options for renovatebot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("renovatebot_options")
        return typing.cast(typing.Optional[_projen_04054675.RenovatebotOptions], result)

    @builtins.property
    def sample(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include sample code and test if the relevant directories don't exist.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sample")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sample_testdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Location of sample tests.

        Typically the same directory where project tests will be located.

        :default: "tests"

        :stability: experimental
        '''
        result = self._values.get("sample_testdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def setup_config(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional fields to pass in the setup() function if using setuptools.

        :stability: experimental
        '''
        result = self._values.get("setup_config")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def setuptools(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use setuptools with a setup.py script for packaging and publishing.

        :default: - true, unless poetry is true, then false

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("setuptools")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto-close of stale issues and pull request.

        See ``staleOptions`` for options.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("stale")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_options(self) -> typing.Optional[_projen_github_04054675.StaleOptions]:
        '''(experimental) Auto-close stale issues and pull requests.

        To disable set ``stale`` to ``false``.

        :default: - see defaults in ``StaleOptions``

        :stability: experimental
        '''
        result = self._values.get("stale_options")
        return typing.cast(typing.Optional[_projen_github_04054675.StaleOptions], result)

    @builtins.property
    def venv(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use venv to manage a virtual environment for installing dependencies inside.

        :default: - true, unless poetry is true, then false

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("venv")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def venv_options(self) -> typing.Optional[_projen_python_04054675.VenvOptions]:
        '''(experimental) Venv options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("venv_options")
        return typing.cast(typing.Optional[_projen_python_04054675.VenvOptions], result)

    @builtins.property
    def vscode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable VSCode integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("vscode")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PythonPackageOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Readme(
    _projen_04054675.FileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-modules.Readme",
):
    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param description: The description of the project.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cc1200292e645dca3ec7cf2cbf9f2c41def9f24ed1dbb485999955eb69cadd7)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        options = ReadmeOptions(description=description)

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="addSection")
    def add_section(self, title: builtins.str, body: builtins.str) -> None:
        '''
        :param title: -
        :param body: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea72ea6648af1397d521aa4c3a3e8209831871f002cc5eed0118e644c221ff53)
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument body", value=body, expected_type=type_hints["body"])
        return typing.cast(None, jsii.invoke(self, "addSection", [title, body]))

    @jsii.member(jsii_name="synthesizeContent")
    def _synthesize_content(
        self,
        _: _projen_04054675.IResolver,
    ) -> typing.Optional[builtins.str]:
        '''Implemented by derived classes and returns the contents of the file to emit.

        :param _: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f98643f5b00531165345da2ee730415f041f7d8dbd28b8b04ea939baaf7bbce)
            check_type(argname="argument _", value=_, expected_type=type_hints["_"])
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "synthesizeContent", [_]))

    @builtins.property
    @jsii.member(jsii_name="sections")
    def sections(self) -> typing.List["Section"]:
        return typing.cast(typing.List["Section"], jsii.get(self, "sections"))

    @sections.setter
    def sections(self, value: typing.List["Section"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b866744efc0f7f57d44f27762344fc5d2fc2a11698dc4f0fe4a59965bec00bc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3be025b008bae89967f33ac0d0514c1355ca95d6c065b6e4bf039717a4005b50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="projen-modules.ReadmeOptions",
    jsii_struct_bases=[],
    name_mapping={"description": "description"},
)
class ReadmeOptions:
    def __init__(self, *, description: typing.Optional[builtins.str] = None) -> None:
        '''
        :param description: The description of the project.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96a11fa5d843f4f5d45e2690ef6a6b6e0851eb4e74c4330cfe550d6b63ce62b8)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the project.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReadmeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Section(metaclass=jsii.JSIIMeta, jsii_type="projen-modules.Section"):
    def __init__(self, options: ISectionOptions) -> None:
        '''
        :param options: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e42be693dde8cd80a4e05381ff22f05cb4318ab11dab8a9118ec46f997b6b78)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="synth")
    def synth(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "synth", []))

    @builtins.property
    @jsii.member(jsii_name="options")
    def options(self) -> ISectionOptions:
        return typing.cast(ISectionOptions, jsii.get(self, "options"))


__all__ = [
    "CdkTypeScriptApp",
    "CdkTypeScriptAppOptions",
    "ISectionOptions",
    "JsiiProject",
    "JsiiProjectOptions",
    "NpmPackage",
    "NpmPackageOptions",
    "PythonPackage",
    "PythonPackageOptions",
    "Readme",
    "ReadmeOptions",
    "Section",
]

publication.publish()

def _typecheckingstub__a544530c4e440f72065d416ace5f306da46147589bc70a0f44ccba0553de9c78(
    value: Readme,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a6354f4c0532263f309ca59025d89b070b95588f76bd5815340cc71a5341012(
    *,
    cdk_version: builtins.str,
    code_owners: typing.Sequence[builtins.str],
    name: builtins.str,
    allow_library_dependencies: typing.Optional[builtins.bool] = None,
    app: typing.Optional[builtins.str] = None,
    app_entrypoint: typing.Optional[builtins.str] = None,
    artifacts_directory: typing.Optional[builtins.str] = None,
    author_email: typing.Optional[builtins.str] = None,
    author_name: typing.Optional[builtins.str] = None,
    author_organization: typing.Optional[builtins.bool] = None,
    author_url: typing.Optional[builtins.str] = None,
    auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    auto_approve_upgrades: typing.Optional[builtins.bool] = None,
    auto_detect_bin: typing.Optional[builtins.bool] = None,
    auto_merge: typing.Optional[builtins.bool] = None,
    auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    biome: typing.Optional[builtins.bool] = None,
    biome_options: typing.Optional[typing.Union[_projen_javascript_04054675.BiomeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    bugs_email: typing.Optional[builtins.str] = None,
    bugs_url: typing.Optional[builtins.str] = None,
    build_command: typing.Optional[builtins.str] = None,
    build_workflow: typing.Optional[builtins.bool] = None,
    build_workflow_options: typing.Optional[typing.Union[_projen_javascript_04054675.BuildWorkflowOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    build_workflow_triggers: typing.Optional[typing.Union[_projen_github_workflows_04054675.Triggers, typing.Dict[builtins.str, typing.Any]]] = None,
    bump_package: typing.Optional[builtins.str] = None,
    bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    bundler_options: typing.Optional[typing.Union[_projen_javascript_04054675.BundlerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    bun_version: typing.Optional[builtins.str] = None,
    cdk_assert: typing.Optional[builtins.bool] = None,
    cdk_assertions: typing.Optional[builtins.bool] = None,
    cdk_cli_version: typing.Optional[builtins.str] = None,
    cdk_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
    cdk_dependencies_as_deps: typing.Optional[builtins.bool] = None,
    cdkout: typing.Optional[builtins.str] = None,
    cdk_test_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
    cdk_version_pinning: typing.Optional[builtins.bool] = None,
    check_licenses: typing.Optional[typing.Union[_projen_javascript_04054675.LicenseCheckerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    clobber: typing.Optional[builtins.bool] = None,
    code_artifact_options: typing.Optional[typing.Union[_projen_javascript_04054675.CodeArtifactOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    code_cov: typing.Optional[builtins.bool] = None,
    code_cov_token_secret: typing.Optional[builtins.str] = None,
    commit_generated: typing.Optional[builtins.bool] = None,
    constructs_version: typing.Optional[builtins.str] = None,
    context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    copyright_owner: typing.Optional[builtins.str] = None,
    copyright_period: typing.Optional[builtins.str] = None,
    default_release_branch: typing.Optional[builtins.str] = None,
    dependabot: typing.Optional[builtins.bool] = None,
    dependabot_options: typing.Optional[typing.Union[_projen_github_04054675.DependabotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    deps_upgrade: typing.Optional[builtins.bool] = None,
    deps_upgrade_options: typing.Optional[typing.Union[_projen_javascript_04054675.UpgradeDependenciesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    dev_container: typing.Optional[builtins.bool] = None,
    dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    disable_tsconfig: typing.Optional[builtins.bool] = None,
    disable_tsconfig_dev: typing.Optional[builtins.bool] = None,
    docgen: typing.Optional[builtins.bool] = None,
    docs_directory: typing.Optional[builtins.str] = None,
    edge_lambda_auto_discover: typing.Optional[builtins.bool] = None,
    entrypoint: typing.Optional[builtins.str] = None,
    entrypoint_types: typing.Optional[builtins.str] = None,
    eslint: typing.Optional[builtins.bool] = None,
    eslint_options: typing.Optional[typing.Union[_projen_javascript_04054675.EslintOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    experimental_integ_runner: typing.Optional[builtins.bool] = None,
    feature_flags: typing.Optional[builtins.bool] = None,
    github: typing.Optional[builtins.bool] = None,
    github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
    git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    gitpod: typing.Optional[builtins.bool] = None,
    homepage: typing.Optional[builtins.str] = None,
    integration_test_auto_discover: typing.Optional[builtins.bool] = None,
    jest: typing.Optional[builtins.bool] = None,
    jest_options: typing.Optional[typing.Union[_projen_javascript_04054675.JestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    jsii_release_version: typing.Optional[builtins.str] = None,
    keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    lambda_auto_discover: typing.Optional[builtins.bool] = None,
    lambda_extension_auto_discover: typing.Optional[builtins.bool] = None,
    lambda_options: typing.Optional[typing.Union[_projen_awscdk_04054675.LambdaFunctionCommonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    libdir: typing.Optional[builtins.str] = None,
    license: typing.Optional[builtins.str] = None,
    licensed: typing.Optional[builtins.bool] = None,
    logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    major_version: typing.Optional[jsii.Number] = None,
    max_node_version: typing.Optional[builtins.str] = None,
    mergify: typing.Optional[builtins.bool] = None,
    mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    min_major_version: typing.Optional[jsii.Number] = None,
    min_node_version: typing.Optional[builtins.str] = None,
    mutable_build: typing.Optional[builtins.bool] = None,
    next_version_command: typing.Optional[builtins.str] = None,
    npm_access: typing.Optional[_projen_javascript_04054675.NpmAccess] = None,
    npm_dist_tag: typing.Optional[builtins.str] = None,
    npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
    npmignore_enabled: typing.Optional[builtins.bool] = None,
    npm_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    npm_provenance: typing.Optional[builtins.bool] = None,
    npm_registry: typing.Optional[builtins.str] = None,
    npm_registry_url: typing.Optional[builtins.str] = None,
    npm_token_secret: typing.Optional[builtins.str] = None,
    outdir: typing.Optional[builtins.str] = None,
    package: typing.Optional[builtins.bool] = None,
    package_manager: typing.Optional[_projen_javascript_04054675.NodePackageManager] = None,
    package_name: typing.Optional[builtins.str] = None,
    parent: typing.Optional[_projen_04054675.Project] = None,
    peer_dependency_options: typing.Optional[typing.Union[_projen_javascript_04054675.PeerDependencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    pnpm_version: typing.Optional[builtins.str] = None,
    post_build_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    prerelease: typing.Optional[builtins.str] = None,
    prettier: typing.Optional[builtins.bool] = None,
    prettier_options: typing.Optional[typing.Union[_projen_javascript_04054675.PrettierOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    project_type: typing.Optional[_projen_04054675.ProjectType] = None,
    projen_command: typing.Optional[builtins.str] = None,
    projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
    projen_dev_dependency: typing.Optional[builtins.bool] = None,
    projenrc_js: typing.Optional[builtins.bool] = None,
    projenrc_json: typing.Optional[builtins.bool] = None,
    projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projenrc_ts: typing.Optional[builtins.bool] = None,
    projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projen_token_secret: typing.Optional[builtins.str] = None,
    projen_version: typing.Optional[builtins.str] = None,
    publish_dry_run: typing.Optional[builtins.bool] = None,
    publish_tasks: typing.Optional[builtins.bool] = None,
    pull_request_template: typing.Optional[builtins.bool] = None,
    pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
    readme: typing.Optional[typing.Union[ReadmeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    releasable_commits: typing.Optional[_projen_04054675.ReleasableCommits] = None,
    release: typing.Optional[builtins.bool] = None,
    release_branches: typing.Optional[typing.Mapping[builtins.str, typing.Union[_projen_release_04054675.BranchOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    release_every_commit: typing.Optional[builtins.bool] = None,
    release_failure_issue: typing.Optional[builtins.bool] = None,
    release_failure_issue_label: typing.Optional[builtins.str] = None,
    release_schedule: typing.Optional[builtins.str] = None,
    release_tag_prefix: typing.Optional[builtins.str] = None,
    release_to_npm: typing.Optional[builtins.bool] = None,
    release_trigger: typing.Optional[_projen_release_04054675.ReleaseTrigger] = None,
    release_workflow: typing.Optional[builtins.bool] = None,
    release_workflow_name: typing.Optional[builtins.str] = None,
    release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    renovatebot: typing.Optional[builtins.bool] = None,
    renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    repository: typing.Optional[builtins.str] = None,
    repository_directory: typing.Optional[builtins.str] = None,
    require_approval: typing.Optional[_projen_awscdk_04054675.ApprovalLevel] = None,
    sample_code: typing.Optional[builtins.bool] = None,
    scoped_packages_options: typing.Optional[typing.Sequence[typing.Union[_projen_javascript_04054675.ScopedPackagesOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    srcdir: typing.Optional[builtins.str] = None,
    stability: typing.Optional[builtins.str] = None,
    stale: typing.Optional[builtins.bool] = None,
    stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    testdir: typing.Optional[builtins.str] = None,
    tsconfig: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    tsconfig_dev: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    tsconfig_dev_file: typing.Optional[builtins.str] = None,
    ts_jest_options: typing.Optional[typing.Union[_projen_typescript_04054675.TsJestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    typescript_version: typing.Optional[builtins.str] = None,
    versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    vscode: typing.Optional[builtins.bool] = None,
    watch_excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
    watch_includes: typing.Optional[typing.Sequence[builtins.str]] = None,
    workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    workflow_container_image: typing.Optional[builtins.str] = None,
    workflow_git_identity: typing.Optional[typing.Union[_projen_github_04054675.GitIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
    workflow_node_version: typing.Optional[builtins.str] = None,
    workflow_package_cache: typing.Optional[builtins.bool] = None,
    workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
    workflow_runs_on_group: typing.Optional[typing.Union[_projen_04054675.GroupRunnerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    yarn_berry_options: typing.Optional[typing.Union[_projen_javascript_04054675.YarnBerryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23029d204b6d2d942365c98cdf1ae37497306087c242e282bc4760de997efd13(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae35859c3728359fce2cd5f37ce86da906192904c18d529b6c42fb7cd911ad9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6f448692015be891a4fa1b5c76f220188ba4be73e94a65360a4338352b1ea99(
    value: Readme,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcc0f0f3d874afabc142961b7ca192083fcad906385166f2e47f7e7399ce16bc(
    *,
    author: builtins.str,
    author_address: builtins.str,
    code_owners: typing.Sequence[builtins.str],
    name: builtins.str,
    repository_url: builtins.str,
    allow_library_dependencies: typing.Optional[builtins.bool] = None,
    artifacts_directory: typing.Optional[builtins.str] = None,
    author_email: typing.Optional[builtins.str] = None,
    author_name: typing.Optional[builtins.str] = None,
    author_organization: typing.Optional[builtins.bool] = None,
    author_url: typing.Optional[builtins.str] = None,
    auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    auto_approve_upgrades: typing.Optional[builtins.bool] = None,
    auto_detect_bin: typing.Optional[builtins.bool] = None,
    auto_merge: typing.Optional[builtins.bool] = None,
    auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    biome: typing.Optional[builtins.bool] = None,
    biome_options: typing.Optional[typing.Union[_projen_javascript_04054675.BiomeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    bugs_email: typing.Optional[builtins.str] = None,
    bugs_url: typing.Optional[builtins.str] = None,
    build_workflow: typing.Optional[builtins.bool] = None,
    build_workflow_options: typing.Optional[typing.Union[_projen_javascript_04054675.BuildWorkflowOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    build_workflow_triggers: typing.Optional[typing.Union[_projen_github_workflows_04054675.Triggers, typing.Dict[builtins.str, typing.Any]]] = None,
    bump_package: typing.Optional[builtins.str] = None,
    bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    bundler_options: typing.Optional[typing.Union[_projen_javascript_04054675.BundlerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    bun_version: typing.Optional[builtins.str] = None,
    check_licenses: typing.Optional[typing.Union[_projen_javascript_04054675.LicenseCheckerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    clobber: typing.Optional[builtins.bool] = None,
    code_artifact_options: typing.Optional[typing.Union[_projen_javascript_04054675.CodeArtifactOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    code_cov: typing.Optional[builtins.bool] = None,
    code_cov_token_secret: typing.Optional[builtins.str] = None,
    commit_generated: typing.Optional[builtins.bool] = None,
    compat: typing.Optional[builtins.bool] = None,
    compat_ignore: typing.Optional[builtins.str] = None,
    compress_assembly: typing.Optional[builtins.bool] = None,
    copyright_owner: typing.Optional[builtins.str] = None,
    copyright_period: typing.Optional[builtins.str] = None,
    default_release_branch: typing.Optional[builtins.str] = None,
    dependabot: typing.Optional[builtins.bool] = None,
    dependabot_options: typing.Optional[typing.Union[_projen_github_04054675.DependabotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    deps_upgrade: typing.Optional[builtins.bool] = None,
    deps_upgrade_options: typing.Optional[typing.Union[_projen_javascript_04054675.UpgradeDependenciesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    dev_container: typing.Optional[builtins.bool] = None,
    dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    disable_tsconfig: typing.Optional[builtins.bool] = None,
    disable_tsconfig_dev: typing.Optional[builtins.bool] = None,
    docgen: typing.Optional[builtins.bool] = None,
    docgen_file_path: typing.Optional[builtins.str] = None,
    docs_directory: typing.Optional[builtins.str] = None,
    dotnet: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiDotNetTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    entrypoint: typing.Optional[builtins.str] = None,
    entrypoint_types: typing.Optional[builtins.str] = None,
    eslint: typing.Optional[builtins.bool] = None,
    eslint_options: typing.Optional[typing.Union[_projen_javascript_04054675.EslintOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    exclude_typescript: typing.Optional[typing.Sequence[builtins.str]] = None,
    github: typing.Optional[builtins.bool] = None,
    github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
    git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    gitpod: typing.Optional[builtins.bool] = None,
    homepage: typing.Optional[builtins.str] = None,
    jest: typing.Optional[builtins.bool] = None,
    jest_options: typing.Optional[typing.Union[_projen_javascript_04054675.JestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    jsii_release_version: typing.Optional[builtins.str] = None,
    jsii_version: typing.Optional[builtins.str] = None,
    keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    libdir: typing.Optional[builtins.str] = None,
    license: typing.Optional[builtins.str] = None,
    licensed: typing.Optional[builtins.bool] = None,
    logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    major_version: typing.Optional[jsii.Number] = None,
    max_node_version: typing.Optional[builtins.str] = None,
    mergify: typing.Optional[builtins.bool] = None,
    mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    min_major_version: typing.Optional[jsii.Number] = None,
    min_node_version: typing.Optional[builtins.str] = None,
    mutable_build: typing.Optional[builtins.bool] = None,
    next_version_command: typing.Optional[builtins.str] = None,
    npm_access: typing.Optional[_projen_javascript_04054675.NpmAccess] = None,
    npm_dist_tag: typing.Optional[builtins.str] = None,
    npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
    npmignore_enabled: typing.Optional[builtins.bool] = None,
    npm_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    npm_provenance: typing.Optional[builtins.bool] = None,
    npm_registry: typing.Optional[builtins.str] = None,
    npm_registry_url: typing.Optional[builtins.str] = None,
    npm_token_secret: typing.Optional[builtins.str] = None,
    outdir: typing.Optional[builtins.str] = None,
    package: typing.Optional[builtins.bool] = None,
    package_manager: typing.Optional[_projen_javascript_04054675.NodePackageManager] = None,
    package_name: typing.Optional[builtins.str] = None,
    parent: typing.Optional[_projen_04054675.Project] = None,
    peer_dependency_options: typing.Optional[typing.Union[_projen_javascript_04054675.PeerDependencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    pnpm_version: typing.Optional[builtins.str] = None,
    post_build_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    prerelease: typing.Optional[builtins.str] = None,
    prettier: typing.Optional[builtins.bool] = None,
    prettier_options: typing.Optional[typing.Union[_projen_javascript_04054675.PrettierOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    project_type: typing.Optional[_projen_04054675.ProjectType] = None,
    projen_command: typing.Optional[builtins.str] = None,
    projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
    projen_dev_dependency: typing.Optional[builtins.bool] = None,
    projenrc_js: typing.Optional[builtins.bool] = None,
    projenrc_json: typing.Optional[builtins.bool] = None,
    projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projenrc_ts: typing.Optional[builtins.bool] = None,
    projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projen_token_secret: typing.Optional[builtins.str] = None,
    projen_version: typing.Optional[builtins.str] = None,
    publish_dry_run: typing.Optional[builtins.bool] = None,
    publish_tasks: typing.Optional[builtins.bool] = None,
    publish_to_go: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiGoTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    publish_to_maven: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiJavaTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    publish_to_nuget: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiDotNetTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    publish_to_pypi: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiPythonTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    pull_request_template: typing.Optional[builtins.bool] = None,
    pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
    python: typing.Optional[typing.Union[_projen_cdk_04054675.JsiiPythonTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    readme: typing.Optional[typing.Union[ReadmeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    releasable_commits: typing.Optional[_projen_04054675.ReleasableCommits] = None,
    release: typing.Optional[builtins.bool] = None,
    release_branches: typing.Optional[typing.Mapping[builtins.str, typing.Union[_projen_release_04054675.BranchOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    release_every_commit: typing.Optional[builtins.bool] = None,
    release_failure_issue: typing.Optional[builtins.bool] = None,
    release_failure_issue_label: typing.Optional[builtins.str] = None,
    release_schedule: typing.Optional[builtins.str] = None,
    release_tag_prefix: typing.Optional[builtins.str] = None,
    release_to_npm: typing.Optional[builtins.bool] = None,
    release_trigger: typing.Optional[_projen_release_04054675.ReleaseTrigger] = None,
    release_workflow: typing.Optional[builtins.bool] = None,
    release_workflow_name: typing.Optional[builtins.str] = None,
    release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    renovatebot: typing.Optional[builtins.bool] = None,
    renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    repository: typing.Optional[builtins.str] = None,
    repository_directory: typing.Optional[builtins.str] = None,
    rootdir: typing.Optional[builtins.str] = None,
    sample_code: typing.Optional[builtins.bool] = None,
    scoped_packages_options: typing.Optional[typing.Sequence[typing.Union[_projen_javascript_04054675.ScopedPackagesOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    srcdir: typing.Optional[builtins.str] = None,
    stability: typing.Optional[builtins.str] = None,
    stale: typing.Optional[builtins.bool] = None,
    stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    testdir: typing.Optional[builtins.str] = None,
    tsconfig: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    tsconfig_dev: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    tsconfig_dev_file: typing.Optional[builtins.str] = None,
    ts_jest_options: typing.Optional[typing.Union[_projen_typescript_04054675.TsJestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    typescript_version: typing.Optional[builtins.str] = None,
    versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    vscode: typing.Optional[builtins.bool] = None,
    workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    workflow_container_image: typing.Optional[builtins.str] = None,
    workflow_git_identity: typing.Optional[typing.Union[_projen_github_04054675.GitIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
    workflow_node_version: typing.Optional[builtins.str] = None,
    workflow_package_cache: typing.Optional[builtins.bool] = None,
    workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
    workflow_runs_on_group: typing.Optional[typing.Union[_projen_04054675.GroupRunnerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    yarn_berry_options: typing.Optional[typing.Union[_projen_javascript_04054675.YarnBerryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cb7da275ba82f1b6bb477c4c22f7721642ea0759b39a4fc1874a92b34daa7eb(
    value: Readme,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b17dce6f2f04ceb519c781a818d66bcf4fef528d5b613028b126fd373e7b4048(
    *,
    code_owners: typing.Sequence[builtins.str],
    name: builtins.str,
    allow_library_dependencies: typing.Optional[builtins.bool] = None,
    artifacts_directory: typing.Optional[builtins.str] = None,
    author_email: typing.Optional[builtins.str] = None,
    author_name: typing.Optional[builtins.str] = None,
    author_organization: typing.Optional[builtins.bool] = None,
    author_url: typing.Optional[builtins.str] = None,
    auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    auto_approve_upgrades: typing.Optional[builtins.bool] = None,
    auto_detect_bin: typing.Optional[builtins.bool] = None,
    auto_merge: typing.Optional[builtins.bool] = None,
    auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    biome: typing.Optional[builtins.bool] = None,
    biome_options: typing.Optional[typing.Union[_projen_javascript_04054675.BiomeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    bugs_email: typing.Optional[builtins.str] = None,
    bugs_url: typing.Optional[builtins.str] = None,
    build_workflow: typing.Optional[builtins.bool] = None,
    build_workflow_options: typing.Optional[typing.Union[_projen_javascript_04054675.BuildWorkflowOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    build_workflow_triggers: typing.Optional[typing.Union[_projen_github_workflows_04054675.Triggers, typing.Dict[builtins.str, typing.Any]]] = None,
    bump_package: typing.Optional[builtins.str] = None,
    bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    bundler_options: typing.Optional[typing.Union[_projen_javascript_04054675.BundlerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    bun_version: typing.Optional[builtins.str] = None,
    check_licenses: typing.Optional[typing.Union[_projen_javascript_04054675.LicenseCheckerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    clobber: typing.Optional[builtins.bool] = None,
    code_artifact_options: typing.Optional[typing.Union[_projen_javascript_04054675.CodeArtifactOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    code_cov: typing.Optional[builtins.bool] = None,
    code_cov_token_secret: typing.Optional[builtins.str] = None,
    commit_generated: typing.Optional[builtins.bool] = None,
    copyright_owner: typing.Optional[builtins.str] = None,
    copyright_period: typing.Optional[builtins.str] = None,
    default_release_branch: typing.Optional[builtins.str] = None,
    dependabot: typing.Optional[builtins.bool] = None,
    dependabot_options: typing.Optional[typing.Union[_projen_github_04054675.DependabotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    deps_upgrade: typing.Optional[builtins.bool] = None,
    deps_upgrade_options: typing.Optional[typing.Union[_projen_javascript_04054675.UpgradeDependenciesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    dev_container: typing.Optional[builtins.bool] = None,
    dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    disable_tsconfig: typing.Optional[builtins.bool] = None,
    disable_tsconfig_dev: typing.Optional[builtins.bool] = None,
    docgen: typing.Optional[builtins.bool] = None,
    docs_directory: typing.Optional[builtins.str] = None,
    entrypoint: typing.Optional[builtins.str] = None,
    entrypoint_types: typing.Optional[builtins.str] = None,
    eslint: typing.Optional[builtins.bool] = None,
    eslint_options: typing.Optional[typing.Union[_projen_javascript_04054675.EslintOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    github: typing.Optional[builtins.bool] = None,
    github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
    git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    gitpod: typing.Optional[builtins.bool] = None,
    homepage: typing.Optional[builtins.str] = None,
    jest: typing.Optional[builtins.bool] = None,
    jest_options: typing.Optional[typing.Union[_projen_javascript_04054675.JestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    jsii_release_version: typing.Optional[builtins.str] = None,
    keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    libdir: typing.Optional[builtins.str] = None,
    license: typing.Optional[builtins.str] = None,
    licensed: typing.Optional[builtins.bool] = None,
    logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    major_version: typing.Optional[jsii.Number] = None,
    max_node_version: typing.Optional[builtins.str] = None,
    mergify: typing.Optional[builtins.bool] = None,
    mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    min_major_version: typing.Optional[jsii.Number] = None,
    min_node_version: typing.Optional[builtins.str] = None,
    mutable_build: typing.Optional[builtins.bool] = None,
    next_version_command: typing.Optional[builtins.str] = None,
    npm_access: typing.Optional[_projen_javascript_04054675.NpmAccess] = None,
    npm_dist_tag: typing.Optional[builtins.str] = None,
    npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
    npmignore_enabled: typing.Optional[builtins.bool] = None,
    npm_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    npm_provenance: typing.Optional[builtins.bool] = None,
    npm_registry: typing.Optional[builtins.str] = None,
    npm_registry_url: typing.Optional[builtins.str] = None,
    npm_token_secret: typing.Optional[builtins.str] = None,
    outdir: typing.Optional[builtins.str] = None,
    package: typing.Optional[builtins.bool] = None,
    package_manager: typing.Optional[_projen_javascript_04054675.NodePackageManager] = None,
    package_name: typing.Optional[builtins.str] = None,
    parent: typing.Optional[_projen_04054675.Project] = None,
    peer_dependency_options: typing.Optional[typing.Union[_projen_javascript_04054675.PeerDependencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    pnpm_version: typing.Optional[builtins.str] = None,
    post_build_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    prerelease: typing.Optional[builtins.str] = None,
    prettier: typing.Optional[builtins.bool] = None,
    prettier_options: typing.Optional[typing.Union[_projen_javascript_04054675.PrettierOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    project_type: typing.Optional[_projen_04054675.ProjectType] = None,
    projen_command: typing.Optional[builtins.str] = None,
    projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
    projen_dev_dependency: typing.Optional[builtins.bool] = None,
    projenrc_js: typing.Optional[builtins.bool] = None,
    projenrc_json: typing.Optional[builtins.bool] = None,
    projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projenrc_ts: typing.Optional[builtins.bool] = None,
    projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projen_token_secret: typing.Optional[builtins.str] = None,
    projen_version: typing.Optional[builtins.str] = None,
    publish_dry_run: typing.Optional[builtins.bool] = None,
    publish_tasks: typing.Optional[builtins.bool] = None,
    pull_request_template: typing.Optional[builtins.bool] = None,
    pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
    readme: typing.Optional[typing.Union[ReadmeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    releasable_commits: typing.Optional[_projen_04054675.ReleasableCommits] = None,
    release: typing.Optional[builtins.bool] = None,
    release_branches: typing.Optional[typing.Mapping[builtins.str, typing.Union[_projen_release_04054675.BranchOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    release_every_commit: typing.Optional[builtins.bool] = None,
    release_failure_issue: typing.Optional[builtins.bool] = None,
    release_failure_issue_label: typing.Optional[builtins.str] = None,
    release_schedule: typing.Optional[builtins.str] = None,
    release_tag_prefix: typing.Optional[builtins.str] = None,
    release_to_npm: typing.Optional[builtins.bool] = None,
    release_trigger: typing.Optional[_projen_release_04054675.ReleaseTrigger] = None,
    release_workflow: typing.Optional[builtins.bool] = None,
    release_workflow_name: typing.Optional[builtins.str] = None,
    release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    renovatebot: typing.Optional[builtins.bool] = None,
    renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    repository: typing.Optional[builtins.str] = None,
    repository_directory: typing.Optional[builtins.str] = None,
    sample_code: typing.Optional[builtins.bool] = None,
    scoped_packages_options: typing.Optional[typing.Sequence[typing.Union[_projen_javascript_04054675.ScopedPackagesOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    srcdir: typing.Optional[builtins.str] = None,
    stability: typing.Optional[builtins.str] = None,
    stale: typing.Optional[builtins.bool] = None,
    stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    testdir: typing.Optional[builtins.str] = None,
    tsconfig: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    tsconfig_dev: typing.Optional[typing.Union[_projen_javascript_04054675.TypescriptConfigOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    tsconfig_dev_file: typing.Optional[builtins.str] = None,
    ts_jest_options: typing.Optional[typing.Union[_projen_typescript_04054675.TsJestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    typescript_version: typing.Optional[builtins.str] = None,
    versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    vscode: typing.Optional[builtins.bool] = None,
    workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Union[_projen_github_workflows_04054675.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    workflow_container_image: typing.Optional[builtins.str] = None,
    workflow_git_identity: typing.Optional[typing.Union[_projen_github_04054675.GitIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
    workflow_node_version: typing.Optional[builtins.str] = None,
    workflow_package_cache: typing.Optional[builtins.bool] = None,
    workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
    workflow_runs_on_group: typing.Optional[typing.Union[_projen_04054675.GroupRunnerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    yarn_berry_options: typing.Optional[typing.Union[_projen_javascript_04054675.YarnBerryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a456e663d7da59de9fd68ca5bb5f5bc98971d99102fdb04adfe975c14215095(
    value: Readme,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__882525f8fb69251a060fbbe97c2383313ea4b9c0269874cb1d13172a5420010c(
    *,
    author_email: builtins.str,
    author_name: builtins.str,
    code_owners: typing.Sequence[builtins.str],
    module_name: builtins.str,
    name: builtins.str,
    version: builtins.str,
    auto_approve_options: typing.Optional[typing.Union[_projen_github_04054675.AutoApproveOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    auto_merge: typing.Optional[builtins.bool] = None,
    auto_merge_options: typing.Optional[typing.Union[_projen_github_04054675.AutoMergeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
    clobber: typing.Optional[builtins.bool] = None,
    commit_generated: typing.Optional[builtins.bool] = None,
    deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    dev_container: typing.Optional[builtins.bool] = None,
    dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    github: typing.Optional[builtins.bool] = None,
    github_options: typing.Optional[typing.Union[_projen_github_04054675.GitHubOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    gitpod: typing.Optional[builtins.bool] = None,
    homepage: typing.Optional[builtins.str] = None,
    license: typing.Optional[builtins.str] = None,
    logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    mergify: typing.Optional[builtins.bool] = None,
    mergify_options: typing.Optional[typing.Union[_projen_github_04054675.MergifyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    outdir: typing.Optional[builtins.str] = None,
    package_name: typing.Optional[builtins.str] = None,
    parent: typing.Optional[_projen_04054675.Project] = None,
    pip: typing.Optional[builtins.bool] = None,
    poetry: typing.Optional[builtins.bool] = None,
    poetry_options: typing.Optional[typing.Union[_projen_python_04054675.PoetryPyprojectOptionsWithoutDeps, typing.Dict[builtins.str, typing.Any]]] = None,
    project_type: typing.Optional[_projen_04054675.ProjectType] = None,
    projen_command: typing.Optional[builtins.str] = None,
    projen_credentials: typing.Optional[_projen_github_04054675.GithubCredentials] = None,
    projenrc_js: typing.Optional[builtins.bool] = None,
    projenrc_json: typing.Optional[builtins.bool] = None,
    projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projenrc_js_options: typing.Optional[typing.Union[_projen_javascript_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projenrc_python: typing.Optional[builtins.bool] = None,
    projenrc_python_options: typing.Optional[typing.Union[_projen_python_04054675.ProjenrcOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projenrc_ts: typing.Optional[builtins.bool] = None,
    projenrc_ts_options: typing.Optional[typing.Union[_projen_typescript_04054675.ProjenrcTsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    projen_token_secret: typing.Optional[builtins.str] = None,
    pull_request_template: typing.Optional[builtins.bool] = None,
    pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
    pytest: typing.Optional[builtins.bool] = None,
    pytest_options: typing.Optional[typing.Union[_projen_python_04054675.PytestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    python_exec: typing.Optional[builtins.str] = None,
    readme: typing.Optional[typing.Union[ReadmeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    renovatebot: typing.Optional[builtins.bool] = None,
    renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    sample: typing.Optional[builtins.bool] = None,
    sample_testdir: typing.Optional[builtins.str] = None,
    setup_config: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    setuptools: typing.Optional[builtins.bool] = None,
    stale: typing.Optional[builtins.bool] = None,
    stale_options: typing.Optional[typing.Union[_projen_github_04054675.StaleOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    venv: typing.Optional[builtins.bool] = None,
    venv_options: typing.Optional[typing.Union[_projen_python_04054675.VenvOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vscode: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cc1200292e645dca3ec7cf2cbf9f2c41def9f24ed1dbb485999955eb69cadd7(
    project: _projen_04054675.Project,
    *,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea72ea6648af1397d521aa4c3a3e8209831871f002cc5eed0118e644c221ff53(
    title: builtins.str,
    body: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f98643f5b00531165345da2ee730415f041f7d8dbd28b8b04ea939baaf7bbce(
    _: _projen_04054675.IResolver,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b866744efc0f7f57d44f27762344fc5d2fc2a11698dc4f0fe4a59965bec00bc0(
    value: typing.List[Section],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3be025b008bae89967f33ac0d0514c1355ca95d6c065b6e4bf039717a4005b50(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96a11fa5d843f4f5d45e2690ef6a6b6e0851eb4e74c4330cfe550d6b63ce62b8(
    *,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e42be693dde8cd80a4e05381ff22f05cb4318ab11dab8a9118ec46f997b6b78(
    options: ISectionOptions,
) -> None:
    """Type checking stubs"""
    pass

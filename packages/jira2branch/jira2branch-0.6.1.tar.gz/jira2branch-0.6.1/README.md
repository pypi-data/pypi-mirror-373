# JIRA 2 Branch

Takes a JIRA issue and creates a git branch

```
Usage: jira2branch [OPTIONS] ISSUE_ID_OR_URL SOURCE_BRANCH

  Simple program that takes a JIRA issue ID and creates a new local and
  tracking remote branch

Options:
  -s, --simple         Basic naming strategy
  -n, --name-only      Generates the branch name and prints it, no actual
                       branch will be created (default is False)
  -p, --push           Push newly created branch to remote (default is False)
  -t, --target PATH    Target repository (default is current directory)
  -r, --merge-request  Create merge request. Requires --push. (default is
                       False)
  -c, --confirm        Request user confirmation (default is False)
  --preview            Preview MR Markdown in browser (default is False)
  -d, --dry-run        Dry run. Prints out the MR payload in JSON format but
                       does not invoke the API
  --config             Show config file location
  --help               Show this message and exit.
  
```

## Naming strategy

### Default naming strategy

Format: `{CONVENTIONAL_COMMIT_PREFIX}/{ISSUE_ID}_{ISSUE_TITLE}`

The [conventional commit](https://www.conventionalcommits.org/) prefix is
inferred from the type of JIRA card.

```console
$ jira2branch ISSUE-10306 master -n

BRANCH NAME: #############################################
feat/ISSUE-10306_implement_foo_function
##########################################################

MR TITLE: ###################################################
feat/ISSUE-10306: Implement foo function
#############################################################
```

### Basic naming strategy format

Format: `{ISSUE_ID}`

Example:

```console
$ jira2branch ISSUE-10306 master -s -n

BRANCH NAME: 
ISSUE-10306
##########

MR TITLE: ##############################################
ISSUE-10306: Implement foo function
########################################################
```

## Requirements

Requires Python 3.11

### Dev env

```
pip install poetry
poetry install
pip install dist/jira2branch-[VERSION]-py3-none-any.whl
```

Afterwards, your command should be available:

```
$ jira2branch WT3-227 develop
fix/WT3-227_some-jira-issue
```

### Configuration

#### JIRA

JIRA credentials will be fetched from `jira2branch/config.toml` under your user config directory with the following format:

```toml
[jira-credentials]

url = ""
email = ""
username = ""
password = ""
token = ""
```

#### Required fields

`url` and `email` are required.

Use either `username` + `password` or `token` depending on how access is configured

#### GitLab integration

You can create merge requests (title and description) using this tool. Only
GitLab is supported for now and it requires the following setup step.

Once done providing `--merge-request` will launch your `$EDITOR` and let you
compose your merge request.

```ini
[gitlab-credentials]

url = ""
token = ""
```

#### Required fields

`token` is required

Set `url` if the GitLab instance you're using is self-hosted

#### Note

You can always retrieve the configuration file location by providing the
`--config` flag

## Usage

`jira2branch [JIRA_ISSUE_ID|JIRA_ISSUE_URL] [TARGET_BRANCH]`

### Examples

`jira2branch WT3-227 main`

`jira2branch https://company.atlassian.net/browse/WT3-227 main`

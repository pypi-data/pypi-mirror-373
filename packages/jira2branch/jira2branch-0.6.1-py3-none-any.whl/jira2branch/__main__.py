import os
import re
import string
import tempfile
from enum import StrEnum
from pathlib import Path
from subprocess import run
from typing import Optional

import click
import gitlab
import toml
from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from git.repo import Repo
from gitlab.exceptions import GitlabGetError
from gitlab.v4.objects.merge_requests import ProjectMergeRequest
from halo import Halo
from jira import JIRA, Issue, JIRAError
from jira.resources import CustomFieldOption
from platformdirs import user_config_dir
from unidecode import unidecode

Environment = StrEnum(
    'Environment', [
        'playground',
        'staging',
        'release',
        'production'
    ])


class JIRACredentials:
    file = ''
    url = ''
    username = ''
    password = ''
    email = ''
    token = ''


def get_config_file_path() -> Path:
    """Returns the configuration file path location."""
    return Path(user_config_dir('jira2branch'))


def get_jira_credentials() -> Optional[JIRACredentials]:
    config = JIRACredentials()
    config_file_path = get_config_file_path()
    config_file_name = 'config.toml'
    config_file = config_file_path.joinpath(config_file_name)

    config.file = str(config_file)

    if config_file.exists():
        with open(config_file, 'r') as f:
            configuration = toml.load(f)
            jira_credentials_section = configuration.get('jira-credentials')
            config.url = jira_credentials_section.get("url")
            config.email = jira_credentials_section.get("email")
            config.token = jira_credentials_section.get("token")
            config.username = jira_credentials_section.get("username")
            config.password = jira_credentials_section.get("password")
    else:
        os.makedirs(config_file_path, exist_ok=True)
        config_file.touch()
        with config_file.open('w') as f:
            f.writelines(["[jira-credentials]\n\n",
                          "url = \"\" \n",
                          "email = \"\" \n",
                          "username = \"\" \n",
                          "password = \"\" \n",
                          "token = \"\" \n"])
        click.echo(
            f'Created empty secrets file under {config_file}, please configure it first')
        exit(1)

    return config


class GitLabCredentials:
    file = ''
    url = ''
    token = ''


# TODO: move configuration logic to a single place
def get_gitlab_credentials() -> Optional[GitLabCredentials]:
    config = GitLabCredentials()
    config_file_path = get_config_file_path()
    config_file_name = 'config.toml'
    config_file = config_file_path.joinpath(config_file_name)

    config.file = str(config_file)

    if config_file.exists():
        with open(config_file, 'r') as f:
            configuration = toml.load(f)
            gitlab_credentials_section = configuration.get('gitlab-credentials')
            config.url = gitlab_credentials_section.get("url")
            config.token = gitlab_credentials_section.get("token")
    else:
        os.makedirs(config_file_path, exist_ok=True)
        config_file.touch()
        with config_file.open('w') as f:
            f.writelines(["[gitlab-credentials]\n\n",
                          "url = \"\" \n",
                          "token = \"\" \n"])
        click.echo(
            f'Created empty config file under {config_file}, please configure it first')
        return None

    return config


def get_jira_rest_endpoint() -> JIRA:
    credentials = get_jira_credentials()

    if not credentials and (not credentials.email or not credentials.token):
        click.secho(
            f"Invalid configuration, please check {credentials.file}", fg='red')
        exit()

    spinner = Halo(text='Connecting to JIRA API', spinner='dots')
    spinner.start()

    jira = None

    if credentials.email and credentials.token:
        try:
            jira = JIRA(credentials.url, basic_auth=(credentials.email, credentials.token),
                        validate=True)
        except JIRAError as error:
            print(error)
            exit(1)
        finally:
            spinner.stop()
        return jira
    elif credentials.username and credentials.password:
        try:
            jira = JIRA(credentials.url, auth=(credentials.username, credentials.password),
                        validate=True)
        except JIRAError as error:
            print(error)
            exit(1)
        finally:
            spinner.stop()
        return jira
    else:
        spinner.stop()
        raise IOError(
            f"Invalid or missing credentials file! Check {credentials.file}, I might have created it for you")


def get_issue_environment(issue: Issue) -> str:

    # Let's have a best guess at figuring out this issue's environment (if any)
    env = Environment.staging  # use develop as default

    environments = [e.value for e in Environment]

    for value in issue.fields.__dict__.values():
        if isinstance(value, CustomFieldOption):
            env_name = value.__str__().lower()
            if env_name in environments:
                env = Environment[env_name]
    return env


def get_jira_issue_details(issue_id: str) -> dict[str, str]:
    jira = None
    issue = None

    try:
        jira = get_jira_rest_endpoint()
    except IOError:
        click.secho(
            'Failed to connect to JIRA, please check configuration', fg='red')
        exit()

    try:
        spinner = Halo(text=f'Fetching JIRA issue {issue_id}', spinner='dots')
        spinner.start()
        issue = jira.issue(issue_id)
        spinner.stop()
    except JIRAError as error:
        click.secho(
            f'Failed to fetch JIRA issue {issue_id}', err=error, fg='red')
        exit(1)

    issue_type = issue.fields.issuetype.name
    if 'task' in str.lower(issue_type):
        issue_type = 'feat'
    else:
        issue_type = 'fix'

    title = f'{issue.fields.summary}'

    env = get_issue_environment(issue)

    return {'id': issue_id, 'type': issue_type, 'title': title, 'environment': env}


def create_branch(branch_name, source_branch, push=False, target: Path = Path.cwd()):
    try:
        repo = Repo(target, search_parent_directories=True)

        stashed_changes = False

        #  if dirty stash all changes and apply them on the new branch
        if repo.is_dirty():
            repo.git.execute(['git', 'stash'])
            stashed_changes = True

        # check if develop exists otherwise switch to master otherwise switch to main
        for branch in [source_branch, 'master', 'main']:
            spinner = Halo(
                text=f'Checking if source branch {branch} exists...', spinner='dots')
            spinner.start()
            if check_if_branch_exists(repo, branch):
                source_branch = branch
                click.secho('YES', fg='green')
                spinner.stop()
                break
            else:
                click.secho('NO', fg='red')

        #  check if a branch by this name already exists locally
        click.secho('Checking if branch already exists on local repository...')
        if check_if_branch_is_local(repo, branch_name):
            click.secho(
                'Local branch already exists, switching to it', fg='blue')
            switch_to_branch(repo, branch_name)
            return source_branch

        #  check if a branch by this name already exists on remote
        spinner = Halo(
            text='Checking if branch already exists on remote repository...', spinner='dots')
        spinner.start()
        if not check_if_branch_exists(repo, branch_name):
            click.secho('Branch name IS available', fg='green')
        else:
            click.secho(
                'A remote branch by that name already exists... aborting', fg='red')
            raise Exception(
                'A remote branch by that name already exists... aborting')
        spinner.stop()

        #  we're good to go
        #  create MR branch from latest develop or master
        try:
            spinner = Halo(text='Fetching all remote branches', spinner='dots')
            spinner.start()
            repo.git.execute(['git', 'fetch', '--all'])
            spinner.stop()
            click.secho('Fetched all remote branches', fg='green')
        except Exception as err:
            print(err)
            spinner.stop()
        try:
            spinner = Halo(
                text=f'Creating local branch {branch_name} from {source_branch}', spinner='dots')
            spinner.start()
            repo.git.execute(['git', 'checkout', source_branch])
            repo.git.execute(['git', 'pull'])
            repo.git.execute(['git', 'branch', branch_name])
            spinner.stop()
            click.secho(f'Created local branch {branch_name}', fg='green')
            switch_to_branch(repo, branch_name)
        except Exception as err:
            click.secho('Failed to create local branch...')
            print(err)
            spinner.stop()

        # setting remote tracking branch
        upstream_branch_command = ['git', 'push',
                                   '-u', 'origin', f'{branch_name}']
        if push:
            repo.git.execute(upstream_branch_command)
        else:
            click.secho(
                'NOTE: Branch NOT pushed to remote (use with -p to push automatically)', fg='blue')
            click.secho(
                'Whenever you decide to push your changes to remote use the following command:', fg='blue')
            upstream_branch_command = ' '.join(upstream_branch_command)
            click.secho(''.ljust(len(upstream_branch_command), '#'))
            click.echo(f' > {upstream_branch_command}')
            click.secho(''.ljust(len(branch_name), '#'))

        if stashed_changes:
            repo.git.execute(['git', 'stash', 'pop'])

        click.secho('Switching to new branch. Good luck!', fg='green')

    except InvalidGitRepositoryError as err:
        click.secho(err, fg='red')
        raise err
    except NoSuchPathError as err:
        click.secho(err, fg='red')
        raise err
    return source_branch


def check_if_branch_is_local(repo, branch_name) -> bool:
    result = repo.git.execute(['git', 'branch', '--list', branch_name])
    if not result:
        return False
    return True


def check_if_branch_exists(repo, branch_name) -> bool:
    remote_branch = repo.git.execute(
        ['git', 'ls-remote', '--heads', 'origin', branch_name])
    if remote_branch:
        return True
    return False


def switch_to_branch(repo, branch_name):
    repo.git.execute(['git', 'checkout', branch_name])


# MERGE REQUEST CREATION

# This requires:
# TOKEN: have it setup in secrets file
# PROJECT_ID: infer from repo?
# SOURCE_BRANCH
# TARGET_BRANCH: develop by default
# TITLE: infer from JIRA issue title
# DESCRIPTION: default is link to JIRA issue, user can then edit once MR has been created

def create_merge_request(repo: Repo,
                         source_branch: str,
                         target_branch: str,
                         issue_id: str,
                         issue_url: str,
                         title: str,
                         confirm: bool = False,
                         preview: bool = False,
                         dry_run: bool = False):
    spinner = Halo(text=f'Creating MR for {issue_id}', spinner='dots')
    spinner.start()

    project_name = None
    project_name_with_namespace = None
    project = None

    try:
        project_name_with_namespace = str(repo.git.execute(
            ['git', 'remote', 'get-url', 'origin']))
        project_name_with_namespace = re.findall(
            r'git@gitlab\.com:(.+)\.git', project_name_with_namespace)[0]
        assert project_name_with_namespace
        project_name = project_name_with_namespace.split("/")[-1]
        assert project_name
    except (GitCommandError, IndexError):
        click.secho("\nFailed to parse repository name, aborting", fg='red')
        exit(1)

    gitlab_credentials = get_gitlab_credentials()

    if not gitlab_credentials and (not gitlab_credentials.url or not gitlab_credentials.token):
        click.secho(
            f"Invalid configuration, please check {gitlab_credentials.file}", fg='red')
        exit()

    if gitlab_credentials.url is not None:
        gl = gitlab.Gitlab(
            url=gitlab_credentials.url,
            private_token=gitlab_credentials.token
        )
    else:
        gl = gitlab.Gitlab(private_token=gitlab_credentials.token)

    gl.auth()

    try:
        print(project_name_with_namespace)
        project = gl.projects.get(project_name_with_namespace)
    except GitlabGetError:
        click.secho(f"Failed to find project named "
                    f"{project_name_with_namespace}",
                    fg='red')
        exit(1)

    # MR DESCRIPTION
    """
    Uses the MR template as defined in project (if set) instead of a custom one.
    Checks and replaces explicit references to Infraspeak's Jira issue URLs
    """
    description = f'[{issue_id}]({issue_url})'

    if hasattr(project, 'merge_requests_template'):
        mr_template = project.merge_requests_template

        if mr_template:
            description = mr_template.replace(
                'https://infraspeak.atlassian.net/browse/', f'[{issue_id}]({issue_url})')
            try:
                spinner.stop()
                description = Utils.edit_mr_description(
                    description, confirm, preview)
                click.secho("Done editing MR", fg='green')
                spinner.start()
            except IOError:
                click.secho(
                    "Failed to edit MR description, using defaults instead", fg='red')

    merge_requests_for_issue: [
        ProjectMergeRequest] = project.mergerequests.list(search=issue_id)

    # filter opened and locked MRs
    merge_requests_for_issue = [
        mr for mr in merge_requests_for_issue if mr.state not in ['merged', 'locked', 'closed']]

    # this check is probably pointless...
    if merge_requests_for_issue and not dry_run:
        spinner.stop()
        click.secho(
            'One or more pending MR already exist for this issue... aborting', fg='red')
        exit(1)

    # check if upstream branch is set
    set_upstream_branch = True
    try:
        upstream_branch = repo.git.execute(
            ["git", "rev-parse", "--abbrev-ref", f"{source_branch}@{{upstream}}"])
        if source_branch in upstream_branch:
            set_upstream_branch = False
    except GitCommandError:
        click.secho(f"No upstream configured for {source_branch}", fg='blue')

    if set_upstream_branch:
        try:
            if dry_run:
                click.secho('\nSet upstream branch', fg='green')
            else:
                repo.git.execute(
                    ["git", "push", "-u", "origin", source_branch])
        except GitCommandError as err:
            click.secho('Something failed while trying to push...', fg='red')
            click.echo(err)
            exit(1)
    else:
        # only create the MR if there are pending commits
        pending_commits = repo.git.execute(["git", "log", "@{upstream}.."])

        # or merges
        pending_merges = repo.git.execute(["git", "log", f"{target_branch}.."])

        if not pending_commits and not pending_merges:
            click.secho('No commits to push, nothing to do here!', fg='green')
            exit(1)
        else:
            try:
                if dry_run:
                    click.secho(
                        '\nWould push any pending commits to the remote repository', fg='magenta')
                else:
                    repo.git.execute(["git", "push"])
            except GitCommandError as err:
                click.secho(
                    'Something failed while trying to push...', fg='red')
                click.echo(err)
                exit(1)

    # Get the current user id
    current_user_id = None

    if gl.user and gl.user.attributes and 'id' in gl.user.attributes:
        current_user_id = gl.user.attributes.get('id') or None

    if current_user_id is None:
        click.secho('Could not determine current user...', fg='red')
        spinner.stop()
        exit(1)

    # WE ARE GOOD TO GO!
    title = f'{title}'  # MARK THE MR AS WORK IN PROGRESS

    mr_payload = {'source_branch': source_branch,
                  'target_branch': target_branch,
                  'title': title,
                  'squash': True,
                  'remove_source_branch': True,
                  'description': description,
                  'assignee_id': current_user_id
                  }

    spinner.stop()

    if confirm:
        Utils.print_mr(mr_payload)
        if not click.confirm('I am about to create the merge request, is this ok?'):
            click.secho('Aborting MR creation', fg='red')
            exit(1)

    try:
        if dry_run:
            click.secho('Would create a MR with following data:', fg='magenta')
            Utils.print_mr(mr_payload)
            spinner.stop()
        else:
            spinner.start()
            mr = project.mergerequests.create(mr_payload)
            spinner.stop()
            click.secho(f'Created MR {mr.title}', fg='green')
    except Exception as err:
        spinner.stop()
        click.secho('Failed to create MR', fg='red')
        click.echo(err)

    return None


class Utils:

    @staticmethod
    def get_branch_name_parts_from_issue(details) -> [str]:
        issue_id = details.get('id')
        issue_type = details.get('type')
        title = details.get('title')
        branch_name = f"{Utils.issue_title_to_branch_name(issue_id, title, issue_type)}"
        mr_title = f"{issue_type}/{issue_id}: {title}"

        return [branch_name, mr_title, title]

    @staticmethod
    def issue_title_to_branch_name(issue_id: str, title: str, issue_type: str) -> str:

        separator = '-'

        title = unidecode(title)  # replace non ascii characters
        title = title.replace(' ', separator)  # no spaces

        # replace all non word, non digit characters
        title = re.sub(r'[^\w\d-]', separator, title)
        title = re.sub(r'-+', separator, title)  # remove repetitions
        title = re.sub(r'^-', '', title)  # trim start
        title = re.sub(r'-$', '', title)  # trim end
        title = title.strip()  # trim both ends

        title = str.lower(title)

        allowed_chars = string.ascii_letters + string.digits + '-'

        branch_title = ''
        for c in title:
            if c in allowed_chars:
                branch_title += c

        branch_title = f'{issue_type}/{issue_id}_{branch_title}'

        # keep the branch name under 255 chars
        branch_title = branch_title[:255]

        return branch_title

    @staticmethod
    def edit_mr_description(description,
                            confirm: bool = False,
                            preview: bool = False) -> str:
        EDITOR = os.environ.get('EDITOR', 'vim')

        with tempfile.NamedTemporaryFile(suffix=".md", mode="w+") as tf:
            tf.write(description)
            tf.flush()

            command = [EDITOR, tf.name]

            if preview:
                command.extend(['-c', ':MarkdownPreview'])

            cp = run(command)

            if cp.returncode > 0:
                click.secho(
                    '\nEditor exited with an error, using default description instead\n', fg='red')
                return description

            save_edits = True

            if confirm:
                if not click.confirm('Save edits? If the answer is \'No\' I\'ll use the default instead'):
                    return description

            tf.seek(0)
            description = tf.read()

            return description

    @staticmethod
    def print_mr(mr):
        click.secho(f'Title: {mr["title"]}', fg='blue')
        click.secho(f'Source: {mr["source_branch"]}', fg='blue')
        click.secho(f'Target: {mr["target_branch"]}', fg='blue')
        click.secho('Description:\n', fg='blue')
        click.secho(f'{mr["description"]}', fg='blue')
        return


@click.command()
@click.argument('issue_id_or_url')
@click.argument('source_branch')
@click.option('-s', '--simple', is_flag=True, default=False,
              help='Basic naming strategy')
@click.option('-n', '--name-only', is_flag=True, default=False,
              help='Generates the branch name and prints it, no actual branch will be created (default is False)')
# @click.option('-s', '--source-branch', default=False,
#               help='Source branch')
@click.option('-p', '--push', is_flag=True, default=False,
              help='Push newly created branch to remote (default is False)')
@click.option('-t', '--target', type=Path, default=Path.cwd(),
              help='Target repository (default is current directory)')
@click.option('-r', '--merge-request', is_flag=True, default=False,
              help='Create merge request. Requires --push. (default is False)')
@click.option('-c', '--confirm', is_flag=True, default=False,
              help='Request user confirmation (default is False)')
@click.option('--preview', is_flag=True, default=False,
              help='Preview MR Markdown in browser (default is False)')
@click.option('-d', '--dry-run', is_flag=True, default=False,
              help='Dry run. Prints out the MR payload in JSON format but does not invoke the API')
@click.option('--config', is_flag=True, default=False,
              help='Show config file location')
def cli(issue_id_or_url,
        simple,
        name_only,
        dry_run,
        confirm,
        preview,
        push,
        target: Path,
        merge_request: bool,
        source_branch: str,
        config: bool):
    """Simple program that takes a JIRA issue ID and creates a new local and tracking remote branch"""
    if config:
        click.echo('Configuration is stored under')
        click.echo(get_config_file_path())
        exit()

    repo = Repo(target, search_parent_directories=True)

    issue_id = issue_id_or_url

    if '/' in issue_id_or_url:
        issue_id = issue_id_or_url.split('/')[-1]

    # print(os.getcwd())
    # repo = Repo(os.getcwd())
    # assert not repo.bare

    issue_details = get_jira_issue_details(issue_id)

    # Validate the source branch against the issue's enviroment
    environment = issue_details.get('environment') or Environment.staging

    try:
        environment = Environment[environment]
    except KeyError:
        click.secho(
            f'Failed to determine environment from "{environment}", '
            f'defaulting to {Environment.staging}',
            fg='blue')
        environment = Environment.staging

    environment_branches = {
        Environment.playground: 'develop',
        Environment.staging: 'develop',
        Environment.release: 'release',
        Environment.production: 'master'
    }

    if name_only is False:
        default_branch = environment_branches.get(environment)
        if source_branch != default_branch:
            click.secho('WHOOPS! this is probably the wrong source branch',
                        fg='red')
            click.secho(
                f'You\'ve set {source_branch} '
                f'as source branch but the issue was reported '
                f'on {environment} environment (defaults to {default_branch} branch)',
                fg='red')
            if click.confirm(f'Do you want me to set '
                             f'{environment_branches.get(environment)} '
                             f'as source branch instead?'):
                source_branch = environment_branches.get(
                    environment, '')
                if not source_branch:
                    click.secho(
                        'Invalid source branch, aborting...',
                        fg='red')

    names = Utils.get_branch_name_parts_from_issue(issue_details)
    branch_name = names[0]
    mr_title = names[1]
    title = names[2]
    credentials = get_jira_credentials()

    # move this logic to some other place that makes sense
    if simple:
        branch_name = issue_id
        mr_title = f"{issue_id}: {title}"

    if name_only:
        click.secho('BRANCH NAME: '.ljust(len(branch_name), '#'), fg='green')
        click.echo(branch_name)
        click.secho(''.rjust(len(branch_name), '#'), fg='green')

        click.echo('')

        click.secho('MR TITLE: '.ljust(len(mr_title), '#'), fg='green')
        click.echo(mr_title)
        click.secho(''.rjust(len(mr_title), '#'), fg='green')

        if check_if_branch_exists(repo, branch_name):
            click.secho(
                '\nWARNING: a remote branch by that name already exists', fg='yellow')
    elif dry_run:
        click.secho(''.center(len(branch_name), '~'), fg='magenta')
        click.secho(' DRY RUN '.center(len(branch_name), '~'), fg='magenta')
        click.secho(''.center(len(branch_name), '~'), fg='magenta')
        click.secho('BRANCH NAME: '.ljust(len(branch_name), '#'), fg='green')
        click.echo(branch_name)
        click.secho(''.rjust(len(branch_name), '#'), fg='green')

        create_merge_request(repo,
                             branch_name,
                             source_branch,  # see target_branch below
                             issue_id,
                             f'{credentials.url}/browse/{issue_id}',
                             mr_title,
                             confirm,
                             preview,
                             True)
    else:
        target_branch = None
        try:
            target_branch = create_branch(
                branch_name, source_branch, push, target)
        except Exception:
            exit(1)
        if target_branch and merge_request:
            create_merge_request(repo,
                                 branch_name,
                                 target_branch,
                                 issue_id,
                                 f'{credentials.url}/browse/{issue_id}',
                                 mr_title,
                                 confirm,
                                 preview)


if __name__ == '__main__':
    cli()

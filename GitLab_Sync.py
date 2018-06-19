import sys
import ConfigParser
import json
import logging
import logging.handlers
import os
import gitlab
from git import Repo

config = None
logger = None


def start():
    app_init()
    process_args()


def app_init():
    _init_conf()
    _init_logs()


def _init_conf():
    global config
    config = ConfigParser.ConfigParser()
    try:
        config.read('configs/host.conf')
    except Exception, e:
        print "Failed to read base config file: {0}".format(str(e))


def _init_logs():
    global logger
    app_name = "GitLab-Sync"
    try:
        app_name = config.get('Host', 'app_name')
    except Exception:
        pass
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)

    # Write to file
    handler = logging.handlers.RotatingFileHandler(app_name + '.log', maxBytes=10485760, backupCount=4)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%d/%m/%Y %I:%M:%S'))
    logger.addHandler(handler)

    # Write to console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                                  '%d/%m/%Y %I:%M:%S'))
    logger.addHandler(stream_handler)


def process_args():
    args = sys.argv
    act_type = None
    for arg in args[1:]:
        arg = arg.lower()
        if 'config=' in arg:
            config_dir = arg.replace('config=', '')
            init_custom_conf(config_dir)
        elif arg in ['repos', 'ignore', 'all', '*']:
            act_type = arg
        else:
            print "Unsupported argument: " + arg
            sys.exit(1)

    action(act_type)


def init_custom_conf(path):
    conf_path = os.path.join(path, 'host.conf')
    if os.path.exists(conf_path):
        try:
            global config
            config = ConfigParser.ConfigParser()
            config.read(conf_path)
            config.set('Host', 'conf_dir', path)
        except Exception, e:
            logger.error("Failed to read config: {0}".format(str(e)))
            sys.exit(1)
    else:
        logger.error("'host.conf' no found at specified path: [{0}]".format(path))
        sys.exit(1)


def action(act_type):
    if act_type is None or act_type == '*' or act_type == 'all':
        sync_all()
        return

    if act_type == 'repos':
        sync_repos()
        return

    if act_type == 'ignore':
        sync_all(True)
        return
    else:
        print "Unknown argument, expected: [ No Arguments | all | * | repos | ignore]"


def sync_all(ignore=False):
    ignored = []
    if ignore:
        ignored = get_ignores()
    base_local_path = os.path.expanduser(config.get('Host', 'local_path'))
    git_lab = gitlab.Gitlab(config.get('Host', 'gitlab_host'), config.get('Host', 'gitlab_secret_token'),
                            ssl_verify=config.getboolean('Host', 'gitlab_verify_ssl'))
    for project in git_lab.projects.list():

        if ignore:
            if project.ssh_url_to_repo in ignored or project.http_url_to_repo in ignored:
                continue

        project_local_path = os.path.join(base_local_path, project.path_with_namespace)
        if os.path.exists(project_local_path):
            fetch(project_local_path)

        else:
            project_root = os.path.join(base_local_path, project.path_with_namespace)
            if not os.path.exists(project_root):
                os.makedirs(project_root)
            is_ssh = (config.get('Host', 'connection_type').lower() == 'ssh')
            remote_url = is_ssh and project.ssh_url_to_repo or project.http_url_to_repo
            clone(project_root, remote_url)

    logger.info("All Done")


def get_ignores():
    ignore_json = 'configs/ignore.json'
    try:
        conf_dir = config.get('Host', 'conf_dir')
        ignore_json = os.path.join(conf_dir, 'ignore.json')
    except Exception:
        pass

    try:
        with open(ignore_json) as f:
            ignores = f.read()
            return json.loads(ignores)
    except Exception, e:
        logger.error("Failed to read [ignore.json]. " + str(e))
        sys.exit(1)


def clone(project_root, remote_url):
    logger.info("Cloning: [{0}] to [{1}]".format(remote_url, project_root))

    try:
        Repo().clone_from(remote_url, project_root, git_progress_handler)
    except Exception, e:
        logger.error("Failed to clone from: {0}. Exception: {1}".format(remote_url, str(e)))


def fetch(project_local_path):
    logger.info("Fetching: [" + project_local_path + "]")
    try:
        Repo(project_local_path).git.fetch('--all')
    except Exception, e:
        logger.error("Failed to fetch all. Exception: {0}".format(str(e)))


def git_progress_handler(op_code, cur_count, max_count=None, message=''):
    if message:
        logger.info("Message: {0}".format(message))


def sync_repos():
    repos = get_repos()
    for dir_name in repos:
        dir_name_expand = os.path.expanduser(dir_name)
        for remote_url in repos[dir_name]:
            url_split_path = remote_url.split('/')
            project_name = url_split_path[len(url_split_path) - 1].split('.')[0]
            group_name = url_split_path[len(url_split_path) - 2]
            full_project_path = os.path.join(dir_name_expand, group_name, project_name)

            if os.path.exists(full_project_path):
                fetch(full_project_path)
            else:
                clone(full_project_path, remote_url)

    logger.info("All Done")


def get_repos():
    repos_json = 'configs/repos.json'
    try:
        conf_dir = config.get('Host', 'conf_dir')
        repos_json = os.path.join(conf_dir, 'repos.json')
    except Exception:
        pass

    try:
        with open(repos_json) as f:
            repos = f.read()
            return json.loads(repos)
    except Exception, e:
        logger.error("Failed to read [repos.json]. " + str(e))
        sys.exit(1)


if __name__ == '__main__':
    start()

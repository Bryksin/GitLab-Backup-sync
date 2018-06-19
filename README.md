# GitLab Projects Backup Sync

## Dependencies:

```pip install -r requirements.txt```

## Requirements:

Please set your [GitLab Access Token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) with API permissions in ```configs/host.conf``` file:

```
gitlab_secret_token=<your_secret_token>
```

If you don't know how to get your security token, please refer to
[this manual](https://help.github.com/articles/creating-an-access-token-for-command-line-use/)


# Usage:

| Sync Type               |        Command        |   Arg  | Optional Arg         |
|-------------------------|:---------------------:|:------:|----------------------|
| All Repos               | python GitLab_Sync.py |        | config=<path_to_dir> |
| All a part from ignored | python GitLab_Sync.py | ignore | config=<path_to_dir> |
| Only Selected projects  | python GitLab_Sync.py | repos  | config=<path_to_dir> |

## Selected:

To sync only selected projects please add records into `configs/repos.json` file in `JSON` format where:<br/>
`Key` is local directory where to clone the project,<br/>
`Value` is an array with repository URL _(SSH||HTTP)_

```
{
    "~/GitLab-Sync/SyncGroup_1": [
        "git@<domain>:<group>/<project_name_1>.git",
        "git@<domain>:<group>/<project_name_2>.git",
        "git@<domain>:<group>/<project_name_X>.git"
        ],
    "~/GitLab-Sync/SyncGroup_2": [
        "git@<domain>:<group>/<project_name_1>.git",
        "git@<domain>:<group>/<project_name_2>.git",
        "git@<domain>:<group>/<project_name_X>.git"
        ]
}
```

## Ignored:

To sync all projects a part from specifically ignored please add records into ```configs/ignore.json``` file in JSON:

```
[
  "git@<domain>:<group>/<project_name_to_ignore_1>.git",
  "git@<domain>:<group>/<project_name_to_ignore_2>.git",
  "git@<domain>:<group>/<project_name_to_ignore_X>.git"
]
```


## Note:

**You should have Admin Rights in GitLab to have permission to sync all projects**
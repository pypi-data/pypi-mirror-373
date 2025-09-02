# Contributing to mater-data-providing

[TOC]

## Set up your environment

The recommended IDE is [Visual Studio Code](https://code.visualstudio.com/) (VSCode). Add the VSCode extension "Ruff".

You can configure your `setting.json` file to unable ruff linting fixes and formatting when saving your script:
`CTRL+SHIFT+P`, type `setting`, select `Preferences: Open User Settings (JSON)`.

Add the following to configure ruff on save:

```json
{
  "git.autofetch": true,
  "editor.formatOnSave": true,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    },
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

### Linux

[curl](https://curl.se/) is needed:

```bash
sudo apt update
sudo apt install curl
```

[Git](https://git-scm.com/) is recommended.

```bash
sudo apt update
sudo apt install git
```

The package manager [uv](https://docs.astral.sh/uv/) must be installed.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

[Python3+](https://www.python.org/) 12 or 13 must be installed. You can use [uv to install python](https://docs.astral.sh/uv/guides/install-python/#getting-started):

```bash
uv python install 3.12
```

### Windows

[Git](https://git-scm.com/) is recommended.

The package manager [uv](https://docs.astral.sh/uv/) must be installed.

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

[Python3+](https://www.python.org/) 12 or 13 must be installed. You can use [uv to install python](https://docs.astral.sh/uv/guides/install-python/#getting-started):

```bash
uv python install 3.12
```

Don't forget to add python to path (check the box when installing or follow the same steps as described in the `Step-By-Step guide to installing Poetry on Windows`section`5. **Add Path to Environment Variables**`). uv gives you the command to add python to path after installing it.

## Clone the Repository

Clone the repository to your local machine using:

```bash
git clone https://gricad-gitlab.univ-grenoble-alpes.fr/isterre-dynamic-modeling/mater-project/mater.git
```

## Branching Guidelines

To keep the repository organized, please follow these branch creation guidelines:

### Create a New Branch from the dev branch

#### Add a feature or update documentation

Always create a new branch for your work. Do not work directly on the dev branch.
Use the following naming convention for branches:

- Features: `feature/<short-description>`
- Documentation: `docs/<short-description>`
- Examples:

  - feature/change-lifetime-distribution
  - docs/update-readme

```bash
git checkout dev
git checkout -b <branch-name>
```

#### Create an issue to report a bug

If you encouner a bug, please report it creating an issue:

- Go to the Plan tab of the gitlab project
- Select `Issues` and click on `New issue`
- Enter the issue informtions and click on `Create issue`

#### Fix an issue (automatic branch creation)

Gitlab automatically create a branch to fix an issue:

- Go to the Plan tab of the gitlab project
- Select the issue you want to fix
- Click on `Create merge request` or `Create branch`
- You can work on this branch locally

### Keep Your Branch Up-to-Date

Regularly update your branch with the latest changes from dev to avoid conflicts:

1. Fetch the latest changes for all branches:

```bash
git fetch --all
```

2. Rebase your branch on top of dev:

```bash
git rebase origin/dev
```

- _Resolve conflicts (if any)_:

  - Git will pause and indicate conflicts. Open the conflicted files, resolve the issues, and stage the resolved changes (this can be done directly in VScode):

```bash
git add <file>
```

- Continue the rebase after resolving conflicts:

```bash
git rebase --continue
```

4. Push your rebased branch:

After rebasing, you need to force-push your branch to update the remote branch:

```bash
git push --force-with-lease
```

### Submitting Your Work

1. Open a Merge request:

- Go to Merge requests in the Code tab of the repository.
- Click New merge request and select your branch as the source and dev as the terget branch.
- Provide a clear description of your changes and link any related issues.

2. Address Feedback:

- Be prepared to revise your changes based on feedback from reviewers.

### Branch Cleanup

After your branch has been merged, delete it to keep the repository tidy:

```bash
git remote prune origin
git branch -D <branch-name>
```

# AA Discord Announcements<a name="aa-discord-announcements"></a>

[![Version](https://img.shields.io/pypi/v/aa-discord-announcements?label=release)](https://pypi.org/project/aa-discord-announcements/)
[![License](https://img.shields.io/github/license/ppfeufer/aa-discord-announcements)](https://github.com/ppfeufer/aa-discord-announcements/blob/master/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/aa-discord-announcements)](https://pypi.org/project/aa-discord-announcements/)
[![Django](https://img.shields.io/pypi/djversions/aa-discord-announcements?label=django)](https://pypi.org/project/aa-discord-announcements/)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ppfeufer/aa-discord-announcements/master.svg)](https://results.pre-commit.ci/latest/github/ppfeufer/aa-discord-announcements/master)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](http://black.readthedocs.io/en/latest/)
[![Discord](https://img.shields.io/discord/790364535294132234?label=discord)](https://discord.gg/zmh52wnfvM)
[![Checks](https://github.com/ppfeufer/aa-discord-announcements/actions/workflows/automated-checks.yml/badge.svg)](https://github.com/ppfeufer/aa-discord-announcements/actions/workflows/automated-checks.yml)
[![codecov](https://codecov.io/gh/ppfeufer/aa-discord-announcements/branch/master/graph/badge.svg?token=9I6HQB6W6J)](https://codecov.io/gh/ppfeufer/aa-discord-announcements)
[![Translation status](https://weblate.ppfeufer.de/widget/alliance-auth-apps/aa-discord-announcements/svg-badge.svg)](https://weblate.ppfeufer.de/engage/alliance-auth-apps/)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](https://github.com/ppfeufer/aa-discord-announcements/blob/master/CODE_OF_CONDUCT.md)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/N4N8CL1BY)

Discord Announcements via [Alliance Auth](https://gitlab.com/allianceauth/allianceauth)

Write announcements and manage who can write announcements on your corporation or
alliance Discord through Alliance Auth.

______________________________________________________________________

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=2 -->

- [Installation](#installation)
  - [Bare Metal Installation](#bare-metal-installation)
    - [Step 1: Install the App](#step-1-install-the-app)
    - [Step 2: Update Your AA Settings](#step-2-update-your-aa-settings)
    - [Step 3: Finalizing the Installation](#step-3-finalizing-the-installation)
  - [Docker Installation](#docker-installation)
    - [Step 1: Add the App](#step-1-add-the-app)
    - [Step 2: Update Your AA Settings](#step-2-update-your-aa-settings-1)
    - [Step 3: Build Auth and Restart Your Containers](#step-3-build-auth-and-restart-your-containers)
    - [Step 4: Run Migrations and Collect Static Files](#step-4-run-migrations-and-collect-static-files)
  - [Common Installation Steps](#common-installation-steps)
    - [Setting up Permission](#setting-up-permission)
    - [Setting up the App](#setting-up-the-app)
- [Changelog](#changelog)
- [Translation Status](#translation-status)
- [Contributing](#contributing)

<!-- mdformat-toc end -->

______________________________________________________________________

## Installation<a name="installation"></a>

This app is a plugin for Alliance Auth. If you don't have Alliance Auth running already,
please install it first before proceeding.
(See the official [AA installation guide](https://allianceauth.readthedocs.io/en/latest/installation/allianceauth.html) for details)

> [!NOTE]
>
> You also want to make sure that you have the
> [Discord service](https://allianceauth.readthedocs.io/en/latest/features/services/discord.html)
> installed, configured and activated before installing this app.

### Bare Metal Installation<a name="bare-metal-installation"></a>

#### Step 1: Install the App<a name="step-1-install-the-app"></a>

Make sure you're in the virtual environment (venv) of your Alliance Auth installation.
Then install the latest version:

```shell
pip install aa-discord-announcements
```

#### Step 2: Update Your AA Settings<a name="step-2-update-your-aa-settings"></a>

Configure your AA settings (`local.py`) as follows:

- Add `"aa_discord_announcements",` to `INSTALLED_APPS`

#### Step 3: Finalizing the Installation<a name="step-3-finalizing-the-installation"></a>

Copy static files and run migrations

```shell
python manage.py collectstatic
python manage.py migrate
```

Restart your supervisor services for AA

### Docker Installation<a name="docker-installation"></a>

#### Step 1: Add the App<a name="step-1-add-the-app"></a>

Add the app to your `conf/requirements.txt`

```text
aa-discord-announcements==2.6.1
```

#### Step 2: Update Your AA Settings<a name="step-2-update-your-aa-settings-1"></a>

Configure your AA settings (`conf/local.py`) as follows:

- Add `"aa_discord_announcements",` to `INSTALLED_APPS`

#### Step 3: Build Auth and Restart Your Containers<a name="step-3-build-auth-and-restart-your-containers"></a>

```shell
docker compose build
docker compose --env-file=.env up -d
```

#### Step 4: Run Migrations and Collect Static Files<a name="step-4-run-migrations-and-collect-static-files"></a>

```shell
docker compose exec allianceauth_gunicorn bash
auth collectstatic
auth migrate
```

### Common Installation Steps<a name="common-installation-steps"></a>

#### Setting up Permission<a name="setting-up-permission"></a>

Now you can set up permissions in Alliance Auth for your users.
Add `aa_discord_announcements | general | Can access this app` to the states and/or
groups you would like to have access.

#### Setting up the App<a name="setting-up-the-app"></a>

In your admin backend you'll find a new section called `Discord Announcements`.
This is where you set all your stuff up, like the webhooks you want to ping and who
can ping them. It's pretty straight forward, so you shouldn't have any issues. Go nuts!

## Changelog<a name="changelog"></a>

See [CHANGELOG.md](https://github.com/ppfeufer/aa-discord-announcements/blob/master/CHANGELOG.md)

## Translation Status<a name="translation-status"></a>

[![Translation status](https://weblate.ppfeufer.de/widget/alliance-auth-apps/aa-discord-announcements/multi-auto.svg)](https://weblate.ppfeufer.de/engage/alliance-auth-apps/)

Do you want to help translate this app into your language or improve the existing
translation? - [Join our team of translators][weblate engage]!

## Contributing<a name="contributing"></a>

Do you want to contribute to this project? That's cool!

Please make sure to read the [Contribution Guidelines].\
(I promise, it's not much, just some basics)

<!-- Links -->

[contribution guidelines]: https://github.com/ppfeufer/aa-discord-announcements/blob/master/CONTRIBUTING.md "Contribution Guidelines"
[weblate engage]: https://weblate.ppfeufer.de/engage/alliance-auth-apps/ "Weblate Translations"

# AA Mumble Quick Connect

[![Version](https://img.shields.io/pypi/v/aa-mumble-quick-connect?label=release)](https://pypi.org/project/aa-mumble-quick-connect/)
[![License](https://img.shields.io/github/license/ppfeufer/aa-mumble-quick-connect)](https://github.com/ppfeufer/aa-mumble-quick-connect/blob/master/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/aa-mumble-quick-connect)](https://pypi.org/project/aa-mumble-quick-connect/)
[![Django](https://img.shields.io/pypi/djversions/aa-mumble-quick-connect?label=django)](https://pypi.org/project/aa-mumble-quick-connect/)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ppfeufer/aa-mumble-quick-connect/master.svg)](https://results.pre-commit.ci/latest/github/ppfeufer/aa-mumble-quick-connect/master)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](http://black.readthedocs.io/en/latest/)
[![Discord](https://img.shields.io/discord/790364535294132234?label=discord)](https://discord.gg/zmh52wnfvM)
[![Checks](https://github.com/ppfeufer/aa-mumble-quick-connect/actions/workflows/automated-checks.yml/badge.svg)](https://github.com/ppfeufer/aa-mumble-quick-connect/actions/workflows/automated-checks.yml)
[![codecov](https://codecov.io/gh/ppfeufer/aa-mumble-quick-connect/graph/badge.svg?token=p2qVe7q36D)](https://codecov.io/gh/ppfeufer/aa-mumble-quick-connect)
[![Translation status](https://weblate.ppfeufer.de/widget/alliance-auth-apps/aa-mumble-quick-connect/svg-badge.svg)](https://weblate.ppfeufer.de/engage/alliance-auth-apps/)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](https://github.com/ppfeufer/aa-mumble-quick-connect/blob/master/CODE_OF_CONDUCT.md)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/N4N8CL1BY)

App for Alliance Auth to provide quick connect links for Mumble channels.

______________________________________________________________________

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=2 -->

- [Screenshots](#screenshots)
  - [Mumble Quick Connect](#mumble-quick-connect)
- [Installation](#installation)
  - [Bare Metal Installation](#bare-metal-installation)
    - [Step 1: Install the App](#step-1-install-the-app)
    - [Step 2: Update Your AA Settings](#step-2-update-your-aa-settings)
    - [Step 3: Finalizing the Installation](#step-3-finalizing-the-installation)
  - [Docker Installation](#docker-installation)
    - [Step 1: Add the App](#step-1-add-the-app)
    - [Step 2: Update Your AA Settings](#step-2-update-your-aa-settings-1)
    - [Step 3: Build Auth and Restart Your Containers](#step-3-build-auth-and-restart-your-containers)
    - [Step 4: Finalizing the Installation](#step-4-finalizing-the-installation)
- [Permissions](#permissions)
- [Changelog](#changelog)
- [Translation Status](#translation-status)
- [Contributing](#contributing)

<!-- mdformat-toc end -->

______________________________________________________________________

## Screenshots<a name="screenshots"></a>

### Mumble Quick Connect<a name="mumble-quick-connect"></a>

![Mumble Quick Connect](https://raw.githubusercontent.com/ppfeufer/aa-mumble-quick-connect/master/docs/images/mumble-quick-connect.jpg "Mumble Quick Connect")

## Installation<a name="installation"></a>

> [!NOTE]
>
> To use this app, you need to have [Alliance Auth](https://gitlab.com/allianceauth/allianceauth) installed, and the [Mumble Service](https://allianceauth.readthedocs.io/en/latest/features/services/mumble.html) enabled.

### Bare Metal Installation<a name="bare-metal-installation"></a>

#### Step 1: Install the App<a name="step-1-install-the-app"></a>

Install the app using pip:

```shell
pip install aa-mumble-quick-connect==0.0.12
```

#### Step 2: Update Your AA Settings<a name="step-2-update-your-aa-settings"></a>

Add the app to your `INSTALLED_APPS` in your `local.py`:

```python
INSTALLED_APPS += [
    "aa_mumble_quick_connect",  # https://github.com/ppfeufer/aa-mumble-quick-connect
]
```

#### Step 3: Finalizing the Installation<a name="step-3-finalizing-the-installation"></a>

Copy static files and run migrations

```shell
python manage.py migrate mumble_quick_connect
python manage.py collectstatic --noinput
```

### Docker Installation<a name="docker-installation"></a>

#### Step 1: Add the App<a name="step-1-add-the-app"></a>

Add the app to your `conf/requirements.txt`:

```text
aa-mumble-quick-connect==0.0.12
```

#### Step 2: Update Your AA Settings<a name="step-2-update-your-aa-settings-1"></a>

Add the app to your `INSTALLED_APPS` in your `conf/local.py`:

```python
INSTALLED_APPS += [
    "aa_mumble_quick_connect",  # https://github.com/ppfeufer/aa-mumble-quick-connect
]
```

#### Step 3: Build Auth and Restart Your Containers<a name="step-3-build-auth-and-restart-your-containers"></a>

```shell
docker compose build --no-cache
docker compose --env-file=.env up -d
```

#### Step 4: Finalizing the Installation<a name="step-4-finalizing-the-installation"></a>

Copy static files and run migrations

```shell
docker compose exec allianceauth_gunicorn bash

auth collectstatic
auth migrate
```

## Permissions<a name="permissions"></a>

The app comes with a default permission `aa_mumble_quick_connect | general | Can access this app` that allows
users to view the Mumble Quick Connect page.

## Changelog<a name="changelog"></a>

See [CHANGELOG.md](https://github.com/ppfeufer/aa-mumble-quick-connect/blob/master/CHANGELOG.md) for a list of changes.

## Translation Status<a name="translation-status"></a>

[![Translation status](https://weblate.ppfeufer.de/widget/alliance-auth-apps/aa-mumble-quick-connect/multi-auto.svg)](https://weblate.ppfeufer.de/engage/alliance-auth-apps/)

Do you want to help translate this app into your language or improve the existing
translation? - [Join our team of translators][weblate engage]!

## Contributing<a name="contributing"></a>

Do you want to contribute to this project? That's cool!

Please make sure to read the [Contribution Guidelines](https://github.com/ppfeufer/aa-mumble-quick-connect/blob/master/CONTRIBUTING.md).\
(I promise, it's not much, just some basics)

<!-- Links -->

[weblate engage]: https://weblate.ppfeufer.de/engage/alliance-auth-apps/ "Weblate Translations"

<p align="center">
  <img src="docs/static/logo.svg" alt=""/>
</p>

<p align="center">
    <a href="https://pypi.org/project/cracknuts/"><img src="https://img.shields.io/pypi/v/cracknuts.svg" /></a>
    <a href="https://github.com/cracknuts-team/cracknuts/blob/main/LICENSE"><img src="https://img.shields.io/github/license/cracknuts-team/cracknuts.svg" /></a>
    <a href="https://github.com/cracknuts-team/cracknuts/releases"><img alt="GitHub release" src="https://img.shields.io/github/release/cracknuts-team/cracknuts.svg"></a>
</p>

A library for `CrackNuts` device.  
This repository is the Python library for controlling the Cracker device and performing key analysis in the CrackNuts project.

## Install

Just run `pip install cracknuts` or run `pip install cracknuts[jupyter]` if you are developing in [Jupyter](https://jupyter.org/).

Then run `cracknuts welcome`, and it will print the welcome message and version information of `CrackNuts`.

```text
   ______                           __      _   __           __
  / ____/   _____  ____ _  _____   / /__   / | / /  __  __  / /_   _____
 / /       / ___/ / __ `/ / ___/  / //_/  /  |/ /  / / / / / __/  / ___/
/ /___    / /    / /_/ / / /__   / ,<    / /|  /  / /_/ / / /_   (__  )
\____/   /_/     \__,_/  \___/  /_/|_|  /_/ |_/   \__,_/  \__/  /____/

Welcome to CrackNuts(0.17.0)! 🎉

Here are some commands to get you started:

1. cracknuts tutorials - Open the tutorials to learn more about CrackNuts.
2. cracknuts lab - Launch Jupyter Lab for interactive analysis.
3. cracknuts --help - View detailed command options and usage instructions.

For more information, visit:
- Official website: https://cracknuts.io
- GitHub repository: https://github.com/cracknuts-team/cracknuts
- API documentation: https://api.cracknuts.io

Enjoy exploring CrackNuts! If you need assistance, feel free to check the documentation or ask for help.
```

Once all the above steps complete without errors, the installation is successful, and you can start using `CrackNuts` for research and study.

Alternatively, you can use the quick install script. It will install Miniconda, create an environment named `cracknuts`, and add two `CrackNuts` shortcuts to the desktop (on Windows) or to the application launcher.

*Windows*

```shell
curl https://raw.githubusercontent.com/cracknuts-team/cracknuts/refs/heads/main/install/win-install.ps1 -o "cracknuts-win-install.ps1"; powershell -ExecutionPolicy Bypass -File ".\cracknuts-win-install.ps1"; del "cracknuts-win-install.ps1"
```

*Linux*

```shell
curl -sSL https://raw.githubusercontent.com/cracknuts-team/cracknuts/refs/heads/main/install/install.sh | bash
```

## Usage

Visit [CrackNuts](https://cracknuts.io) for more information.  

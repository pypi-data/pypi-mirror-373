rosdep
------
[![Build status](https://github.com/ros-infrastructure/rosdep/actions/workflows/ci.yaml/badge.svg?branch=master&event=push)](https://github.com/ros-infrastructure/rosdep/actions/workflows/ci.yaml?query=branch%3Amaster+event%3Apush)
[![codecov](https://codecov.io/gh/ros-infrastructure/rosdep/branch/master/graph/badge.svg)](https://codecov.io/gh/ros-infrastructure/rosdep)

rosdep is a command-line tool for installing system dependencies. For *end-users*, rosdep helps you install system dependencies for software that you are building from source. For *developers*, rosdep simplifies the problem of installing system dependencies on different platforms. Instead of having to figure out which debian package on Ubuntu Oneiric contains Boost, you can just specify a dependency on 'boost'.

Includes support for pip alternatives like uv, and extra command line options to make integration with automated build systems more convenient

* Runs `apt` and `pip` installs in a single command
* Adds `--reinstall` option to the `check` command (to produce a list of all resolved dependencies, per installer)
* Supports use of `uv` (and others) via environment variable `ROSDEP_PIP_CMD="uv pip"`
* Supports pip package version specification in `rosdep.yaml`

[rosdep Users/Developers Guide](http://docs.ros.org/independent/api/rosdep/html/)

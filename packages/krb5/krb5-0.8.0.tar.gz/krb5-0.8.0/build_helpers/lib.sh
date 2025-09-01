#!/bin/bash


lib::setup::debian_requirements() {
    echo "Installing Debian based pre-requisites"
    export DEBIAN_FRONTEND=noninteractive
    apt-get update

    if [ x"$KRB5_PROVIDER" = "xheimdal" ]; then
        echo "Installing Heimdal packages for Debian"
        apt-get -y install \
            heimdal-{clients,dev,kdc}

        export PATH="/usr/lib/heimdal-servers:${PATH}"

    else
        echo "Installing MIT Kerberos packages for Debian"
        apt-get -y install \
            krb5-{user,kdc,admin-server,multidev} \
            libkrb5-dev
    fi
}

lib::setup::system_requirements() {
    if [ x"${GITHUB_ACTIONS}" = "xtrue" ]; then
        echo "::group::Installing System Requirements"
    fi

    if [ -f /etc/debian_version ]; then
        lib::setup::debian_requirements

    elif [ "$(uname)" == "Darwin" ]; then
        echo "No system requirements required for macOS"

    else
        echo "Distro not found!"
        false
    fi

    if [ x"${GITHUB_ACTIONS}" = "xtrue" ]; then
        echo "::endgroup::"
    fi
}

lib::setup::python_requirements() {
    if [ x"${GITHUB_ACTIONS}" = "xtrue" ]; then
        echo "::group::Installing Python Requirements"
    fi

    echo "Installing krb5"

    # Getting the version is important so that pip prioritises our local dist
    python -m pip install build
    KRB5_VERSION="$( python -c "import build.util; print(build.util.project_wheel_metadata('.').get('Version'))" )"

    python -m pip install krb5=="${KRB5_VERSION}" \
        --find-links dist \
        --verbose

    echo "Installing dev dependencies"
    python -m pip install -r requirements-dev.txt

    if [ x"${GITHUB_ACTIONS}" = "xtrue" ]; then
        echo "::endgroup::"
    fi
}

lib::sanity::run() {
    if [ x"${GITHUB_ACTIONS}" = "xtrue" ]; then
        echo "::group::Running Sanity Checks"
    fi

    python -m black . --check
    python -m isort . --check-only
    python -m mypy .

    if [ x"${GITHUB_ACTIONS}" = "xtrue" ]; then
        echo "::endgroup::"
    fi
}

lib::tests::run() {
    if [ x"${GITHUB_ACTIONS}" = "xtrue" ]; then
        echo "::group::Running Tests"
    fi

    python -m pytest -v --junitxml junit/test-results.xml

    if [ x"${GITHUB_ACTIONS}" = "xtrue" ]; then
        echo "::endgroup::"
    fi
}

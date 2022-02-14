#!/bin/bash
# See: https://stackoverflow.com/questions/59895/how-to-get-the-source-directory-of-a-bash-script-from-within-the-script-itself
# Note: you can't refactor this out: its at the top of every script so the scripts can find their includes.
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
cd "${SCRIPT_DIR}" || exit 1  # This is an unlikely failure, so don't worry too much.

# Source common includes
source include.sh

PYTHON_VERSION=${PYTHON_VERSION:-3.9}

# Check setup requirements
requires=(
    "virtualenv"
    "git"
)

check_requirements "${requires[@]}"

log "Ensure pull request rebase."
# Note: will break for git < 1.7.9 (looking at you Centos 7 users)
log "Setup pull request rebasing"
if ! git config pull.rebase true ; then
    fatal 1 "Failed to setup git pull request rebease."
fi

log "Ensure pull-request checkout for github is active."
if ! git config --get remote.origin.fetch "\+refs/pull/\*/head:refs/remotes/origin/pr/\*" ; then
    log "Setting up automatic fetch of pull requests"
    if ! git config --add remote.origin.fetch "+refs/pull/*/head:refs/remotes/origin/pr/*" ; then
        fatal 1 "Failed to configure pull request fetch for origin."
    fi
fi

log "Linking hook scripts"
if [ -e ".githooks" ] ; then
  while read -r hook; do
      log "$hook"
    if ! ln -sf "$hook" ".git/hooks/$(basename "$hook")"; then
          fatal 1 "Failed to activate repository git hooks."
    fi
  done < <(find ".githooks" -type f)
fi

log "Checking for virtualenv"
if [ ! -d venv ]; then
    if ! virtualenv -p "python${PYTHON_VERSION}" venv ; then
        fatal 1 "Could not setup a python 3.9 virtual environment."
    fi
fi

log "Activating virtualenv and installing development environment"
source activate

if ! pip install --upgrade --upgrade-strategy eager -e . ; then
    fatal 1 "Failed to install the application into the virtualenv."
fi

if ! pip install --upgrade --upgrade-strategy eager -r "requirements.dev.txt" ; then
    fatal 1 "Failed to install development requirements (hooks and tests will not work properly)."
fi

log "Success."
exit 0

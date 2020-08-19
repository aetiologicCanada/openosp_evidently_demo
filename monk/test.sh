#!/bin/bash -x

open_osp_user=$1

# Require a username on the CLI
if [ -z "$open_osp_user" ]
  then
    echo Please provider a username.
    exit 1
  fi


printf "Testing user %s: " "$open_osp_user"

# shellcheck disable=SC1091
source ./testscript.sh "$open_osp_user"

# shellcheck disable=SC1091
source ./testscript_assert.sh "$open_osp_user"

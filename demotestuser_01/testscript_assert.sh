#!/bin/bash

open_osp_user=$1

dirTestOutput="./testscript_Output";

# Re-create necessary local directories.
rm -rf $dirTestOutput
mkdir -p $dirTestOutput;

# Fetch all files in writable.
files=$(sftp -i sftp_rsa "$open_osp_user"@pickup.evidently.ca:writable <<< "ls -1tr")

# Resolve the most recent file from writable; trim whitespace.
file=$(echo "$files" | tail -n 1 | tr -d '[:space:]')

# Fetch the most recent file
sftp -i sftp_rsa "$open_osp_user@pickup.evidently.ca:writable/$file" $dirTestOutput

untarred=$(echo "$file" | cut -f 1 -d '.')
tarDestination="$dirTestOutput/$untarred"
mkdir "$tarDestination"

tar -xvf "$dirTestOutput/$file" -C "$tarDestination"

# Assert 
testFileExists() {
  assertTrue "Expected file '$1' to exist" "[ -f $1 ]"
  echo "File exists: $1"
}

pwd

# shellcheck disable=SC1091
source "/home/bigfont/evidently/openosp_evidently_demo/shunit2/shunit2"

exit

# The *.tar files contains the expected payload.
# testFileExists "$tarDestination/debug/evidently_env"
# testFileExists "$tarDestination/debug/app.py.logs"
# testFileExists "$tarDestination/output/evidently_*.tar.gz.enc"
# testFileExists "$tarDestination/output/evidently_*_key.bin.enc"

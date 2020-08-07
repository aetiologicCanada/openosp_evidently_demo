#!/bin/bash

dirTestOutput="./testscript_Output";

# Re-create necessary local directories.
rm -rf $dirTestOutput
mkdir -p $dirTestOutput;

# Fetch all files in writable.
files=$(sftp -i sftp_rsa demotestuser_01@pickup.evidently.ca:writable <<< "ls -1tr")

# Resolve the most recent file from writable; trim whitespace.
file=$(echo "$files" | tail -n 1 | tr -d '[:space:]')

# Fetch the most recent file
sftp -i sftp_rsa "demotestuser_01@pickup.evidently.ca:writable/$file" $dirTestOutput

untarred=$(echo "$file" | cut -f 1 -d '.')
tarDestination="$dirTestOutput/$untarred"
mkdir "$tarDestination"

tar -xvf "$dirTestOutput/$file" -C "$tarDestination"

# Assert 
testFileExists() {
  assertTrue "[ -f $1 ]"
}

# shellcheck disable=SC1091
source ./../shunit2/shunit2

# The *.tar files contains the expected payload.
testFileExists "$tarDestination/debug/evidently_env"
testFileExists "$tarDestination/output/evidently_*.tar.gz.enc"
testFileExists "$tarDestination/output/evidently_*_key.bin.enc"
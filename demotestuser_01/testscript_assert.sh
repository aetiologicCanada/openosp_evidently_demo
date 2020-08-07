#!/bin/bash 

files=$(sftp -i sftp_rsa -b ./sftp_batch.sh demotestuser_01@pickup.evidently.ca)

file=$(echo "$files" | tail -n 1 | tr -d '[:space:]')

sftp -i sftp_rsa "demotestuser_01@pickup.evidently.ca:writable/$file"

destination=$(echo "$file" | cut -f 1 -d '.')
mkdir "$destination"
tar -xvf "$file" -C "$destination"

# Assert 
testFileExists() {
  assertTrue "[ -f $1 ]"
}

# shellcheck disable=SC1091
source ./../shunit2/shunit2

# The *.tar file contains the `evidently_env` file.
testFileExists "$destination/debug/evidently_env"

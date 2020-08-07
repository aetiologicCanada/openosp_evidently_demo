#!/bin/bash -x

# Assert 
# 1. There is a *.tar file.
# 2. The *.tar file contains the `evidently_env` file.

mkdir -p ./testscript_output
file=$(sftp -i sftp_rsa -b ./sftp_batch.sh demotestuser_01@pickup.evidently.ca | tail -n 1 | tr -d '[:space:]')
sftp -i sftp_rsa "demotestuser_01@pickup.evidently.ca:writable/$file"

tar -xvf "$file"

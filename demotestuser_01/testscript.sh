#!/bin/bash

dirOscarRemitFiles="/home/jenkins/workspace/demotestuser_01/volumes/OscarDocument/oscar/document"
fileSourceRemit="/tmp/junkfile"
fileTargetRemit="$dirOscarRemitFiles/teleplanremitjunk"

# Print the current working directory.
pwd

# Clean-up previous test artifacts.
sudo rm -f $fileSourceRemit
sudo rm -f $fileTargetRemit

# Rebuild the docker image in the **parent** directory.
sudo docker image build -t evidentlyslocker/openosp_evidently_demo:latest ..
sudo docker push evidentlyslocker/openosp_evidently_demo:latest

# Restart Docker and follow its logs.
docker-compose stop
docker-compose up --force-recreate --build -d

# Make a 5 MB junk file; write the date to it.
fallocate -l $((5*1024*1024)) $fileSourceRemit
date >> $fileSourceRemit

# Create the oscar documents directory.
mkdir -p $dirOscarRemitFiles

# Copy the remit file to the oscar document directory.
# This triggers the watchdog.
rsync $fileSourceRemit $fileTargetRemit

# Inspect the docker logs.
docker-compose logs -f

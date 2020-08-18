#!/bin/bash

dirOscarRemitFiles="/home/jenkins/workspace/demotestuser_01/volumes/OscarDocument/oscar/document"
dirOscarBillingFiles="/home/jenkins/workspace/demotestuser_01/volumes/OscarDocument/oscar/billing/download"
fileSourceJunk="/tmp/junkfile"
fileTargetRemit="$dirOscarRemitFiles/teleplanremitjunk"
fileTargetBilling="$dirOscarBillingFiles/H0001"

# Print the current working directory.
pwd

# Clean-up previous test artifacts.
sudo rm -f $fileSourceJunk
sudo rm -f $fileTargetRemit
sudo rm -f $fileTargetBilling

# Rebuild the docker image in the **parent** directory.
sudo docker image build -t evidentlyslocker/openosp_evidently_demo:latest ..
sudo docker push evidentlyslocker/openosp_evidently_demo:latest

# Restart Docker and follow its logs.
docker-compose stop
docker-compose up --force-recreate --build -d

# Make a 5 MB junk file; write the date to it.
fallocate -l $((5*1024*1024)) $fileSourceJunk
date >> $fileSourceJunk

cat $fileSourceJunk

# Create the oscar documents directory.
mkdir -p $dirOscarRemitFiles
mkdir -p $dirOscarBillingFiles

# Copy the remit file to the oscar document directory.
# This triggers the watchdog.
rsync $fileSourceJunk $fileTargetBilling
rsync $fileSourceJunk $fileTargetRemit

# Follow the docker logs
docker-compose logs -ft
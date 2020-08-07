> NOTE This documentation is out of date. See `demotestuser_01/testscript.sh` file.

# Production

## Image Deployment

```bash
sudo docker image build -t evidentlyslocker/openosp_evidently_demo:latest .
sudo docker push evidentlyslocker/openosp_evidently_demo:latest
```

You can use this app without credentials, and it will fail at the stage where it tries to sftp. That's fine as a test. If you want credentials, contact
the developer.

## Use of Deployed Image

```bash
# I switch to /root/evidently and put the user folders tokens and identiiers there, but each to their own
# mkdir /root/evidently
# cd /root/evidently
# on initialization, there is no ../OscarDocuments/oscar/billing folder
# so, just in case, we create a billing folder if one does not already exist

# here we create a folder and file for claims
# right now the files are only for one user. Relative paths are forthcoming

mkdir -p /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/billing/document
# here we create a folder for remittance advice files
mkdir -p /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/document

# throw a blank file in there just to keep awk happy.

sudo  /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/document/change_this_to_targetname.txt
sudo touch /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/billing/download/Hempty_file

# note that these steps are conducted outside of the docker container because the docker-container is mounted
# read only and cannot make the folders and files


mkdir -p demo_testUser01
cd demo_testUser01
docker-compose stop
docker-compose rm -f
chmod 700 sftp_rsa
docker-compose up -d

sudo mv /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/document/change_this_to_targetname.txt /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/document/teleplanremittance_moved_here.txt

docker-compose logs -f
# should show the watchdog is triggered, and the scrub, encrypt process is underway.
# as noted above sftp will fail without user name, and ssh keys.




```

# Development

## Locally Testing using SFTP directly.

```bash
cd demo_testUser01

sftp -i sftp_rsa testUser01@pickup.evidently.ca
```

## Locally Testing using Docker.

Start the container.

```bash
cd demo_testUser01
docker-compose up --force-recreate --build -d
```

Then trigger the watcher. The watcher will send the file to the `public.evidently.ca`
server. Tail the logs to see the SFTP result.

```bash
# Ensure required directories exist (required for testing only).
mkdir -p /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/billing/download
mkdir -p /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/document
# Trigger the watcher (see config.yml for details).
sudo -s
date >  \
/home/jenkins/workspace/monk/volumes/OscarDocument/oscar/billing/download/Htest_file
date > /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/document/change_my_name.txt
docker-compose logs -f  # should show no file sftp activity

mv /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/document/change_my_name.txt /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/document/teleplanremit_testfile.txt
#Tail the logs
docker-compose logs -f
```

Unless you have a valid sftp key, the process will fail at the sftp statement. If you need to prove that the sftp works with a valid sftp key and userid, contact EVIDENTLY.

If you have an account and sftp keys, and rsa keys, then decrypt the payload. Note that `chauffeur` only works if we are running the VPN.

```bash
cd demo_testUser01
scp chauffeur@vpn.pickup.evidently.ca:/home/testUser01/sftp/writable/*.enc .
openssl rsautl -decrypt -inkey ./encrypt_rsa -in evidently-20200508-224231.tar.gz.enc -out output.tar.gz
gunzip output.tar.gz
tar -xf output.tar
cd output
```

I have broken app.py. The issue appears to be that the previous version assumed that the file teleplanremit was being created, when in fact it appears that it
is being renamed/moved, and this is a distinct thing in the watchdog framework. I attempted to modify the app to trigger the awk, encrypt, sftp function on move or create, but this has failed. My python skills have failed.

# Production

## Image Deployment

```bash
sudo docker image build -t evidentlyslocker/openosp_evidently_demo:latest .
sudo docker push evidentlyslocker/openosp_evidently_demo:latest
```

## Use of Deployed Image

```bash
# I switch to /root/evidently and put the user folders there, but each to their own
# mkdir /root/evidently
# cd /root/evidently
# on initialization, there is no ../OscarDocuments/oscar/billing folder
# so, just in case, we create a billing folder if one does not already exist

mkdir -p /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/billing/document
mkdir -p /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/document

# throw a blank file in there just to keep awk happy.

touch /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/document/change_this_to_targetname.txt
touch /home/jenkins/workspace/monk/volumes/OscarDocument/oscar/billing/download/Hempty_file

# note that these steps are conducted outside of the docker container because the docker-container is mounted
# read only and cannot make the folders and files


mkdir -p demo_testUser01
cd demo_testUser01
docker-compose stop
docker-compose rm -f
chmod 700 sftp_rsa
docker-compose up -d
```

# Development

## Locally Testing using SFTP directly.

```bash
cd demo_testUser01

sftp -i sftp_rsa testUser01@pickup.evidently.ca
```

## Locally Testing using Docker.

Start the container and tail the logs.

```bash
cd demo_testUser01
docker-compose up -f docker-compose.dev.yml --force-recreate --build -d
docker-compose logs -f
```

Then, open a new console and trigger the watcher. The watcher will send the file
to the `public.evidently.ca` server. The tail of the logs will show the SFTP result.

```bash
# Ensure required directories exist (required for testing only).
mkdir -p /root/open-osp/volumes/OscarDocument/oscar/billing/document
mkdir -p /root/open-osp/volumes/OscarDocument/oscar/document
# Trigger the watcher (see config.yml for details).
sudo -s
cd /root/open-osp/volumes/OscarDocument/
# Create
touch foobar.txt
# Move
mv foobar.txt foobar.moved.txt
```

Decrypt the payload. Note that `chauffeur` only works if we are running the VPN.

```bash
cd demo_testUser01
scp chauffeur@vpn.pickup.evidently.ca:/home/testUser01/sftp/writable/*.enc .
openssl rsautl -decrypt -inkey ./encrypt_rsa -in evidently-20200508-224231.tar.gz.enc -out output.tar.gz
gunzip output.tar.gz
tar -xf output.tar
cd output
```

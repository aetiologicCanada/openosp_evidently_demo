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

mkdir -p /root/open-osp/volumes/OscarDocument/oscar/billing

# throw a blank file in there just to keep awk happy.

touch /root/open-osp/volumes/OscarDocument/oscar/billing/Hempty_file

# note that these steps are conducted outside of the docker container because the docker-container is mounted
# read only and cannot make the folders and files


mkdir demo_testUser01
cd demo_testUser01
docker-compose stop
docker-compose rm -f
docker-compose pull
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

Start the container.

```bash
cd demo_testUser01
docker-compose up --force-recreate --build -d
```

Then trigger the watcher. The watcher will send the file to the `public.evidently.ca`
server. Tail the logs to see the SFTP result.

```bash
# Ensure required directories exist (required for testing only).
sudo mkdir -p /root/open-osp/volumes/OscarDocument/oscar/billing/
# Trigger the watcher (see config.yml for details).
sudo touch \
  /root/open-osp/volumes/OscarDocument/oscar/billing/HelloWorld \
  /root/open-osp/volumes/OscarDocument/teleplanremit_test_01 \
# Tail the logs
docker-compose logs -f
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

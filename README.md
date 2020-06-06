# Test using SFTP directly.

```bash
cd demo_testUser01
chmod 700 sftp_rsa
sftp -i sftp_rsa testUser01@pickup.evidently.ca
```

# Test using Docker.

Start the container.

```bash
cd demo_testUser01
docker-compose up --force-recreate --build -d
```

Then trigger the watcher. The watcher will send the file to the `public.evidently.ca`
server. Tail the logs to see the SFTP result.

```bash
# Ensure required directories exist (required for testing only).
sudo mkdir -p /root/open-osp/volumes/OscarDocuments/oscar/billing/
# Trigger the watcher (see config.yml for details).
sudo touch \
  /root/open-osp/volumes/OscarDocuments/oscar/billing/HelloWorld \
  /root/open-osp/volumes/OscarDocuments/teleplanremit_test_01 \
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

# Test with SFTP directly:

```bash
sftp -i sftp_rsa_testUser01 testUser01@pickup.evidently.ca
```

# Test using the Docker container.

Start the container:

```bash
cd live
docker-compose up --force-recreate --build -d
cd /root/open-osp/volumes/OscarDocument
```

Then trigger the watcher. The watcher will send the file to
then public.evidently.ca server. Tail the logs to see the
SFTP result.

```bash
cd live/data
touch teleplanremit_01
docker-compose logs -f # tail the logs
```

Decrypt the payload.

```bash
cd live/
scp chauffeur@vpn.pickup.evidently.ca:/home/testUser01/sftp/writable/*.enc .
openssl rsautl -decrypt -inkey ./encrypt_rsa -in evidently-20200508-224231.tar.gz.enc -out output.tar.gz
gunzip output.tar.gz
tar -xf output.tar
cd output
```

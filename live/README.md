# Test with SFTP directly:

```bash
sftp -i sftp_rsa_testUser01 testUser01@pickup.evidently.ca
```

# Test using the Docker container.

In one bash terminal, start the container.

```bash
cd live
docker-compose build
docker-compose up -d # daemon mode
docker-compose logs -f # tail the logs
```

In another bash terminal, trigger the watcher. The watcher will send the file to
then public.evidently.ca server. The local log output will be visible in the
previous terminal window that we recently started.

```bash
cd live/data
touch test01.trigger
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

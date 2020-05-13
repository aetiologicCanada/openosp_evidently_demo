Test with SFTP directly:

```bash
sftp -i sftp_rsa_testUser01 testUser01@pickup.evidently.ca
```

Test using the Docker container.

```bash
cd live
docker-compose build
docker-compose up -d # daemon mode
docker-compose logs -f # tail the logs
```

Decrypt the payload

```bash
cd evidently/live/
scp chauffeur@vpn.pickup.evidently.ca:/home/testUser01/sftp/writable/*.enc .
openssl rsautl -decrypt -inkey ./encrypt_rsa -in evidently-20200508-224231.tar.gz.enc -out output.tar.gz
gunzip output.tar.gz
tar -xf output.tar
cd output
```

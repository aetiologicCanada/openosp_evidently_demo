Modify docker-compose.tml so that /data on the host points to the appropriate folder

Modify config.yml target so that the glob for laim.awk points to the proper folder: currently it assumes /data/folder1/folder2/H*

cd ../live
docker-compose build
docker-compose up & 
then in data/ copy the extant teleplan file to a new file with prefix teleplanremit

monitor docker-compose logs -f to see files send to evidently.


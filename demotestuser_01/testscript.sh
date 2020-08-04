docker-compose stop
docker-compose up -d
pwd
docker-compose logs  -t
date > /tmp/junkfile
cp /tmp/junkfile  /home/jenkins/workspace/demotestuser_01/volumes/OscarDocument/oscar/document/
docker-compose logs  -t
mv /tmp/junkfile /home/jenkins/workspace/demotestuser_01/volumes/OscarDocument/oscar/document/teleplanremitjunk
sleep 20
docker-compose stop


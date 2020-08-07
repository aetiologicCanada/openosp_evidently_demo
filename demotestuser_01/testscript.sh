docker-compose stop
docker-compose up -d
pwd
docker-compose logs  -t
date >> /tmp/junkfile
fallocate -l $((5*1024*1024)) /tmp/junkfile
sync
mkdir -p /home/jenkins/workspace/demotestuser_01/volumes/OscarDocument/oscar/document

cp /tmp/junkfile /home/jenkins/workspace/demotestuser_01/volumes/OscarDocument/oscar/document/
sync
docker-compose logs  -t
sudo rm -f /home/jenkins/workspace/demotestuser_01/volumes/OscarDocument/oscar/document/teleplanremitjunk
rsync /tmp/junkfile /home/jenkins/workspace/demotestuser_01/volumes/OscarDocument/oscar/document/teleplanremitjunk
docker-compose stop


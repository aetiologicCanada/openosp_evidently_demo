For demonstration purposes

cd ./live

docker-compose build

docker-compose up & 

then from shell

Copy the extant teleplan file to a new file in the same folder, ensure new file has prefix teleplanremit,
eg. sudo cp data/teleplanremit1234567.txt data/teleplanremit_junk01

then:

monitor with:

docker-compose logs -f to see files send to evidently.


Once this is working, we can:

modify live/docker-compose.yml so that /data on the host points to the appropriate OSCARDOCUMENTS folder on a real OSCAR instance

Modify live/config.yml target so that the glob for claim.awk points to the proper folder: currently it assumes
OSCARDOCUMENTS maps to /data and that claims are in OSCARDOCUMENTS//folder1/folder2/H* 

If the claims are not below OSCARDOCUMENTS I will  have to make some adjustments


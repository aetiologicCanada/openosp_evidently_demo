To install

Obtain a shell on an open-osp instance
     
     git clone https://github.com/aetiologicCanada/openosp_evidently_demo/
     cd openosp_evidently_demo
     
     modify evidently_env to correct userid
     install user-specific keys as provided.. default userid (testUser01) is available for testing, but
     data is immediately discarded.
     
     cd ./live
     docker-compose build

     docker-compose up & 

To force initial transfer of data add a new file of filename teleplanremit.. to ../OscarDocument  
e.g. :

    cd /root/open-osp/volumes/OscarDocuments
    rm -f teleplanremit_evidently_junk
    touch teleplanremit_evidently_jun
    # This just generates a file with the appropriate trigger filename 
    # and this trigers the scrub, tarball, encrypt, sftp and cleanup processes 

monitor with:

    docker-compose logs -f to see files send to evidently.


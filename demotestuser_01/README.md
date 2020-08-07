# Usage

```
# Start docker
sudo service docker start

# Clone the repo and enter the directory
git clone git@github.com:aetiologicCanada/openosp_evidently_demo.git
cd demotestuser_01/

# Run the test script.
sudo ./testscript.sh

# Once it finishes, run the assertion script
sudo ./testscript_assert.sh
```

# Description

The `demotestuser_01` is intended to be an account which will "support"
the `openosp_evidently_demo` docker testing process.

There are corresponding files in /home/jenkin/workspace/demotestuser_01/volumes
where we keep dummy claims and billing data.

The ./testscript.sh shell file brings up docker-compose, puts a file in the
remittance advice folder, renames it to trigger watchdog, then waits for it to
mawk, encrypt and sftp the output object to pickup.

Then it shuts down docker-compose.

import logging
import os
import shutil
import subprocess
import time
from fnmatch import fnmatch
from glob import glob
from shutil import copyfile

import yaml

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

with open('config.yml') as f:
    config = yaml.safe_load(f)

SOURCE_DIR = '/remittance_directory'
SOURCE_DIR_CLAIMS = '/claims_directory'
TARGET_DIR = '/output'
TARGET_DATA_DIR = os.path.join(TARGET_DIR, '/output/evidently_data/')
ENCRYPT_KEY = '/app/encrypt.pub.pem'
SFTP_KEY = '/app/sftp.pk'
DEBUG_DIRECTORY = '/debug'
# TODO Why are we doubling up the '.pem' suffix here?
ENCRYPT_KEY_PKCS8 = ENCRYPT_KEY + '.pem'
TIME_STAMP = time.strftime("%Y%m%d-%H%M%S")
SYMMETRIC_KEY = '/output/key.bin'
SYMMETRIC_KEY_ENC = '/output/evidently_{}_key.bin.enc'.format(TIME_STAMP)

shutil.rmtree(TARGET_DATA_DIR, ignore_errors=True, onerror=None)
os.makedirs(TARGET_DATA_DIR, exist_ok=True)
os.makedirs(TARGET_DIR,      exist_ok=True)


def is_trigger_file(file_path):
    return fnmatch(file_path, config['trigger_file_glob'])


def run_awk_scripts():
    for script in config['awk_scripts']:
        script_path = script['script']
        target_file_glob = script['target_file_glob']
        assert os.path.exists(
            script_path), 'Missing file {}'.format(script_path)
        cmd = 'mawk -f {} -v output_directory={} {}'.format(
            script_path, TARGET_DATA_DIR, target_file_glob)
        logging.info(cmd)
        subprocess.check_call(cmd, shell=True)


def tar_output_files():
    result_file = os.path.join(
        TARGET_DIR, 'evidently_{}.tar.gz'.format(TIME_STAMP))
    logging.info('Gzipping {} into {}'.format(TARGET_DATA_DIR, result_file))
    subprocess.check_call(['tar', 'czf', result_file, TARGET_DATA_DIR])
    logging.info('Gzip completed')
    return result_file


def encrypt_setup():
    """Generate the symmetric key and its encrypted counterpart.
    Follows https://www.czeskis.com/random/openssl-encrypt-file.html
    """

    # generate a symmetric key
    logging.info('Generating symmetric key')
    subprocess.check_call(
        'openssl rand -base64 32 > {}'.format(SYMMETRIC_KEY),
        shell=True)
    logging.info("bin created")

    # encrypt the symmetric key using the asymmetric keys
    subprocess.check_call(
        'openssl rsautl -encrypt -inkey {} -pubin -in {} -out {}'.format(
            ENCRYPT_KEY, SYMMETRIC_KEY, SYMMETRIC_KEY_ENC),
        shell=True)


def encrypt_tar_ball(in_path):
    """Encrypt the tarball with the symmetric key.
    """

    out_path = '{}.enc'.format(in_path)

    # encrypt the tar ball
    subprocess.check_call(
        'openssl enc  -pbkdf2 -salt -in {} -out {} -pass file:{}'.format(
            in_path, out_path, SYMMETRIC_KEY_ENC),
        shell=True)

    file_stats = os.stat(out_path)

    logging.info(out_path)
    logging.info(file_stats)

    return out_path


def push_to_sftp(file_path):

    sftp_uri = '{}@{}'.format(config['sftp']['user'], config['sftp']['host'])
    target_dir = config['sftp']['remote_dir']

    logging.info("SFTP put {} to {} {}".format(
        file_path, sftp_uri, target_dir))

    subprocess.check_call(["sftp -oIdentityFile={} -oStrictHostKeyChecking=accept-new {} <<< $'cd {}\nput {}'"
                           .format(SFTP_KEY, sftp_uri, target_dir, file_path)],
                          shell=True, executable='/bin/bash')

    logging.info("SFTP completed")


def add_files_to_sftp_message(files):
    """Create a new tar achive that contains 
    1. the symmetrically encrypted SFTP payload and 
    2. the assymmetrically encrypted symmetric key that encrypted it.
    """
    logging.info('Creating sftp envelope for {}'.format(files))
    envelope = 'evidently_{}_message.tar'.format(TIME_STAMP)
    subprocess.check_call(
        ['tar', 'cfv', envelope, *files])
    return envelope


def cleanup():
    shutil.rmtree(TARGET_DIR, TARGET_DATA_DIR)
    os.makedirs(TARGET_DATA_DIR, exist_ok=True)


def run_file_trigger(dest_path):
    logging.info('run_file_trigger {}'.format(dest_path))
    if is_trigger_file(dest_path):
        try:
            logging.info("Workflow triggered")
            run_awk_scripts()
            tarball = tar_output_files()
            encrypt_setup()
            encrypted_file = encrypt_tar_ball(tarball)
            sftp_envelope = add_files_to_sftp_message([
                encrypted_file,
                SYMMETRIC_KEY_ENC,
                DEBUG_DIRECTORY
            ])
            # here, wrap push_to_sftp in exponential backoff: https://coderwall.com/p/--eiqg/exponential-backoff-in-bash
            push_to_sftp(sftp_envelope)
        except Exception as ex:
            logging.error(ex)
        finally:
            cleanup()


def is_app_running_with_docker_compose():
    return os.path.isdir(SOURCE_DIR) and os.path.isdir(SOURCE_DIR_CLAIMS) and os.path.isdir(DEBUG_DIRECTORY)


class Handler(FileSystemEventHandler):
    def on_moved(self, event):
        logging.info(event)
        run_file_trigger(event.dest_path)

    def on_created(self, event):
        logging.info(event)
        run_file_trigger(event.src_path)


if not is_app_running_with_docker_compose():
    raise ValueError(
        'Ferdinand, please start the app with docker-compose not with docker.')


# https://stackoverflow.com/questions/38537905/set-logging-levels
logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(DEBUG_DIRECTORY, 'app.py.logs'),
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


if __name__ == '__main__':
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Starting Evidently with config: {}".format(config))

    observer = Observer()
    observer.schedule(Handler(), SOURCE_DIR)
    observer.start()
    logging.info("Watching {}".format(SOURCE_DIR))
    observer.join()

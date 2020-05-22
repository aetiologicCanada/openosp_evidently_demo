import logging
import os
import shutil
import subprocess
import time
from fnmatch import fnmatch
from glob import glob

import yaml

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

with open('config.yml') as f:
    config = yaml.safe_load(f)

SOURCE_DIR = '/data'
TARGET_DIR = '/output'
TARGET_DATA_DIR = os.path.join(TARGET_DIR, '/output/evidently_data')
ENCRYPT_KEY = '/app/encrypt.pub.pem'
SFTP_KEY = '/app/sftp.pk'
ENCRYPT_KEY_PKCS8 = ENCRYPT_KEY + '.pem'
TIME_STAMP = time.strftime("%Y%m%d-%H%M%S")
logging.info(TIME_STAMP)
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
        assert os.path.exists(
            script_path), 'Missing file {}'.format(script_path)
        cmd = 'awk -f {} -v output_directory={} {}'.format(script_path,
                                                           TARGET_DATA_DIR, script['target_file_glob'])
        logging.info(cmd)
        subprocess.check_call(cmd, shell=True)


def tar_output_files():
    result_file = os.path.join(
        TARGET_DIR, 'evidently_{}.tar.gz'.format(TIME_STAMP))
    logging.info('Gzipping {} into {}'.format(TARGET_DATA_DIR, result_file))
    subprocess.check_call(['tar', 'czf', result_file, TARGET_DATA_DIR])
    logging.info('Gzip completed')
    file_stats = os.stat(result_file)
    return result_file


def encrypt_setup():
    # follows: https://www.czeskis.com/random/openssl-encrypt-file.html

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
    return(SYMMETRIC_KEY)


def encrypt_tar_ball(in_path):
    out_path = '{}.enc'.format(in_path)

# encrypt the tar ball
    subprocess.check_call(
        'openssl enc  -pbkdf2 -salt -in {} -out {} -pass file:{}'.format(
            in_path, out_path, ENCRYPT_KEY),
        shell=True)

    #file_stats = os.stat(out_path)
    # logging.info(out_path)
    # logging.info(file_stats)

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


def cleanup():
    shutil.rmtree(TARGET_DIR, TARGET_DATA_DIR)
    os.makedirs(TARGET_DATA_DIR, exist_ok=True)


def run_file_trigger(file_event):
    logging.info("File event {}".format(file_event))
    if is_trigger_file(file_event.src_path):
        try:
            logging.info("Workflow triggered")
            run_awk_scripts()
            tarball = tar_output_files()
            encrypted_file = encrypt_tar_ball(tarball)

            '''
            TODO [shaun] Make a new directory for both files.
            TODO [shaun] Put both files into that directory.
            TODO [shaun] SFTP that single directory with one call to `push_to_sftp`.

            Here is the target directory and naming structure.
            ```
            evidently_date_time_message/
                evidently_date_time_key.bin.enc
                evidently_date_time_payload.tar.gz.enc
            ```
            '''

            push_to_sftp(SYMMETRIC_KEY_ENC)
            push_to_sftp(encrypted_file)
        except Exception as ex:
            logging.error(ex)
        finally:
            cleanup()


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        run_file_trigger(event)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    observer = Observer()
    observer.schedule(Handler(), SOURCE_DIR)
    observer.start()
    logging.info("Watching {}".format(SOURCE_DIR))
    observer.join()

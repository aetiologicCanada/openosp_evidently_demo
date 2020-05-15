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
TARGET_DATA_DIR = os.path.join(TARGET_DIR, 'data')
ENCRYPT_KEY = '/app/encrypt.pub'
SFTP_KEY = '/app/sftp.pk'
ENCRYPT_KEY_PKCS8 = ENCRYPT_KEY + '.pem'

os.makedirs(TARGET_DATA_DIR, exist_ok=True)


def is_trigger_file(file_path):
    return fnmatch(file_path, config['trigger_file_glob'])


def run_awk_scripts():
    for script in config['awk_scripts']:
        script_path = script['script']
        assert os.path.exists(script_path), 'Missing file {}'.format(script_path)
        for source_file in glob(os.path.join(SOURCE_DIR, script['target_file_glob'])):
            target_file = os.path.join(TARGET_DATA_DIR, os.path.basename(source_file))
            cmd = 'awk -f {} {} > {}'.format(script_path, source_file, target_file)
            logging.info(cmd)
            subprocess.check_call(cmd, shell=True)


def tar_output_files():
    result_file = os.path.join(TARGET_DIR, 'evidently-{}.tar.gz'.format(time.strftime("%Y%m%d-%H%M%S")))
    logging.info('Gzipping {} into {}'.format(TARGET_DATA_DIR, result_file))
    subprocess.check_call(['tar', 'czf', result_file, TARGET_DATA_DIR])
    return result_file


def encrypt_file(in_path):
    out_path = '{}.enc'.format(in_path)
    logging.info('Encrypting {} to {}'.format(in_path, out_path))
    # openssl rsautl expects a public key in PKCS8 format, so we convert it first
    subprocess.check_call(
        'ssh-keygen -f {} -e -m pkcs8 > {}'.format(ENCRYPT_KEY, ENCRYPT_KEY_PKCS8),
        shell=True)
    subprocess.check_call(
        'openssl rsautl -encrypt -inkey {} -pubin -in {} -out {}'.format(ENCRYPT_KEY_PKCS8, in_path, out_path),
        shell=True)
    return out_path


def push_to_sftp(file_path):
    sftp_uri = '{}@{}'.format(config['sftp']['user'], config['sftp']['host'])
    target_dir = config['sftp']['remote_dir']
    logging.info("SFTP put {} to {}".format(file_path, sftp_uri))
    subprocess.check_call(["sftp -oIdentityFile={} -oStrictHostKeyChecking=accept-new {} <<< $'cd {}\nput {}'"
                          .format(SFTP_KEY, sftp_uri, target_dir, file_path)],
                          shell=True, executable='/bin/bash')


def cleanup():
    shutil.rmtree(TARGET_DIR)
    os.makedirs(TARGET_DATA_DIR, exist_ok=True)


def run_file_trigger(file_event):
    logging.info("File event {}".format(file_event))
    if is_trigger_file(file_event.src_path):
        try:
            logging.info("Workflow triggered")
            run_awk_scripts()
            tarball = tar_output_files()
            encrypted_file = encrypt_file(tarball)
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

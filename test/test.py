import os
import shutil
import subprocess
import time
from glob import glob
from pathlib import Path

import pytest

pytest_plugins = ["docker_compose"]


@pytest.fixture(autouse=True)
def setup_and_teardown():
    os.makedirs('./share', exist_ok=True)
    yield
    shutil.rmtree('./share')


def test_all(function_scoped_container_getter):
    time.sleep(5)
    Path('./data/go.trigger').touch()
    time.sleep(30)
    files = list(glob('share/evidently-*.tar.gz.enc'))
    assert len(files) > 0
    out_file = 'share/out.tar.gz'
    subprocess.check_call('openssl rsautl -decrypt -inkey encrypt_rsa -in {} -out {}'.format(files[0], out_file),
                          shell=True)
    subprocess.check_call('tar xzf {} -C share'.format(out_file), shell=True)
    with open('share/output/data/test_data.ssv', 'r') as f:
        assert f.readlines() == ['yes 2\n']


if __name__ == '__main__':
    pytest.main()

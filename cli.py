__title__ = "python-backups"
__author__ = "Paulo Antunes"
__credits__ = [
    "Paulo Antunes",
]
__license__ = "MIT"
__maintainer__ = "Paulo Antunes"
__email__ = "pjmlantunes@gmail.com"
__version__ = "0.1.0"

import logging
import os
import sys
import shutil
import schedule
import time
import subprocess
from datetime import datetime
from environs import Env


logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


env = Env()
env.read_env()


def _rsync(now):
    for path in env.list('SOURCE_PATHS'):
        folder_name = path.split('/')[-2]
        destination_path = os.path.join(
            env('DESTINATION_PATH'),
            now.strftime('%Y-%m-%d %H%M'),
            folder_name
        )
        os.makedirs(destination_path)
        logger.info(
            'SOURCE_PATH: {} DESTINATION_PATH: {}'.format(
                path, destination_path
            )
        )
        out = subprocess.check_output(
            ['rsync', '-av', path, destination_path],
            universal_newlines=True
        )
        logger.info(out)


def _clean_old_backups():
    list_backups = sorted([x for x in os.listdir(env('DESTINATION_PATH'))])
    to_remove = list_backups[:-env.int('NUMBER_OF_LAST_BACKUPS_KEPT')]

    logger.info('REMOVE: {}'.format(to_remove))
    for x in to_remove:
        shutil.rmtree(os.path.join(env('DESTINATION_PATH'), x))


def job():
    now = datetime.now()

    try:
        _rsync(now=now)
    except subprocess.CalledProcessError as e:
        logger.info(e.output)
        sys.exit(0)

    _clean_old_backups()

    logger.info(
        'TIME: {:0.2f} minute(s)'.format(
            (datetime.now() - now).total_seconds() / 60
        )
    )


if __name__ == "__main__":
    pim = env.int('POOLING_INTERVAL_IN_MINUTES', None)
    pt = env('POOLING_TIME', None)

    if not (bool(pim) ^ bool(pt)):
        logger.info('Only 1 POOLING config should be set')
        sys.exit(0)

    if pim:
        logger.info('Scheduling Task to run each {} minutes'.format(pim))
        schedule.every(pim).minutes.do(job)
    elif pt:
        logger.info('Scheduling Task at {}'.format(pt))
        schedule.every().day.at(pt).do(job)
    else:
        logger.info('POOLING config not found')
        sys.exit(0)

    while True:
        schedule.run_pending()
        time.sleep(1)

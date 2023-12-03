import time

from flask import Flask, request, jsonify
import requests
import asyncio
import logging
import os
from multiprocessing import Process
import multiprocessing
from CountDownLatch import CountDownLatch

logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)

app.message_counter = 0

app.msgs = []

secondaries = [os.environ.get('SECONDARY1_URL'), os.environ.get('SECONDARY2_URL')]


HEALTH_CHECK_INTERVAL = 10


def increment_counter():
    app.message_counter += 1


@app.route('/append', methods=['POST'])
async def append():
    # Get message
    new_msg = request.get_json().get('message')
    if not new_msg:
        raise requests.RequestException('Your request isn\'t correct')
    app.logger.debug("New message is correct")

    increment_counter()

    # Get write concern parameter and make it list for use it as link type parameter
    w = multiprocessing.Value('i', int(request.get_json().get('write_concern')))
    w.value -= 1  # Minus one as there is no need to wait for master replication

    # Set Condition for wait write concern replication
    condition = CountDownLatch(count=w, app=app)

    # Add replication on master
    app.msgs.append((app.message_counter, new_msg))
    app.logger.debug('Replication for master was ended')

    # Replicate it for each secondaries
    for inx, sec in enumerate(secondaries):
        Process(target=replication_on_secondary,
                args=(sec, (app.message_counter, new_msg), condition)
                ).start()

    # Wait for condition
    condition.awaiter()

    app.logger.info(f'Replication was ended')

    return jsonify({"message": "Message was created"}), 201


@app.route('/msgs_list', methods=['GET'])
def msgs_list():
    return jsonify({'list': app.msgs})


@app.errorhandler(requests.RequestException)
def handle_request_exception(error):
    app.logger.error(error)
    return jsonify({"error": str(error)}), 500


def replication_on_secondary(host, new_msg, condition, delay=None, retry=False):
    app.logger.debug('Start replication for {0}'.format(host))

    if retry:
        app.logger.debug('Delay equals to {0}'.format(sum(delay)))
        time.sleep(sum(delay))
        delay = next_delay(delay)

    try:
        response = requests.post(host + '/append', json={'message': new_msg})

        # Check each request on succeed work
        if response.status_code != 201:
            raise requests.RequestException()
    except requests.RequestException as e:
        app.logger.debug(e)
        replication_on_secondary(host, new_msg, condition, delay=delay, retry=True)

    if not retry:
        app.logger.debug('Replication for {0} was ended'.format(host))
        condition.count_down()


def next_delay(delay):
    if delay is None:
        delay = [0, 1]

    buffer = delay[1]
    delay[1] = sum(delay)
    delay[0] = buffer

    return delay


def check_health(host, delay=None, retry=False):
    delay = next_delay(delay)
    time.sleep(sum(delay))

    # Turn off retries in requests library in order check only my retries
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=0))
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=0))

    while True:
        app.logger.debug(f'Health check with {delay} delay for {host}')
        try:
            response = session.get(host + '/health')
            # Check each request on succeed work
            if response.status_code != 200:
                raise requests.RequestException()
        except requests.RequestException as e:
            app.logger.debug(e)
            check_health(host, delay, retry=True)

        if retry:
            break

        time.sleep(HEALTH_CHECK_INTERVAL)


if __name__ == '__main__':
    for host in secondaries:
        health_check_thread = multiprocessing.Process(target=check_health,
                                                      args=(host,)
                                                      )
        health_check_thread.start()

    app.run(host='0.0.0.0')

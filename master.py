import time

from flask import Flask, request, jsonify
import requests
import asyncio
import logging
import os
from multiprocessing import Process
import multiprocessing
from CountDownLatch import CountDownLatch
from SecondaryClass import SecondaryClass

logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)

app.message_counter = 0

app.msgs = []

secondaries_hosts = [os.environ.get('SECONDARY1_URL'), os.environ.get('SECONDARY2_URL')]

secondaries = []

HEALTH_CHECK_INTERVAL = 10

# Take QUORUM (for 2 sec and master is 2)
QUORUM = (len(secondaries_hosts) + 1) // 2 + 1
quorum_status = multiprocessing.Value('i', 1)


def check_quorum():
    health_hosts = 1
    for sec in secondaries:
        health_hosts += sec.get_status() == 'Healthy'
    quorum_status.value = health_hosts
    return quorum_status.value < QUORUM


def increment_counter():
    app.message_counter += 1


@app.route('/append', methods=['POST'])
async def append():
    app.logger.debug(f"Healthy hosts is {quorum_status.value} where quorum is {QUORUM}")
    if check_quorum():
        return jsonify({"message": "Server in read-only mode"}), 500

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


def replication_on_secondary(sec, new_msg, condition, retry=False):
    app.logger.debug('Start replication for {0}'.format(sec.get_host()))
    if retry:
        delay = sec.get_delay()
        app.logger.debug('Delay equals to {0}'.format(delay.value))
        time.sleep(delay.value)

    try:
        response = requests.post(sec.get_host() + '/append', json={'message': new_msg})

        # Check each request on succeed work
        if response.status_code != 201:
            raise requests.RequestException()
    except requests.RequestException as e:
        app.logger.debug(e)
        replication_on_secondary(sec, new_msg, condition, retry=True)

    if not retry:
        app.logger.debug('Replication for {0} was ended'.format(sec.get_host()))
        condition.count_down()


def check_health(sec, retry=False):
    delay = sec.next_delay()
    time.sleep(delay.value)

    # Turn off retries in requests library in order check/use only my retries
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=0))
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=0))

    while True:
        app.logger.debug(f'Health check with {delay.value} delay for {sec.get_host()} with status {sec.get_status()}')
        try:
            response = session.get(sec.host + '/health')
            # Check each request on succeed work
            if response.status_code != 200:
                raise requests.RequestException()
        except requests.RequestException as e:
            app.logger.error(e)
            check_health(sec, retry=True)
            sec.clear_delay()

        if retry:
            break

        #  When secondary is healthy - I check it for each HEALTH_CHECK_INTERVAL second
        time.sleep(HEALTH_CHECK_INTERVAL)


if __name__ == '__main__':
    for host in secondaries_hosts:
        sec = SecondaryClass(host=host)
        secondaries.append(sec)
        health_check_thread = multiprocessing.Process(target=check_health,
                                                      args=(sec,)
                                                      )
        health_check_thread.start()

    app.run(host='0.0.0.0')

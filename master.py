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

global message_counter
message_counter = 0

msgs = []

secondaries = [os.environ.get('SECONDARY1_URL'), os.environ.get('SECONDARY2_URL')]


def increment_counter():
    global message_counter
    message_counter += 1


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

    # Replicate it for each secondaries
    for inx, sec in enumerate(secondaries):
        Process(target=replication_on_secondary,
                args=(sec, (message_counter, new_msg), condition)
                ).start()

    # Add replication on master
    msgs.append((message_counter, new_msg))
    app.logger.debug('Replication for master was ended')

    # Wait for condition
    condition.awaiter()

    app.logger.info(f'Replication was ended')

    return jsonify({"message": "Message was created"}), 201


@app.route('/msgs_list', methods=['GET'])
def msgs_list():
    return jsonify({'list': sorted(msgs)})


@app.errorhandler(requests.RequestException)
def handle_request_exception(error):
    app.logger.error(error)
    return jsonify({"error": str(error)}), 500


def replication_on_secondary(host, new_msg, condition):
    app.logger.debug('Start replication for {0}'.format(host))
    response = requests.post(host + '/append', json={'message': new_msg})
    # Check each request on succeed work
    if response.status_code != 201:
        raise requests.RequestException("Do not receive an acknowledgment")

    app.logger.debug('Replication for {0} was ended'.format(host))
    condition.count_down()


if __name__ == '__main__':
    app.run(host='0.0.0.0')

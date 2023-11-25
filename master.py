from flask import Flask, request, jsonify
import requests
import asyncio
import logging
import os
import aiohttp

logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)

global message_counter
message_counter = 0

msgs = []

secondaries = [os.environ.get('SECONDARY1_URL'), os.environ.get('SECONDARY2_URL')]


class CountDownLatch:
    def __init__(self, count):
        self.count = count
        self.lock = asyncio.Condition()

    async def count_down(self):
        async with self.lock:
            self.count -= 1
            if self.count <= 0:
                self.lock.notify_all()

    async def awaiter(self):
        async with self.lock:
            while self.count > 0:
                await self.lock.wait()


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
    w = [int(request.get_json().get('write_concern'))]

    # Set Condition for wait write concern replication
    condition = CountDownLatch(w[0] - 1)

    background_tasks = set()

    # Replicate it for each secondaries
    for inx, sec in enumerate(secondaries):
        task = asyncio.create_task(replication_on_secondary(sec, (message_counter, new_msg), condition=condition))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

    # Add replication on master
    msgs.append((message_counter, new_msg))
    app.logger.debug('Replication for master was ended')

    await condition.awaiter()

    app.logger.info(f'Replication was ended')

    return jsonify({"message": "Message was created"}), 201


@app.route('/msgs_list', methods=['GET'])
def msgs_list():
    return jsonify({'list': sorted(msgs)})


@app.errorhandler(requests.RequestException)
def handle_request_exception(error):
    app.logger.error(error)
    return jsonify({"error": str(error)}), 500


async def replication_on_secondary(host, new_msg, condition):
    app.logger.debug('Start replication for {0}'.format(host))
    async with aiohttp.ClientSession() as session:
        async with session.post(host + '/append', json={'message': new_msg}) as response:
            # Check each request on succeed work
            if response.status != 201:
                raise requests.RequestException("Do not receive an acknowledgment")

    app.logger.debug('Replication for {0} was ended'.format(host))

    await condition.count_down()


if __name__ == '__main__':
    app.run(host='0.0.0.0')

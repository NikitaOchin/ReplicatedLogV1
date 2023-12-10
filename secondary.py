from flask import Flask, jsonify, request
import os
import random
import time
import random
import asyncio
import requests
import logging

logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)

app.msgs = []

app.buffer_msgs = []

NETWORK_DELAY = int(os.environ.get('SECONDARY_DELAY'))

master = os.environ.get('MASTER_URL')


@app.route('/append', methods=['POST'])
async def append():
    new_msg = request.get_json().get('message')

    delay = NETWORK_DELAY + random.randint(3, 10)

    app.logger.info(f"New message is {new_msg} with delay {delay}")

    await asyncio.sleep(delay)

    app.logger.debug(f"New message index is {new_msg[0]} \n Max index in msgs is {max([0] + [x[0] for x in app.msgs])}")
    app.logger.debug(f"All msgs {app.msgs} \n All buffer {app.buffer_msgs}")

    if app.buffer_msgs or new_msg[0] != max([0] + [num for num, _ in app.msgs]) + 1:
        buffer_msgs_handle(new_msg)
    # Check on duplicates and sort array to get the right order
    elif not any(num == new_msg[0] for num, _ in app.msgs):
        app.msgs.append(new_msg)
        if app.buffer_msgs:
            buffer_msgs_handle()

    app.logger.info(f"End replicate message {new_msg}")

    return jsonify({"message": "ACK"}), 201


@app.route('/msgs_list', methods=['GET'])
def msgs_list():
    return jsonify({'list': app.msgs})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


def buffer_msgs_handle(new_msg=None):
    if new_msg is not None:
        app.buffer_msgs.append(new_msg)

    # app.logger.debug(f'Max in msgs is {max([0] + [num for num, _ in app.msgs])}')
    # app.logger.debug(f'Min in buffer msgs is {min([num for num, _ in app.buffer_msgs])}')

    if max([0] + [num for num, _ in app.msgs]) + 1 == min([num for num, _ in app.buffer_msgs]):
        app.buffer_msgs.sort()
        res = 1
        for x in range(1, len(app.buffer_msgs)):
            if app.buffer_msgs[x][0] == app.buffer_msgs[x - 1][0] + 1:
                res = x + 1
            else:
                break
        app.logger.debug(f"BEFORE: All msgs {app.msgs} \n All buffer {app.buffer_msgs}")

        app.msgs.extend(app.buffer_msgs[:res])
        app.buffer_msgs[:] = app.buffer_msgs[res:]

        app.logger.debug(f"AFTER: All msgs {app.msgs} \n All buffer {app.buffer_msgs}")


if __name__ == '__main__':
    app.run(host='0.0.0.0')

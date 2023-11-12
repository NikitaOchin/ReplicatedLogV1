import random

from flask import Flask, jsonify, request
import os
import time
import random
import asyncio
import logging

logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)

msgs = []

NETWORK_DELAY = int(os.environ.get('SECONDARY_DELAY'))


@app.route('/append', methods=['POST'])
async def append():
    new_msg = request.get_json().get('message')

    delay = NETWORK_DELAY + random.randint(3, 10)

    app.logger.info(f"New message is {new_msg} with delay {delay}")
    await asyncio.sleep(delay)

    # Check on duplicates and sort array to get the right order
    if any(num == new_msg[0] for num, _ in msgs):
        msgs.append(new_msg)
        msgs.sort(key=lambda x: x[0])

    app.logger.info(f"End replicate message {new_msg}")

    return jsonify({"message": "ACK"}), 201


@app.route('/msgs_list', methods=['GET'])
def msgs_list():
    return jsonify({'list': msgs})


if __name__ == '__main__':
    app.run(host='0.0.0.0')

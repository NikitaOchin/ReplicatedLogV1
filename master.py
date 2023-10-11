from flask import Flask, request, jsonify
import requests
import asyncio
import logging

logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)

msgs = []

secondaries = ["http://secondary1:5000", "http://secondary2:5000"]


@app.route('/append', methods=['POST'])
async def append():
    # Get message
    new_msg = request.get_json().get('message')
    if not new_msg:
        raise requests.RequestException('Your request isn\'t correct')

    app.logger.debug("New message is correct")

    background_tasks = set()
    # Replicate it into each secondaries
    for sec in secondaries:
        app.logger.debug('Start replication for {0}'.format(sec))

        task = asyncio.create_task(replication_on_secondary(sec, new_msg))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

    await asyncio.gather(*background_tasks)

    app.logger.info('Replication was ended for each secondary')

    # Post message in master after succeed work
    msgs.append(new_msg)
    return jsonify({"message": "Message was created"}), 201


@app.route('/msgs_list', methods=['GET'])
def msgs_list():
    return jsonify({'list': msgs})


@app.errorhandler(requests.RequestException)
def handle_request_exception(error):
    app.logger.error(error)
    return jsonify({"error": str(error)}), 500


async def replication_on_secondary(host, new_msg):
    response = requests.post(host + '/append', json={'message': new_msg})

    # Check each request on succeed work
    if response.json().get("message") != "ACK":
        raise requests.RequestException("Do not receive an acknowledgment")

    app.logger.debug('Replication for {0} was ended'.format(host))


if __name__ == '__main__':
    app.run(host='0.0.0.0')

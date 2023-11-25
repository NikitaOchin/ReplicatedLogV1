from flask import Flask, request, jsonify
import requests
import asyncio
import logging
import os
import aiohttp
from multiprocessing import Process
import multiprocessing

logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)


class CountDownLatch:
    def __init__(self, count):
        self.count = count
        self.lock = asyncio.Lock()

    def count_down(self):
        self.lock = acquari


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
    # global w
    w = multiprocessing.Value('i', int(request.get_json().get('write_concern')))
    # w = [int(request.get_json().get('write_concern'))]

    # Set Event for wait write concern replication
    # event = asyncio.Event()

    background_tasks = set()

    # Replicate it for each secondaries
    for inx, sec in enumerate(secondaries):
        # await asyncio.create_subprocess_exec(
        # replication_on_secondary(sec, (message_counter, new_msg), w)
        # )
        Process(target=replication_on_secondary,
                args=(sec, (message_counter, new_msg), w)
                ).start()
        # task = asyncio.create_task(replication_on_secondary(sec, (message_counter, new_msg), counter=w, event=event))
        # background_tasks.add(task)
        # task.add_done_callback(background_tasks.discard)

    # Add replication on master
    replication_on_master((message_counter, new_msg), w)
    # task1 = asyncio.create_task(replication_on_master(new_msg, counter=w, event=event))
    # background_tasks.add(task1)
    # task1.add_done_callback(background_tasks.discard)

    # while w.value > 0:
    #     await asyncio.sleep(3)
    #     app.logger.info(f'{w.value}')

    condition = asyncio.Condition()
    # acquire the condition
    async with condition:
        # wait to be notified and a function to return true
        await condition.wait_for(lambda: w.value <= 0)

    app.logger.info(f'Replication was ended')

    return jsonify({"message": "Message was created"}), 201


@app.route('/msgs_list', methods=['GET'])
def msgs_list():
    return jsonify({'list': sorted(msgs)})


@app.errorhandler(requests.RequestException)
def handle_request_exception(error):
    app.logger.error(error)
    return jsonify({"error": str(error)}), 500


def replication_on_master(new_msg, counter):
    msgs.append((message_counter, new_msg))
    app.logger.debug('Replication for master was ended')
    count_down(counter)


#
# def replication_on_secondary_proccess(host, new_msg, counter, event):
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(replication_on_secondary(host, new_msg, counter, event))
#     # loop = asyncio.new_event_loop()
#     # asyncio.set_event_loop(loop)
#     # loop.run_until_complete(replication_on_secondary(host, new_msg, counter, event))


def replication_on_secondary(host, new_msg, counter):
    app.logger.debug('Start replication for {0}'.format(host))
    # async with aiohttp.ClientSession() as session:
    #     async with session.post(host + '/append', json={'message': new_msg}) as response:
    response = requests.post(host + '/append', json={'message': new_msg})
    # Check each request on succeed work
    if response.status_code != 201:
        raise requests.RequestException("Do not receive an acknowledgment")

    app.logger.debug('Replication for {0} was ended'.format(host))

    count_down(counter=counter)


def count_down(counter):
    # Function that receives counter with the remaining count of secondaries required for replication
    # When that counter equals zero - it return successful message to client
    app.logger.info(f'W equal to before {counter}')
    with counter.get_lock():
        counter.value -= 1
    app.logger.info(f'W equal to after {counter.value}')
    # if counter[0] <= 0:
    #     event[0].set()


if __name__ == '__main__':
    app.run(host='0.0.0.0')

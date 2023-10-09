from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

msgs = []

secondaries = ["http://secondary1:5000", "http://secondary2:5000"]


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/append', methods=['POST'])
def append():
    # Get message
    new_msg = request.get_json().get('message')
    if not new_msg:
        raise requests.RequestException('Your request isn\'t correct')

    # Replicate it into each secondaries
    replication_on_secondary(new_msg)

    # Post message in master after succeed work
    msgs.append(new_msg)
    return jsonify({"message": "Message was created"}), 201


@app.route('/msgs_list', methods=['GET'])
def msgs_list():
    return jsonify({'list': msgs})


@app.errorhandler(requests.RequestException)
def handle_request_exception(error):
    return jsonify({"error": str(error)}), 500


def replication_on_secondary(new_msg):
    for sec in secondaries:
        # Check each request on succeed work
        # return requests.get(sec + '/msgs_list')
        response = requests.post(sec + '/append', json={'message': new_msg})
        if response.json().get("message") != "ACK":
            raise requests.RequestException("Do not receive an acknowledgment")


if __name__ == '__main__':
    app.run(host='0.0.0.0')

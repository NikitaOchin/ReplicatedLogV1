from flask import Flask, jsonify, request
import sys

app = Flask(__name__)

msgs = []


# @app.route('/')
# def hello_world():
#     return 'Hello, World!'


@app.route('/append', methods=['POST'])
def append():
    new_msg = request.get_json().get('message')
    msgs.append(new_msg)
    return jsonify({"message": "ACK"}), 201


@app.route('/msgs_list', methods=['GET'])
def msgs_list():
    return jsonify({'list': msgs})


# port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
if __name__ == '__main__':
    app.run(host='0.0.0.0')

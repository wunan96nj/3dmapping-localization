#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uuid
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

captures = {
    'capture1': {'task': 'build an API'},
    'capture2': {'task': '哈哈哈11'},
    'capture3': {'task': 'profit!'},
}


def abort_if_capture_doesnt_exist(capture_id):
    if capture_id not in captures:
        abort(404,
              message="Capture picture {} doesn't exist".format(capture_id))


parser = reqparse.RequestParser()
parser.add_argument('task')


# Capture
# shows a single Capture item and lets you delete a Capture item
class Capture(Resource):
    def get(self, capture_id):
        abort_if_capture_doesnt_exist(capture_id)
        return captures[capture_id]

    def delete(self, capture_id):
        abort_if_capture_doesnt_exist(capture_id)
        del captures[capture_id]
        return '', 204

    def put(self, capture_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        captures[capture_id] = task
        return task, 201


# captureList
# shows a list of all captures, and lets you POST to add new tasks
class CaptureList(Resource):
    # http://127.0.0.1:5000/captures
    def get(self):
        return captures

    # http://127.0.0.1:5000/captures
    # curl http://localhost:5000/captures -d "task=something new" -X POST -v
    def post(self):
        file_uuid = str(uuid.uuid4());
        args = parser.parse_args()
        capture_id = int(max(captures.keys()).lstrip('Capture')) + 1
        capture_id = 'Capture%i' % capture_id
        captures[capture_id] = {'task': args['task']}
        return captures[capture_id], 201


##
## Actually setup the Api resource routing here
##
api.add_resource(CaptureList, '/captures')
api.add_resource(Capture, '/captures/<capture_id>')

if __name__ == '__main__':
    app.run(debug=True)

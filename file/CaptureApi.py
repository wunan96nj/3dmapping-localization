#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uuid
import base64
from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('task', type=str)


# Todo
#   show a single todo item and lets you delete them
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


# TodoList
#   shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    # curl http://localhost:5000/todos/todo3 -d "task=something different" -X PUT -v
    def post(self):
        file_uuid = str(uuid.uuid4());
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        #
        b64 = args['b64']
        altitude = args['altitude']
        longitude = args['longitude']
        b64 = args['b64']
        b64 = args['b64']
        b64 = args['b64']
        b64 = args['b64']

        return TODOS[todo_id], 201


class CapturePhoto(Resource):

    def save_files(json_data, png_file_full_path, json_file_full_path, self):
        b64 = json_data['b64']
        json_data['b64']="omitted"
        png_base64_bytes = b64.encode('ascii')
        png_bytes = base64.b64decode(png_base64_bytes)
        with open(png_file_full_path, 'wb') as f:
            f.write(png_bytes)
        josn_base64_bytes = str(json_data).encode('ascii')
        with open(json_file_full_path, 'wb') as f:
            f.write(josn_base64_bytes)

    def post(self):
        file_uuid = uuid.uuid4().hex;
        image_base_dir = '/Users/akui/Desktop/images/'
        json_data = request.get_json(force=True)
        token = json_data['token']
        bank = json_data['bank']
        run = json_data['run']
        index = json_data['index']
        anchor = json_data['anchor']
        px = json_data['px']
        py = json_data['py']
        pz = json_data['pz']
        r00 = json_data['r00']
        r01 = json_data['r01']
        r02 = json_data['r02']
        r10 = json_data['r10']
        r11 = json_data['r11']
        r12 = json_data['r12']
        r20 = json_data['r20']
        r21 = json_data['r21']
        r22 = json_data['r22']
        fx = json_data['fx']
        fy = json_data['fy']
        ox = json_data['ox']
        oy = json_data['oy']
        b64 = json_data['b64']
        png_file_full_path = image_base_dir + str(
            bank) + "/" + file_uuid + ".png"
        json_file_path = image_base_dir + str(
            bank) + "/" + file_uuid + ".json"
        print("write png file to " + png_file_full_path)
        print("write json file to " + json_file_path)
        CapturePhoto.save_files(json_data, png_file_full_path, json_file_path,self)
        return jsonify(file_uuid=file_uuid, image_base_dir=image_base_dir)


##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')
# http://localhost:5444/capture-photo
api.add_resource(CapturePhoto, '/capture-photo/captureb64')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5444, debug=True)

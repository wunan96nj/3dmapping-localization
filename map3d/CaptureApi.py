#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy
import shutil
import json
from flask import Flask, jsonify, request
from flask_restful import reqparse, Api, Resource
import os
from map3d.util import QueryLocalUtil, Utils

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('task', type=str)

COLMAP = "/Users/akui/eclipse-workspace/py-colmap-rest-gate/map3d/COLMAP.app/Contents/MacOS/colmap"
workspace_dir = "/Users/akui/Desktop" + "/"
image_base_dir = workspace_dir + "images/"
json_base_dir = workspace_dir + "json/"
sparse_dir = workspace_dir + 'sparse/'
database_name = 'database.db'


class CapturePhoto(Resource):

    def save_files(json_data, image_file_full_path, json_file_full_path, self):
        b64 = json_data['b64']
        json_data['b64'] = "omitted"
        Utils.write_to_file(b64, image_file_full_path, True, self)
        Utils.write_to_file("omitted", json_file_full_path, False, self)
        return

    def post(self):
        # file_uuid = uuid.uuid4().hex;
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
        image_name = json_data['image_name']
        image_name = image_name.split('.')[0]
        b64 = json_data['b64']
        if not os.path.exists(image_base_dir):
            os.mkdir(image_base_dir)
        if not os.path.exists(json_base_dir):
            os.mkdir(json_base_dir)
        if not os.path.exists(image_base_dir + str(bank)):
            os.mkdir(image_base_dir + str(bank))
        if not os.path.exists(json_base_dir + str(bank)):
            os.mkdir(json_base_dir + str(bank))
        jpg_file_full_path = image_base_dir + str(
            bank) + "/" + image_name + ".jpg"
        json_file_path = json_base_dir + str(
            bank) + "/" + image_name + ".json"
        print("write image file to " + jpg_file_full_path)
        print("write json file to " + json_file_path)
        CapturePhoto.save_files(json_data, jpg_file_full_path, json_file_path,
                                self)
        return jsonify(image_name=image_name,
                       jpg_file_full_path=jpg_file_full_path,
                       json_file_path=json_file_path)


# construction by images
class StartMapConstruction(Resource):

    def post(self):
        print("StartMapConstruction BEGIN")
        json_data = request.get_json(force=True)
        bank = json_data['bank']
        feature_dim = json_data['feature_dim']
        StartMapConstruction.build(feature_dim, bank, self)
        Utils.gen_newdb(sparse_dir, database_name, feature_dim, bank, self)
        Utils.remove_build_useless_files(sparse_dir, feature_dim, bank, self)
        print("StartMapConstruction FIN")
        return

    def build(feature_dim, bank, self):
        print("StartMapConstruction build() start.....")
        (tmp_database_dir, image_dir) = Utils.create_image_db_env(
            image_base_dir, sparse_dir, bank, self)
        print("1. feature_extractor")
        Utils.feature_colmap(COLMAP, database_name, tmp_database_dir, image_dir,
                             self)
        # Utils.feature_cv(tmp_database_dir + database_name, image_dir)

        print("2. Matching")
        Utils.match_colmap(COLMAP, database_name, tmp_database_dir, image_dir,
                           self)

        print("3. point_triangulator")
        Utils.point_triangulator_colmap(COLMAP, database_name, sparse_dir,
                                        tmp_database_dir, image_dir, self)
        print("StartMapConstruction build() end .....")
        return


class ClearWorkspace(Resource):
    def post(self):
        print("ClearWorkspace BEGIN, ")
        json_data = request.get_json(force=True)
        bank = json_data['bank']
        image_dir = image_base_dir + str(bank) + "/"
        json_dir = json_base_dir + str(bank) + "/"
        sparse_dir_bank = sparse_dir + str(bank) + "/"
        if os.path.exists(image_dir):
            shutil.rmtree(image_dir, ignore_errors=True)
        if os.path.exists(json_dir):
            shutil.rmtree(json_dir, ignore_errors=True)
        if os.path.exists(sparse_dir_bank):
            shutil.rmtree(sparse_dir_bank, ignore_errors=True)
        print("StartMapConstruction FIN")


class QueryLocal(Resource):
    def post(self):
        print("QueryLocal BEGIN, ")
        json_data = request.get_json(force=True)
        bank = json_data['bank']
        b64 = json_data['b64']
        image_name = json_data['image_name']
        (
            image_name, upload_image_file_full_path,
            upload_database_file_full_path,
            upload_image_tmp_dir,
            base_images_db_path) = QueryLocalUtil.establish_env(image_name,
                                                                sparse_dir,
                                                                database_name,
                                                                bank)
        print("QueryLocal image_name_prefix: " + image_name)
        print(
            "QueryLocal upload_image_file_full_path: " + upload_image_file_full_path)
        print(
            "QueryLocal upload_database_file_full_path: " + upload_database_file_full_path)

        QueryLocalUtil.save_image(b64, bank, upload_image_tmp_dir,
                                  upload_image_file_full_path,
                                  self)
        QueryLocalUtil.get_feature_upload(COLMAP, image_name + ".db",
                                          upload_image_tmp_dir, self)
        (image_name_jpg, q, t) = QueryLocalUtil.compare_upload_base_local(
            base_images_db_path,
            upload_database_file_full_path,
            image_name + ".jpg",
            self)
        print("QueryLocal (image_name_jpg, q, t):" + str(
            (image_name_jpg, q, t)) + " FIN")
        return json.dumps((image_name_jpg, q, t), cls=Utils.NDArrayEncoder)

    ##


class CVQueryLocal(Resource):
    def post(self):
        print("CVQueryLocal BEGIN, ")
        json_data = request.get_json(force=True)
        bank = json_data['bank']
        fg_des = json_data['fg_des']
        fg_kp = json_data['fg_kp']
        params = json_data['params']
        image_name_jpg = json_data['image_name']

        fg_kp = numpy.array(fg_kp)
        fg_des = numpy.array(fg_des).astype(numpy.uint8)
        params = numpy.array(params)
        #
        sparse_dir_bank = sparse_dir + str(bank) + "/"
        base_images_db_path = sparse_dir_bank + database_name
        print("CVQueryLocal image_name_jpg: " + image_name_jpg)
        print("CVQueryLocal sparse_dir_bank: " + sparse_dir_bank)
        print("CVQueryLocal base_images_db_path: " + base_images_db_path)
        (image_name_jpg, q, t) = QueryLocalUtil.compare_upload_base_local_cv(
            base_images_db_path, image_name_jpg, fg_kp,
            fg_des, params, self)
        print("CVQueryLocal (image_name_jpg, q, t):" + str(
            (image_name_jpg, q, t)) + " FIN")
        return json.dumps((image_name_jpg, q, t), cls=Utils.NDArrayEncoder)

    ##


## Actually setup the Api resource routing here
##
# api.add_resource(TodoList, '/todos')
# api.add_resource(Todo, '/todos/<todo_id>')
# http://localhost:5444/capture-photo
api.add_resource(CapturePhoto, '/capture-photo/captureb64')
api.add_resource(StartMapConstruction, '/capture-photo/construct')
api.add_resource(ClearWorkspace, '/capture-photo/clear')
api.add_resource(QueryLocal, '/capture-photo/querylocal')
api.add_resource(CVQueryLocal, '/capture-photo/cvquerylocal')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5444, debug=True)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy
import shutil
import json
from flask import Flask, jsonify, request
from flask_restful import reqparse, Api, Resource
import os
from map3d.util import QueryLocalUtil, Utils, Env
from map3d.util.calc import read_model

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('task', type=str)

COLMAP = "/Users/akui/eclipse-workspace/py-3dmap-rest-gate/map3d/COLMAP.app/Contents/MacOS/colmap"
root_dir = "/Users/akui/Desktop/"

image_bin_name = "images.bin"
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
        (workspace_dir, image_base_dir, json_base_dir, sparse_dir, database_dir, col_bin_dir) = Env.get_env_total_dir(
            root_dir, bank,
            self)
        (jpg_file_full_path, json_file_path) = Env.get_jpg_json_file_path(image_base_dir, json_base_dir, image_name,
                                                                          self)
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
        # Utils.gen_newdb(sparse_dir, database_name, feature_dim, bank, self)
        # Utils.remove_build_useless_files(sparse_dir, feature_dim, bank, self)
        print("StartMapConstruction FIN")
        return

    def build(feature_dim, bank, self):
        print("StartMapConstruction build() start.....")
        (workspace_dir, image_base_dir, json_base_dir, sparse_dir, database_dir, col_bin_dir) = Env.get_env_total_dir(
            root_dir, bank,
            self)
        print("1. feature_extractor")
        Utils.feature_colmap(COLMAP, database_name, database_dir, image_base_dir,
                             self)
        # Utils.feature_cv(tmp_database_dir + database_name, image_dir)
        print("2. Matching")
        Utils.match_colmap(COLMAP, database_name, database_dir, image_base_dir, self)

        print("3. point_triangulator")
        Utils.point_triangulator_colmap(COLMAP, database_name, sparse_dir, database_dir, image_base_dir, self)
        print("StartMapConstruction build() end .....")
        return


class ClearWorkspace(Resource):
    def post(self):
        print("ClearWorkspace BEGIN, ")
        json_data = request.get_json(force=True)
        bank = json_data['bank']
        (workspace_dir, image_base_dir, json_base_dir, sparse_dir, database_dir, col_bin_dir) = Env.get_env_total_dir(
            root_dir,
            bank, self)
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
        (workspace_dir, image_base_dir, json_base_dir, sparse_dir, database_dir, col_bin_dir) = Env.get_env_total_dir(
            root_dir, bank,
            self)
        (
            image_name_prefix, upload_image_file_full_path,
            upload_database_file_full_path,
            upload_image_tmp_dir) = Env.establish_env(image_name,
                                                      sparse_dir,
                                                      self)
        print("QueryLocal image_name_prefix: " + image_name_prefix)
        print(
            "QueryLocal upload_image_file_full_path: " + upload_image_file_full_path)
        print(
            "QueryLocal upload_database_file_full_path: " + upload_database_file_full_path)

        QueryLocalUtil.save_image(b64, bank, upload_image_tmp_dir,
                                  upload_image_file_full_path,
                                  self)
        QueryLocalUtil.get_feature_upload(COLMAP, image_name_prefix + ".db",
                                          upload_image_tmp_dir, self)
        (image_name_jpg, q, t) = QueryLocalUtil.compare_upload_base_local(
            sparse_dir,
            col_bin_dir,
            upload_database_file_full_path,
            image_name_prefix + ".jpg",
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
        (workspace_dir, image_base_dir, json_base_dir, sparse_dir, database_dir, col_bin_dir) = Env.get_env_total_dir(
            root_dir, bank,
            self)

        print("CVQueryLocal image_name_jpg: " + image_name_jpg)
        print("CVQueryLocal sparse_dir_bank: " + sparse_dir)
        (image_name_jpg, q, t) = QueryLocalUtil.compare_upload_base_local_cv(sparse_dir, col_bin_dir, image_name_jpg,
                                                                             fg_kp,
                                                                             fg_des, params, self)
        print("CVQueryLocal (image_name_jpg, q, t):" + str(
            (image_name_jpg, q, t)) + " FIN")
        return json.dumps((image_name_jpg, q, t), cls=Utils.NDArrayEncoder)

    ##


class ImageBinInfo(Resource):
    def post(self):
        print("ImageBinInfo BEGIN, ")
        json_data = request.get_json(force=True)
        bank = json_data['bank']
        the_image_name = json_data['image_name']
        (workspace_dir, image_base_dir, json_base_dir, sparse_dir, database_dir, col_bin_dir) = Env.get_env_total_dir(
            root_dir, bank,
            self)
        image_bin_path = Env.image_bin_path(sparse_dir, image_bin_name, self)
        (image_id, qvec, tvec,
         camera_id, image_name,
         xys, point3D_ids) = read_model.read_images_binary_for_one(image_bin_path,
                                                                   the_image_name)
        print("ImageBinInfo (image_id, qvec, tvec, camera_id, image_name, xys, point3D_ids):" + str(
            (image_id, qvec, tvec, camera_id, image_name, xys, point3D_ids)) + " FIN")
        return json.dumps((image_id, qvec, tvec, camera_id, image_name, xys, point3D_ids), cls=Utils.NDArrayEncoder)


class Query3DCouldPoint(Resource):
    def post(self):
        print("Query3DCouldPoint BEGIN, ")
        json_data = request.get_json(force=True)
        bank = json_data['bank']
        params = json_data['params']
        #
        (workspace_dir, image_base_dir, json_base_dir, sparse_dir, database_dir, col_bin_dir) = Env.get_env_total_dir(
            root_dir, bank,
            self)
        print("Query3DCouldPoint sparse_dir: " + sparse_dir)
        (db_points_pos, db_points_des, dp_points_rgb) = Utils.load_all_3dmap_cloud_point(sparse_dir, col_bin_dir)
        print("Query3DCouldPoint (db_points_pos, db_points_des, dp_points_rgb):" + str(
            (db_points_pos, db_points_des, dp_points_rgb)) + " FIN")
        return json.dumps((db_points_pos, db_points_des, dp_points_rgb), cls=Utils.NDArrayEncoder)


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
api.add_resource(ImageBinInfo, '/capture-photo/imagebininfo')
api.add_resource(Query3DCouldPoint, '/capture-photo/query3dcloudpoint')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5444, debug=True)

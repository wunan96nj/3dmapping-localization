#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uuid
import numpy
import cv2
import time
import datetime
import base64
import shutil
import json
from json import JSONEncoder
from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
import os
import subprocess
import sys
import write_to_nw_db
import get_point_pos_des
import database
from scipy.spatial.transform import Rotation as R

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('task', type=str)

COLMAP = "/Users/akui/eclipse-workspace/py-colmap-rest-gate/file/COLMAP.app/Contents/MacOS/colmap"
workspace_dir = "/Users/akui/Desktop" + "/"
image_base_dir = workspace_dir + "images/"
json_base_dir = workspace_dir + "json/"
sparse_dir = workspace_dir + 'sparse/'
database_name = 'database.db'


class NDArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


class Utils(Resource):
    def write_to_file(content_s, file_full_path, is_base64, self):
        if is_base64:
            base64_bytes = content_s.encode('ascii')
            file_bytes = base64.b64decode(base64_bytes)
        else:
            file_bytes = content_s.encode('ascii')
        with open(file_full_path, 'wb') as f:
            f.write(file_bytes)
        return


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


class StartMapConstruction(Resource):

    def build(bank, self):
        print("StartMapConstruction build() start.....")
        image_dir = image_base_dir + str(bank) + "/"
        sparse_dir_bank = sparse_dir + str(bank) + "/"
        tmp_database_dir = sparse_dir_bank + "temp/"
        print("image_dir: " + image_dir)
        print("sparse_dir_bank: " + sparse_dir_bank)
        print("tmp_database_dir: " + tmp_database_dir)

        if not os.path.exists(sparse_dir):
            os.mkdir(sparse_dir)
        if not os.path.exists(sparse_dir_bank):
            os.mkdir(sparse_dir_bank)
        if not os.path.exists(tmp_database_dir):
            os.mkdir(tmp_database_dir)

        print("1. feature_extractor")
        pIntrisics = subprocess.Popen(
            [COLMAP, "feature_extractor", "--database_path",
             tmp_database_dir + database_name, "--image_path", image_dir,
             "--ImageReader.camera_model", "SIMPLE_PINHOLE"])
        pIntrisics.wait()

        print("2. Matching")
        pIntrisics = subprocess.Popen(
            [COLMAP, "exhaustive_matcher", "--database_path",
             tmp_database_dir + database_name])
        pIntrisics.wait()

        print("3. point_triangulator")
        pIntrisics = subprocess.Popen(
            [COLMAP, "mapper", "--database_path",
             tmp_database_dir + database_name,
             "--image_path", image_dir, "--output_path",
             sparse_dir, "--Mapper.ba_refine_focal_length", "0",
             "--Mapper.ba_refine_extra_params", "0"])
        pIntrisics.wait()
        print("StartMapConstruction build() end .....")
        return

    def gen_newdb(bank, self):
        print("StartMapConstruction gen_newdb() start .....")
        sparse_dir_bank = sparse_dir + str(bank) + "/"
        tmp_database_dir = sparse_dir_bank + "/temp/"
        print("sparse_dir_bank: " + sparse_dir_bank)
        print("tmp_database_dir: " + tmp_database_dir)
        print("1. write_to_nw_db.read_cip")
        cameras, images, points = write_to_nw_db.read_cip(sparse_dir_bank)
        print(cameras)
        print("2. write_to_nw_db.read_database")
        db_images, kp_table, des_table = write_to_nw_db.read_database(
            tmp_database_dir)

        print("3. write_to_nw_db.get_points_pos_des")
        points_pos, points_des, points_rgb = write_to_nw_db.get_points_pos_des(
            cameras, images,
            points,
            kp_table,
            des_table)

        # print(len(points))
        # print(len(points_pos))
        # print(len(points_des))
        # print(points)
        print(list(points_pos[-1]))
        print(list(points_des[-1]))
        print(list(points_rgb[-1]))
        print("4. write_to_nw_db.write_points3D_nw_db")
        write_to_nw_db.write_points3D_nw_db(points_pos, points_rgb, points_des,
                                            sparse_dir_bank + database_name)
        print("StartMapConstruction gen_newdb() end .....")
        return

    def remove_useless_files(bank, self):
        print("StartMapConstruction remove_useless_files() start .....")
        sparse_dir_bank = sparse_dir + str(bank) + "/"
        tmp_database_dir = sparse_dir_bank + "temp/"
        if os.path.exists(tmp_database_dir):
            shutil.rmtree(tmp_database_dir, ignore_errors=True)
        if os.path.exists(sparse_dir_bank + "project.ini"):
            os.remove(sparse_dir_bank + "project.ini")
        if os.path.exists(sparse_dir_bank + "points3D.bin"):
            os.remove(sparse_dir_bank + "points3D.bin")

        print("StartMapConstruction remove_useless_files() end .....")
        return

    def post(self):
        print("StartMapConstruction BEGIN")
        json_data = request.get_json(force=True)
        bank = json_data['bank']
        StartMapConstruction.build(bank, self)
        StartMapConstruction.gen_newdb(bank, self)
        StartMapConstruction.remove_useless_files(bank, self)
        print("StartMapConstruction FIN")
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
        image_name = image_name.split('.')[0]
        print("QueryLocal image_name: " + image_name)
        sparse_dir_bank = sparse_dir + str(bank) + "/"
        base_images_db_path = sparse_dir_bank + database_name
        upload_image_tmp_dir = sparse_dir_bank + "upload_temp/"
        # the upload image file full path
        upload_image_file_full_path = upload_image_tmp_dir + image_name + ".jpg"
        # the upload image's feature database file full path
        upload_database_file_full_path = upload_image_tmp_dir + image_name + ".db"

        print(
            "QueryLocal upload_image_file_full_path: " + upload_image_file_full_path)
        print(
            "QueryLocal upload_database_file_full_path: " + upload_database_file_full_path)

        QueryLocal.save_image(b64, bank, upload_image_tmp_dir,
                              upload_image_file_full_path, self)
        QueryLocal.get_feature_upload(upload_image_tmp_dir,
                                      upload_database_file_full_path, self)
        (image_name_jpg, t) = QueryLocal.compare_upload_base_local(
            base_images_db_path,
            upload_database_file_full_path,
            image_name + ".jpg",
            self)
        print("QueryLocal (image_name_jpg, t):" + str(
            (image_name_jpg, t)) + " FIN")
        return json.dumps((image_name_jpg, t), cls=NDArrayEncoder)

    def correct_colmap_q(qvec):
        ret = numpy.roll(qvec, -1)
        return ret

    def save_image(b64, bank, upload_image_tmp_dir, upload_image_file_full_path,
                   self):
        print("QueryLocal save_image() start .....")
        if not os.path.exists(upload_image_tmp_dir):
            os.mkdir(upload_image_tmp_dir)
        print("write image file to " + upload_image_file_full_path)
        Utils.write_to_file(b64, upload_image_file_full_path, True, self)
        return

    def get_feature_upload(upload_image_tmp_dir, upload_database_file_full_path,
                           self):
        print("QueryLocal get_feature_upload() start .....")
        print(
            "QueryLocal get_feature_upload() upload_image_tmp_dir: " + upload_image_tmp_dir)
        print(
            "QueryLocal get_feature_upload() upload_database_file_full_path: " + upload_database_file_full_path)
        print("1. feature_extractor")
        pIntrisics = subprocess.Popen(
            [COLMAP, "feature_extractor", "--database_path",
             upload_database_file_full_path, "--image_path",
             upload_image_tmp_dir,
             "--ImageReader.camera_model", "SIMPLE_PINHOLE"])
        pIntrisics.wait()
        return

    def compare_upload_base_local(base_images_db_path,
                                  upload_database_file_full_path,
                                  image_name_jpg,
                                  self):
        print("QueryLocal query_local() start .....")

        print(
            "QueryLocal query_local() base_images_db_path: " + base_images_db_path)
        print(
            "QueryLocal query_local() upload_database_file_full_path: " + upload_database_file_full_path)
        print(
            "QueryLocal query_local() image_name_jpg: " + image_name_jpg)

        # read the feture of database of images dataware
        db_points_pos, db_points_rgb, db_points_des = get_point_pos_des.get_points_pos_des(
            base_images_db_path)

        # query uploaded image's database
        query = database.COLMAPDatabase.connect(upload_database_file_full_path)
        rows = query.execute("SELECT params FROM cameras")
        params = next(rows)
        params = database.blob_to_array(params[0], numpy.float64)
        query_kp = dict(
            (image_id, database.blob_to_array(data, numpy.float32, (-1, 6)))
            for image_id, data in query.execute(
                "SELECT image_id, data FROM keypoints"))
        query_des = dict(
            (image_id, database.blob_to_array(data, numpy.uint8, (-1, 128)))
            for image_id, data in query.execute(
                "SELECT image_id, data FROM descriptors"))
        # localize every image in the query database
        for image_id in range(1, 2):
            print(image_id)
            fg_kp = query_kp[image_id]
            fg_des = query_des[image_id]
            # print(fg_kp.shape)
            # print(fg_des.shape)
            match_start = time.time()
            bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
            matches = bf.match(db_points_des, fg_des)
            matches = sorted(matches, key=lambda x: x.distance)
            print("time used for knnMatching:", time.time() - match_start)
            points2D_coordinate = []
            points3D_coordinate = []

            for match in matches:
                points2D_coordinate.append(fg_kp[match.trainIdx][:2])
                points3D_coordinate.append(db_points_pos[match.queryIdx])
            points2D_coordinate = numpy.asarray(points2D_coordinate)
            points3D_coordinate = numpy.asarray(points3D_coordinate)
            # localization with pycolmap absolute_pose_estimation
            localize_start = time.time()
            focal_length, principal_x, principal_y = params[0], params[1], \
                                                     params[2]
            # Intrinsic Matrix
            camera_K = numpy.array([[focal_length, 0, principal_x],
                                    [0, focal_length, principal_y],
                                    [0, 0, 1]], dtype=numpy.double)
            dist_coeffs = numpy.zeros((4, 1))

            result = cv2.solvePnPRansac(points3D_coordinate,
                                        points2D_coordinate, camera_K,
                                        dist_coeffs, flags=cv2.SOLVEPNP_P3P,
                                        iterationsCount=1000)

            t = result[2].flatten()
            q = R.from_rotvec(result[1].flatten()).as_quat()
            print(result[0])
            print("QueryLocal query_local() t: " + str(t))
            q = QueryLocal.correct_colmap_q(q)
            print("QueryLocal query_local() q: " + str(q))
            print("QueryLocal query_local() end .....")
            return (image_name_jpg, t)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5444, debug=True)

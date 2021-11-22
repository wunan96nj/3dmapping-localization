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
import Utils


def save_image(b64, bank, upload_image_tmp_dir, upload_image_file_full_path,
               feature_dim,
               self):
    print("QueryLocal save_image() start .....")
    if not os.path.exists(upload_image_tmp_dir):
        os.mkdir(upload_image_tmp_dir)
    print("write image file to " + upload_image_file_full_path)
    Utils.write_to_file(b64, upload_image_file_full_path, True, self)
    return


def get_feature_upload(COLMAP, database_name, upload_image_tmp_dir,
                       self):
    print("QueryLocal get_feature_upload() start .....")
    print(
        "QueryLocal get_feature_upload() database_name: " + database_name)
    print(
        "QueryLocal get_feature_upload() upload_image_tmp_dir: " + upload_image_tmp_dir)
    print("1. feature_extractor")
    Utils.feature_colmap(COLMAP, database_name, upload_image_tmp_dir,
                         upload_image_tmp_dir, self)
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
        (image_id,
         database.blob_to_array(data, numpy.float32, (-1, 6)))
        for image_id, data in query.execute(
            "SELECT image_id, data FROM keypoints"))
    query_des = dict(
        (image_id,
         database.blob_to_array(data, numpy.uint8, (-1, 128)))
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
        q = Utils.correct_colmap_q(q)
        print("QueryLocal query_local() q: " + str(q))
        print("QueryLocal query_local() end .....")
        return (image_name_jpg, q, t)

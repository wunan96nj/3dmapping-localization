#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy
import cv2
import base64
import shutil
from json import JSONEncoder
import os
import subprocess
from map3d.util.db import database, write_to_nw_db


class NDArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

def correct_colmap_q(qvec):
    ret = numpy.roll(qvec, 1)
    return ret


def write_to_file(content_s, file_full_path, is_base64, self):
    if is_base64:
        base64_bytes = content_s.encode('ascii')
        file_bytes = base64.b64decode(base64_bytes)
    else:
        file_bytes = content_s.encode('ascii')
    with open(file_full_path, 'wb') as f:
        f.write(file_bytes)
    return


def create_image_db_env(image_base_dir, sparse_dir, bank, self):
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
    return (tmp_database_dir, image_dir)


def feature_cv(database_path, img_folder, ):
    img_names = os.listdir(img_folder)
    print(img_names)
    if os.path.exists(database_path):
        os.remove(database_path)
    db = database.COLMAPDatabase.connect(database_path)
    db.create_tables()
    for i in range(len(img_names)):
        img_name = img_names[i]

        print("img_name:%s" % img_name)
        (model, width, height, params) = get_camera_info_cv()
        camera_id = db.add_camera(model, width, height, params)
        image_id = db.add_image(img_name, camera_id)
        (fg_kp, fg_des) = feature_one_image_cv(img_name, img_folder, model,
                                               width, height, params)
        print(fg_kp.shape)
        print(fg_des.shape)
        db.add_keypoints(image_id, fg_kp)
        db.add_descriptors(image_id, fg_des)
        db.commit()
    db.close()


def get_camera_info_cv():
    model, width, height, params = 0, 3072, 2304, numpy.array(
        (2457.6, 1536., 1152.))
    return (model, width, height, params)


def feature_one_image_cv(img_name, img_folder):
    img_path = img_folder + "/" + img_name
    img = cv2.imread(img_path, 0)
    sift = cv2.SIFT_create(10000)
    fg_kp, fg_des = sift.detectAndCompute(img, None)
    fg_kp = numpy.array([fg_kp[i].pt for i in range(len(fg_kp))])
    fg_des = numpy.array(fg_des).astype(numpy.uint8)
    return (fg_kp, fg_des)


def feature_colmap(COLMAP, database_name, tmp_database_dir, image_dir, self):
    pIntrisics = subprocess.Popen(
        [COLMAP, "feature_extractor", "--database_path",
         tmp_database_dir + database_name, "--image_path", image_dir,
         "--ImageReader.camera_model", "SIMPLE_PINHOLE"])
    pIntrisics.wait()


def match_colmap(COLMAP, database_name, tmp_database_dir, image_dir, self):
    pIntrisics = subprocess.Popen(
        [COLMAP, "exhaustive_matcher", "--database_path",
         tmp_database_dir + database_name])
    pIntrisics.wait()


def point_triangulator_colmap(COLMAP, database_name, sparse_dir,
                              tmp_database_dir, image_dir, self):
    pIntrisics = subprocess.Popen(
        [COLMAP, "mapper", "--database_path",
         tmp_database_dir + database_name,
         "--image_path", image_dir, "--output_path",
         sparse_dir, "--Mapper.ba_refine_focal_length", "0",
         "--Mapper.ba_refine_extra_params", "0"])
    pIntrisics.wait()


def gen_newdb(sparse_dir, database_name, feature_dim, bank, self):
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
        tmp_database_dir, feature_dim)

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


def remove_build_useless_files(sparse_dir, feature_dim, bank, self):
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

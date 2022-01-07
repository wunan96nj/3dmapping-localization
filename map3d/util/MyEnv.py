#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os


def get_env_total_dir(username, root_dir, bank):
    user_dir = root_dir + "/" + username + "/"
    workspace_dir = user_dir + "workspace-" + str(bank) + "/"
    image_base_dir = workspace_dir + "images/"
    json_base_dir = workspace_dir + "json/"
    sparse_dir = workspace_dir + "sparse/"
    database_dir = sparse_dir
    col_bin_dir = sparse_dir + "0/"
    print("workspace_dir: " + workspace_dir)
    print("image_base_dir: " + image_base_dir)
    print("json_base_dir: " + json_base_dir)
    print("sparse_dir: " + sparse_dir)
    print("database_dir: " + database_dir)
    print("col_bin_dir: " + col_bin_dir)
    if not os.path.exists(user_dir):
        os.mkdir(user_dir)
    if not os.path.exists(workspace_dir):
        os.mkdir(workspace_dir)
    if not os.path.exists(image_base_dir):
        os.mkdir(image_base_dir)
    if not os.path.exists(json_base_dir):
        os.mkdir(json_base_dir)
    if not os.path.exists(sparse_dir):
        os.mkdir(sparse_dir)
    if not os.path.exists(database_dir):
        os.mkdir(database_dir)
    return (workspace_dir, image_base_dir, json_base_dir, sparse_dir, database_dir, col_bin_dir)


def get_jpg_json_file_path(image_base_dir, json_base_dir, image_name):
    jpg_file_full_path = image_base_dir + image_name + ".jpg"
    json_file_path = json_base_dir + image_name + ".json"
    print("write image file to " + jpg_file_full_path)
    print("write json file to " + json_file_path)
    return (jpg_file_full_path, json_file_path)


def image_bin_path(sparse_dir, image_bin_name):
    # colmap will use 0 as bin files' father director,
    return sparse_dir + "0/" + image_bin_name


def establish_env(image_name, sparse_dir):
    image_name_prefix = image_name.split('.')[0]
    # sparse include bank info like "/Users/akui/Desktop/sparse-0"
    upload_image_tmp_dir = sparse_dir + "upload_temp/"
    # the upload image file full path
    upload_image_file_full_path = upload_image_tmp_dir + image_name_prefix + ".jpg"
    # the upload image's feature database file full path
    upload_database_file_full_path = upload_image_tmp_dir + image_name_prefix + ".db"

    return (
        image_name_prefix, upload_image_file_full_path, upload_database_file_full_path,
        upload_image_tmp_dir)

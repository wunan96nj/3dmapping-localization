import os
import numpy as np
from map3d.util.db import database
from map3d.util.db import nw_database
from map3d.util.calc import read_write_model


def read_cip(col_bin_dir):
    cameras_bin = os.path.join(col_bin_dir, "cameras.bin")
    images_bin = os.path.join(col_bin_dir, "images.bin")
    points_bin = os.path.join(col_bin_dir, "points3D.bin")

    cameras = read_write_model.read_cameras_binary(cameras_bin)
    images = read_write_model.read_images_binary(images_bin)
    points = read_write_model.read_points3D_binary(points_bin)

    return cameras, images, points


def read_database(file_path):
    database_path = os.path.join(file_path, "database.db")
    db = database.COLMAPDatabase.connect(database_path)

    images = dict(
        (image_id, name)
        for image_id, name in db.execute(
            "SELECT image_id, name FROM images"))

    keypoints = dict(
        (image_id, database.blob_to_array(data, np.float32, (-1, 6)))
        for image_id, data in db.execute(
            "SELECT image_id, data FROM keypoints"))

    # print(keypoints)

    descriptors = dict(
        (image_id, database.blob_to_array(data, np.uint8, (-1, 128)))
        for image_id, data in db.execute(
            "SELECT image_id, data FROM descriptors"))

    return images, keypoints, descriptors


def get_points_pos_des(cameras, images, points, kp_table, des_table):
    points_des = []
    points_pos = []
    points_rgb = []

    for pointid, point3D in points.items():
        des_array = None
        position = point3D.xyz
        rgb = point3D.rgb
        # print(type(rgb[0]))
        for i in range(len(point3D.image_ids)):
            imageid = point3D.image_ids[i]
            point2Did = point3D.point2D_idxs[i]

            descriptor = des_table[imageid][point2Did]
            # print(descriptor)

            if des_array is None:
                des_array = [descriptor]
            else:
                des_array = np.append(des_array, [descriptor], axis=0)
        points_pos.append(position)
        point_des = np.mean(des_array, axis=0).astype(np.uint8)
        points_des.append(point_des)
        points_rgb.append(rgb)
    points_pos = np.asarray(points_pos)
    points_des = np.asarray(points_des)
    points_rgb = np.asarray(points_rgb)

    return points_pos, points_des, points_rgb


def write_points3D_nw_db(points_pos, points_rgb, points_des, path_to_model_file):
    db = nw_database.COLMAPDatabase.connect(path_to_model_file)
    db.create_tables()

    for i in range(len(points_pos)):
        db.add_points(i + 1, points_pos[i].tolist(), points_rgb[i].tolist(), points_des[i].tolist())
    db.commit()


def main():
    file_path = "sparse/0/"
    cameras, images, points = read_cip(file_path)
    print(images)

    db_images, kp_table, des_table = read_database(file_path)
    # print(db_images)

    points_pos, points_des, points_rgb = get_points_pos_des(cameras, images, points, kp_table, des_table)

    # print(len(points))
    # print(len(points_pos))
    # print(len(points_des))
    # print(points)
    print(list(points_pos[-1]))
    print(list(points_des[-1]))
    print(list(points_rgb[-1]))


# write_points3D_nw_db(points_pos, points_rgb,  points_des, "nw_db/database.db")


if __name__ == '__main__':
    main()

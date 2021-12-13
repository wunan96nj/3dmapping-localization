
import os
import numpy as np
from map3d.util.calc import read_model
from map3d.util.db import database


def read_cameras_images(file_path):
	cameras_bin = os.path.join(file_path, "cameras.bin")
	images_bin = os.path.join(file_path, "images.bin")
	#points_bin = os.path.join(file_path, "points3D.bin")

	cameras = read_model.read_cameras_binary(cameras_bin)
	images = read_model.read_images_binary(images_bin)
	#points = read_model.read_points3d_binary(points_bin)

	return cameras, images
'''def read_cip(file_path):
	cameras_bin = os.path.join(file_path, "cameras.bin")
	images_bin = os.path.join(file_path, "images.bin")
	points_bin = os.path.join(file_path, "points3D.bin")
	
	cameras = read_model.read_cameras_binary(cameras_bin)
	images = read_model.read_images_binary(images_bin)
	points = read_model.read_points3d_binary(points_bin)

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


	#print(keypoints)

	descriptors = dict(
    	(image_id, database.blob_to_array(data, np.uint8, (-1, 128)))
     	for image_id, data in db.execute(
        	"SELECT image_id, data FROM descriptors"))

	return images, keypoints, descriptors'''

def get_points_pos_des(database_fp):
	db = database.COLMAPDatabase.connect(database_fp)
	points = dict(
		(point_id, ((x,y,z), (r, g, b,), database.blob_to_array(descriptor, np.uint8, (-1, 128))[0]))
		for point_id, x, y, z, r, g, b, descriptor in db.execute(
			"SELECT point_id, x, y, z, r, g, b, descriptor FROM points"))

	points_des = []
	points_pos = []
	points_rgb = []
	for pt3D in points.values():
		points_pos.append(pt3D[0])
		points_rgb.append(pt3D[1])
		points_des.append(pt3D[2])

	points_pos = np.asarray(points_pos)
	points_rgb = np.asarray(points_rgb)
	points_des = np.asarray(points_des)

	return points_pos, points_rgb, points_des

def main():
	'''file_path = "sparse/0/"
	cameras, images, points = read_cip(file_path)
	print(images)

	kp_table, des_table = read_database(file_path)

	points_pos, points_des = get_points_pos_des(cameras, images, points, kp_table, des_table)'''

	points_pos, points_rgb, points_des = get_points_pos_des("sparse/0/database.db")
	file_path = "sparse/0/"
	cameras, images = read_cameras_images(file_path)
	print(cameras)
	print(images)

	#print(len(points))
	print(len(points_pos))
	print(len(points_des))



if __name__ == '__main__':
	main()

import database
import os
import numpy as np
import cv2


def feature_cv(database_path, img_folder, ):
    img_names = os.listdir(img_folder)
    print(img_names)
    if os.path.exists(database_path):
        os.remove(database_path)
    db = database.COLMAPDatabase.connect(database_path)
    db.create_tables()
    for i in range(len(img_names)):
        img_name = img_names[i]
        img_path = img_folder + "/" + img_name
        print("img_name:%s" % img_name)
        model, width, height, params = 0, 3072, 2304, np.array(
            (2457.6, 1536., 1152.))
        camera_id = db.add_camera(model, width, height, params)
        image_id = db.add_image(img_name, camera_id)
        img = cv2.imread(img_path, 0)
        sift = cv2.SIFT_create(13000)
        fg_kp, fg_des = sift.detectAndCompute(img, None)
        fg_kp = np.array([fg_kp[i].pt for i in range(len(fg_kp))])
        fg_des = np.array(fg_des).astype(np.uint8)
        print(fg_kp.shape)
        print(fg_des.shape)
        db.add_keypoints(image_id, fg_kp)
        db.add_descriptors(image_id, fg_des)
        db.commit()
    db.close()


def main():
    database_path = "/Users/akui/Desktop/images/database.db"
    img_folder = "/Users/akui/Desktop/images/0/"
    img_names = os.listdir(img_folder)
    print(img_names)
    if os.path.exists(database_path):
        os.remove(database_path)
    db = database.COLMAPDatabase.connect(database_path)
    db.create_tables()
    for i in range(len(img_names)):
        img_name = img_names[i]
        print("img_name:%s" % img_name)
        model, width, height, params = 0, 3072, 2304, np.array(
            (2457.6, 1536., 1152.))
        camera_id = db.add_camera(model, width, height, params)
        image_id = db.add_image(img_name, camera_id)
        img = cv2.imread(img_folder + img_name, 0)
        sift = cv2.SIFT_create(10000)
        fg_kp, fg_des = sift.detectAndCompute(img, None)
        fg_kp = np.array([fg_kp[i].pt for i in range(len(fg_kp))])
        fg_des = np.array(fg_des).astype(np.uint8)
        print(fg_kp.shape)
        print(fg_des.shape)
        db.add_keypoints(image_id, fg_kp)
        db.add_descriptors(image_id, fg_des)
        db.commit()
    db.close()


if __name__ == '__main__':
    main()

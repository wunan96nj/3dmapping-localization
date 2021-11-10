import requests
import json
import time
import base64
import os
from PIL import Image
from datetime import datetime
import read_model


def find_photos_filenames(full_dir_path, isPng=False):
    for root, ds, fs in os.walk(full_dir_path):
        for f in fs:
            fullname = os.path.join(root, f)
            # need png file, jpg convert to png
            if isPng:
                if f.lower().endswith('.png'):
                    yield fullname
                elif f.lower().endswith('.jpg'):
                    print("convert jpg 2 png...start...")
                    file_base_name = (f.split("."))[0]
                    img = Image.open(fullname)
                    png_full_name = os.path.join(root, file_base_name) + ".png"
                    img.save(png_full_name)
                    print("convert jpg 2 png...end...")
                    yield png_full_name
            else:
                #only need jpg now
                if f.lower().endswith('.jpg'):
                    yield fullname


def ConvertToBase64(src_filepath):
    with open(src_filepath, 'rb') as imageFileAsBinary:
        fileContent = imageFileAsBinary.read()
        b64_encoded_img = base64.b64encode(fileContent)
        return b64_encoded_img


def post_to_server(api_url, token, image_base_dir, seq_base, bank):
    for i, imagePath in enumerate(find_photos_filenames(image_base_dir)):
        seq = seq_base + i
        print("sequence: " + str(seq))
        print("imagePath: " + imagePath)
        print("bank: " + str(bank))
        submit_image(api_url, token, imagePath, seq, bank);
    return


def submit_image(api_url, token, imagePath, seq, bank):
    print("submit_image...start...")
    complete_url = api_url + '/captureb64'
    (image_dir, image_name) = os.path.split(imagePath)
    image_name = image_name.split('.')[0] + ".jpg"
    data = {
        "token": token,
        "bank": bank,  # default workspace/image bank
        "run": seq,
        # a running integer for the tracker session. Increment if tracking is lost or image is from a different session
        "index": seq,  # running index for images
        "anchor": False,  # flag for the image used as an anchor/map origin
        "px": 0.0,  # camera x position from the tracker
        "py": 0.0,  # camera y position from the tracker
        "pz": 0.0,  # camera z position from the tracker
        "r00": 1.0,  # camera orientation as a 3x3 matrix
        "r01": 0.0,
        "r02": 0.0,
        "r10": 0.0,
        "r11": 1.0,
        "r12": 0.0,
        "r20": 0.0,
        "r21": 0.0,
        "r22": 1.0,
        "fx": 2457.5,  # image focal length in pixels on x axis
        "fy": 2457.5,  # image focal length in pixels on y axis
        "ox": 1152,  # image principal point on x axis
        "oy": 1536,  # image principal point on y axis
        "b64": str(ConvertToBase64(imagePath), 'utf-8'),
        "image_name": image_name
        # base64 encoded .jpg image
    }

    json_data = json.dumps(data)
    # print(json_data)
    r = requests.post(complete_url, data=json_data)
    print(r.text)
    print("submit_image...end...")
    return


def StartMapConstruction(url, token, mapName, windowSize, bank):
    print("StartMapConstruction...start...")
    complete_url = url + '/construct'
    data = {
        "token": token,
        "bank": bank,
        "name": mapName,
        # If the images are shot in sequence like a video stream, this optional parameter can be used to limit
        # image matching to x previous and following frames.
        # This can decrease map construction times and help constructing maps in repetitive environments.
        # A value of 0 disables the feature.
        "window_size": windowSize
    }
    json_data = json.dumps(data)
    r = requests.post(complete_url, data=json_data)
    print(r.text)
    print("StartMapConstruction...end...")
    return


# opencv-python
def QueryLocal(url, token, uploadImagePath, bank):
    t_beign = time.time()
    print("QueryLocal...start...t_beign: " + str(int(t_beign)))
    print("QueryLocal...uploadImagePath: " + str(uploadImagePath))
    complete_url = url + '/querylocal'
    (image_dir, image_name) = os.path.split(uploadImagePath)
    image_name = image_name.split('.')[0] + ".jpg"
    data = {
        "token": token,
        "bank": bank,
        "b64": str(ConvertToBase64(uploadImagePath), 'utf-8'),
        "image_name": image_name
    }
    json_data = json.dumps(data)
    r = requests.post(complete_url, data=json_data)
    print(r.text)
    t_end = time.time()
    print("QueryLocal...end...t_end:" + str(int(t_end)))
    print("total seconds:" + str(int(t_end) - int(t_beign)))
    return


def ClearWorkspace(url, token, deleteAnchorImage, bank):
    print("ClearWorkspace...start...")
    complete_url = url + '/clear'
    data = {
        "token": token,
        "bank": bank,  # default workspace/image bank
        "anchor": deleteAnchorImage
    }

    json_data = json.dumps(data)

    r = requests.post(complete_url, data=json_data)
    print(r.text)
    print("ClearWorkspace...end...")
    return


def printTimestamp():
    now = datetime.now()
    dt_string = now.strftime("%Y/%m/%d/ %H:%M:%S")
    print("date and time =", dt_string)
    return


def printImageBinInfo():
    print("printImageBinInfo ... start ...")
    image_bin_path = "/Users/akui/Desktop/sparse/0/images.bin"
    images = read_model.read_images_binary(image_bin_path)
    print(images)
    print("printImageBinInfo ... end ...")
    return


def main_test():
    printTimestamp()
    # api_url = "https://api.immersal.com"
    api_url = "http://localhost:5444/capture-photo"
    token = "192b47014ee982495df0a08674ac49a11eca4cb4427e3115a0254b89d07587cc"
    image_base_dir = '/Users/akui/Desktop/south-building/images'
    seq_base = 0
    map_name = "pyFirstMap"
    windowSize = 0
    deleteAnchorImage = True
    bank = 0
    ClearWorkspace(api_url, token, deleteAnchorImage, bank)
    post_to_server(api_url, token, image_base_dir, seq_base, bank)
    StartMapConstruction(api_url, token, map_name, windowSize, bank)

    uploadImagePath = "/Users/akui/Desktop/south-building/images/P1180347.png"
    QueryLocal(api_url, token, uploadImagePath, bank)
    printImageBinInfo()
    printTimestamp()
    return


def main():
    main_test()
    return


if __name__ == "__main__":
    main()

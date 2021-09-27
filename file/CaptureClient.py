import requests
import json
import base64
import os
from PIL import Image
from datetime import datetime


def find_photos_filenames(full_dir_path):
    for root, ds, fs in os.walk(full_dir_path):
        for f in fs:
            fullname = os.path.join(root, f)
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


def ConvertToBase64(src_filepath):
    with open(src_filepath, 'rb') as imageFileAsBinary:
        fileContent = imageFileAsBinary.read()
        b64_encoded_img = base64.b64encode(fileContent)
        return b64_encoded_img


def post_to_server(api_url, token, image_base_dir, seq_base=0):
    for i, imagePath in enumerate(find_photos_filenames(image_base_dir)):
        seq = seq_base + i
        print("sequence: " + str(seq))
        print("imagePath: " + imagePath)
        submit_image(api_url, token, imagePath, seq);
    return


def submit_image(api_url, token, imagePath, seq):
    print("submit_image...start...")
    complete_url = api_url + '/captureb64'
    data = {
        "token": token,
        "bank": 0,  # default workspace/image bank
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
        "b64": str(ConvertToBase64(imagePath), 'utf-8')
        # base64 encoded .png image
    }

    json_data = json.dumps(data)
    print(json_data)
    r = requests.post(complete_url, data=json_data)
    print(r.text)
    print("submit_image...end...")


def StartMapConstruction(url, token, mapName, windowSize):
    print("StartMapConstruction...start...")
    complete_url = url + '/construct'
    data = {
        "token": token,
        "bank": 0,
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


def ClearWorkspace(url, token, deleteAnchorImage):
    print("ClearWorkspace...start...")
    complete_url = url + '/clear'
    data = {
        "token": token,
        "bank": 0,  # default workspace/image bank
        "anchor": deleteAnchorImage
    }

    json_data = json.dumps(data)

    r = requests.post(complete_url, data=json_data)
    print(r.text)
    print("ClearWorkspace...end...")


def printTimestamp():
    now = datetime.now()
    dt_string = now.strftime("%Y/%m/%d/ %H:%M:%S")
    print("date and time =", dt_string)
    return


def main():
    printTimestamp()
    # api_url = "https://api.immersal.com"
    api_url = "http://localhost:5444/capture-photo"
    token = "192b47014ee982495df0a08674ac49a11eca4cb4427e3115a0254b89d07587cc"
    image_base_dir = '/Users/akui/Desktop/south-building/images'
    seq_base = 0
    map_name = "pyFirstMap"
    windowSize = 0
    deleteAnchorImage = True
    post_to_server(api_url, token, image_base_dir, seq_base)
    StartMapConstruction(api_url, token, map_name, windowSize)
    ClearWorkspace(api_url, token, deleteAnchorImage)
    printTimestamp()


if __name__ == "__main__":
    main()

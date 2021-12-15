
![](/Users/akui/Desktop/cloudpoint.png)
# **About:**

Restfull 3D Map Service API
Using images to contribute 3D map

![img.png](img.png)

# **1. Upload all the images of map**

import CaptureSDK

CaptureSDK.ClearWorkspace(api_url, token, deleteAnchorImage, bank)

CaptureSDK.post_to_server(api_url, token, image_base_dir, seq_base, bank)

|Parameters:||
| ----- | --------- |
|api_url:| server url, like: http://localhost:5444/capture-photo|
|token: |standby field, for future permission verification|
|deleteAnchorImage: |standby field, whether to delete the anchor image|
|image_base_dir: |the client local director of images|
|seq_base: |image sequence number like: 0|
|bank: |workspace bank number like: 0|

# **2. Build 3D map according these images of map**

import CaptureSDK

CaptureSDK.StartMapConstruction(api_url, token, map_name, windowSize, feature_dim, bank)

|Parameters:||
| ----- | --------- |
|api_url: |server url, like: http://localhost:5444/capture-photo|
|token: |standby field, for future permission verification|
|map_name: |standby field, name of 3D map|
|windowSize: |standby field|
|feature_dim: |images feature contribute by colmap engine is 6; by CV is 2|
|bank: |workspace bank number like: 0|

# **3. Clear the workspace(clear all data and files related the map)**

import CaptureSDK
CaptureSDK.ClearWorkspace(api_url, token, deleteAnchorImage, bank)

|Parameters:||
| ----- | --------- |
|api_url: |server url, like: http://localhost:5444/capture-photo|
|token: |standby field, for future permission verification|
|deleteAnchorImage: |standby field, whether to delete the anchor image|

# **4. Upload one image to get coordinate of the map**

import CaptureSDK

CaptureSDK.QueryLocal(api_url, token, uploadImagePath, bank)

|Parameters:||
| ----- | --------- |
|api_url: |server url, like: http://localhost:5444/capture-photo|
|token: |standby field, for future permission verification|
|uploadImagePath: |the client image's full file path, like: /Users/akui/Desktop/south-building/images/P1180141.jpg|
|bank: |workspace bank number like: 0|

# **5. Upload the cv feature of a image to get coordinate of the map**

import CaptureSDK

CaptureSDK.CVQueryLocal(api_url, token, uploadImagePath, bank)

|Parameters:||
| ----- | --------- |
|api_url: |server url, like: http://localhost:5444/capture-photo|
|token: |standby field, for future permission verification|
|uploadImagePath: |the client image's full file path, like: /Users/akui/Desktop/south-building/images/P1180141.jpg|
|bank: |workspace bank number like: 0|
import numpy

import CaptureSDK


def main_test():
    CaptureSDK.printTimestamp()
    # api_url = "https://api.immersal.com"
    api_url = "http://localhost:5444/capture-photo"
    token = "192b47014ee982495df0a08674ac49a11eca4cb4427e3115a0254b89d07587cc"
    username = 'sample_user'
    password = 'pass'
    image_base_dir = 'images'
    seq_base = 0
    map_name = "pyFirstMap"
    windowSize = 0
    deleteAnchorImage = True
    bank = 0
    # feature_dim: colmap use 6, cv use 2
    feature_dim = 6
    uploadImagePath = "images/P1180141.jpg"
    cloudPlyFile = "cloudPlyFile.ply"

    print("post_to_server---------------BEGIN")
    print("ClearWorkspace...start...")
    r = CaptureSDK.ClearWorkspace(api_url, token, deleteAnchorImage, bank, username, password)
    print(r.text)
    CaptureSDK.post_to_server(api_url, token, image_base_dir, seq_base, bank, username, password)
    print("ClearWorkspace...end...")
    print("post_to_server---------------END")

    print("StartMapConstruction---------------BEGIN")
    print("StartMapConstruction...start...")
    ret = CaptureSDK.StartMapConstruction(api_url, token, map_name, windowSize, feature_dim,
                                          bank, username, password)
    print(ret)
    print("StartMapConstruction...end...")
    print("StartMapConstruction---------------FIN")

    print("QueryLocal---------------BEGIN")
    print("QueryLocal...uploadImagePath: " + str(uploadImagePath))
    (ret_image_name, ret_qvec, ret_tvec) = CaptureSDK.QueryLocal(
        api_url, token, uploadImagePath, bank, username, password)
    print(
        "(ret_image_name, ret_qvec, ret_tvec):%s" % str(
            (ret_image_name, ret_qvec, ret_tvec)))
    ##
    (image_id, qvec, tvec,
     camera_id, image_name,
     xys, point3D_ids) = CaptureSDK.ImageBinInfo(api_url, token, ret_image_name, bank, username,
                                                 password)
    distance_q = numpy.sqrt(
        numpy.sum(numpy.square(numpy.array(ret_qvec) - qvec)))
    distance_t = numpy.sqrt(
        numpy.sum(numpy.square(numpy.array(ret_tvec) - tvec)))
    print(
        "(distance_q, distance_t):%s" % str(
            (distance_q, distance_t)))
    print("QueryLocal---------------END")
    #
    '''print("CVQueryLocal---------------BEGIN")
    (ret_image_name, ret_qvec, ret_tvec) = CaptureSDK.CVQueryLocal(
        api_url, token, uploadImagePath, bank, username, password)
    print(
        "(ret_image_name, ret_qvec, ret_tvec):%s" % str(
            (ret_image_name, ret_qvec, ret_tvec)))
    (image_id, qvec, tvec,
     camera_id, image_name,
     xys, point3D_ids) = CaptureSDK.ImageBinInfo(api_url, token, ret_image_name, bank, username,
                                                 password)
    distance_q = numpy.sqrt(
        numpy.sum(numpy.square(numpy.array(ret_qvec) - qvec)))
    distance_t = numpy.sqrt(
        numpy.sum(numpy.square(numpy.array(ret_tvec) - tvec)))
    print(
        "(distance_q, distance_t):%s" % str(
            (distance_q, distance_t)))
    print("CVQueryLocal---------------END")'''

    print("Query3DCouldPoint to file ---------------BEGIN")
    (db_points_pos, db_points_des, dp_points_rgb) = CaptureSDK.Query3DCouldPoint(api_url, token, bank, username,
                                                                                 password)
    # print(db_points_pos, db_points_des, dp_points_rgb)
    CaptureSDK.Write3dmap2PlyFile(db_points_pos, db_points_des, dp_points_rgb, cloudPlyFile)
    print("Query3DCouldPoint---------------END")
    return


def main():
    main_test()
    return


if __name__ == "__main__":
    main()

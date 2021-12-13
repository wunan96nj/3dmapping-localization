import CaptureSDK


def main_test():
    CaptureSDK.printTimestamp()
    # api_url = "https://api.immersal.com"
    api_url = "http://localhost:5444/capture-photo"
    token = "192b47014ee982495df0a08674ac49a11eca4cb4427e3115a0254b89d07587cc"
    image_base_dir = '/Users/akui/Desktop/south-building/images'
    seq_base = 0
    map_name = "pyFirstMap"
    windowSize = 0
    deleteAnchorImage = True
    bank = 0
    # feature_dim: colmap use 6, cv use 2
    feature_dim = 6
    uploadImagePath = "/Users/akui/Desktop/south-building/images/P1180141.jpg"

    print("post_to_server---------------BEGIN")
    CaptureSDK.ClearWorkspace(api_url, token, deleteAnchorImage, bank)
    CaptureSDK.post_to_server(api_url, token, image_base_dir, seq_base, bank)
    print("post_to_server---------------END")

    print("StartMapConstruction---------------BEGIN")
    CaptureSDK.StartMapConstruction(api_url, token, map_name, windowSize, feature_dim,
                                    bank)
    print("StartMapConstruction---------------FIN")
    #
    print("QueryLocal---------------BEGIN")
    CaptureSDK.QueryLocal(api_url, token, uploadImagePath, bank)
    CaptureSDK.printTimestamp()
    print("QueryLocal---------------END")

    print("CVQueryLocal---------------BEGIN")
    CaptureSDK.CVQueryLocal(api_url, token, uploadImagePath, bank)

    CaptureSDK.printTimestamp()
    print("CVQueryLocal---------------END")
    return


def main():
    main_test()
    return


if __name__ == "__main__":
    main()
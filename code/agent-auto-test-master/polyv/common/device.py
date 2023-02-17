import os


def get_android_device():
    devices = []
    try:
        device_list = os.popen("adb devices").readlines()
        for device in device_list:
            if 'List of devices attached' in device:
                continue
            if 'device\n' in device:
                devices.append(device.split("\t")[0])
        return devices
    except Exception as err:
        print(err)


def get_ios_device():
    devices = []
    try:
        # TODO
        return devices
    except Exception as err:
        print(err)


if __name__ == '__main__':
    print(get_android_device())

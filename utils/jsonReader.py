import json

def jsonRead(filePath):
    # read json file
    with open(filePath) as data_file:
        data = json.load(data_file)

    return data
import json

def jsonRead(filePath):
    # read json file
    with open(filePath) as data_file:
        data = json.load(data_file)

    return data

def jsonWrite(data, filePath):
    jsonData = json.dumps(data, indent=4)
    fd = open(filePath, 'w')
    fd.write(jsonData)
    fd.close()
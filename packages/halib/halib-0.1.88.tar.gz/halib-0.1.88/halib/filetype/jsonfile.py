import json


def read(file):
    with open(file) as f:
        data = json.load(f)
        return data


def write(data_dict, outfile):
    with open(outfile, "w") as json_file:
        json.dump(data_dict, json_file)


def beautify(json_str):
    formatted_json = json_str
    try:
        parsed = json.loads(json_str)
        formatted_json = json.dumps(parsed, indent=4, sort_keys=True)
    except Exception as e:
        pass
    return formatted_json

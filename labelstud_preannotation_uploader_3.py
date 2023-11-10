from jsonpath_ng import jsonpath, parse
import requests
import json
import os

# Get the project ID
def get_project_id(name, uri, key):
    url = 'http://' + uri + '/api/projects/'
    headers = {'Authorization': 'Token ' + key}

    response = requests.get(url, headers=headers)

    data = json.loads(response.text)

    for item in data.get("results", []):
        if "title" in item and item["title"] == name:
            return item["id"]
    return '\n\nUnable to find the project ID'

# Get all task IDs for a project
def get_all_task_ids_for_project(projectID, uri, key):
    print('projectID')
    print(projectID)
    url = 'http://' + uri + '/api/tasks/?project=' + str(projectID)
    headers = {'Authorization': 'Token ' + key}

    response = requests.get(url, headers=headers)

    data = json.loads(response.text)
    dataDic = {}

    for task in data.get("tasks", []):
        id = task["id"]
        storage_filename = task["storage_filename"].split("\\")[-1]
        dataDic[storage_filename] = id
    return dataDic

# Read label definitions and convert predictions to a manageable format
def read_and_convert_labels_predictions():
    root_directory = os.path.dirname(os.path.abspath(__file__))
    notes_path = os.path.join(root_directory, "notes.json")
    labels_directory = os.path.join(root_directory, "labels")

    with open(notes_path, 'r') as file:
        json_data = json.load(file)

    categories = json_data.get('categories', [])
    labels_dict = {item['id']: item['name'] for item in categories}

    data = []

    for filename in os.listdir(labels_directory):
        if filename.endswith(".txt"):
            with open(os.path.join(labels_directory, filename), 'r') as file:
                content = file.readlines()
                content_list = [[float(x) for x in line.split()]
                                for line in content]
                data.append((filename, content_list))

    r_dict = {}

    for item in data:
        arr = []
        for item2 in item[1]:
            for key, value in labels_dict.items():
                if item2[0] == key:
                    arr += [[value] + item2]
            r_dict[item[0][:item[0].rfind('.')]] = arr

    return r_dict

# Convert YOLO to Label Studio format
def yolo_to_ls(width, height, x, y, original_width, original_height):
    lsArr = []

    pixel_x = (x - original_width / 2) * 100
    pixel_y = (y - original_height / 2) * 100
    pixel_width = original_width * 100
    pixel_height = original_height * 100

    lsArr.append(pixel_x)
    lsArr.append(pixel_y)
    lsArr.append(pixel_width)
    lsArr.append(pixel_height)

    return lsArr

# Add predictions to LS Tasks task ID
def add_prediction_to_ls(task, label, x, y, width, height, inUri, key):
    url = "http://" + inUri + "/api/tasks/" + str(task[0]) + "/annotations/"
    headers = {
        "Authorization": "Token " + key,
        "Content-Type": "application/json"
    }

    data = {
        "task": task[0],
        "result": [],
    }

    for index in range(len(task)):
        new_result = {
            "from_name": "label",
            "score": 0,
            "to_name": "image",
            "type": "rectanglelabels",
            "value": {
                "height": height[index],
                "rectanglelabels": [label[index]],
                "width": width[index],
                "x": x[index],
                "y": y[index],
            }
        }
        data["result"].append(new_result)

    print("\nSending request:")
    print(data)

    response = requests.post(url, headers=headers, json=data)
    print(response.json())
    return response.text


def main(key, uri, taskName, width, height):
    projectID = get_project_id(taskName, uri, key)
    dataDic = get_all_task_ids_for_project(projectID, uri, key)
    r_dict = read_and_convert_labels_predictions()

    task, label, x, y, width, height = [], [], [], [], [], []
    for dataDic_key, dataDic_value in dataDic.items():
        if len(label) != 0:
            add_prediction_to_ls(task, label, x, y, width, height, uri, key)
            task, label, x, y, width, height = [], [], [], [], [], []

        for r_dict_key, r_dict_value in r_dict.items():
            taskName = dataDic_key[:dataDic_key.rfind('.')]
            if r_dict_key == taskName:
                for item in r_dict_value:
                    lsArr = yolo_to_ls(
                        # x, y, w, h
                        width, height, item[2], item[3], item[4], item[5])
                    task.append(dataDic_value)
                    label.append(item[0])
                    x.append(lsArr[0])
                    y.append(lsArr[1])
                    width.append(lsArr[2])
                    height.append(lsArr[3])

    print('\nEnd')


main('you labelstud key',
     'localhost:8080', 'you labelstud task name', 'width', 'height')

import os
import sys
import pickle
import json
import numpy as np
import requests
from io import BytesIO

METRICS_FILES_KEY = "file"
OUTPUT_FILE = "output"
INPUT_FILE = "input"
FILE_TYPE_EXTERNAL = "external"
FILE_TYPE_INTERMEDIATE = "intermediate"
EXECUTION_ENGINE_RUNTIME_CONFIG_PREFIX = "execution_engine_runtime_config"
EXECUTION_ENGINE_RUNTIME_CONFIG = next(filename for filename in os.listdir('.')
                                     if filename.startswith(EXECUTION_ENGINE_RUNTIME_CONFIG_PREFIX))
RESULTS_FILE = "experiment_results.json"

with open(EXECUTION_ENGINE_RUNTIME_CONFIG, 'r') as file:
    runtime_job_config = json.load(file)
    execution_engine_mapping = runtime_job_config["mapping"]
    exp_engine_metadata = runtime_job_config["exp_engine_metadata"]
    dataset_config = runtime_job_config["dataset_config"]
    DATASET_MANAGEMENT = dataset_config["DATASET_MANAGEMENT"]
    DDM_URL = dataset_config["DDM_URL"]
    DDM_TOKEN = dataset_config["DDM_TOKEN"]

AUTH_HEADERS = {'Authorization': DDM_TOKEN}

def get_experiment_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as file:
            return json.load(file)
    print("results file does not exist")
    return None


def save_datasets(variables, resultMap, key, values, file_names=None):
    if DATASET_MANAGEMENT == "DDM":
        return save_datasets_ddm(variables, resultMap, key, values, file_names)
    print("save_datasets is only available for DDM, please update your config.py")
    exit(1)


def save_dataset(variables, resultMap, key, value):
    if DATASET_MANAGEMENT == "LOCAL":
        return save_dataset_local(variables, resultMap, key, value)
    if DATASET_MANAGEMENT == "DDM":
        return save_datasets_ddm(variables, resultMap, key, [value])
    print("Cannot load dataset, please setup DATASET_MANAGEMENT in config.py")
    exit(1)


def save_dataset_local(variables, resultMap, key, value):
    value_size = sys.getsizeof(value)
    print(f"Saving output data of size {value_size} with key {key}")
    if key in variables:
        output_file_path = variables.get(key)
        folder_path = output_file_path.rsplit("/", 1)[0]
        _create_folder(folder_path)
        with open(output_file_path, "wb") as outfile:
            outfile.write(value)
    else:
        job_id = variables.get("PA_JOB_ID")
        task_id = variables.get("PA_TASK_ID")
        task_folder = os.path.join("/shared", job_id, task_id)
        os.makedirs(task_folder, exist_ok=True)
        output_file_path = os.path.join(task_folder, key)
        with open(output_file_path, "wb") as outfile:
            pickle.dump(value, outfile)
        variables.put("PREVIOUS_TASK_ID", str(task_id))
        print(f"resultMap: {resultMap}")
    if resultMap is not None:
        print(f"Adding file {output_file_path} path for file {key} to job results")
        resultMap.put(key, output_file_path)


def save_datasets_ddm(variables, resultMap, key, values, file_names=None):
    upload_url = f"{DDM_URL}/ddm/files/upload"
    file_url_template = f"{DDM_URL}/ddm/file/{{}}"
    task_name = variables['PA_TASK_NAME']
    variables.put("PREVIOUS_TASK_ID", str(task_name))

    project_id_prefix = os.path.join(exp_engine_metadata["exp_name"],
                                     exp_engine_metadata["exp_id"],
                                     exp_engine_metadata["wf_id"])
    if key in variables:
        file_type = FILE_TYPE_EXTERNAL
        ddm_value = variables.get(key)
        ddm_value_parts = ddm_value.split("|")
        output_file_name = ddm_value_parts[0]
        project_name = ddm_value_parts[1]
        project_id = os.path.join(project_id_prefix, OUTPUT_FILE, task_name)
        if project_name:
            project_id = os.path.join(project_id, project_name)
    else:
        file_type = FILE_TYPE_INTERMEDIATE
        output_file_name = key
        project_id = os.path.join(project_id_prefix, OUTPUT_FILE, task_name)
    provided_output_file_name = output_file_name
    result_value = []
    result_key = f"file:{task_name}:{OUTPUT_FILE}:{key}"
    for i in range(len(values)):
        value = values[i]
        if len(provided_output_file_name) == 0:
            if file_names:
                output_file_name = file_names[i]
            else:
                output_file_name = f"output_{i}"
        try:
            file_bytes = BytesIO(value)
            upload_files = []
            upload_files.append(("files", (output_file_name, file_bytes, "application/octet-stream")))

            metadata_files = []
            file_metadata = {"dataset_signature": key, 'task': task_name, 'assembled_wf': variables['PA_JOB_NAME']}
            metadata_json = json.dumps(file_metadata)
            metadata_bytes = BytesIO(metadata_json.encode("utf-8"))
            metadata_files.append(("metadata-files", ("", metadata_bytes, "application/json")))

        except Exception as e:
            print(f"Error processing:", str(e))

        form_data = {
            "project_id": project_id,
            "descriptions": "Generated by the exp engine",
        }
        all_files = upload_files + metadata_files

        print("Uploading to:", upload_url)
        response = requests.post(upload_url, headers=AUTH_HEADERS, files=all_files, data=form_data)
        print("Status:", response.status_code)

        generated_file_id = response.json()["files"][0]["id"]
        file_url = file_url_template.format(generated_file_id)
        file_metadata = _return_file_metadata(output_file_name, file_url, project_id, file_type)
        result_value.append(file_metadata)

        try:
            print("Response:", response.json())
        except Exception:
            print("Raw response:", response.text)
    resultMap.put(result_key, json.dumps(result_value))


def load_datasets(variables, resultMap, key):
    if DATASET_MANAGEMENT == "DDM":
        return load_datasets_ddm(variables, key, resultMap)
    print("load_datasets is only available for DDM, please update your config.py")
    exit(1)


def load_dataset(variables, resultMap, key):
    if DATASET_MANAGEMENT == "LOCAL":
        return load_dataset_local(variables, key)
    if DATASET_MANAGEMENT == "DDM":
        return load_datasets_ddm(variables, key, resultMap)[0]
    print("Cannot load dataset, please setup DATASET_MANAGEMENT in config.py")
    exit(1)


def load_dataset_local(variables, key):
    print(f"Loading input data with key {key}")
    if key in variables:
        input_filename = variables.get(key)
        return load_dataset_by_path(input_filename)
    else:
        job_id = variables.get("PA_JOB_ID")
        task_id = variables.get("PREVIOUS_TASK_ID")
        task_folder = os.path.join("/shared", job_id, task_id)
        task_name = variables.get("PA_TASK_NAME")
        if task_name in execution_engine_mapping:
            if key in execution_engine_mapping[task_name]:
                key = execution_engine_mapping[task_name][key]
        input_filename = os.path.join(task_folder, key)
        return load_pickled_dataset_by_path(input_filename)


def load_datasets_ddm(variables, key, resultMap):
    file_url_template = f"{DDM_URL}/ddm/file/{{}}"
    task_name = variables.get("PA_TASK_NAME")
    if key in variables:
        file_type = FILE_TYPE_EXTERNAL
        ddm_value = variables.get(key)
        ddm_value_parts = ddm_value.split("|")
        fname = ddm_value_parts[0]
        project_id = ddm_value_parts[1]
    else:
        file_type = FILE_TYPE_INTERMEDIATE
        fname = key
        if task_name in execution_engine_mapping:
            if fname in execution_engine_mapping[task_name]:
                fname = execution_engine_mapping[task_name][fname]
        task_id = variables.get("PREVIOUS_TASK_ID")
        project_id_prefix = os.path.join(exp_engine_metadata["exp_name"],
                                         exp_engine_metadata["exp_id"],
                                         exp_engine_metadata["wf_id"])
        project_id = os.path.join(project_id_prefix, OUTPUT_FILE, task_id)
    results = _look_up_file_in_catalog(fname, project_id)

    contents = []
    result_key = f"file:{task_name}:{INPUT_FILE}:{key}"
    result_value = []
    for entry in results:
        file_id = entry.get("id")
        file_url = file_url_template.format(file_id)
        print("Downloading:", file_url)
        f_response = requests.get(file_url, headers=AUTH_HEADERS)
        file_metadata = _return_file_metadata(entry.get("upload_filename"), file_url, project_id, file_type)
        result_value.append(file_metadata)
        f_response.raise_for_status()
        contents.append(f_response.content)
    resultMap.put(result_key, json.dumps(result_value))
    return contents


def _return_file_metadata(file_name, file_url, project_id, file_type):
    file_metadata = {
        "file_name": file_name,
        "file_url": file_url,
        "project_id": project_id,
        "file_type": file_type
    }
    return file_metadata


def _look_up_file_in_catalog(fname, project_id):
    print(f"Looking up {fname} in project {project_id}")
    catalog_url = f"{DDM_URL}/ddm/catalog/list"
    r = requests.get(
        catalog_url,
        headers=AUTH_HEADERS,
        params={
            "filename": fname,
            # "sort": "created,desc",
            # "page": 1,
            "perPage": 1000,
        }
    )
    r.raise_for_status()
    results = r.json().get("data", [])
    if not results:
        raise Exception(f"No files with name {fname}.")
    results = [r for r in results if r["project_id"] == project_id]
    if len(results) == 0:
        raise Exception(f"No files with name {fname} found in project {project_id}.")
    return results


def load_pickled_dataset_by_path(file_path):
    with open(file_path, "rb") as f:
        file_contents = pickle.load(f)
    return file_contents


def load_dataset_by_path(file_path):
    with open(file_path, "rb") as f:
        file_contents = BytesIO(f.read())
    return file_contents.getvalue()


def create_dir(variables, key):
    job_id = variables.get("PA_JOB_ID")
    # TODO Check: shouldn't the next line be PA_TASK_ID instead of PREVIOUS_TASK_ID?
    task_id = variables.get("PREVIOUS_TASK_ID")
    folder = os.path.join("/shared", job_id, task_id, key)
    os.makedirs(folder, exist_ok=True)

    return folder


def get_file_path(variables, data_set_folder_path, file_name):
    folder_path = variables.get(data_set_folder_path)
    file_path = os.path.join(folder_path, file_name)
    _create_folder(folder_path)
    return file_path


def _create_folder(folder_path):
    os.makedirs(folder_path, exist_ok=True)
    # TODO remove the next 3 lines once the bug with output files if fixed
    placeholder_path = os.path.join(folder_path, ".placeholder")
    with open(placeholder_path, 'w'):
        pass


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

from . import run_experiment
from .executionware import proactive_runner as proactive_runner
from .data_abstraction_layer.data_abstraction_api import set_data_abstraction_config, create_experiment
import os
import requests
import logging.config
from . import exceptions

logger = logging.getLogger(__name__)


def get_ddm_token(config):
    if config.DATASET_MANAGEMENT != "DDM":
        return None
    url = f"{config.DDM_URL}/extreme_auth/api/v1/person/login"
    data = {
        "username": config.PORTAL_USERNAME,
        "password": config.PORTAL_PASSWORD
    }
    response = requests.post(url, json=data)
    status_code = response.status_code
    response_json = response.json()
    if status_code == 401:
        logger.error("Portal authentication failed.")
        error_code = response_json["error_code"]
        if error_code == 4012:
            raise exceptions.PortalUserDoesNotExist(
                "Portal user not found - please check the PORTAL_USERNAME in your configuration")
        if error_code == 4011:
            raise exceptions.PortalPasswordDoesNotMatch(
                "Portal user found, but password does not match - please check PORTAL_PASSWORD in your configuration")
    if status_code == 200:
        access_token = response.json()["access_token"]
        logger.info("portal authentication successful, ddm token retrieved")
        return f"Bearer {access_token}"


class Config:

    def __init__(self, config):
        self.TASK_LIBRARY_PATH = config.TASK_LIBRARY_PATH
        self.EXPERIMENT_LIBRARY_PATH = config.EXPERIMENT_LIBRARY_PATH
        self.DATASET_LIBRARY_RELATIVE_PATH = config.DATASET_LIBRARY_RELATIVE_PATH
        self.PYTHON_DEPENDENCIES_RELATIVE_PATH = config.PYTHON_DEPENDENCIES_RELATIVE_PATH
        if 'DATASET_MANAGEMENT' not in dir(config) or len(config.DATASET_MANAGEMENT) == 0:
            raise exceptions.DatasetManagementNotSet(
                "Please set the variable DATASET_MANAGEMENT in config.py to either \"LOCAL\" or \"DDM\"")
        else:
            self.DATASET_MANAGEMENT = config.DATASET_MANAGEMENT
        if config.DATASET_MANAGEMENT == "DDM":
            if 'DDM_URL' not in dir(config) or len(config.DDM_URL) == 0:
                raise exceptions.DatasetManagementSetToDDMButNoURLProvided(
                    "Please set the variable DDM_URL in config.py")
            if 'PORTAL_USERNAME' not in dir(config) or len(config.PORTAL_USERNAME) == 0:
                raise exceptions.DatasetManagementSetToDDMButNoPortalUserOrPasswordProvided(
                    "Please set the variable PORTAL_USERNAME in config.py")
            if 'PORTAL_PASSWORD' not in dir(config) or len(config.PORTAL_PASSWORD) == 0:
                raise exceptions.DatasetManagementSetToDDMButNoPortalUserOrPasswordProvided(
                    "Please set the variable PORTAL_PASSWORD in config.py")
        self.DDM_URL = config.DDM_URL if 'DDM_URL' in dir(config) else None
        self.DDM_TOKEN = get_ddm_token(config)
        self.DATA_ABSTRACTION_BASE_URL = config.DATA_ABSTRACTION_BASE_URL
        self.DATA_ABSTRACTION_ACCESS_TOKEN = config.DATA_ABSTRACTION_ACCESS_TOKEN
        self.EXECUTIONWARE = config.EXECUTIONWARE
        self.PROACTIVE_URL = config.PROACTIVE_URL
        self.PROACTIVE_USERNAME = config.PROACTIVE_USERNAME
        self.PROACTIVE_PASSWORD = config.PROACTIVE_PASSWORD
        self.PROACTIVE_PYTHON_VERSIONS = config.PROACTIVE_PYTHON_VERSIONS if 'PROACTIVE_PYTHON_VERSIONS' in dir(config) else None
        self.PYTHON_CONDITIONS = config.PYTHON_CONDITIONS if 'PYTHON_CONDITIONS' in dir(config) else None
        self.PYTHON_CONFIGURATIONS = config.PYTHON_CONFIGURATIONS if 'PYTHON_CONFIGURATIONS' in dir(config) else None
        if 'MAX_WORKFLOWS_IN_PARALLEL_PER_NODE' in dir(config):
            logger.debug(f"Setting MAX_WORKFLOWS_IN_PARALLEL_PER_NODE to {config.MAX_WORKFLOWS_IN_PARALLEL_PER_NODE}")
            self.MAX_WORKFLOWS_IN_PARALLEL_PER_NODE = config.MAX_WORKFLOWS_IN_PARALLEL_PER_NODE
        else:
            default_max_workflows_in_parallel_per_node = 1
            logger.debug(f"Setting MAX_WORKFLOWS_IN_PARALLEL_PER_NODE to the default value of {default_max_workflows_in_parallel_per_node}")
            self.MAX_WORKFLOWS_IN_PARALLEL_PER_NODE = default_max_workflows_in_parallel_per_node


def run(runner_file, exp_name, config):
    logger.info(f"abspath: {os.path.relpath(config.EXPERIMENT_LIBRARY_PATH)}")
    logger.info(f"os.listdir: {os.listdir(config.EXPERIMENT_LIBRARY_PATH)}")

    with open(os.path.join(config.EXPERIMENT_LIBRARY_PATH, exp_name + ".xxp"), 'r') as file:
        workflow_specification = file.read()

    if 'LOGGING_CONFIG' in dir(config):
        logging.config.dictConfig(config.LOGGING_CONFIG)

    new_exp = {
        'name': exp_name,
        'model': str(workflow_specification),
    }

    config_obj = Config(config)
    set_data_abstraction_config(config_obj)

    exp_id = create_experiment(new_exp, "dummy_user")

    run_experiment(exp_id, workflow_specification, os.path.dirname(os.path.abspath(runner_file)), config_obj)

    return exp_id


def kill_job(job_id, config):
    gateway = proactive_runner.create_gateway_and_connect_to_it(config.PROACTIVE_USERNAME, config.PROACTIVE_PASSWORD)
    gateway.killJob(job_id)


def pause_job(job_id, config):
    gateway = proactive_runner.create_gateway_and_connect_to_it(config.PROACTIVE_USERNAME, config.PROACTIVE_PASSWORD)
    gateway.pauseJob(job_id)


def resume_job(job_id, config):
    gateway = proactive_runner.create_gateway_and_connect_to_it(config.PROACTIVE_USERNAME, config.PROACTIVE_PASSWORD)
    gateway.resumeJob(job_id)


def kill_task(job_id, task_name, config):
    gateway = proactive_runner.create_gateway_and_connect_to_it(config.PROACTIVE_USERNAME, config.PROACTIVE_PASSWORD)
    gateway.killTask(job_id, task_name)

import logging
logger = logging.getLogger(__name__)


class Dataset:

    def __init__(self, name):
        self.name = name
        self.path = ""
        self.filename = ""
        self.project = ""
        self.name_in_task_signature = None
        self.name_in_generating_task = None

    def add_path(self, path):
        self.path = path

    def add_filename(self, filename):
        self.filename = filename

    def add_project(self, project):
        self.project = project

    def set_name_in_task_signature(self, name_in_task_signature):
        self.name_in_task_signature = name_in_task_signature

    def set_name_in_generating_task(self, name_in_generating_task):
        self.name_in_generating_task = name_in_generating_task

    def print(self, tab=""):
        logger.debug(f"{tab}\twith dataset name : {self.name}")
        logger.debug(f"{tab}\twith dataset name in task signature : {self.name_in_task_signature}")
        logger.debug(f"{tab}\twith dataset name in generating task : {self.name_in_generating_task}")
        logger.debug(f"{tab}\twith dataset path : {self.path}")
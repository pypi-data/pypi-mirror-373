import dataclasses as dc
import importlib.util
import os
import sys

from orc_sdk.constants import BASE_IMAGE
from orc_sdk.docker import DockerImageBuildRequest
from orc_sdk.step import FuncStep
from orc_sdk.utils import catchtime
from orc_sdk.workflow import WorkflowRuntimeObject
from orc_sdk.workflow_builder.base import (
    BaseWorkflowBuilder,
    compile_wf_config,
    WorkflowInfo,
    get_docker_image_build_request,
)


@dc.dataclass
class LocalFilesWorkflowBuilder(BaseWorkflowBuilder):
    filename: str

    def build(self):
        with catchtime("get_wfro_from_file"):
            wfro = get_wfro_from_file(self.filename)
        with catchtime("compile_wf_config"):
            wf_config = compile_wf_config(wfro)

        wf_file_module = get_file_module_root(self.filename)

        if os.path.abspath(wf_file_module) != os.path.abspath(self.filename):
            wf_file_module_dir = os.path.dirname(wf_file_module)  # FIXME
            rel_file_path = os.path.abspath(self.filename).removeprefix(wf_file_module_dir + "/")
        else:
            rel_file_path = os.path.basename(self.filename)  # TODO FIXME
        path_in_container = f"/orc/lib/{rel_file_path}"

        default_image_added = False

        wfro_steps = wfro.get_steps()

        docker_build_requests: list[DockerImageBuildRequest] = []

        print("Preparing workflow config")
        for step in wf_config["steps"]:
            step_id = step["step_id"]
            sci = wfro_steps[step_id].sci
            if not isinstance(sci, FuncStep):
                continue

            is_default_image = not (sci.additional_requirements or sci.base_image)

            image_name = "default" if is_default_image else step_id
            dbr = self._get_docker_build_request_for_step(
                image_name=image_name, sci=sci, wfro=wfro, files_to_copy=[wf_file_module],
            )

            if not is_default_image or is_default_image and not default_image_added:
                docker_build_requests.append(dbr)

            if is_default_image and not default_image_added:
                default_image_added = True

            step["task_params"]["docker_image"] = dbr.image_tag

            step["task_params"]["env"] = {"PYTHONPATH": "/orc/lib", "YT_BASE_LAYER": step["task_params"]["docker_image"]}
            step["task_params"]["command"] = f"exec orc_run_step {path_in_container} {sci.func.__name__} >&2"
            step["task_params"]["func_code_hash"] = sci.func_code_hash

        self._build_images(build_root=os.path.dirname(wf_file_module), build_requests=docker_build_requests)

        return WorkflowInfo(workflow_path=wfro.workflow_path, workflow_config=wf_config)


def load_module(file_name, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def get_wfro_from_file(filename: str) -> WorkflowRuntimeObject:
    module = load_module(filename, "user_code")
    for key, obj in module.__dict__.items():
        if getattr(obj, "is_workflow", False):
            wfro = obj()  # TODO: args?
            return wfro
    else:
        raise Exception("No workflow found")


def get_file_module_root(filename: str) -> str:
    dirname = os.path.dirname(os.path.abspath(filename))
    if not os.path.exists(os.path.join(dirname, "__init__.py")):
        return filename
    return get_file_module_root(dirname)

import dataclasses as dc
import os

import cloudpickle

from orc_sdk.docker import DockerImageBuildRequest
from orc_sdk.step import FuncStep
from orc_sdk.workflow import WorkflowRuntimeObject
from orc_sdk.workflow_builder.base import (
    BaseWorkflowBuilder,
    compile_wf_config,
    WorkflowInfo,
)


@dc.dataclass
class TaskObjectsWorkflowBuilder(BaseWorkflowBuilder):
    wfro: WorkflowRuntimeObject
    default_base_image: str

    def build(self):
        wf_config = compile_wf_config(self.wfro)

        wfro_steps = self.wfro.get_steps()

        docker_build_requests: list[DockerImageBuildRequest] = []

        print("Preparing workflow config")

        wf_tasks_pickled_path = f"wf_tasks_pickled"
        wf_tasks_map = {}

        path_in_container = f"/orc/lib/{wf_tasks_pickled_path}"

        default_image_added = False

        for step in wf_config["steps"]:
            step_id = step["step_id"]
            sci = wfro_steps[step_id].sci
            if not isinstance(sci, FuncStep):
                continue

            wf_tasks_map[sci.func.__name__] = sci

            is_default_image = not (sci.additional_requirements or sci.base_image)

            image_name = "default" if is_default_image else step_id
            dbr = self._get_docker_build_request_for_step(
                image_name=image_name, sci=sci, wfro=self.wfro, files_to_copy=[wf_tasks_pickled_path],
            )

            if not is_default_image or is_default_image and not default_image_added:
                docker_build_requests.append(dbr)

            if is_default_image and not default_image_added:
                default_image_added = True

            step["task_params"]["docker_image"] = dbr.image_tag

            step["task_params"]["env"] = {"PYTHONPATH": "/orc/lib", "YT_BASE_LAYER": step["task_params"]["docker_image"]}
            step["task_params"]["command"] = f"exec orc_run_step {path_in_container} {sci.func.__name__} --mode pickled_tasks >&2"
            step["task_params"]["func_code_hash"] = sci.func_code_hash

        open(wf_tasks_pickled_path, "wb").write(cloudpickle.dumps(wf_tasks_map))

        self._build_images(build_root=".", build_requests=docker_build_requests)

        wf_info = WorkflowInfo(workflow_path=self.wfro.workflow_path, workflow_config=wf_config)
        return wf_info

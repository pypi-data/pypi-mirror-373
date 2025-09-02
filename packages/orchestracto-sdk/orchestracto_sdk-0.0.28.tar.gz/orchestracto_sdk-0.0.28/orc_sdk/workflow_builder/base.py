import abc
import dataclasses as dc
import inspect
import os
import sys
from typing import Any, Iterable, Literal

from orc_sdk import each, RawStep
from orc_sdk.constants import BASE_IMAGE
from orc_sdk.docker import DockerImageBuildRequest
from orc_sdk.env_config import EnvConfig
from orc_sdk.step import FuncStep
from orc_sdk.step_chain import RetValWrapper, StepChainItem
from orc_sdk.workflow import WorkflowRuntimeObject, WfArgWrapper
from orc_sdk.user_info import UserInfo, get_user_info
from orc_sdk.utils import catchtime
from orc_sdk.docker import DockerImageBuilderLocal, DockerImageBuilderWizard


def compile_wf_config(wfro: WorkflowRuntimeObject) -> dict[str, Any]:
    wf_config = {
        "triggers": [],
        "steps": [],
        "workflow_params": [{"name": wfp.name, "default_value": wfp.default_value} for wfp in wfro.wf_parameters],
    }

    steps = wfro.get_steps()
    each_arg_names = dict()
    for step_id, sci_info in steps.items():
        if isinstance(sci_info.sci, FuncStep):
            func_signature = inspect.signature(sci_info.sci.func)

            passed_args = {}
            for i, arg in enumerate(sci_info.sci.func_args):
                arg_name = list(func_signature.parameters.keys())[i]  # FIXME??
                passed_args[arg_name] = arg

            for name, value in sci_info.sci.func_kwargs.items():
                passed_args[name] = value

            step_args = []
            for i, name in enumerate(func_signature.parameters):
                if name in passed_args:
                    if isinstance(passed_args[name], RetValWrapper):
                        src_type = "step_output"
                        src_ref = f"{passed_args[name].sci.step_id}.{passed_args[name].name}"
                    elif isinstance(passed_args[name], WfArgWrapper):
                        src_type = "workflow_param"
                        src_ref = passed_args[name].name
                    else:
                        src_type = "constant"
                        src_ref = passed_args[name]
                else:
                    src_type = "constant"
                    src_ref = func_signature.parameters[name].default

                if src_ref is each:
                    each_arg_names[step_id] = name
                    continue

                step_args.append({
                    "name": name,
                    "src_type": src_type,
                    "src_ref": src_ref,
                })

            task_type = "docker"

            task_params = {
                "docker_image": "TODO",
                "command": sci_info.sci.func.__name__,
            }

            if sci_info.sci.memory_limit_bytes is not None:
                task_params["memory_limit"] = sci_info.sci.memory_limit_bytes

            if sci_info.sci.disk_request is not None:
                task_params["disk_request"] = sci_info.sci.disk_request

            outputs = [{
                "name": name,
            } for name in sci_info.sci.retval_names]


        elif isinstance(sci_info.sci, RawStep):
            task_type = sci_info.sci.task_type
            task_params = sci_info.sci.task_params

            step_args = []
            for arg in sci_info.sci.args:
                step_args.append({
                    "name": arg["name"],
                    "src_type": arg["src_type"],
                    "src_ref": arg["src_ref"],
                })

            outputs = []
            for output_name in sci_info.sci.outputs:
                outputs.append({
                    "name": output_name,
                })

            for key, value in task_params.items():
                if isinstance(value, RetValWrapper):
                    task_params[key] = f"{{{{ args.{value.name} }}}}"  # TODO: randomize value.name?
                    step_args.append({
                        "name": value.name,
                        "src_type": "step_output",
                        "src_ref": f"{value.sci.step_id}.{value.name}",
                    })

        else:
            raise NotImplementedError

        secrets = []
        for secret in sci_info.sci.secrets:
            secrets.append({
                "key": secret.key,
                "value_ref": secret.value_ref,
                "value_src_type": secret.value_src_type,
            })

        for_each = None
        if sci_info.sci._for_each is not None:
            iterable = sci_info.sci._for_each
            if isinstance(iterable, Iterable):
                arg_val = list(iterable)
                step_args.append({
                    "name": each_arg_names[step_id],
                    "src_type": "constant",
                    "src_ref": arg_val,
                })
                for_each = {
                    "loop_arg_name": each_arg_names[step_id],
                }
            elif isinstance(iterable, RetValWrapper):
                step_args.append({
                    "name": each_arg_names[step_id],
                    "src_type": "step_output",
                    "src_ref": f"{iterable.sci.step_id}.{iterable.name}",
                })
                for_each = {
                    "loop_arg_name": each_arg_names[step_id],
                }
            else:
                raise ValueError(f"Invalid for_each iterable: {iterable}")

        wf_config["steps"].append({
            "step_id": step_id,
            "task_type": task_type,
            "task_params": task_params,
            "args": step_args,
            "secrets": secrets,
            "outputs": outputs,
            "depends_on": list(sci_info.depends_on),
            "for_each": for_each,
            "cache": {
                "enable": sci_info.sci.cache.enable,
            },
            "max_retries": sci_info.sci.max_retries,
            "min_retry_interval_seconds": sci_info.sci.min_retry_interval_seconds,
        })

    wf_config["triggers"] = wfro.triggers

    return wf_config


def get_docker_image_build_request(
        workflow_path: str,
        image_name: str,
        files_to_copy: list[str],
        additional_requirements: list[str],
        registry_url: str,
        tenant_dir_tag: str,
        base_image: str = BASE_IMAGE,
) -> DockerImageBuildRequest:
    py_packages_installation = f"""
            RUN pip install -U {" ".join(additional_requirements)}
            """ if additional_requirements else ""

    dockerfile = f"""
        FROM {BASE_IMAGE} AS sdk_runtime
        FROM {base_image}
        USER root
        {py_packages_installation}
        RUN mkdir /orc
        COPY --from=sdk_runtime /usr/local/lib/python3.12/site-packages/orc_sdk /orc/lib/orc_sdk
        COPY --from=sdk_runtime /usr/local/lib/python3.12/site-packages/cloudpickle /orc/lib/cloudpickle
        COPY --from=sdk_runtime /usr/local/bin/orc_run_step /usr/local/bin/orc_run_step
        RUN new_shebang='#!/usr/bin/env python3' && sed -i "1s|.*|$new_shebang|" /usr/local/bin/orc_run_step
        RUN chmod +x /usr/local/bin/orc_run_step
    """
    for file_path in files_to_copy:
        dockerfile += f"COPY {os.path.basename(file_path)} /orc/lib/{os.path.basename(file_path)}\n"

    image_rel_path = workflow_path.removeprefix("//") + "/" + image_name
    docker_tag = f"{registry_url}/{tenant_dir_tag}/public_registry/{image_rel_path}:latest"

    return DockerImageBuildRequest(dockerfile=dockerfile, image_tag=docker_tag, files=files_to_copy)


@dc.dataclass
class WorkflowInfo:
    workflow_path: str
    workflow_config: dict[str, Any]


@dc.dataclass
class BaseWorkflowBuilder:
    env_config: EnvConfig
    docker_builder: Literal["local", "wizard"]
    debug_docker_build: bool

    default_base_image: str = dc.field(init=False)

    def __post_init__(self):
        self.default_base_image = BASE_IMAGE

    @abc.abstractmethod
    def build(self) -> WorkflowInfo:
        pass

    @property
    def user_info(self) -> UserInfo:
        return get_user_info(env_config=self.env_config)

    @property
    def registry_url(self) -> str:
        if self.user_info is not None and self.user_info.tenant_cr_host is not None:
            return self.user_info.tenant_cr_host
        return self.env_config.registry_url

    def _get_tenant_dir_tag(self):
        if self.user_info is None:
            return "home/orchestracto"
        else:
            return f"sys/orchestracto/tenants/{self.user_info.tenant_group}"  # TODO: switch to tenant name

    def _get_docker_build_request_for_step(
            self, image_name: str, sci: FuncStep, wfro: WorkflowRuntimeObject, files_to_copy: list[str]
    ) -> DockerImageBuildRequest:
        dbr = get_docker_image_build_request(
            workflow_path=wfro.workflow_path, image_name=image_name,
            files_to_copy=files_to_copy,
            additional_requirements=wfro.additional_requirements + sci.additional_requirements,
            registry_url=self.registry_url,
            base_image=sci.base_image or self.default_base_image,
            tenant_dir_tag=self._get_tenant_dir_tag(),
        )
        return dbr

    def _build_images(self, build_root: str, build_requests: list[DockerImageBuildRequest]) -> None:
        print("Building and pushing images")
        builder_cls = {
            "local": DockerImageBuilderLocal,
            "wizard": DockerImageBuilderWizard,
        }[self.docker_builder]

        builder = builder_cls(
            build_root=build_root,
            env_config=self.env_config,
            registry_url=self.registry_url,
            user_info=self.user_info,
            debug_docker_build=self.debug_docker_build,
        )
        builder.login_in_registry(self.env_config.yt_token)

        with catchtime("build_and_push_docker_images"):
            build_errors = builder.build_batch(build_requests)

        if build_errors:
            print("BUILD FAILED")
            for error in build_errors:
                print("=== stderr ===")
                print(error.stderr)
            sys.exit(1)

        print("Images are built and pushed")

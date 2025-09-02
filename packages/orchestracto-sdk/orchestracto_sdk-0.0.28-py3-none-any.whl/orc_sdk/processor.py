import argparse
import os
from typing import Literal, Callable

import yt.wrapper as yt

from orc_client.client import OrcClient
from orc_sdk.env_config import EnvConfig

from orc_sdk.workflow import WorkflowRuntimeObject
from orc_sdk.utils import catchtime
from orc_sdk.workflow_builder.task_objects import TaskObjectsWorkflowBuilder
from orc_sdk.workflow_builder.local_files import LocalFilesWorkflowBuilder


def process_python_file(
        filename: str,
        docker_builder: Literal["local", "wizard"] = "local",
        debug_docker_build: bool = False,
):
    env_config = EnvConfig.from_env()

    with catchtime("prepare_workflow_config"):
        wf_builder = LocalFilesWorkflowBuilder(
            filename=filename,
            env_config=env_config,
            docker_builder=docker_builder,
            debug_docker_build=debug_docker_build,
        )
        wf_info = wf_builder.build()

    orc_client = OrcClient(orc_url=env_config.orc_url, yt_token=env_config.yt_token)
    with catchtime("update_workflow_config_on_yt"):
        orc_client.update_workflow(wf_info.workflow_path, wf_info.workflow_config)

    print("Workflow is updated")


def process_workflow_object(wfro_func: Callable[[], WorkflowRuntimeObject], use_base_layer_as_base_image: bool = False):
    env_config = EnvConfig.from_env()

    if use_base_layer_as_base_image:
        yt_base_image = os.environ["YT_BASE_LAYER"]
    else:
        yt_client = yt.YtClient(
            proxy=env_config.yt_proxy,
            token=env_config.yt_token,
        )
        yt_base_image = yt_client.get("//sys/jupyt/defaults/@value/base_kernel_image")

    wfro = wfro_func()
    with catchtime("prepare_workflow_config"):
        wf_builder = TaskObjectsWorkflowBuilder(
            wfro=wfro,
            env_config=env_config,
            docker_builder="wizard",
            debug_docker_build=False,
            default_base_image=yt_base_image,
        )
        wf_info = wf_builder.build()

    orc_client = OrcClient(orc_url=env_config.orc_url, yt_token=env_config.yt_token)
    with catchtime("update_workflow_config_on_yt"):
        orc_client.update_workflow(wf_info.workflow_path, wf_info.workflow_config)

    print("Workflow is updated")


def configure_arg_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    subparsers = parser.add_subparsers(dest="command")

    get_config = subparsers.add_parser("get-config")
    get_config.add_argument("filename", type=str)

    process_parser = subparsers.add_parser("process")
    process_parser.add_argument("filename", type=str)
    process_parser.add_argument("--debug-docker-build", action="store_true")
    process_parser.add_argument("--docker-builder", default="local")

    return parser


def process_args(args: argparse.Namespace):
    match args.command:
        case "process":
            process_python_file(
                args.filename,
                docker_builder=args.docker_builder,
                debug_docker_build=args.debug_docker_build,
            )

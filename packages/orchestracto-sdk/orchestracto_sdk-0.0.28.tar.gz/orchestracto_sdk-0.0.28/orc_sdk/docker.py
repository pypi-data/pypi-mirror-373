import abc
import concurrent.futures
import contextlib
import dataclasses
import os
import subprocess
import sys
import uuid
from typing import Any, Generator

import yt.wrapper as yt

from orc_sdk.utils import catchtime_deco
from orc_sdk.env_config import EnvConfig
from orc_sdk.user_info import UserInfo
from orc_sdk.wizard_client import WizardClient

DEFAULT_DOCKER_COMMAND = "docker"


@dataclasses.dataclass
class DockerImageBuildRequest:
    dockerfile: str
    image_tag: str
    files: list[str]


@dataclasses.dataclass
class DockerImageBuildErrorInfo:
    stderr: str | None


@dataclasses.dataclass
class DockerImageBuilderBase:
    build_root: str
    env_config: EnvConfig
    registry_url: str
    user_info: UserInfo | None
    debug_docker_build: bool = False
    max_parallel: int = 4

    @abc.abstractmethod
    def login_in_registry(self, token: str) -> None:
        pass

    @abc.abstractmethod
    def build_image(self, build_request: DockerImageBuildRequest) -> DockerImageBuildErrorInfo | None:
        pass

    def build_batch(self, build_requests: list[DockerImageBuildRequest]) -> list[DockerImageBuildErrorInfo]:
        errors = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
            future_to_build_request = {
                executor.submit(self.build_image, build_request): build_request
                for build_request in build_requests
            }
            for idx, future in enumerate(concurrent.futures.as_completed(future_to_build_request)):
                error_data = future.result()
                if error_data is not None:
                    errors.append(error_data)
                print("Build", idx + 1, "of", len(build_requests), "is done")

        return errors


@dataclasses.dataclass
class DockerImageBuilderLocal(DockerImageBuilderBase):
    docker_command: str = dataclasses.dataclass(init=False)

    def __post_init__(self):
        self.docker_command = os.environ.get("DOCKER_COMMAND", DEFAULT_DOCKER_COMMAND)

    def _supports_push_on_build(self) -> bool:
        return self.docker_command.split("/")[-1] != "buildah"  # TODO: check `--version`

    @catchtime_deco
    def login_in_registry(self, token: str) -> None:
        proc = subprocess.Popen(
            [self.docker_command, "login", "--password-stdin", "-u", "user", self.registry_url],
            stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr
        )
        proc.communicate(token.encode())
        if proc.wait() != 0:
            raise Exception("Login failed")

    def build_image(self, build_request: DockerImageBuildRequest) -> DockerImageBuildErrorInfo | None:
        stdout = sys.stdout if self.debug_docker_build else subprocess.PIPE
        stderr = sys.stderr if self.debug_docker_build else subprocess.PIPE

        build_command = [
            self.docker_command, "build",
            "--platform", "linux/amd64",
            "-t", build_request.image_tag,
            "-f", "-",
            self.build_root,
        ]

        if self._supports_push_on_build():
            build_command.append("--push")

        run_res = subprocess.run(
            build_command,
            input=build_request.dockerfile.encode(),
            env={"BUILDKIT_PROGRESS": "plain", **os.environ},
            stdout=stdout, stderr=stderr,
        )
        if run_res.returncode != 0:
            provided_stderr = run_res.stderr.decode() if not self.debug_docker_build else None
            return DockerImageBuildErrorInfo(stderr=provided_stderr)

        if not self._supports_push_on_build():
            run_res = subprocess.run([self.docker_command, "push", build_request.image_tag], stdout=stdout, stderr=stderr)
            if run_res.returncode != 0:
                provided_stderr = run_res.stderr.decode() if not self.debug_docker_build else None
                return DockerImageBuildErrorInfo(stderr=provided_stderr)


@contextlib.contextmanager
def temporary_cypress_files(
        yt_client: yt.YtClient, tmp_path: str, files: list[str]
) -> Generator[list[Any], Any, None]:
    yt_paths = []
    tmp_dir = f"{tmp_path}/{uuid.uuid4().hex}"

    for file_path in files:
        if os.path.isdir(file_path):
            raise NotImplementedError("Directory uploads are not supported in local builds yet")

        yt_file_path = f"{tmp_dir}/{os.path.basename(file_path)}"
        yt_client.create("file", yt_file_path, recursive=True)
        yt_client.write_file(yt_file_path, open(file_path, "rb"))
        yt_paths.append(yt_file_path)

    yield yt_paths

    yt_client.remove(tmp_dir, recursive=True)


@dataclasses.dataclass
class DockerImageBuilderWizard(DockerImageBuilderBase):
    def __post_init__(self):
        self.yt_client = yt.YtClient(
            proxy=self.env_config.yt_proxy,
            token=self.env_config.yt_token,
        )

    def login_in_registry(self, token: str) -> None:
        pass

    def build_image(self, build_request: DockerImageBuildRequest) -> DockerImageBuildErrorInfo | None:
        tmp_path = self.user_info.tmp_path if self.user_info else "//tmp"

        with temporary_cypress_files(
            yt_client=self.yt_client,
            tmp_path=tmp_path,
            files=build_request.files,
        ) as yt_files:
            files = [{"local": os.path.basename(p), "yt_path": p} for p in yt_files]

            wc = WizardClient(
                wizard_url=self.env_config.wizard_url,
                yt_token=self.env_config.yt_token,
            )
            run_id = wc.create_run(
                dockerfile=build_request.dockerfile,
                image_tag=build_request.image_tag,
                files=files,
            )
            msg_tmpl = (
                "Building image {tag}: {status}".format(tag=build_request.image_tag, status="{status}")
                if self.debug_docker_build else None
            )
            wc.wait_for_run(run_id, message_template=msg_tmpl)

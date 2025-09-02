import dataclasses as dc
import enum
import sys
import time
from typing import TypeAlias
import uuid

import requests


WizardRunId: TypeAlias = str


@dc.dataclass(frozen=True)
class ImageTagInfo:
    registry: str
    name: str
    tag: str

    @classmethod
    def from_full_tag(cls, full_tag: str) -> "ImageTagInfo":
        registry, name_tag = full_tag.split("/", 1)
        name, tag = name_tag.rsplit(":", 1)
        return cls(registry=registry, name=name, tag=tag)


class WizardRunStatus(enum.Enum):
    STARTING = "starting"
    RUNNING = "running"
    FAILED = "failed"
    ABORTED = "aborted"
    COMPLETED = "completed"
    UNKNOWN = "unknown"


@dc.dataclass
class WizardRunInfo:
    run_id: WizardRunId
    status: WizardRunStatus


@dc.dataclass
class WizardClient:
    wizard_url: str
    yt_token: str = dc.field(repr=False)

    def _make_request(self, method: str, endpoint: str, json=None, params=None, expect_status_code: int = 200):
        headers = {"Authorization": f"OAuth {self.yt_token}"}
        url = f"{self.wizard_url}/api/v1/{endpoint}"
        response = requests.request(method, url, json=json, params=params, headers=headers)
        if response.status_code != expect_status_code:
            print(f"Unexpected response from wizard: {response.status_code}", file=sys.stderr)
            print(response.json(), file=sys.stderr)
            raise requests.HTTPError(f"Unexpected response from wizard: {response.status_code}")
        return response.json()

    def create_run(
            self, dockerfile: str, image_tag: str,
            files: list[dict[str, str]] | None = None,
            blueprint_id: str | None = None,
    ) -> WizardRunId:
        image_tag_info = ImageTagInfo.from_full_tag(image_tag)
        blueprint_id = blueprint_id or uuid.uuid4().hex

        resp_data = self._make_request(
            "POST","runs",
            json={
                "blueprint_id": blueprint_id,
                "blueprint": {
                    "content": [
                        {
                            "type": "raw",
                            "content": dockerfile,
                        },
                    ],
                    "files": files,
                    "registry_auth": [],
                    "docker_params": {
                        "image": {
                            "registry": image_tag_info.registry,
                            "name": image_tag_info.name,
                        },
                        "build_args": "",
                    },
                    "builder_params": {},
                },
                "run_params": {
                    "tag": image_tag_info.tag,
                },
            },
        )
        run_id = resp_data["run_id"]
        return run_id

    def get_run(self, run_id: str) -> WizardRunInfo:
        resp_data = self._make_request(
            "GET", f"runs/{run_id}",
            expect_status_code=200
        )
        run_info = resp_data["run"]
        return WizardRunInfo(
            run_id=run_info["run_id"],
            status=WizardRunStatus(run_info["status"]),
        )

    def wait_for_run(
            self, run_id: str,
            timeout_sec: int | None = None,
            message_template: str | None = "Run {run_id} is still running: {status}",
            check_interval_sec: int = 5,
    ) -> WizardRunInfo:
        start_time = time.monotonic()
        while True:
            run_info = self.get_run(run_id)
            if run_info.status in {WizardRunStatus.COMPLETED, WizardRunStatus.FAILED, WizardRunStatus.ABORTED}:
                return run_info

            if message_template is not None:
                print(message_template.format(run_id=run_id, status=run_info.status.value))

            if timeout_sec is not None and (time.monotonic() - start_time) > timeout_sec:
                raise TimeoutError(f"Run {run_id} did not complete within {timeout_sec} seconds")

            time.sleep(check_interval_sec)

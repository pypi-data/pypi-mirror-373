import dataclasses as dc

import requests

from orc_sdk.env_config import EnvConfig


@dc.dataclass
class UserInfo:
    login: str
    tenant_group: str
    account_name: str
    available_pool_trees: list[str]
    pool_tree_name: str
    pool_name: str
    home_path: str
    tmp_path: str
    tenant_cr_host: str | None


def get_user_info(env_config: EnvConfig) -> UserInfo | None:
    resp = requests.get(
        f"{env_config.yt_proxy}/auth/whoami",
        headers={"Authorization": f"OAuth {env_config.yt_token}"},
    )
    resp.raise_for_status()

    login = resp.json()["login"]
    resp = requests.post(
        f"{env_config.yt_proxy}/api/v4/get",
        json={"path": f"//sys/users/{login}/@user_info"},
        headers={"Authorization": f"OAuth {env_config.yt_token}"},
    )
    if resp.status_code == 400 and resp.json().get("code") == 500:
        return None
    resp.raise_for_status()
    user_info = resp.json()["value"]
    return UserInfo(
        login=login,
        tenant_group=user_info["tenant_group"],
        account_name=user_info["account_name"],
        available_pool_trees=user_info["available_pool_trees"],
        pool_tree_name=user_info["pool_tree_name"],
        pool_name=user_info["pool_name"],
        home_path=user_info["home_path"],
        tmp_path=user_info["tmp_folder"],
        tenant_cr_host=user_info.get("tenant_tracto_registry"),
    )

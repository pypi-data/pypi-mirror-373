import dataclasses
import os


@dataclasses.dataclass
class EnvConfig:
    yt_proxy: str
    yt_token: str = dataclasses.field(repr=False)
    orc_url: str
    registry_url: str
    wizard_url: str

    @classmethod
    def from_env(cls) -> "EnvConfig":
        yt_host = None

        if any(
                os.environ.get(env_var, "").startswith("https://")
                for env_var in ["YT_PROXY", "ORC_URL"]
        ):
            default_proto = "https"
        else:
            default_proto = "http"

        if yt_proxy := os.environ.get("YT_PROXY"):
            yt_host = yt_proxy.removeprefix("http://").removeprefix("https://")
            if not yt_proxy.startswith(("http://", "https://")):
                yt_proxy = f"{default_proto}://{yt_proxy}"

        if orc_url := os.environ.get("ORC_URL"):
            yt_host = orc_url.removeprefix("http://").removeprefix("https://").removeprefix("orc.")
            if not orc_url.startswith(("http://", "https://")):
                orc_url = f"{default_proto}://{orc_url}"

        assert yt_host is not None, "YT_PROXY or ORC_URL environment variable must be set"
        if yt_proxy is None:
            yt_proxy = f"{default_proto}://{yt_host}"
        if orc_url is None:
            orc_url = f"{default_proto}://orc.{yt_host}"

        if (registry_url := os.environ.get("REGISTRY_URL")) is None:
            registry_url = f"cr.{yt_host}"

        assert yt_proxy is not None
        assert orc_url is not None
        assert registry_url is not None

        return cls(
            yt_proxy=yt_proxy,
            yt_token=os.environ["YT_TOKEN"],
            orc_url=orc_url,
            registry_url=registry_url,
            wizard_url=f"{default_proto}://tracto-wizard.{yt_host}"
        )

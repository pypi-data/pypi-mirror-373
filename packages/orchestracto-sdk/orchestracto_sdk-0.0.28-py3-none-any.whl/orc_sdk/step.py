import dataclasses
import hashlib
import inspect
import types
import typing
from typing import Callable, Any
from functools import wraps
from collections import defaultdict
from typing_extensions import Self

from orc_sdk.step_chain import StepChainItem, RetValWrapper


@dataclasses.dataclass
class SecretRecord:
    key: str
    value_ref: str
    value_src_type: str


@dataclasses.dataclass
class SecretsMixin:
    secrets: list[SecretRecord] = dataclasses.field(default_factory=list)

    def with_secret(self, key: str, value_ref: str, value_src_type: str) -> Self:
        self.secrets.append(SecretRecord(key=key, value_ref=value_ref, value_src_type=value_src_type))
        return self


@dataclasses.dataclass
class CacheSettings:
    enable: bool = dataclasses.field(default=False)
    enable_write: bool | None = dataclasses.field(default=None)
    enable_read: bool | None = dataclasses.field(default=None)
    cache_version: str = dataclasses.field(default="v1")


@dataclasses.dataclass
class CacheMixin:
    cache: CacheSettings = dataclasses.field(default_factory=CacheSettings)

    def with_cache(self, version: str | None = None) -> Self:
        self.cache.enable = True
        if version is not None:
            self.cache.cache_version = version
        return self


@dataclasses.dataclass
class StepArg:
    name: str
    src_type: str
    src_ref: Any


@dataclasses.dataclass
class ArgsOutputsMixin:  # TODO: check if it really works for raw steps
    args: list[...] = dataclasses.field(default_factory=list)
    outputs: list[str] = dataclasses.field(default_factory=list)

    def with_arg(self, name: str, src_type: str, src_ref: Any) -> Self:
        self.args.append(StepArg(name=name, src_type=src_type, src_ref=src_ref))
        return self

    def with_output(self, name: str) -> Self:
        self.outputs.append(name)
        return self


@dataclasses.dataclass
class RetriableMixin:
    max_retries: int = dataclasses.field(default=0)
    min_retry_interval_seconds: int = dataclasses.field(default=0)

    def with_retries(self, max_retries: int, min_retry_interval_seconds: int = 0) -> Self:
        self.max_retries = max_retries
        self.min_retry_interval_seconds = min_retry_interval_seconds
        return self


@dataclasses.dataclass
class RawStep(SecretsMixin, CacheMixin, ArgsOutputsMixin, RetriableMixin, StepChainItem):
    task_type: str = dataclasses.field(default="docker")
    task_params: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class ResourcesMixin:
    memory_limit_bytes: int | None = dataclasses.field(default=None)
    disk_request: dict[str, Any] | None = dataclasses.field(default=None)

    def with_memory_limit(self, limit_bytes: int) -> Self:
        self.memory_limit_bytes = limit_bytes
        return self

    def with_disk_request(self, disk_request: dict[str, Any]) -> Self:
        self.disk_request = disk_request
        return self


@dataclasses.dataclass
class FuncStep(SecretsMixin, CacheMixin, ResourcesMixin, RetriableMixin, StepChainItem):
    func: Callable[..., Any] = dataclasses.field(default_factory=lambda: None)
    func_args: tuple[Any, ...] = dataclasses.field(default_factory=list)
    func_kwargs: dict = dataclasses.field(default_factory=dict)
    retval_names: list[str] = dataclasses.field(default_factory=list)
    additional_requirements: list[str] = dataclasses.field(default_factory=list)
    base_image: str | None = dataclasses.field(default=None)
    func_code_hash: str | None = dataclasses.field(default=None)

    def __post_init__(self):
        super().__post_init__()
        for arg in self.func_args + tuple(self.func_kwargs.values()):
            if isinstance(arg, RetValWrapper):
                if arg.sci.step_id not in [ps.step_id for ps in self._prev_steps]:  # TODO: traverse
                    self._prev_steps.append(arg.sci)
                    arg.sci._next_steps.append(self)
                    self._first.extend(arg.sci._first)


    def with_additional_requirements(self, additional_requirements: list[str]) -> Self:
        self.additional_requirements = additional_requirements
        return self

    def with_base_image(self, base_image: str) -> Self:
        self.base_image = base_image
        return self

    @property
    def outputs(self):
        ret_vars = inspect.signature(self.func).return_annotation
        # TODO: maybe tuple and one value can be handled as the same case
        if typing.get_origin(ret_vars) is tuple:
            parameters = {
                self.retval_names[i]: RetValWrapper(value=None, sci=self, name=self.retval_names[i])
                for i in range(len(ret_vars.__args__))
            }
            return dataclasses.dataclass(type(self.func.__name__.capitalize(), (), parameters))
        else:
            parameters = {
                self.retval_names[0]: RetValWrapper(value=ret_vars, sci=self, name=self.retval_names[0])}
            name = self.func.__name__.capitalize()
            cls = type(name, (), parameters)
            return dataclasses.dataclass(cls)


FUNC_NAME_COUNTER = defaultdict(lambda: 0)


def task(retval_names: list[str] | None = None) -> Callable[[Callable[..., Any]], Callable[..., FuncStep]]:
    def decorator(function: Callable[..., Any]) -> Callable[..., FuncStep]:
        @wraps(function)
        def wrapper(*args, **kwargs) -> FuncStep:
            FUNC_NAME_COUNTER[function.__name__] += 1
            sro_id = function.__name__ + "_" + str(FUNC_NAME_COUNTER[function.__name__])
            func_code_hash = hashlib.md5(inspect.getsource(function).encode()).hexdigest()

            nonlocal retval_names
            if retval_names is None and inspect.signature(function).return_annotation is not inspect._empty:
                num_outputs = 1 if not inspect.signature(function).return_annotation is tuple else len(inspect.signature(function).return_annotation)
                retval_names = [f"output_{i}" for i in range(1, num_outputs + 1)]

            sro = FuncStep(
                step_id=sro_id, func=function, func_args=args, func_kwargs=kwargs,
                retval_names=retval_names or [], func_code_hash=func_code_hash,
            )
            return sro

        wrapper.is_task = True
        return wrapper

    return decorator

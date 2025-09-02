import inspect
import dataclasses
from typing import Any
from functools import wraps

from orc_sdk.step_chain import StepChainItem


@dataclasses.dataclass
class SCIInfo:
    sci: StepChainItem
    depends_on: set[str]


@dataclasses.dataclass
class WfArgWrapper:
    value: Any
    name: str


@dataclasses.dataclass
class WorkflowParameter:
    name: str
    default_value: Any = None


class WorkflowRuntimeObject:
    def __init__(
            self, workflow_path: str, triggers: list[Any],
            additional_requirements: list[str],
            wf_parameters: list[WorkflowParameter],
    ):
        self.workflow_path = workflow_path
        self.triggers = triggers
        self.additional_requirements = additional_requirements
        self.wf_parameters = wf_parameters

        self.first_steps = []


    def register_first_step(self, step: StepChainItem) -> StepChainItem:
        self.first_steps.append(step)
        return step

    def get_steps(self):
        steps: dict[str, SCIInfo] = {}

        scis_to_inspect: list[tuple[StepChainItem, str | None]] = [(sci, None) for sci in self.first_steps]

        while scis_to_inspect:
            sci, parent = scis_to_inspect.pop(0)

            if sci.step_id in steps:
                assert parent is not None
                steps[sci.step_id].depends_on.add(parent)
            elif parent is not None:
                steps[sci.step_id] = SCIInfo(sci, {parent})
            else:
                steps[sci.step_id] = SCIInfo(sci, set())

            for next_sro in sci._next_steps:
                scis_to_inspect.append((next_sro, sci.step_id))

        return steps


def workflow(workflow_path: str, triggers: list[Any] | None = None, additional_requirements: list[str] | None = None):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            wrapped_args = []
            wf_parameters = []

            for idx, arg in enumerate(inspect.signature(function).parameters.values()):
                wrapped_args.append(WfArgWrapper(value=arg.default, name=arg.name))

                if idx != 0:
                    def_val = arg.default if arg.default != inspect.Parameter.empty else None
                    wf_parameters.append(WorkflowParameter(name=arg.name, default_value=def_val))

            wfro = WorkflowRuntimeObject(
                workflow_path,
                triggers=triggers or [],
                additional_requirements=additional_requirements or [],
                wf_parameters=wf_parameters,
            )

            wrapped_args[0] = wfro

            step_chain_item = function(*wrapped_args)
            wfro.step_chain_item = step_chain_item
            return wfro

        wrapper.is_workflow = True
        return wrapper

    return decorator

import argparse
import shlex
import tempfile
import uuid
from collections import OrderedDict, defaultdict

from IPython.core.magic import magics_class, cell_magic, Magics, line_magic
from IPython.core.getipython import get_ipython

from orc_sdk.processor import process_python_file


@magics_class
class WorkflowMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        self.workflows = defaultdict(OrderedDict)

    @line_magic
    def clear_workflow(self, line):
        parser = argparse.ArgumentParser()
        parser.add_argument("wf_id", nargs="?", default=None)
        args = parser.parse_args(shlex.split(line))

        wf_id = args.wf_id if args.wf_id else "default"
        if wf_id in self.workflows:
            del self.workflows[wf_id]
            print(f"Workflow '{wf_id}' cleared.")
        else:
            print(f"Workflow '{wf_id}' does not exist.")


    @cell_magic
    def register_tasks(self, line, cell):
        parser = argparse.ArgumentParser()
        parser.add_argument("cell_id", nargs="?", default=uuid.uuid4().hex)
        parser.add_argument("wf_id", nargs="?", default="default")
        args = parser.parse_args(shlex.split(line))

        self.workflows[args.wf_id][args.cell_id] = cell
        get_ipython().run_cell(cell)


    @cell_magic
    def register_workflow(self, line, cell):
        parser = argparse.ArgumentParser()
        parser.add_argument("cell_id", nargs="?", default=uuid.uuid4().hex)
        parser.add_argument("wf_id", nargs="?", default="default")
        parser.add_argument("--debug-docker-build", action="store_true")
        args = parser.parse_args(shlex.split(line))

        self.workflows[args.wf_id][args.cell_id] = cell
        get_ipython().run_cell(cell)

        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(f"{tmp_dir}/workflow.py", "w") as tmp_f:
                for cell in self.workflows[args.wf_id].values():
                    tmp_f.write(cell)

            process_python_file(
                f"{tmp_dir}/workflow.py",
                docker_builder="wizard",
                debug_docker_build=args.debug_docker_build,
            )


def load_ipython_extension(ipython):
    ipython.register_magics(WorkflowMagics)

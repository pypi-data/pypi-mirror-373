import pathlib
import sys
import json

import clearskies
from clearskies_doc_builder import models, backends
from clearskies_doc_builder.build_callable import build_callable


def build(build_file_string: str) -> None:
    # We assume a folder structure here where the repo root contains a `src/` folder and a `docs/python` folder.
    # `build_file_string` should contain the absolute path to the file that kicked this off, which should
    # live in the `docs/python` folder.  This comes in as a string, which we convert to a path.
    # We then also need to calculate the path to the `src/` folder and add that to our
    # python path.  We do this because we want to import the clearskies module in question, since the python
    # code is where all of our documentation lives.

    doc_python_path = pathlib.Path(build_file_string).parents[0]
    project_root = doc_python_path.parents[1]
    sys.path.append(str(project_root / "src"))

    config_file = open(str(doc_python_path / "config.json"), "r")
    config = json.loads(config_file.read())
    config_file.close()

    cli = clearskies.contexts.Cli(
        build_callable,
        modules=[models, backends],
        bindings={
            "config": config,
            "project_root": project_root / "docs",
        },
    )
    cli()

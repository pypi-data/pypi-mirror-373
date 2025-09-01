import blueness
import bluer_ai
import bluer_algo
import bluer_options
import bluer_objects
import bluer_flow
import bluer_geo
import bluer_journal
import bluer_plugin
import bluer_sandbox
import bluer_sbc
import bluer_ugv
import vancouver_watching
from bluer_objects import README
import gizai


items = README.Items(
    [
        {
            "name": module.NAME,
            "marquee": module.MARQUEE,
            "description": " ".join(
                [
                    module.DESCRIPTION.replace(module.ICON, "").strip(),
                    " [![PyPI version](https://img.shields.io/pypi/v/{}.svg)](https://pypi.org/project/{}/)".format(
                        module.NAME, module.NAME
                    ),
                ]
            ),
            "url": f"https://github.com/kamangir/{module.REPO_NAME}",
        }
        for module in [
            bluer_ai,
            bluer_sbc,
            bluer_geo,
            bluer_ugv,
            bluer_algo,
            bluer_flow,
            vancouver_watching,
            bluer_journal,
            bluer_options,
            bluer_objects,
            bluer_plugin,
            bluer_sandbox,
            blueness,
            gizai,
        ]
    ]
)

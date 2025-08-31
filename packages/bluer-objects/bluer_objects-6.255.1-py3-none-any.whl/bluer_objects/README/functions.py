from typing import List, Dict, Union, Callable
import os
import yaml

from blueness import module

from bluer_objects import NAME as MY_NAME
from bluer_objects.metadata import get_from_object
from bluer_objects import file, env
from bluer_objects import markdown
from bluer_objects.README.utils import (
    apply_legacy,
    process_assets,
    process_details,
    process_envs,
    process_help,
    process_include,
    process_mermaid,
    process_objects,
    process_title,
    process_variable,
    signature,
    variables,
)
from bluer_objects.logger import logger

MY_NAME = module.name(__file__, MY_NAME)


def build(
    NAME: str,
    VERSION: str,
    REPO_NAME: str,
    items: List[str] = [],
    template_filename: str = "",
    filename: str = "",
    path: str = "",
    cols: int = 3,
    ICON: str = "",
    MODULE_NAME: str = "",
    macros: Dict[str, str] = {},
    help_function: Union[Callable[[List[str]], str], None] = None,
    legacy_mode: bool = True,
    assets_repo: str = "kamangir/assets",
) -> bool:
    if path:
        if path.endswith(".md"):
            filename = path
            template_filename = file.add_suffix(path, "template")
        else:
            filename = os.path.join(path, "README.md")
            template_filename = os.path.join(path, "template.md")

    if not MODULE_NAME:
        MODULE_NAME = REPO_NAME

    logger.info(
        "{}.build: {}-{}: {}[{}]: {} -{}> {}".format(
            MY_NAME,
            NAME,
            VERSION,
            REPO_NAME,
            MODULE_NAME,
            template_filename,
            "+legacy-" if legacy_mode else "",
            filename,
        )
    )

    table_of_items = markdown.generate_table(items, cols=cols) if cols > 0 else items

    success, template = file.load_text(template_filename)
    if not success:
        return success

    if legacy_mode:
        template = apply_legacy(template)

    content: List[str] = []
    mermaid_started: bool = False
    for template_line in template:
        if template_line.startswith("ignore:::"):
            content += [template_line.split(":::", 1)[1].strip()]
            continue

        template_line = process_envs(template_line)

        for key, value in variables.items():
            template_line = template_line.replace(
                f"get:::{key}",
                value,
            )

        if "metadata:::" in template_line:
            object_name_and_key = template_line.split("metadata:::", 1)[1]
            if " " in object_name_and_key:
                object_name_and_key = object_name_and_key.split(" ", 1)[0]
            if ":::" not in object_name_and_key:
                object_name_and_key += ":::"
            object_name, key = object_name_and_key.split(":::", 1)

            value = get_from_object(
                object_name,
                key,
                {},
                download=True,
            )

            logger.info(f"metadata[{object_name_and_key}] = {value}")

            if template_line.startswith("metadata:::"):
                content += (
                    ["```yaml"]
                    + yaml.dump(
                        value,
                        default_flow_style=False,
                    ).split("\n")
                    + ["```"]
                )
                continue

            template_line = template_line.replace(
                f"metadata:::{object_name}:::{key}",
                str(value),
            )

        if template_line.startswith("set:::"):
            process_variable(template_line)
            continue

        template_line = process_assets(template_line, assets_repo)

        template_line = process_objects(template_line)

        if template_line.startswith("details:::"):
            content += process_details(template_line)
            continue

        if "items:::" in template_line:
            content += table_of_items
            continue

        if "include:::" in template_line:
            content += process_include(
                template_line,
                file.path(template_filename),
            )
            continue

        if "signature:::" in template_line:
            content += signature(
                REPO_NAME,
                NAME,
                ICON,
                MODULE_NAME,
                VERSION,
            )
            continue

        if template_line.startswith("title:::"):
            success, updated_content = process_title(
                template_line,
                filename,
            )
            if not success:
                return success

            content += updated_content
            continue

        if "help:::" in template_line:
            if help_function is None:
                logger.error("help_function not found.")
                return False

            success, updated_content = process_help(
                template_line,
                help_function,
            )
            if not success:
                return success

            content += updated_content
            continue

        content_section = [template_line]
        if template_line.startswith("```mermaid"):
            mermaid_started = True
            logger.info("🧜🏽‍♀️  detected ...")
        elif mermaid_started and template_line.startswith("```"):
            mermaid_started = False
        elif mermaid_started:
            if '"' in template_line and ":::folder" not in template_line:
                content_section = process_mermaid(template_line)
        else:
            for macro, macro_value in macros.items():
                if macro in template_line:
                    content_section = macro_value
                    break

        content += content_section

    return file.save_text(filename, content)

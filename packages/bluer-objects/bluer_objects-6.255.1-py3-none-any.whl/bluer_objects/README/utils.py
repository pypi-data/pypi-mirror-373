import os
from typing import List, Dict, Union, Callable, Tuple

from bluer_options.env import get_env
from bluer_objects import file
from bluer_objects import env
from bluer_objects import NAME as MY_NAME, ICON as MY_ICON

from bluer_objects.logger import logger


variables: Dict[str, str] = {}


def apply_legacy_on_line(line: str) -> str:
    for before, after in {
        "yaml:::": "metadata:::",
        "--help--": "help:::",
        "--include": "include:::",
        "--table--": "items:::",
        "--signature--": "signature:::",
    }.items():
        line = line.replace(before, after)
    return line


def apply_legacy(template: List[str]) -> List[str]:
    logger.info("applying legacy conversions...")
    template = [apply_legacy_on_line(line) for line in template]
    return template


def process_assets(
    template_line: str,
    assets_repo: str,
) -> str:
    if "assets:::" in template_line:
        template_line = " ".join(
            [
                (
                    (
                        "![image](https://github.com/{}/blob/main/{}?raw=true)".format(
                            assets_repo,
                            token.split(":::")[1].strip(),
                        )
                        if any(
                            token.endswith(extension)
                            for extension in ["png", "jpg", "jpeg", "gif"]
                        )
                        else "[{}](https://github.com/{}/blob/main/{})".format(
                            file.name_and_extension(token.split(":::")[1].strip()),
                            assets_repo,
                            token.split(":::")[1].strip(),
                        )
                    )
                    if token.startswith("assets:::")
                    else token
                )
                for token in template_line.split(" ")
            ]
        )

    return template_line


def process_details(template_line: str) -> List[str]:
    suffix = template_line.split(":::", 1)[1]
    if suffix:
        content_section = [
            "",
            "<details>",
            f"<summary>{suffix}</summary>",
            "",
        ]
    else:
        content_section = [
            "",
            "</details>",
            "",
        ]

    return content_section


def process_envs(template_line: str) -> str:
    while "env:::" in template_line:
        env_name = template_line.split("env:::", 1)[1]
        if " " in env_name:
            env_name = env_name.split(" ", 1)[0]
        else:
            if ":::" in env_name:
                env_name = env_name.split(":::", 1)[0]

        env_value = get_env(env_name)

        template_line = template_line.replace(
            f"env:::{env_name}",
            env_value,
        )
        logger.info(f"{env_name} -> {env_value}")

    return template_line


def process_help(
    template_line: str,
    help_function: Union[Callable[[List[str]], str], None] = None,
) -> Tuple[bool, List[str]]:
    help_command = template_line.split("help:::")[1].strip()

    tokens = help_command.strip().split(" ")[1:]

    help_content = help_function(tokens)
    if not help_content:
        logger.error(f"help not found: {help_command}: {tokens}")
        return False, []

    logger.info(f"+= help: {help_command}")
    print(help_content)
    content_section = [
        "```bash",
        help_content,
        "```",
    ]

    return True, content_section


def process_include(
    template_line: str,
    template_path: str,
) -> List[str]:
    include_filename_relative = template_line.split(" ")[1].strip()
    include_filename = file.absolute(
        include_filename_relative,
        template_path,
    )

    success, content_section = file.load_text(include_filename)
    if not success:
        return success

    content_section = [
        line for line in content_section if not line.startswith("used by:")
    ]

    include_title = (template_line.split(" ", 2) + ["", "", ""])[2]
    if include_title:
        content_section = [f"## {include_title}"] + content_section[1:]

    if "include:::noref" not in template_line:
        content_section += [
            "using [{}]({}).".format(
                file.name(include_filename),
                include_filename_relative,
            )
        ]

    logger.info(f"{MY_NAME}.build: including {include_filename} ...")

    return content_section


def process_mermaid(template_line: str) -> List[str]:
    template_line_pieces = template_line.split('"')
    if len(template_line_pieces) != 3:
        logger.error(f"🧜🏽‍♀️  mermaid line not in expected format: {template_line}.")
        return False

    template_line_pieces[1] = (
        template_line_pieces[1]
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace(" ", "<br>")
        .replace("~~", " ")
    )

    return ['"'.join(template_line_pieces)]


def process_objects(template_line: str) -> str:
    if "object:::" in template_line:
        template_line = " ".join(
            [
                (
                    "[{}](https://{}.{}/{}.tar.gz)".format(
                        token.split(":::")[1].strip(),
                        env.S3_PUBLIC_STORAGE_BUCKET,
                        env.S3_STORAGE_ENDPOINT_URL.split("https://", 1)[1],
                        token.split(":::")[1].strip(),
                    )
                    if token.startswith("object:::")
                    else token
                )
                for token in template_line.split(" ")
            ]
        )

    return template_line


def process_title(
    template_line: str,
    filename: str,
) -> Tuple[bool, List[str]]:
    template_line_pieces = [
        piece for piece in template_line.strip().split(":::") if piece
    ]
    reference = template_line_pieces[1] if len(template_line_pieces) >= 2 else "docs"

    filename_path_pieces = file.path(filename).split(os.sep)
    if reference not in filename_path_pieces:
        logger.error(
            "reference: {} not found in {}.".format(
                reference,
                template_line,
            )
        )
        return False, []

    title_pieces = filename_path_pieces[filename_path_pieces.index(reference) + 1 :]
    filename_name = file.name(filename)
    if filename_name != "README":
        title_pieces.append(filename_name)

    return True, [
        "# {}".format(
            ": ".join(
                [
                    piece.replace(
                        "_",
                        "-",
                    )
                    for piece in title_pieces
                ]
            )
        )
    ]


def process_variable(template_line: str):
    key, value = template_line.split("set:::", 1)[1].split(" ", 1)
    variables[key] = value
    logger.info(f"{key} = {value}")


def signature(
    REPO_NAME: str,
    NAME: str,
    ICON: str,
    MODULE_NAME: str,
    VERSION: str,
) -> List[str]:
    return [
        "",
        " ".join(
            [
                f"[![pylint](https://github.com/kamangir/{REPO_NAME}/actions/workflows/pylint.yml/badge.svg)](https://github.com/kamangir/{REPO_NAME}/actions/workflows/pylint.yml)",
                f"[![pytest](https://github.com/kamangir/{REPO_NAME}/actions/workflows/pytest.yml/badge.svg)](https://github.com/kamangir/{REPO_NAME}/actions/workflows/pytest.yml)",
                f"[![bashtest](https://github.com/kamangir/{REPO_NAME}/actions/workflows/bashtest.yml/badge.svg)](https://github.com/kamangir/{REPO_NAME}/actions/workflows/bashtest.yml)",
                f"[![PyPI version](https://img.shields.io/pypi/v/{MODULE_NAME}.svg)](https://pypi.org/project/{MODULE_NAME}/)",
                f"[![PyPI - Downloads](https://img.shields.io/pypi/dd/{MODULE_NAME})](https://pypistats.org/packages/{MODULE_NAME})",
            ]
        ),
        "",
        "built by {} [`{}`]({}), based on {}[`{}-{}`]({}).".format(
            MY_ICON,
            "bluer README",
            "https://github.com/kamangir/bluer-objects/tree/main/bluer_objects/README",
            f"{ICON} " if ICON else "",
            NAME,
            VERSION,
            f"https://github.com/kamangir/{REPO_NAME}",
        ),
    ]

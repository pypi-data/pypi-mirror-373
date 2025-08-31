from PIL import Image
from tqdm import tqdm
from typing import List

from blueness import module
from bluer_options.logger import crash_report

from bluer_objects import NAME
from bluer_objects.logger import logger


NAME = module.name(__file__, NAME)


def generate_animated_gif(
    list_of_images: List[str],
    output_filename: str,
    frame_duration: int = 150,
    scale: int = 1,
    log: bool = True,
) -> bool:
    if not list_of_images:
        return True

    max_width = 0
    max_height = 0
    frames = []
    for filename in tqdm(list_of_images):
        image = Image.open(filename)

        frames.append(image)

        width, height = image.size
        max_width = max(max_width, width)
        max_height = max(max_height, height)

    padded_frames = []
    for image in frames:
        padded_image = Image.new(
            "RGB",
            (max_width, max_height),
            (255, 255, 255),
        )

        width, height = image.size
        left_pad = (max_width - width) // 2
        top_pad = (max_height - height) // 2
        padded_image.paste(image, (left_pad, top_pad))

        if scale != 1:
            padded_image = padded_image.resize(
                (max_width // scale, max_height // scale),
                Image.Resampling.LANCZOS,
            )

        padded_frames.append(padded_image)

    success = True
    try:
        padded_frames[0].save(
            output_filename,
            save_all=True,
            append_images=padded_frames[1:],
            duration=frame_duration,
            loop=0,  # 0 means infinite loop
        )
    except Exception:
        success = False

    message = "{}.generate_animated_gif({}x{}x{}) -scale={}-> {} @ {:.2f}ms".format(
        NAME,
        len(list_of_images),
        height,
        width,
        scale,
        output_filename,
        frame_duration,
    )

    if success:
        if log:
            logger.info(message)
        return True

    crash_report(message)
    return False

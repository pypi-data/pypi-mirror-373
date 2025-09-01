from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from highlighter.core.exceptions import require_package

try:
    import cv2
except ModuleNotFoundError as _:
    cv2 = None

from highlighter.core.const import OBJECT_CLASS_ATTRIBUTE_UUID

__all__ = [
    "draw_text",
    "draw_annotated_box",
    "draw_annotated_boxes",
    "draw_masks_on_image",
    "draw_polys_on_image",
    "draw_annotations_on_image",
]


def _to_pil_image_as_needed(pil_or_np_image):
    if isinstance(pil_or_np_image, np.ndarray):
        image_copy = Image.fromarray(pil_or_np_image)
    elif isinstance(pil_or_np_image, Image.Image):
        image_copy = pil_or_np_image.copy()
    else:
        raise ValueError(f"Invalide image type: {type(pil_or_np_image)}")
    return image_copy


def draw_annotations_on_image(pil_or_np_image, annotations):

    boxes = []
    labels = []
    confidences = []
    for anno in annotations:

        boxes.append(anno.location.bounds)
        object_class_obs = anno.observations_where(attribute_id=OBJECT_CLASS_ATTRIBUTE_UUID)[0]
        if object_class_obs is not None:
            labels.append(
                anno.observations_where(attribute_id=OBJECT_CLASS_ATTRIBUTE_UUID)[0].value.short_str()
            )
        else:
            labels.append("")
        confidences.append(anno.datum_source.confidence)

    image_copy = _to_pil_image_as_needed(pil_or_np_image)
    return draw_annotated_boxes(image_copy, labels, boxes, confidences=confidences)


def draw_polys_on_image(pil_or_np_image, polys, labels: Optional[List[Optional[str]]] = None):
    """

    Args:
        polys: [[(x0,y0), ... (xn,yn)], ...]
        labels: [str, None, str, str] or None
    """
    if labels is None:
        labels = [None for _ in polys]

    assert len(labels) == len(polys)

    image_copy = _to_pil_image_as_needed(pil_or_np_image)

    # Create a drawing context
    draw = ImageDraw.Draw(image_copy)

    # Define the box color (you can change this if you prefer a different color)
    box_color = "red"  # Change this to the color of your choice

    # Draw rectangles for each box
    for poly, label in zip(polys, labels):
        try:
            draw.polygon(poly, outline=box_color, width=1)
        except ValueError as e:
            raise ValueError(f"{e}. Check each coordinate is a tuple, got {poly}")

    return image_copy


@require_package(cv2, "cv2", "opencv")
def draw_masks_on_image(image, masks, labels=None):
    """
    Draw boolean masks on the image with 10% transparency.

    Args:
        image (numpy.ndarray): Input image.
        masks (list of numpy.ndarray): List of boolean masks to draw.

    Returns:
        numpy.ndarray: Image with masks drawn.
    """
    # Convert image to RGBA format
    image_rgba = cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)

    # Set transparency level (alpha channel) to 10%
    alpha = int(0.1 * 255)

    # Iterate through masks
    for mask in masks:
        # Convert boolean mask to uint8
        mask_uint8 = mask.astype(np.uint8) * 255

        # Create RGBA mask
        mask_rgba = cv2.cvtColor(mask_uint8, cv2.COLOR_GRAY2BGRA)

        # Set transparency level
        mask_rgba[:, :, 3] = alpha

        # Combine mask with image
        image_rgba = cv2.addWeighted(image_rgba, 1, mask_rgba, 1, 0)

    image_rgb = cv2.cvtColor(image_rgba, cv2.COLOR_RGBA2RGB)

    return image_rgb


BOX_XYXY = Tuple[int, int, int, int]
FONT = str(Path(__file__).parent / "DejaVuSans.ttf")
LINE_WEIGHT_SCALE = 0.004  # Just eyeballed this magic number
RGB = Tuple[int, int, int]
RGB_WHITE = (255, 255, 255)
TEXT_SIZE_SCALE = 0.02  # Just eyeballed this magic number
XY = Tuple[int, int]

label_colourer = None
label_to_color = {}


def draw_annotated_boxes(
    pil_img: Image.Image,
    labels: List[str],
    bboxes: List[BOX_XYXY],
    color_map: Optional[Dict[str, RGB]] = None,
    confidences: Optional[List[float]] = None,
):
    # print(f"boxes: {bboxes}")
    """Draw a list of boxes and labels onto an image"""
    global label_to_color, label_colourer

    if (color_map is None) and (label_colourer is None):
        # If no color_map is provided we instantiate the
        # label_colourer
        label_colourer = LabelColourer(as_int=True)
    elif color_map is not None:
        label_to_color = color_map

    if confidences is None:
        confidences = [None] * len(labels)

    for bbox, label, conf in zip(bboxes, labels, confidences):
        if label in label_to_color:
            color = label_to_color[label]
        elif color_map is not None:
            # Color map is set but a label cannot be found
            raise ValueError(f"'{label}' is not in color_map: '{color_map}'")
        else:
            color = label_colourer[label]
            label_to_color[label] = color

        pil_img = draw_annotated_box(pil_img, label, bbox, confidence=conf, color=color)
        # print(f"{label} - {bbox} - {conf} - {color}")
    return pil_img


def draw_annotated_box(
    pil_img: Image.Image,
    label: str,
    bbox: BOX_XYXY,
    confidence: Optional[float] = None,
    color: RGB = (209, 239, 8),
):
    image_height = pil_img.size[1]
    draw = ImageDraw.Draw(pil_img)
    # font = ImageFont.load_default()
    draw.rectangle(
        (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])),
        width=int(LINE_WEIGHT_SCALE * image_height),
        outline=color,
    )

    if confidence is not None:
        label = f"{label}: {confidence:0.2f}"

    pil_img = draw_text(
        pil_img,
        label,
        (bbox[0], bbox[1]),
        text_color=color,
        bg_color=(0, 0, 0),
    )

    return pil_img


def draw_text(
    pil_img,
    text: str,
    bottom_left: XY,
    text_color: RGB = RGB_WHITE,
    bg_color: Optional[RGB] = None,
):
    image_height = pil_img.size[1]
    draw = ImageDraw.Draw(pil_img)

    fontsize = 1
    font = ImageFont.truetype(FONT, fontsize)

    # Fn the get the full bbox of a string including multiline strings
    def get_text_wh(text, font):
        text_height = 0
        text_width = []
        for line in text.split("\n"):
            # Add \n back in because it effects the height of the textbox
            # by accounting for the space between the lines
            _line = f"{line}\n"
            text_height += font.getbbox(_line)[3] - font.getbbox(_line)[1]
            text_width.append(font.getbbox(_line)[2] - font.getbbox(_line)[0])

        return max(text_width), text_height

    # Loop over some text to get a scaled text height
    # we're only interested in the hight of a single line
    # of text so we pass a dummy string as opposed to the
    # actual text argument
    while get_text_wh("dummy text", font)[1] < (image_height * TEXT_SIZE_SCALE):
        fontsize += 1
        font = ImageFont.truetype(FONT, fontsize)

    # Here we're interested in the bbox containing the whole
    # text so we pass the text argument not a dummpy string
    text_w, text_h = get_text_wh(text, font)

    offset = max(int(text_h * 0.04), 2)

    # We draw the text on top of the bounding box.
    # This means the top_left of the bounding box is
    # the bottom left of the text box.
    #
    #               --------------
    #               |x0,y0       |x1,y0
    #   text_box    |            |
    #               |x0,y1       |x1,y1
    #               -----------------------
    #               |bottom_left          |
    #               |                     |
    #    bbox       |                     |
    #               |                     |
    #               |                     |
    #               -----------------------
    x0 = int(bottom_left[0])
    y1 = int(bottom_left[1])

    x1 = int(x0 + text_w + (2 * offset))
    y0 = int(y1 - text_h - (2 * offset))

    if bg_color is not None:
        draw.rectangle(
            (x0, y0, x1, y1),
            width=1,
            outline=bg_color,
            fill=bg_color,
        )

    draw.text(
        (int(x0 + offset), int(y0 + offset)),
        text,
        fill=text_color,
        font=font,
    )
    return pil_img


class _CMAP_Tab20:
    """Equivalent to matplotlib.cm.tab20(i)"""

    _cmap = [
        (
            0.12156862745098039,
            0.4666666666666667,
            0.7058823529411765,
            1.0,
        ),
        (
            0.6823529411764706,
            0.7803921568627451,
            0.9098039215686274,
            1.0,
        ),
        (1.0, 0.4980392156862745, 0.054901960784313725, 1.0),
        (1.0, 0.7333333333333333, 0.47058823529411764, 1.0),
        (
            0.17254901960784313,
            0.6274509803921569,
            0.17254901960784313,
            1.0,
        ),
        (
            0.596078431372549,
            0.8745098039215686,
            0.5411764705882353,
            1.0,
        ),
        (
            0.8392156862745098,
            0.15294117647058825,
            0.1568627450980392,
            1.0,
        ),
        (1.0, 0.596078431372549, 0.5882352941176471, 1.0),
        (
            0.5803921568627451,
            0.403921568627451,
            0.7411764705882353,
            1.0,
        ),
        (
            0.7725490196078432,
            0.6901960784313725,
            0.8352941176470589,
            1.0,
        ),
        (
            0.5490196078431373,
            0.33725490196078434,
            0.29411764705882354,
            1.0,
        ),
        (
            0.7686274509803922,
            0.611764705882353,
            0.5803921568627451,
            1.0,
        ),
        (
            0.8901960784313725,
            0.4666666666666667,
            0.7607843137254902,
            1.0,
        ),
        (
            0.9686274509803922,
            0.7137254901960784,
            0.8235294117647058,
            1.0,
        ),
        (
            0.4980392156862745,
            0.4980392156862745,
            0.4980392156862745,
            1.0,
        ),
        (
            0.7803921568627451,
            0.7803921568627451,
            0.7803921568627451,
            1.0,
        ),
        (
            0.7372549019607844,
            0.7411764705882353,
            0.13333333333333333,
            1.0,
        ),
        (
            0.8588235294117647,
            0.8588235294117647,
            0.5529411764705883,
            1.0,
        ),
        (
            0.09019607843137255,
            0.7450980392156863,
            0.8117647058823529,
            1.0,
        ),
        (
            0.6196078431372549,
            0.8549019607843137,
            0.8980392156862745,
            1.0,
        ),
    ]
    N = len(_cmap)

    def __call__(self, i):
        return self._cmap[i]


_cmap_tab20 = _CMAP_Tab20()


def LabelColourer(cmap=None, as_int=False, consistent_by_key=True):  # noqa: N802
    """Returns a default dict where the default value is generated
    by the get_colour function.

    It simply iterates a counter and gets the next color from cmap.
    By default returns a float, but can also cast as_int.

    If consistent_by_key is True then the same key will produce the
    same colour each time the function is called. Even if it's called
    from a different process.
    """

    cmap = _cmap_tab20 if cmap is None else cmap

    # Get a color from cmap, convert to int rbg as needed
    # if idx is passed then use it otherwise update count and
    # use that number instead.
    def get_colour(idx=None):
        if idx is None:
            get_colour.count += 1
            *rgb, _ = cmap(get_colour.count % cmap.N)
        else:
            *rgb, _ = cmap(idx % cmap.N)
        if as_int:
            rgb = [int(255 * i) for i in rgb]
        return tuple(rgb)

    if consistent_by_key:

        def default_fatcory(key):
            # Sum the characters in the key by their position in
            # the ascii table
            idx = sum([ord(c) for c in key])

            # ToDo: check if there is a color clash, if there are remaining
            # colors increment by one untill you find a unique one.

            return get_colour(idx=idx)

        class KeyDependantDefaultDict(defaultdict):
            def __missing__(self, key):
                return default_fatcory(str(key))

        dd = KeyDependantDefaultDict(default_fatcory)
    else:
        get_colour.count = -1
        dd = defaultdict(get_colour)

    return dd


def overlay_images(base_image, overlay_image, where: str = "bottom-right", alpha=0.9):
    """
    Overlay one RGB image onto another with specified alpha transparency using NumPy,
    placing the overlay at the bottom-right corner.

    Args:
        base_image: NumPy array (H, W, 3) for RGB base image
        overlay_image: NumPy array (H', W', 3) for RGB overlay image, smaller than base
        alpha: Float between 0.0 and 1.0 for overlay transparency

    Returns:
        NumPy array (H, W, 3) with the overlay applied at bottom-right
    """
    # Validate input
    if base_image.shape[2] != 3 or overlay_image.shape[2] != 3:
        raise ValueError(
            f"Both images must be RGB with 3 channels, got: base_image.shape = {base_image.shape}, overlay_image.shape = {overlay_image.shape}"
        )
    if overlay_image.shape[0] > base_image.shape[0] or overlay_image.shape[1] > base_image.shape[1]:
        raise ValueError(
            "Overlay image must be smaller than base image, got: base_image.shape = {base_image.shape}, overlay_image.shape = {overlay_image.shape}"
        )

    # Convert to float32 for calculations
    base = base_image.astype(np.float32) / 255.0
    overlay = overlay_image.astype(np.float32) / 255.0

    # Create padded overlay with zeros (black background)
    padded_overlay = np.zeros_like(base, dtype=np.float32)

    # Calculate bottom-right position
    if where == "top-right":
        _, base_w = base.shape[:2]
        overlay_h, overlay_w = overlay.shape[:2]
        start_h = 0
        start_w = base_w - overlay_w
    elif where == "bottom-left":
        base_h, _ = base.shape[:2]
        overlay_h, overlay_w = overlay.shape[:2]
        start_h = base_h - overlay_h
        start_w = 0
    elif where == "top-left":
        overlay_h, overlay_w = overlay.shape[:2]
        start_h = 0
        start_w = 0
    else:
        # Default to bottom-right
        base_h, base_w = base.shape[:2]
        overlay_h, overlay_w = overlay.shape[:2]
        start_h = base_h - overlay_h
        start_w = base_w - overlay_w

    # Place overlay in the bottom-right corner
    padded_overlay[start_h : start_h + overlay_h, start_w : start_w + overlay_w] = overlay

    # Create alpha channels
    overlay_alpha = np.zeros(base.shape[:2], dtype=np.float32)
    overlay_alpha[start_h : start_h + overlay_h, start_w : start_w + overlay_w] = alpha

    # Blend RGB channels using simplified alpha compositing
    out_rgb = padded_overlay * overlay_alpha[..., None] + base * (1 - overlay_alpha[..., None])

    # Convert back to uint8 RGB
    return (np.clip(out_rgb, 0, 1) * 255).astype(np.uint8)


def overlay_pyplot_fig(base_image: np.ndarray, fig, where="bottom-right", alpha=0.9):
    import io

    # Convert to image
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor="black", edgecolor="none", bbox_inches="tight", pad_inches=0.05)
    buf.seek(0)

    plot_img = np.array(Image.open(buf))[..., :3]
    return overlay_images(base_image, plot_img, where=where, alpha=alpha)

import errno
from pathlib import Path

try:
    import cv2
except ImportError:  # pragma: no cover
    msg = [
        "Please install one of the following:",
        "pip install opencv-python                   # the most popular",
        "pip install opencv-python-headless          # the most popular, without GUI functionality (for servers)",
        "pip install opencv-contrib-python           # extended functionality",
        "pip install opencv-contrib-python-headless  # extended functionality, without GUI functionality (for servers)",
    ]
    raise ImportError("\n\t".join(msg))

import numpy as np
import PIL.Image
from cv2 import cvtColor as __cv2_cvtColor
from cv2 import imwrite as __cv2_imwrite
from numpy import array as __np_array
from numpy import ndarray as __np_ndarray

__PIL_Image_open = PIL.Image.open
__PIL_Image_Image = PIL.Image.Image

from katalytic._pkg import _UNDEFINED, KatalyticInterrupt, mark
from katalytic.data.checks import is_iterable, is_number, is_sequence


def bhwc(arr):
    """
    Returns a tuple representing the shape of the input array in the BHWC format: batch, height, width, and channels. The missing dimensions are filled with 1s.

    Parameters:
        arr (numpy.ndarray): The input array.

    Returns:
        tuple: A tuple representing the shape of the input array in the BHWC format.

    Raises:
        ValueError: If the input array has 5 or more dimensions.

    """
    if arr.shape == (0,):
        return (0, 0, 0, 0)
    elif arr.ndim == 1:
        return (1, *arr.shape, 1, 1)
    elif arr.ndim == 2:
        return (1, *arr.shape, 1)
    elif arr.ndim == 3:
        return (1, *arr.shape)
    elif arr.ndim == 4:
        return arr.shape
    else:
        raise ValueError(f"arr.ndim = {arr.ndim}")


def convert_image(image, before, after):
    """
    Converts an image from one color space to another.

    Parameters:
        image: The input image to be converted. It can be either a NumPy array or a PIL Image object.
        before (str): The color space of the input image. It should be a string representing a valid color space, e.g., 'RGB', 'BGR', 'GRAY'.
        after (str): The desired color space of the output image. It should be a string representing a valid color space.

    Returns:
        The converted image as either a NumPy array or a PIL Image object, depending on the type of the input image.

    Raises:
        TypeError: If the 'before' or after' parameters are not a string.
        ValueError: If the conversion code is not found for the specified color space conversion.

    """
    if not isinstance(before, str):
        raise TypeError(f"type(before) = {type(before)!r}")
    elif not isinstance(after, str):
        raise TypeError(f"type(after) = {type(after)!r}")

    return_PIL = isinstance(image, PIL.Image.Image)
    if return_PIL:
        image = np.array(image)
    else:
        image = load_image(image)

    conversion_code = f"COLOR_{before}2{after}"
    conversion_code = conversion_code.replace("gray", "GRAY")
    conversion_code = getattr(cv2, conversion_code, None)

    if conversion_code is not None:
        img = __cv2_cvtColor(image, conversion_code)
    elif before.startswith("binary") or after.startswith("binary"):
        raise NotImplementedError
    else:
        raise ValueError

    if return_PIL:
        return PIL.Image.fromarray(img)
    else:
        return img


def create_line(p1, p2, color, *, thickness=3, **kwargs):
    """
    Create a dict representing a line shape to be used by draw()() or draw_inplace().

    Parameters:
        p1 (tuple or list): The (x, y) coordinates of the first point.
        p2 (tuple or list): The (x, y) coordinates of the second point.
        color: The color of the line. It can be specified in various formats supported by the underlying drawing library.
        thickness (int): The thickness of the line. Defaults to 3.
        **kwargs: Additional keyword arguments that can be used to customize the shape.

    Returns:
        dict: A dictionary representing the line to be drawn

    """
    return {
        "type": "line",
        "p1": tuple(map(int, p1)),
        "p2": tuple(map(int, p2)),
        "color": color,
        "thickness": thickness,
        **kwargs,
    }


def create_circle(center, radius, color, *, thickness=3, **kwargs):
    """
    Create a dict representing a circle shape to be used by draw()() or draw_inplace().

    Parameters:
        center (tuple or list): The (x, y) coordinates of the center.
        radius (int): The radius of the circle.
        color: The color of the circle. It can be specified in various formats supported by the underlying drawing library.
        thickness (int): The thickness of the circle. Use -1 to fill it up. Defaults to 3.
        **kwargs: Additional keyword arguments that can be used to customize the circle object.

    Returns:
        dict: A dictionary representing the circle to be drawn

    """
    return {
        "type": "circle",
        "center": tuple(map(int, center)),
        "radius": int(radius),
        "color": color,
        "thickness": thickness,
        **kwargs,
    }


def create_rectangle(p1, p2, color, *, thickness=3, **kwargs):
    """
    Create a dict representing a rectangle shape to be used by draw()() or draw_inplace().

    Parameters:
        p1 (tuple or list): The (x, y) coordinates of the top left corner.
        p2 (tuple or list): The (x, y) coordinates of the bottom right corner.
        color: The color of the rectangle. It can be specified in various formats supported by the underlying drawing library.
        thickness (int): The thickness of the line. Use -1 to fill it up. Defaults to 3.
        **kwargs: Additional keyword arguments that can be used to customize the shape.

    Returns:
        dict: A dictionary representing the rectangle to be drawn

    """
    return {
        "type": "rectangle",
        "p1": tuple(map(int, p1)),
        "p2": tuple(map(int, p2)),
        "color": color,
        "thickness": thickness,
        **kwargs,
    }


def create_text(
    text, origin, color, *, font=cv2.FONT_HERSHEY_SIMPLEX, scale=1.25, thickness=3, bg=None, bg_pad=None, **kwargs
):
    """Create a text shape.
    The text shape represents a text string with its origin point, color, font, scale, and thickness. It can also include a background rectangle behind the text.

    Parameters:
        text (str): The text string to be displayed.
        origin (tuple or list): The (x, y) coordinates of the origin point.
        color: The color of the text. It can be specified in various formats supported by the underlying drawing library.
        font: The font to be used for the text. Defaults to cv2.FONT_HERSHEY_SIMPLEX.
        scale (float): The scale factor for the font size. Defaults to 1.25.
        thickness (int): The thickness of the text. Defaults to 3.
        bg: The color of the background rectangle behind the text. If None, no background rectangle will be created. It can be specified in various formats supported by the underlying drawing library.
        bg_pad: The padding for the background rectangle. It can be specified as a single number, a sequence of two numbers for horizontal and vertical padding, or a sequence of four numbers for left, top, right, and bottom padding. Defaults to None.
        **kwargs: Additional keyword arguments that can be used to customize the text shape.

    Returns:
        dict: A dictionary representing the text shape to be drawn

    Raises:
        ValueError: If the 'bg' parameter is None, but the 'bg_pad' parameter is set to a value.
        ValueError: If the 'bg_pad' parameter has an invalid format.
        TypeError: If the 'bg_pad' parameter has an unsupported type.

    """
    shape = {
        "type": "text",
        "text": text,
        "origin": tuple(map(int, origin)),
        "color": color,
        "font": font,
        "font_scale": scale,
        "thickness": thickness,
        **kwargs,
    }

    if bg is None:
        if bg_pad is None:
            return shape
        else:
            # bg_pad is set to None by default instead of 5 ot alert the user
            # when he sets <bg_pad> and forgets <bg>.
            # Otherwise the mistake would be ignored silently
            raise ValueError("<bg> is None, even though <bg_pad> is set to a value")

    if bg_pad is None:
        bg_pad = [5] * 4
    elif is_number(bg_pad):
        bg_pad = [bg_pad] * 4
    elif is_sequence(bg_pad):
        if len(bg_pad) == 2:
            bg_pad = [*bg_pad, *bg_pad]
        elif len(bg_pad) != 4:
            raise ValueError(
                f"<bg_pad> expects None, a number or a sequence like (horizontal, vertical) or (left, top, right, bottom). Got a sequence of length {len(bg_pad)}"
            )
    else:
        raise TypeError(f"type(bg_pad) = {type(bg_pad)!r}")

    shape["background"] = {"color": bg, "pad": bg_pad}
    return shape


def create_polylines(pts, color, *, thickness=3, is_closed=True, **kwargs):
    """
    Create a dict representing a polylines shape to be used by draw() or draw_inplace().

    Parameters:
        pts (list or ndarray): The points of the polylines as a list of tuples or an ndarray of shape (N, 2), representing the (x, y) coordinates.
        color: The color of the polylines. It can be specified in various formats supported by the underlying drawing library.
        thickness (int): The thickness of the polylines. Use -1 to fill it up. Defaults to 3.
        is_closed (bool): A flag indicating whether the polylines should be closed or not. Defaults to True.
        **kwargs: Additional keyword arguments that can be used to customize the polylines object.

    Returns:
        dict: A dictionary representing the polylines to be drawn

    """
    return {"type": "polylines", "pts": pts, "color": color, "thickness": thickness, "is_closed": is_closed, **kwargs}


def create_mask(pts, color, **kwargs):
    """
    Create a dict representing a mask shape to be used by draw() or draw_inplace().

    Parameters:
        pts (list or ndarray): The points of the polylines as a list of tuples or an ndarray of shape (N, 2), representing the (x, y) coordinates.
        color: The color of the polylines. It can be specified in various formats supported by the underlying drawing library.
        **kwargs: Additional keyword arguments that can be used to customize the polylines object.

    Returns:
        dict: A dictionary representing the mask to be drawn

    """
    return {"type": "mask", "pts": pts, "color": color, **kwargs}


def draw(image, data):
    """Draws shapes on a copy of the input image

    This function takes an image and an collection specifying the shapes to be drawn on the image.
    The shapes can include lines, circles, rectangles, text, masks, and polylines.
    The calls the corresponding drawing functions for each shape in the order it appears in the collection.

    Parameters:
        image: a numpy array representing the image on which the shapes will be drawn.
        data:
            The shapes to be drawn. It can be either a dictionary representing a single shape
            or a list of dictionaries representing multiple shapes.

    Raises:
        TypeError: If the 'data' parameter is not an iterable of shapes or a dict
        KeyError: If the 'type' key is missing in any shape dictionary.
        ValueError: If the 'type' key in any shape dictionary has an invalid value.
        ValueError: If the 'pts' key in a mask or polylines shape dictionary has an invalid format.

    """
    if isinstance(image, __PIL_Image_Image):
        new_image = np.array(image)
        return_PIL = True
    else:
        new_image = image.copy()
        return_PIL = False

    draw_inplace(new_image, data)

    if return_PIL:
        return PIL.Image.fromarray(new_image)
    else:
        return new_image


def draw_inplace(image, data):
    """Draws shapes on the input image by modifying it in-place

    This function takes an image and an collection specifying the shapes to be drawn on the image.
    The shapes can include lines, circles, rectangles, text, masks, and polylines.
    The calls the corresponding drawing functions for each shape in the order it appears in the collection.

    Parameters:
        image: a numpy array representing the image on which the shapes will be drawn.
        data: The shapes to be drawn. It can be either a dictionary representing a single shape or a list of dictionaries representing multiple shapes.

    Raises:
        TypeError: If the 'data' parameter is not an iterable of shapes or a dict
        KeyError: If the 'type' key is missing in any shape dictionary.
        ValueError: If the 'type' key in any shape dictionary has an invalid value.
        ValueError: If the 'pts' key in a mask or polylines shape dictionary has an invalid format.

    """
    if isinstance(data, dict):
        data = [data]
    elif not is_iterable(data):
        raise TypeError(f"type(data) = {type(data)!r}")

    for shape in data:
        draw_shape = _pick_draw_function(shape["type"])
        shape = _rename_kwargs(shape)

        if shape["type"] == "text":
            # extract background info only after the call to _rename_kwargs()
            # Otherwise you might miscalculate the bg size and position
            bg = _create_rectangle_for_text_background(shape.pop("background", None), shape)
            if bg:
                draw_inplace(image, bg)
        elif shape["type"] in ("mask", "polylines"):
            pts = shape["pts"]
            if is_iterable(pts):
                if not is_iterable(pts[0][0]):
                    pts = [pts]

            if not isinstance(pts, np.ndarray):
                pts = np.array(pts, dtype=np.int32)
            elif pts.dtype != np.int32:
                pts = pts.astype(np.int32)

            shape["pts"] = pts

        del shape["type"]
        draw_shape(image, **shape)


def _create_rectangle_for_text_background(bg, text):
    """Create a rectangle to act as background for the text.

    Parameters:
        bg: The background information for the text shape. It can be specified as a color value, a dictionary with color and padding information, or None if no background is required.
        text: The properties of the text shape. It should be a dictionary containing the text, font face, font scale, thickness, and origin information.

    Returns:
        dict or None: A dictionary representing the background rectangle for the text shape. If no background is required, None is returned.

    Raises:
        TypeError: If the 'bg' parameter has an invalid type.
        ValueError: If the 'pad' value has an invalid format.

    """
    if not bg:
        return None

    if is_sequence(bg) or is_number(bg):
        color = bg
        pad = 5 * text["fontScale"]
    elif isinstance(bg, dict):
        color = bg.pop("color")
        pad = bg.pop("pad", 5 * text["fontScale"])
    else:
        raise TypeError(f"type(background) = {type(bg).__name__!r}")

    error_msg = f"Expected <pad> to be an int or a sequence like (horizontal, vertical) or (left, top, right, bottom). Got {pad!r}"

    if is_number(pad):
        pad = (pad, pad, pad, pad)
    elif is_sequence(pad):
        if len(pad) == 2:
            pad = (*pad, *pad)
        elif len(pad) == 4:
            pass
        else:
            raise ValueError(error_msg)
    else:
        raise ValueError(error_msg)

    kwargs = {k: text[k] for k in ["text", "fontFace", "fontScale", "thickness"]}
    (w, h), baseline = cv2.getTextSize(**kwargs)
    baseline += text["thickness"] * text["fontScale"]
    if text.get("bottomLeftOrigin", False):
        raise NotImplementedError("Calculate baseline for bottomLeftOrigin=True")

    p1 = (text["org"][0] - pad[0], text["org"][1] - h - pad[1])
    p2 = (text["org"][0] + w + pad[2], text["org"][1] + baseline + pad[3])
    return create_rectangle(p1, p2, color, thickness=-1)


def _rename_kwargs(shape):
    """Rename the keys to match the corresponding OpenCV function parameters."""
    conversion = {
        "font": "fontFace",
        "font_scale": "fontScale",
        "line_type": "lineType",
        "draw_above_origin": "bottomLeftOrigin",
        "p1": "pt1",
        "p2": "pt2",
        "origin": "org",
        "is_closed": "isClosed",
    }

    return {conversion.get(k, k): v for k, v in shape.items()}


def _pick_draw_function(shape_type):
    """Pick the corresponding OpenCV drawing function based on the shape type."""
    fn = {
        "arrowed_line": cv2.arrowedLine,
        "circle": cv2.circle,
        "contours": cv2.drawContours,
        "convex_polygon": cv2.fillConvexPoly,
        "ellipse": cv2.ellipse,
        "ellipse_polygon": cv2.ellipse2Poly,
        "line": cv2.line,
        "marker": cv2.drawMarker,
        "mask": cv2.fillPoly,
        "polylines": cv2.polylines,
        "rectangle": cv2.rectangle,
        "text": cv2.putText,
    }

    if shape_type not in fn:
        raise ValueError(f"Unknown shape: {shape_type!r}")
    else:
        return fn[shape_type]


@mark("load::png")
@mark("load::jpg")
@mark("load::jpeg")
def load_image(image, mode=None, *, default=_UNDEFINED):
    """
    Load an image and return it as a NumPy array.

    Parameters:
        image: The image to be loaded. It can be specified as a file path (string or Path object), a PIL Image object, or a NumPy array.
        mode (str, optional): The mode to be used when loading the image. It should be a string representing the desired mode, e.g., 'RGB', 'L', 'RGBA'. If None, the default mode of the image will be used.
        default (Any):
            The default value to return if the specified file path does not exist.

    Returns:
        numpy.ndarray: The loaded image as a NumPy array.

    Raises:
        TypeError: If the 'mode' parameter is not None or a string.
        TypeError: If the 'image' parameter has an unsupported type.

    """
    if not (mode is None or isinstance(mode, str)):
        raise TypeError(f"mode expected None or str. Got {type(mode)!r}")

    if isinstance(image, (str, Path)):
        # noinspection PyProtectedMember
        from katalytic.files import (
            _load_funcs,
            _warn_if_another_function_should_be_used,
        )

        _warn_if_another_function_should_be_used(str(image), _load_funcs)
        if not Path(image).exists() and default is not _UNDEFINED:
            return default
        else:
            return __np_array(__PIL_Image_open(image))
    elif isinstance(image, __PIL_Image_Image):
        return image.copy()
    elif isinstance(image, __np_ndarray):
        return image.copy()
    else:
        raise TypeError(f"type(image) = {type(image)!r}")


def hwc(arr):
    """
    Returns a tuple representing the shape of the input array in the HWC format: height, width, and channels. The missing dimensions are filled with 1s.

    Parameters:
        arr (numpy.ndarray): The input array.

    Returns:
        tuple: A tuple representing the shape of the input array in the HWC format.

    Raises:
        ValueError: If the input array has 5 or more dimensions.

    """
    return bhwc(arr)[1:]


def hw(arr):
    """
    Returns a tuple representing the shape of the input array in the HW format: height and width. The missing dimensions are filled with 1s.

    Parameters:
        arr (numpy.ndarray): The input array.

    Returns:
        tuple: A tuple representing the shape of the input array in the HW format.

    Raises:
        ValueError: If the input array has 5 or more dimensions.

    """
    return bhwc(arr)[1:3]


def are_arrays_equal(image_1, image_2, check_type=False):
    """
    Check if two images represented as NumPy arrays are equal.
    The equality comparison is performed based on the shape and optionally the data type of the arrays.

    Parameters:
        image_1: The first image to compare. It can be specified as a file path (string or Path object), a PIL Image object, or a NumPy array.
        image_2: The second image to compare. It can be specified as a file path (string or Path object), a PIL Image object, or a NumPy array.
        check_type (bool, optional): A flag indicating whether to perform an additional check on the data type of the arrays. If True, the data type of the arrays must also match for the arrays to be considered equal. Defaults to False.

    Returns:
        bool: True if the images are equal, False otherwise.

    """
    image_1 = load_image(image_1)
    image_2 = load_image(image_2)

    if image_1.shape != image_2.shape:
        return False
    elif check_type and image_1.dtype != image_2.dtype:
        return False
    else:
        # noinspection PyUnresolvedReferences
        return (image_1 == image_2).all()


@mark("save::png")
@mark("save::jpg")
@mark("save::jpeg")
def save_image(image, path, *, exists="replace", make_dirs=True, mode="RGB"):
    """
    Save an image to the specified file path.
    The image can be provided as a PIL Image object, a NumPy array, or a file path.
    The function supports specifying the behavior when the target file already exists.

    Parameters:
        image: The image to be saved. It can be specified as a PIL Image object, a NumPy array, or a file path (string or Path object).
        path: The file path to save the image to. It should be a string or Path object.
        exists (str, optional):
            Specifies the behavior if the destination file already exists. Defaults to 'replace'.

            - 'error': Raise an error.
            - 'replace': Replace the existing file.
            - 'skip': Skip copying the file.
        make_dirs (bool or str, optional):
            Specifies whether to create the destination directory if it doesn't exist. Defaults to True.

            - True: Create the directory if it doesn't exist.
            - False: Raise an error if the destination directory doesn't exist.
        mode (str, optional): The mode to be used when saving the image. It should be a string representing the desired mode, e.g., 'RGB', 'BGR'. Defaults to 'RGB'.

    Raises:
        TypeError: If the 'mode' parameter is not a string.
        ValueError: If the 'exists' parameter is not one of 'error', 'skip', 'replace'.
        FileExistsError: If the target file already exists and the 'exists' parameter is set to 'error'.

    """
    if not isinstance(mode, str):
        raise TypeError(f"type(mode) = {type(mode)!r}")
    elif exists not in ("error", "skip", "replace"):
        raise ValueError(f"exists must be one of 'error', 'skip', 'replace'. Got {exists!r}")

    # noinspection PyProtectedMember
    from katalytic.files import _save_funcs, _warn_if_another_function_should_be_used

    _warn_if_another_function_should_be_used(str(path), _save_funcs)
    if Path(path).exists():
        if exists == "error":
            raise FileExistsError(f"[Errno {errno.EEXIST}] File exists: {str(path)!r}")
        elif exists == "replace":
            pass  # continue executing
        elif exists == "skip":
            return

    try:
        dest_dir = Path(path).parent
        if make_dirs:
            from katalytic.files import make_dir

            make_dir(dest_dir, create_parents=True, exists_ok=True)
        elif not dest_dir.exists():
            raise FileNotFoundError(f"[Errno {errno.ENOENT}] Directory does not exist: {str(dest_dir)!r}")
        elif dest_dir.is_file():
            raise NotADirectoryError(f"[Errno {errno.ENOTDIR}] Not a directory: {str(dest_dir)!r}")

        if isinstance(image, __PIL_Image_Image):
            image = __np_array(image)

        if isinstance(image, __np_ndarray):
            if mode != "BGR":
                image = convert_image(image, mode, "BGR")

            ext = str(path).rpartition(".")[2]
            tmp_path = f"{path}.part.{ext}"
            __cv2_imwrite(tmp_path, image)

            if save_image.__katalytic_test_atomicity_race_condition__:
                save_image.__katalytic_test_atomicity_race_condition__ = False

                # I can't use save_image('race condition', path) directly
                # It would replace the tmp_path = f'{path}.part' created above
                # and then move it to the target `path`. This function wouldn't
                # be able to find the tmp_path anymore and will throw an error
                # at the end of the function: `Path(tmp_path).rename(path)`
                tmp_path_2 = f"{path}.part2.{ext}"
                save_image(np.array([[[0, 255, 0]]], dtype=np.uint8), tmp_path_2)
                Path(tmp_path_2).rename(path)

            # Checking these conditions again to make the function
            # as robust as possible against race conditions
            if Path(path).exists():
                if exists == "error":
                    raise FileExistsError(f"[Errno {errno.EEXIST}] File exists: {str(path)!r}")
                elif exists == "replace":
                    pass  # continue executing
                elif exists == "skip":
                    return

            if save_image.__katalytic_test_atomicity_interrupt__:
                save_image.__katalytic_test_atomicity_interrupt__ = False
                raise KatalyticInterrupt(f"Testing atomicity ...")

            Path(tmp_path).rename(path)
        elif isinstance(image, (str, Path)):
            from katalytic.files import copy_file

            copy_file(image, path, exists=exists)
        else:
            raise TypeError(f"type(image) = {type(image)!r}")
    except BaseException as e:
        if not isinstance(e, KatalyticInterrupt):
            raise


save_image.__katalytic_test_atomicity_interrupt__ = False
save_image.__katalytic_test_atomicity_race_condition__ = False

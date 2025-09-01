import copy
from pathlib import Path

import cv2
import numpy as np
import PIL.Image
import pytest
from katalytic._pkg import all_types_besides
from katalytic.files import (
    delete_file,
    get_unique_path,
    load,
    load_csv,
    load_json,
    load_text,
    move_file,
    save,
    save_csv,
    save_json,
    save_text,
)
from PIL import Image

from katalytic_images import (
    are_arrays_equal,
    bhwc,
    convert_image,
    create_circle,
    create_line,
    create_mask,
    create_polylines,
    create_rectangle,
    create_text,
    draw,
    hw,
    hwc,
    load_image,
    save_image,
)


def _create_RGB(dtype=np.uint8):
    return np.array(
        [
            [[255, 0, 0], [0, 255, 0], [0, 0, 255]],  # RGB
            [[0, 255, 255], [255, 0, 255], [255, 255, 0]],  # CMY
            [[0, 0, 255], [0, 255, 0], [255, 0, 0]],  # BGR
            [[0, 0, 0], [128, 128, 128], [255, 255, 255]],  # black, gray, white
        ],
        dtype=dtype,
    )


class Test_bhwc:
    @pytest.mark.parametrize("ndim", [5, 10, 100])
    def test_bhwc_error(self, ndim):
        with pytest.raises(ValueError):
            bhwc(np.zeros(range(ndim)))

    @pytest.mark.parametrize(
        "data, expected",
        [
            ([], (0, 0, 0, 0)),
            ([1], (1, 1, 1, 1)),
            ([1, 2], (1, 2, 1, 1)),
            ([[1, 2], [3, 4], [5, 6]], (1, 3, 2, 1)),
            ([[1, 2, 3], [4, 5, 6]], (1, 2, 3, 1)),
            (_create_RGB(), (1, 4, 3, 3)),
            (np.zeros((2, 3, 4, 5)), (2, 3, 4, 5)),
        ],
    )
    def test_bhwc(self, data, expected):
        if isinstance(data, list):
            data = np.array(data)

        assert bhwc(data) == expected

    @pytest.mark.parametrize(
        "data, expected",
        [
            ([], (0, 0, 0)),
            ([1], (1, 1, 1)),
            ([1, 2], (2, 1, 1)),
            ([[1, 2], [3, 4], [5, 6]], (3, 2, 1)),
            ([[1, 2, 3], [4, 5, 6]], (2, 3, 1)),
            (_create_RGB(), (4, 3, 3)),
        ],
    )
    def test_hwc(self, data, expected):
        if isinstance(data, list):
            data = np.array(data)

        assert hwc(data) == expected

    @pytest.mark.parametrize(
        "data, expected",
        [
            ([], (0, 0)),
            ([1], (1, 1)),
            ([1, 2], (2, 1)),
            ([[1, 2], [3, 4], [5, 6]], (3, 2)),
            ([[1, 2, 3], [4, 5, 6]], (2, 3)),
            (_create_RGB(), (4, 3)),
        ],
    )
    def test_hw(self, data, expected):
        if isinstance(data, list):
            data = np.array(data)

        assert hw(data) == expected


class Test_convert_image:
    """TODO:
    - implement all with image as str/Path
    - if image is ndarray/Image -> you have to try infering what kind of mode it has
        - 4 channels -> rgba or hsva (or a weird one, but you can ignore that)
        - 3 ch -> rgb / hsv / Lab
            - how do I differentiate between them?
                - can I do it based on type or channel ranges?
                - can I use the gray world hypothesis
        - 1 ch and only 2 values -> binary x (nonzero, th, adaptive, otsu) x (1, 255, True) x ('inv', '')
        - 1 ch and (==0 or >= 3 values) -> gray
    - should I handle images saved as float differently?
    - for the binary cases I can split the mode str and parse the sequence
        - this will let me handle all cases with less code
        - e.g. 'binary_otsu_True_inv'.split('_') -> ['binary', 'otsu', 'True', 'inv'] ->
            - type = bool
            - values = False/True
            - invert bg with fg
            - use otsu
    """

    def test_returns_PIL_if_PIL(self):
        img = PIL.Image.fromarray(_create_RGB())
        img2 = convert_image(img, "RGB", "BGR")
        assert isinstance(img2, PIL.Image.Image)

    def test_returns_numpy_if_numpy(self):
        img = _create_RGB()
        img2 = convert_image(img, "RGB", "BGR")
        assert isinstance(img2, np.ndarray)

    def test_returns_numpy_if_str(self):
        path = get_unique_path("{}.png")
        save_image(_create_RGB(), path)
        img2 = convert_image(path, "RGB", "BGR")
        assert isinstance(img2, np.ndarray)

    def test_returns_numpy_if_Path(self):
        path = Path(get_unique_path("{}.png"))
        save_image(_create_RGB(), path)
        img2 = convert_image(path, "RGB", "BGR")
        assert isinstance(img2, np.ndarray)

    @pytest.mark.xfail(reason="Not implemented")
    def test_convert_binary(self):
        img = np.array([[[0, 0, 0], [255, 255, 255]]])
        img2 = convert_image(img, "RGB", "binary")
        assert np.all(img2 == img.astype(bool).astype(np.uint8))

    def test_convert_to_unknown(self):
        img = np.array([[[0, 0, 0], [255, 255, 255]]])
        with pytest.raises(ValueError):
            _ = convert_image(img, "RGB", "unknown")

    def test_convert_from_unknown(self):
        img = np.array([[[0, 0, 0], [255, 255, 255]]])
        with pytest.raises(ValueError):
            _ = convert_image(img, "unknown", "RGB")

    @pytest.mark.parametrize("before", all_types_besides("str"))
    def test_save_raises_TypeError_for_before(self, before):
        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            convert_image(_create_RGB(), before, "RGB")

    @pytest.mark.parametrize("after", all_types_besides("str"))
    def test_save_raises_TypeError_for_after(self, after):
        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            convert_image(_create_RGB(), "RGB", after)

    def test_RGB2RGBA(self):
        path = get_unique_path("{}.png")
        save_image(_create_RGB(), path)
        img2 = convert_image(path, "RGB", "RGBA")
        assert isinstance(img2, np.ndarray)
        print(img2)


class Test_draw:
    @pytest.mark.parametrize("wrong_type", all_types_besides("iterables"))
    def test_wrong_type(self, wrong_type):
        with pytest.raises(TypeError):
            draw(np.zeros((5, 5)), wrong_type)

    def test_returns_PIL_if_PIL(self):
        img = np.zeros((5, 5, 3), dtype=np.uint8)
        img = PIL.Image.fromarray(img)
        shape = create_circle((4, 4), 2, (0, 0, 255))

        img2 = draw(img, shape)
        assert isinstance(img2, PIL.Image.Image)

    def test_draws_on_a_copy(self):
        img = np.zeros((5, 5, 3), dtype=np.uint8)
        img_copy = img.copy()
        shapes = [
            create_line((0, 0), (0, 3), (0, 255, 0), thickness=1),
            create_rectangle([1, 1], (3, 3), (255, 0, 0), thickness=-1),
            create_circle((4, 4), 2, (0, 0, 255)),
        ]

        img = draw(img, shapes)
        assert (img == [255, 0, 0]).all(axis=2).any()
        assert (img == [0, 255, 0]).all(axis=2).any()
        assert (img == [0, 0, 255]).all(axis=2).any()

        assert not (img_copy == [255, 0, 0]).all(axis=2).any()
        assert not (img_copy == [0, 255, 0]).all(axis=2).any()
        assert not (img_copy == [0, 0, 255]).all(axis=2).any()

    def test_converts_to_type_expected_by_opencv(self):
        line = create_line([0.0, 0.0], [0.0, 3.0], (0, 255, 0), thickness=1)
        assert isinstance(line["p1"], tuple)
        assert isinstance(line["p2"], tuple)
        assert all([isinstance(x, int) for x in line["p1"] + line["p2"]])

        rect = create_rectangle([1.0, 1.0], [3.0, 3.0], (255, 0, 0), thickness=-1)
        assert isinstance(rect["p1"], tuple)
        assert isinstance(rect["p2"], tuple)
        assert all([isinstance(x, int) for x in rect["p1"] + rect["p2"]])

        circle = create_circle([4.0, 4.0], 2, (0, 0, 255))
        assert isinstance(circle["center"], tuple)
        assert all([isinstance(x, int) for x in circle["center"]])

        text = create_text("hello", [0.0, 50.0], (0, 255, 0))
        assert isinstance(text["origin"], tuple)
        assert all([isinstance(x, int) for x in text["origin"]])

        # This will raise an error if anything else goes wrong
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        draw(img, [line, rect, circle, text])

    def test_maintains_order_if_sequence(self):
        data = [
            create_line((0, 0), (0, 2), (0, 255, 0), thickness=1),
            create_line((0, 1), (0, 3), (0, 0, 255), thickness=1),
        ]
        expected = np.array([[[0, 255, 0]], [[0, 0, 255]], [[0, 0, 255]], [[0, 0, 255]]])

        img = np.zeros((4, 1, 3), dtype=np.uint8)
        img = draw(img, copy.deepcopy(data))
        assert are_arrays_equal(img, expected)

        expected = np.array([[[0, 255, 0]], [[0, 255, 0]], [[0, 255, 0]], [[0, 0, 255]]])

        img = np.zeros((4, 1, 3), dtype=np.uint8)
        img = draw(img, data[::-1])
        assert are_arrays_equal(img, expected)

    def test_text_with_background_color(self):
        original = 255 * np.ones((100, 100, 3), dtype=np.uint8)
        shape = create_text("hello", (0, 50), (0, 255, 0), bg=(255, 0, 255), bg_pad=(5, 10, 15, 20))

        processed = draw(original, shape)
        assert not are_arrays_equal(original, processed)
        assert (processed == (0, 255, 0)).any()
        assert (processed == (255, 0, 255)).any()

    def test_text_with_pad_but_without_bg_color(self):
        with pytest.raises(ValueError):
            create_text("hello", (0, 50), (0, 255, 0), bg_pad=(5, 10, 15, 20))

    @pytest.mark.parametrize("pad", [(1, 2, 3), (1, 2, 3, 4, 5)])
    def test_text_with_invalid_pad_values(self, pad):
        with pytest.raises(ValueError):
            create_text("hello", (0, 50), (0, 255, 0), bg=(0, 0, 255), bg_pad=pad)

    @pytest.mark.parametrize("pad", all_types_besides(["none", "numbers", "sequences"]))
    def test_text_with_invalid_pad_types(self, pad):
        with pytest.raises(TypeError):
            create_text("hello", (0, 50), (0, 255, 0), bg=(0, 0, 255), bg_pad=pad)

    @pytest.mark.parametrize(
        "input_pad, expected_pad",
        [(None, [5, 5, 5, 5]), (1, [1, 1, 1, 1]), ((1, 2), [1, 2, 1, 2]), ((1, 2, 3, 4), (1, 2, 3, 4))],
    )
    def test_text_with_different_pad_values(self, input_pad, expected_pad):
        shape = create_text("hello", (0, 50), (0, 255, 0), bg=(0, 0, 255), bg_pad=input_pad)
        assert shape == {
            "type": "text",
            "text": "hello",
            "origin": (0, 50),
            "color": (0, 255, 0),
            "font": cv2.FONT_HERSHEY_SIMPLEX,
            "font_scale": 1.25,
            "thickness": 3,
            "background": {"color": (0, 0, 255), "pad": expected_pad},
        }

    def test_text_without_bg_color_or_pad(self):
        shape = create_text("hello", (0, 50), (0, 255, 0))
        assert shape == {
            "type": "text",
            "text": "hello",
            "origin": (0, 50),
            "color": (0, 255, 0),
            "font": cv2.FONT_HERSHEY_SIMPLEX,
            "font_scale": 1.25,
            "thickness": 3,
        }

    @pytest.mark.parametrize(
        "shape",
        [
            create_mask([(100, 100), (250, 250), (250, 100), (150, 200)], (0, 255, 0)),
            create_mask(
                [[(100, 100), (250, 250), (250, 100), (150, 200)], ((0, 0), (0, 1), (1, 0), (2, 0))], (0, 255, 0)
            ),
            create_mask(np.array([[(100, 100), (250, 250), (250, 100), (150, 200)]]), (0, 255, 0)),
            create_mask(np.array([[(100, 100), (250, 250), (250, 100), (150, 200)]], dtype=np.uint8), (0, 255, 0)),
            create_polylines([(100, 100), (250, 250), (250, 100), (150, 200)], (0, 255, 0)),
            create_polylines(
                [[(100, 100), (250, 250), (250, 100), (150, 200)], ((0, 0), (0, 1), (1, 0), (2, 0))], (0, 255, 0)
            ),
            create_polylines(np.array([[(100, 100), (250, 250), (250, 100), (150, 200)]]), (0, 255, 0)),
            create_polylines(np.array([[(100, 100), (250, 250), (250, 100), (150, 200)]], dtype=np.uint8), (0, 255, 0)),
        ],
    )
    def test_masks_and_polylines(self, shape):
        original = 255 * np.ones((1000, 1000, 3), dtype=np.uint8)
        processed = draw(original, shape)
        assert not are_arrays_equal(original, processed)


class Test_are_arrays_equal:
    @pytest.mark.parametrize(
        "img_1, img_2",
        [
            (_create_RGB(), _create_RGB()),
            (_create_RGB(np.float32), _create_RGB(np.uint8)),
            (_create_RGB(np.float32), _create_RGB(np.uint8)),
            (np.array([[0, 1], [2, 3]]), np.array([[0, 1], [2, 3]])),
        ],
    )
    def test_equal(self, img_1, img_2):
        assert are_arrays_equal(img_1, img_2)

    @pytest.mark.parametrize(
        "img_1, img_2",
        [(np.zeros((5, 5, 3)), np.zeros((5, 5))), (np.array([[1, 2], [3, 4]]), np.array([[3, 4], [1, 2]]))],
    )
    def test_not_equal(self, img_1, img_2):
        assert not are_arrays_equal(img_1, img_2)

    def test_not_equal_type(self):
        assert not are_arrays_equal(_create_RGB(np.float32), _create_RGB(np.uint8), check_type=True)


class Test_load_and_save:
    def test_atomicity_interrupt(self):
        path = get_unique_path("{}.png")
        data = _create_RGB()

        save_image.__katalytic_test_atomicity_interrupt__ = True
        save_image(data, path)
        assert not Path(path).exists()

        # make sure it's still working after the test
        # the atomicity flag is set back to False inside the function
        save_image(data, path)
        assert are_arrays_equal(load(path), data)

    def test_atomicity_race_condition_error(self):
        path = get_unique_path("{}.png")
        data = _create_RGB()

        save_image.__katalytic_test_atomicity_race_condition__ = True
        assert not Path(path).exists()
        with pytest.raises(FileExistsError):
            save_image(data, path, exists="error")

        expected = np.array([[[0, 255, 0]]], dtype=np.uint8)
        assert are_arrays_equal(load(path), expected)

        # make sure it's still working after the test
        # the atomicity flag is set back to False inside the function
        delete_file(path)
        assert not Path(path).exists()
        save_image(data, path, exists="error")
        assert are_arrays_equal(load(path), data)

    def test_atomicity_race_condition_replace(self):
        path = get_unique_path("{}.png")
        data = _create_RGB()

        save_image.__katalytic_test_atomicity_race_condition__ = True
        assert not Path(path).exists()
        save_image(data, path, exists="replace")
        assert are_arrays_equal(load(path), data)

        # make sure it's still working after the test
        # the atomicity flag is set back to False inside the function
        delete_file(path)
        assert not Path(path).exists()
        save_image(data, path, exists="replace")
        assert are_arrays_equal(load(path), data)

    def test_atomicity_race_condition_skip(self):
        path = get_unique_path("{}.png")
        data = _create_RGB()

        save_image.__katalytic_test_atomicity_race_condition__ = True
        assert not Path(path).exists()
        save_image(data, path, exists="skip")
        expected = np.array([[[0, 255, 0]]], dtype=np.uint8)
        assert are_arrays_equal(load(path), expected)

        # make sure it's still working after the test
        # the atomicity flag is set back to False inside the function
        delete_file(path)
        assert not Path(path).exists()
        save_image(data, path, exists="skip")
        assert are_arrays_equal(load(path), data)

    # noinspection PyBroadException
    @pytest.mark.parametrize(
        "ext, wrong_load, correct_load",
        [("jpeg", load_csv, "load_image"), ("jpg", load_json, "load_image"), ("png", load_text, "load_image")],
    )
    def test_using_the_wrong_loader_should_always_warn(self, ext, wrong_load, correct_load):
        # The warning should be triggered regardless of whether the file exists or not.
        with pytest.warns(UserWarning, match=f'Use "{correct_load}" for ".{ext}" files.'):
            try:
                wrong_load(get_unique_path("{}." + ext))
            except Exception:
                pass

    # noinspection PyBroadException
    @pytest.mark.parametrize(
        "ext, wrong_save, correct_save",
        [("jpeg", save_csv, "save_image"), ("jpg", save_json, "save_image"), ("png", save_text, "save_image")],
    )
    def test_using_the_wrong_saver_should_always_warn(self, ext, wrong_save, correct_save):
        with pytest.warns(UserWarning, match=f'Use "{correct_save}" for ".{ext}" files.'):
            try:
                wrong_save(_create_RGB(), get_unique_path("{}." + ext))
            except Exception:
                pass

    def test_str(self):
        image_1 = _create_RGB()
        path = get_unique_path("{}.png")
        save_image(image_1, path)
        assert are_arrays_equal(image_1, load_image(path))

    def test_Path(self):
        image_1 = _create_RGB()
        path = Path(get_unique_path("{}.png"))
        save_image(image_1, path)
        assert are_arrays_equal(image_1, load_image(path))

    def test_save_PIL_Image(self):
        image_1 = _create_RGB()
        path = Path(get_unique_path("{}.png"))
        save_image(Image.fromarray(image_1), path)
        assert are_arrays_equal(image_1, load_image(path))

    def test_load_PIL_Image(self):
        image_1 = _create_RGB()
        path = Path(get_unique_path("{}.png"))
        save_image(image_1, path)

        image_2 = load_image(Image.fromarray(image_1))
        assert are_arrays_equal(image_1, np.array(image_2))
        assert isinstance(image_2, PIL.Image.Image)

    def test_load_returns_copy(self):
        img = _create_RGB()
        img_copy = load_image(img)
        img[0][0] = [255, 255, 255]
        assert not are_arrays_equal(img, img_copy)

    def test_path_exists_replace(self):
        path = get_unique_path("{}.png")
        Path(path).touch()

        img = _create_RGB()
        save_image(img, path, exists="replace")
        assert are_arrays_equal(load_image(path), img)

    def test_save_uses_copy_file(self):
        path = get_unique_path("{}.png")
        save_image(_create_RGB(), path)

        path2 = get_unique_path("{}.png")
        save_image(path, path2, exists="replace")

        assert are_arrays_equal(load_image(path2), load_image(path))

    def test_path_exists_skip(self):
        path = get_unique_path("{}.png")
        img = _create_RGB()
        save_image(img, path)

        img2 = convert_image(img, "RGB", "BGR")
        save_image(img2, path, exists="skip")
        assert not are_arrays_equal(load_image(path), img2)

    def test_path_exists_error(self):
        path = get_unique_path("{}.png")
        Path(path).touch()

        with pytest.raises(FileExistsError):
            save_image(_create_RGB(), path, exists="error")

    def test_universal_load_and_save(self):
        path = get_unique_path("{}.png")
        img = _create_RGB()
        save(img, path)
        assert are_arrays_equal(load(path), img)

    def test_default(self):
        path = get_unique_path("{}.png")
        img = load_image(path, default=_create_RGB())
        assert are_arrays_equal(img, _create_RGB())

    def test_make_dirs_False(self):
        img = _create_RGB()
        path = get_unique_path("{}/data.png")
        with pytest.raises(FileNotFoundError):
            save_image(img, path, make_dirs=False)

        # save image, then move it to a filename without extension
        path = get_unique_path("{}/data")
        save_image(img, f"{path}.png", make_dirs=True)
        move_file(f"{path}.png", path)

        # then try to use that filename as a directory
        with pytest.raises(NotADirectoryError):
            save_image(img, f"{path}/x.png", make_dirs=False)

    @pytest.mark.parametrize("img", [1, True, None, [], {}, (), object()])
    def test_load_raises_TypeError_for_image(self, img):
        with pytest.raises(TypeError):
            load_image(img)

    @pytest.mark.parametrize("mode", [1, True, [], {}, (), object()])
    def test_load_raises_TypeError_for_mode(self, mode):
        with pytest.raises(TypeError):
            load_image("img.png", mode)

    @pytest.mark.parametrize("path", [1, True, None, [], {}, (), object()])
    def test_save_raises_TypeError_for_path(self, path):
        with pytest.raises(TypeError):
            save_image(_create_RGB(), path)

    @pytest.mark.parametrize("image", [1, True, None, [], {}, (), object()])
    def test_save_raises_TypeError_for_image(self, image):
        with pytest.raises(TypeError):
            save_image(image, get_unique_path("{}.png"))

    @pytest.mark.parametrize("mode", [1, True, None, [], {}, (), object()])
    def test_save_raises_ValueError_for_mode(self, mode):
        with pytest.raises(TypeError):
            save_image(_create_RGB(), get_unique_path("{}.png"), mode=mode)

    @pytest.mark.parametrize("exists", ["unkonwn", "", 1, True, None, [], {}, (), object()])
    def test_save_raises_ValueError_for_exists(self, exists):
        with pytest.raises(ValueError):
            save_image(_create_RGB(), get_unique_path("{}.png"), exists=exists)

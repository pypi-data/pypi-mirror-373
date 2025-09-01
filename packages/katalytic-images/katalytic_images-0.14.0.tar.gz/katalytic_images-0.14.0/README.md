# katalytic-images [![version](https://img.shields.io/pypi/v/katalytic-images)](https://pypi.org/project/katalytic-images/) [![tests](https://gitlab.com/katalytic/katalytic-images/badges/main/pipeline.svg?key_text=tests&key_width=38)](https://gitlab.com/katalytic/katalytic-images/-/commits/main) [![coverage](https://gitlab.com/katalytic/katalytic-images/badges/main/coverage.svg)](https://gitlab.com/katalytic/katalytic-images/-/commits/main) [![docs](https://img.shields.io/readthedocs/katalytic-images.svg)](https://katalytic-images.readthedocs.io/en/latest/) [![license: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Don't use in production yet.**
I will probably introduce backwards incompatible changes

Process images with less boilerplate and more flexibility than you've ever dreamed of.

- loading images in a specific colorspace (RGB, HSV, grayscale, and more) with a single command
- converting image colorspaces
- The functions accept numpy arrays and Pillow images as input and return the same type
- defining the shapes to be drawn on top of an image in a declarative way as a list of dicts and passing it to draw()
- Many more (TODO: Link to tocs)

## Example (TODO)

## Installation
First, install opencv, which is not added as dependency so you can install the contrib/headless versions
```bash
if [[ ! $(pip freeze | grep -Pi 'opencv') ]]; then
    pip install opencv-python
fi
```
Then, install this package
```bash
pip install katalytic-images
```

## Roadmap
- make pillow an optional dependency.
   - setup_load_image() should pick opencv if pillow is not available
- image thresholding and masking operations
- interactive data exploration widgets (maybe as part of another package)
- higher level API on top of opencv
- utilities for video processing

## Contributing
We appreciate any form of contribution, including but not limited to:
- **Code contributions**: Enhance our repository with your code and tests.
- **Feature suggestions**: Your ideas can shape the future development of our package.
- **Architectural improvements**: Help us optimize our system's design and API.
- **Bug fixes**: Improve user experience by reporting or resolving issues.
- **Documentation**: Help us maintain clear and up-to-date instructions for users.

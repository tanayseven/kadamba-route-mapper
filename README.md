Kadamba Route Mapper
====================

This is a simple tool to map the routes of the buses in Kadamba Transport Corporation, Goa. The tool is written in Python and uses the Tesseract OCR to extract the text from the images.

## Setup and build

### Make sure your Python is at least 3.12

```shell
pyenv install
pyenv local
pyenv exec python --version # should be 3.12
 pyenv exec python -m venv .venv
. ./.venv/bin/activate
pip install -r requirements.txt
```

## Running the script

1. Extract all the images in a new `raw_images` directory
2. The script will read it from there and generate a `routes.xlsx` file
3. Run the script as follows

```shell
python -m main
```

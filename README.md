# Paint by Number Generator

Converts images to paint by number SVGs that can be colored in with interactive JavaScript.

## Features

- Upload your own images or use sample images
- Adjust the number of colors in the generated paint-by-number
- Interactive coloring interface
- Download the generated SVG file

## Getting Started

### Prerequisites

Make sure you have Python installed (Python 3.7 or higher recommended).

Install the required packages:

```bash
pip install streamlit pillow opencv-python numpy scikit-learn
```

### Running the Application

To start the application, simply run:

```bash
run_app.bat
```

Or manually with:

```bash
python -m streamlit run simple_app_alternative_combined.py
```

## How to Use

1. Upload an image using the file uploader in the sidebar
2. Adjust the number of colors if desired
3. Click "Generate Paint by Number"
4. Once generated, you can:
   - Select colors from the palette and click on regions to color them
   - Download the SVG file for offline use
   - Start over with a new image

## Sample Images

The application includes sample images that you can use if you don't have your own images to upload. Click the "Download Sample Images" button if they're not already available.

## Original Project

This is based on the original paint-by-number project:

- Original web app was deployed [here](https://paint-by-number-21987.web.app/)
- Original project was completed for Computational Photography (CS445) at UIUC

![demo.gif](demo.gif)

## Original Project Structure

- `src`
  - the Python source code for generating a paint by number from an image
  - this contains a `PbnGen` class that can be invoked as `PbnGen("images/input_image.jpg")` with some optional parameters
  - to get the final pbn you must run `self.set_final_pbn()` which will set the internal image of the class to be the paint by number image
  - then you must run `self.output_to_svg()` to get the final SVG image and JSON color palette
- `frontend`
  - the React app for filling in SVG paint by number images
- `functions`
  - the PBN generator deployed to google cloud functions

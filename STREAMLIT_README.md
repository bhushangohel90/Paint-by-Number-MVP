# Paint by Number - Streamlit Demo

This is a Streamlit-based MVP demo for the Paint by Number generator. It allows you to upload images, convert them to paint-by-number style SVGs, and color them in.

## Features

- Upload your own images
- Adjust the number of colors in the generated paint-by-number
- View and download the generated SVG
- Interactive coloring interface

## How to Run

1. Install the required dependencies:
   ```
   pip install -r streamlit_requirements.txt
   ```

2. Run the Streamlit app:
   ```
   streamlit run streamlit_app.py
   ```

3. Open your browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

## Usage

1. Upload an image using the file uploader in the sidebar
2. Adjust the number of colors using the slider
3. Click "Generate Paint by Number" to process the image
4. Once processed, you can view and color in the SVG
5. Download the SVG and palette files if desired

## Sample Images

Place sample images in the `images` directory to have them appear as examples in the app.

## Notes

- Processing high-resolution images may take some time
- The coloring functionality is basic and meant for demonstration purposes
- This is an MVP (Minimum Viable Product) version of the full application

## Credits

This demo is based on the Paint by Number project, which converts images to paint-by-number SVGs that can be colored in with JavaScript.

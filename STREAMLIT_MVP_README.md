# Paint by Number - Streamlit MVP Demo

This is a Streamlit-based MVP (Minimum Viable Product) demo for the Paint by Number generator. It allows you to upload images, convert them to paint-by-number style SVGs, and color them in interactively.

![Demo Screenshot](https://i.imgur.com/example.png)

## Features

- Upload your own images or use sample images
- Adjust the number of colors in the generated paint-by-number
- Interactive coloring interface
- Download the SVG and palette files
- Simple and intuitive user interface

## Quick Start

### Windows

1. Double-click the `run_streamlit_app.bat` file
2. Wait for the dependencies to install
3. The app will open in your default web browser

If you've already installed the dependencies:
- Use `run_app_only.bat` to just start the app without reinstalling packages

### Mac/Linux

1. Open a terminal in the project directory
2. Run `chmod +x run_streamlit_app.sh` to make the script executable
3. Run `./run_streamlit_app.sh`
4. The app will open in your default web browser

### Manual Installation

If the scripts don't work, you can install and run manually:

```bash
# Install base packages first (important for Python 3.12+)
pip install setuptools wheel

# Install the requirements
pip install -r streamlit_requirements.txt

# Run the app (use this method if 'streamlit' command isn't recognized)
python -m streamlit run streamlit_app.py
```

### Troubleshooting Common Issues

If you see `'streamlit' is not recognized as a command`:
```bash
# Use this command instead
python -m streamlit run streamlit_app.py
```

For other issues, see the `TROUBLESHOOTING.md` file.

## Using the App

1. **Upload an image** using the file uploader in the sidebar
   - Or use one of the sample images provided
   - If no sample images are available, you can create them with the "Create Sample Images" button

2. **Adjust settings** in the sidebar
   - Use the slider to set the number of colors (5-30)

3. **Generate the paint by number**
   - Click the "Generate Paint by Number" button
   - Wait for processing to complete (this may take a minute for larger images)

4. **Color the image**
   - Select a color from the palette in the sidebar
   - Click on shapes in the SVG to fill them with the selected color
   - Use "Clear All" to reset all colors to white
   - Use "Fill All" to fill all shapes with the selected color

5. **Download your work**
   - Use the download buttons to save the SVG and palette files
   - The SVG can be opened in any web browser or vector graphics editor

## Troubleshooting

If you encounter any issues, please refer to the `TROUBLESHOOTING.md` file for common problems and solutions.

## Technical Details

This Streamlit app uses the existing Paint by Number generator code to:

1. Process images through several steps:
   - Blur the image to reduce noise
   - Resize the image for processing
   - Cluster colors using K-means to reduce the color palette
   - Prune small clusters to simplify the image
   - Generate SVG with numbered regions and a color palette

2. Provide an interactive coloring interface using:
   - Streamlit's session state for persistent color selection
   - JavaScript for interactive coloring functionality
   - SVG manipulation for real-time updates

## Limitations

As an MVP, this demo has some limitations:

- Processing high-resolution images may take a long time
- The coloring functionality is basic and may require page refreshes
- JavaScript interactivity in Streamlit has some limitations
- The app doesn't save coloring progress between sessions

## Credits

This demo is based on the Paint by Number project, which converts images to paint-by-number SVGs that can be colored in with JavaScript.

## License

This project is licensed under the same terms as the original Paint by Number project.

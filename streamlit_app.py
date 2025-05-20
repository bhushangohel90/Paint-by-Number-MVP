import streamlit as st
# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Paint by Number Generator",
    page_icon="🎨",
    layout="wide"
)

import os
import tempfile
import base64
from PIL import Image
import io
import json
import sys
import cv2
import numpy as np
# Try to import matplotlib, but it's optional
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
except ImportError:
    print("Matplotlib not installed. Some features may not work properly.")
import requests  # For downloading sample images
from copy_sample_images import copy_sample_images  # For copying sample images from frontend assets

# Add the current directory and src directory to the path
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))
sys.path.insert(0, os.path.join(os.path.abspath("."), "functions"))

# Try to import PbnGen from src or functions directory
try:
    from src.pbn_gen import PbnGen as SrcPbnGen
    PBN_MODULE = "src"
    print("Successfully imported PbnGen from src directory")
except ImportError as e:
    print(f"Error importing from src: {e}")
    try:
        from functions.pbn_gen import PbnGen as FuncPbnGen
        PBN_MODULE = "functions"
        print("Successfully imported PbnGen from functions directory")
    except ImportError as e:
        print(f"Error importing from functions: {e}")
        print("Using simplified PbnGen implementation")
        from simple_pbn_gen import SimplePbnGen
        PBN_MODULE = "simple"

# Create a wrapper class that works with either version
class PbnGenWrapper:
    def __init__(self, image_path, num_colors=None):
        if PBN_MODULE == "src":
            self.pbn = SrcPbnGen(image_path, num_colors=num_colors)
        elif PBN_MODULE == "functions":
            # For functions version, we need to load the image first
            bgr_image = cv2.imread(image_path)
            self.pbn = FuncPbnGen(bgr_image, num_colors=num_colors)
        elif PBN_MODULE == "simple":
            # Use our simplified implementation
            self.pbn = SimplePbnGen(image_path, num_colors=num_colors)
        else:
            raise ImportError("No PbnGen implementation available")

    def set_final_pbn(self):
        self.pbn.set_final_pbn()

    def output_to_svg(self, svg_path, json_path):
        if PBN_MODULE == "src":
            # src version saves to file and returns palette
            palette = self.pbn.output_to_svg(svg_path, json_path)
            return palette
        elif PBN_MODULE == "functions":
            # functions version returns svg string and palette
            svg_string, palette = self.pbn.output_to_svg()

            # Save the SVG string to file
            with open(svg_path, 'w') as f:
                f.write(svg_string)

            # Save the palette to file
            with open(json_path, 'w') as f:
                json.dump(palette, f)

            return palette
        elif PBN_MODULE == "simple":
            # simple version can handle both approaches
            return self.pbn.output_to_svg(svg_path, json_path)

st.title("🎨 Paint by Number Generator")
st.markdown("""
This app converts your images into paint-by-number style SVGs that you can color in.
Upload an image to get started!
""")

# Sidebar with options
st.sidebar.header("Options")
num_colors = st.sidebar.slider("Number of Colors", min_value=5, max_value=30, value=15)

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

# Function to process the image and generate SVG
def process_image(image_path, num_colors):
    try:
        # Create a PbnGenWrapper instance
        pbn = PbnGenWrapper(image_path, num_colors=num_colors)

        # Generate the paint by number
        with st.spinner("Processing image... (Step 1/2: Generating paint by number)"):
            pbn.set_final_pbn()

        # Create temporary files for the SVG and JSON
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as svg_file, \
             tempfile.NamedTemporaryFile(suffix='.json', delete=False) as json_file:

            svg_path = svg_file.name
            json_path = json_file.name

        # Generate the SVG and JSON
        with st.spinner("Processing image... (Step 2/2: Generating SVG)"):
            pbn.output_to_svg(svg_path, json_path)

        # Read the generated files
        with open(svg_path, 'r') as f:
            svg_content = f.read()

        with open(json_path, 'r') as f:
            palette = json.load(f)

        # Clean up temporary files
        os.unlink(svg_path)
        os.unlink(json_path)

        return svg_content, palette

    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        st.exception(e)  # This will show the full traceback
        return None, None

# Function to display SVG with interactive coloring
def display_svg_with_coloring(svg_content, palette):
    # Create a unique ID for the SVG container
    svg_container_id = "svg-container"

    # Inject the SVG into the page
    st.markdown(f"""
    <div id="{svg_container_id}" style="width: 100%; overflow: auto; max-height: 70vh; border: 1px solid #ddd; border-radius: 5px; padding: 10px;">
        {svg_content}
    </div>
    """, unsafe_allow_html=True)

    # Create color palette UI
    st.sidebar.header("Color Palette")

    # Create a session state for the selected color if it doesn't exist
    if 'selected_color' not in st.session_state:
        st.session_state.selected_color = None

    # Display color palette with clickable colors
    color_cols = st.sidebar.columns(3)
    for idx, color_data in enumerate(palette):
        color = color_data["color"]
        # Convert color string to RGB format
        color_str = color.replace("(", "").replace(")", "")
        rgb_values = [int(x) for x in color_str.split(",")]
        hex_color = "#{:02x}{:02x}{:02x}".format(*rgb_values)

        # Create a clickable color button
        col_idx = idx % 3
        with color_cols[col_idx]:
            if st.button(
                f"Color {idx+1}",
                key=f"color_{idx}",
                help=f"RGB: {color}",
                use_container_width=True,
                type="primary" if st.session_state.selected_color == hex_color else "secondary"
            ):
                st.session_state.selected_color = hex_color

    # Display the currently selected color
    if st.session_state.selected_color:
        st.sidebar.markdown(
            f"""
            <div style="display: flex; align-items: center; margin: 20px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                <div style="background-color: {st.session_state.selected_color}; width: 40px; height: 40px; margin-right: 10px; border: 1px solid black;"></div>
                <span>Selected: {st.session_state.selected_color}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Add JavaScript for interactive coloring
    js_code = f"""
    <script>
    // Function to update the SVG when the page loads
    function updateSVG() {{
        // Get all the SVG groups
        const groups = document.querySelectorAll('svg g');

        // Add click event listeners to each group
        groups.forEach(group => {{
            // Get the polygon within the group
            const polygon = group.querySelector('polygon');
            if (polygon) {{
                group.addEventListener('click', function() {{
                    // Get the current selected color from Streamlit's session state
                    const selectedColor = '{st.session_state.selected_color}';
                    if (selectedColor) {{
                        // Set the fill color of the clicked shape
                        polygon.setAttribute('fill', selectedColor);
                    }}
                }});
            }}
        }});
    }}

    // Call the function when the DOM is loaded
    document.addEventListener('DOMContentLoaded', updateSVG);

    // Also call it now in case the DOM is already loaded
    updateSVG();
    </script>
    """

    st.markdown(js_code, unsafe_allow_html=True)

    # Add instructions for coloring
    st.sidebar.markdown("""
    ### How to Color
    1. Select a color from the palette above
    2. Click on a shape in the image to fill it with the selected color
    3. Continue until your masterpiece is complete!
    """)

    # Add buttons for clearing or filling all shapes
    cols = st.sidebar.columns(2)
    with cols[0]:
        if st.button("Clear All", use_container_width=True):
            st.markdown(
                """
                <script>
                document.querySelectorAll('svg polygon').forEach(polygon => {
                    polygon.setAttribute('fill', 'white');
                });
                </script>
                """,
                unsafe_allow_html=True
            )

    with cols[1]:
        if st.button("Fill All", use_container_width=True):
            st.markdown(
                f"""
                <script>
                document.querySelectorAll('svg polygon').forEach(polygon => {{
                    const selectedColor = '{st.session_state.selected_color}';
                    if (selectedColor) {{
                        polygon.setAttribute('fill', selectedColor);
                    }}
                }});
                </script>
                """,
                unsafe_allow_html=True
            )

    # Note about JavaScript limitations in Streamlit
    st.sidebar.info(
        "Note: Due to Streamlit's limitations with JavaScript, you may need to click the 'Fill All' or 'Clear All' buttons twice, "
        "or refresh the page to see changes take effect."
    )

# Initialize session state for storing processed results
if 'svg_content' not in st.session_state:
    st.session_state.svg_content = None
if 'palette' not in st.session_state:
    st.session_state.palette = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'temp_file_path' not in st.session_state:
    st.session_state.temp_file_path = None

# Function to handle image processing
def handle_process_image(image_path):
    st.session_state.processing = True
    st.session_state.svg_content, st.session_state.palette = process_image(image_path, num_colors)
    st.session_state.processing = False
    # Force a rerun to update the UI
    st.experimental_rerun()

# Main app logic
if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption="Uploaded Image", use_column_width=True)

    # Save the uploaded image to a temporary file if not already saved
    if st.session_state.temp_file_path is None:
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            image.save(temp_file.name)
            st.session_state.temp_file_path = temp_file.name

    # Process button
    if st.sidebar.button("Generate Paint by Number", disabled=st.session_state.processing):
        # Start processing in a separate thread
        st.session_state.processing = True
        st.experimental_rerun()

    # If processing is in progress, show a spinner
    if st.session_state.processing:
        with st.spinner("Processing image... This may take a minute."):
            # Process the image
            st.session_state.svg_content, st.session_state.palette = process_image(st.session_state.temp_file_path, num_colors)
            st.session_state.processing = False
            # Force a rerun to update the UI
            st.experimental_rerun()

    # If we have results, display them
    if st.session_state.svg_content and st.session_state.palette:
        # Display the SVG with interactive coloring
        st.success("Paint by number generated successfully!")
        display_svg_with_coloring(st.session_state.svg_content, st.session_state.palette)

        # Add download buttons for SVG and palette
        col1, col2 = st.columns(2)
        with col1:
            b64_svg = base64.b64encode(st.session_state.svg_content.encode()).decode()
            href = f'<a href="data:image/svg+xml;base64,{b64_svg}" download="paint_by_number.svg" class="download-button">Download SVG</a>'
            st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                {href}
            </div>
            <style>
            .download-button {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            .download-button:hover {{
                background-color: #45a049;
            }}
            </style>
            """, unsafe_allow_html=True)

        with col2:
            b64_json = base64.b64encode(json.dumps(st.session_state.palette).encode()).decode()
            href_json = f'<a href="data:application/json;base64,{b64_json}" download="palette.json" class="download-button">Download Palette</a>'
            st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                {href_json}
            </div>
            """, unsafe_allow_html=True)

        # Add a button to clear results and start over
        if st.sidebar.button("Start Over", type="secondary"):
            # Clean up the temporary file
            if st.session_state.temp_file_path and os.path.exists(st.session_state.temp_file_path):
                os.unlink(st.session_state.temp_file_path)

            # Reset session state
            st.session_state.svg_content = None
            st.session_state.palette = None
            st.session_state.temp_file_path = None
            st.session_state.selected_color = None

            # Force a rerun to update the UI
            st.experimental_rerun()
else:
    # Display sample images
    st.info("Upload an image to get started, or try one of our sample images.")

    # Sample images section
    st.header("Sample Images")

    # Check if sample images directory exists
    sample_dir = "images"
    if os.path.exists(sample_dir):
        sample_images = [f for f in os.listdir(sample_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]

        if sample_images:
            cols = st.columns(min(4, len(sample_images)))
            for i, img_name in enumerate(sample_images[:4]):
                img_path = os.path.join(sample_dir, img_name)
                img = Image.open(img_path)
                cols[i].image(img, caption=img_name, use_column_width=True)
                if cols[i].button("Use this image", key=f"sample_{i}", disabled=st.session_state.processing):
                    # Process the selected sample image
                    st.session_state.processing = True
                    st.session_state.sample_index = i
                    st.experimental_rerun()

            # If processing is in progress for a sample image
            if st.session_state.processing and 'sample_index' in st.session_state:
                with st.spinner("Processing image... This may take a minute."):
                    img_path = os.path.join(sample_dir, sample_images[st.session_state.sample_index])
                    st.session_state.svg_content, st.session_state.palette = process_image(img_path, num_colors)
                    st.session_state.processing = False
                    # Force a rerun to update the UI
                    st.experimental_rerun()
        else:
            st.warning(f"No sample images found in the '{sample_dir}' directory.")

            # Add buttons to create sample images
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Copy Sample Images"):
                    # Try to copy sample images from frontend assets
                    if copy_sample_images():
                        st.success("Sample images copied successfully!")
                        st.experimental_rerun()
                    else:
                        st.warning("No sample images found in frontend assets. Try downloading instead.")

            with col2:
                if st.button("Download Sample Images"):
                    # Create the images directory if it doesn't exist
                    os.makedirs(sample_dir, exist_ok=True)

                    # Download some sample images
                    sample_urls = [
                        "https://images.unsplash.com/photo-1546587348-d12660c30c50?w=500",  # Landscape
                        "https://images.unsplash.com/photo-1575936123452-b67c3203c357?w=500",  # Flower
                        "https://images.unsplash.com/photo-1564349683136-77e08dba1ef3?w=500",  # Panda
                        "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500",   # Portrait
                    ]

                    for i, url in enumerate(sample_urls):
                        try:
                            response = requests.get(url)
                            img_name = ["landscape.jpg", "flower.jpg", "panda.jpg", "portrait.jpg"][i]
                            img_path = os.path.join(sample_dir, img_name)
                            with open(img_path, 'wb') as f:
                                f.write(response.content)
                        except Exception as e:
                            st.error(f"Error downloading sample image: {str(e)}")

                    st.success("Sample images downloaded successfully!")
                    st.experimental_rerun()
    else:
        st.warning(f"Sample images directory '{sample_dir}' not found.")

        # Create the directory and add buttons to create sample images
        os.makedirs(sample_dir, exist_ok=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Copy Sample Images", key="copy_samples_2"):
                # Try to copy sample images from frontend assets
                if copy_sample_images():
                    st.success("Sample images copied successfully!")
                    st.experimental_rerun()
                else:
                    st.warning("No sample images found in frontend assets. Try downloading instead.")

        with col2:
            if st.button("Download Sample Images", key="download_samples_2"):
                # Download some sample images
                sample_urls = [
                    "https://images.unsplash.com/photo-1546587348-d12660c30c50?w=500",  # Landscape
                    "https://images.unsplash.com/photo-1575936123452-b67c3203c357?w=500",  # Flower
                    "https://images.unsplash.com/photo-1564349683136-77e08dba1ef3?w=500",  # Panda
                    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500",   # Portrait
                ]

                for i, url in enumerate(sample_urls):
                    try:
                        response = requests.get(url)
                        img_name = ["landscape.jpg", "flower.jpg", "panda.jpg", "portrait.jpg"][i]
                        img_path = os.path.join(sample_dir, img_name)
                        with open(img_path, 'wb') as f:
                            f.write(response.content)
                    except Exception as e:
                        st.error(f"Error downloading sample image: {str(e)}")

                st.success("Sample images downloaded successfully!")
                st.experimental_rerun()

# Display results if we have them (for sample images)
if st.session_state.svg_content and st.session_state.palette:
    # Display the SVG with interactive coloring
    st.success("Paint by number generated successfully!")
    display_svg_with_coloring(st.session_state.svg_content, st.session_state.palette)

    # Add download buttons for SVG and palette
    col1, col2 = st.columns(2)
    with col1:
        b64_svg = base64.b64encode(st.session_state.svg_content.encode()).decode()
        href = f'<a href="data:image/svg+xml;base64,{b64_svg}" download="paint_by_number.svg" class="download-button">Download SVG</a>'
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            {href}
        </div>
        <style>
        .download-button {{
            display: inline-block;
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }}
        .download-button:hover {{
            background-color: #45a049;
        }}
        </style>
        """, unsafe_allow_html=True)

    with col2:
        b64_json = base64.b64encode(json.dumps(st.session_state.palette).encode()).decode()
        href_json = f'<a href="data:application/json;base64,{b64_json}" download="palette.json" class="download-button">Download Palette</a>'
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            {href_json}
        </div>
        """, unsafe_allow_html=True)

    # Add a button to clear results and start over
    if st.sidebar.button("Start Over", type="secondary"):
        # Reset session state
        st.session_state.svg_content = None
        st.session_state.palette = None
        st.session_state.temp_file_path = None
        st.session_state.selected_color = None

        # Force a rerun to update the UI
        st.experimental_rerun()

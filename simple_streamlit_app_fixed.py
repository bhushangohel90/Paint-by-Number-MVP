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
import requests

# Create images directory if it doesn't exist
os.makedirs("images", exist_ok=True)

# Simple PbnGen implementation
class SimplePbnGen:
    """
    A simplified version of PbnGen for the Streamlit demo
    """
    def __init__(self, image_path, num_colors=15):
        # Read the image
        if isinstance(image_path, str):
            # It's a file path
            self.bgr_image = cv2.imread(image_path)
        else:
            # It's already an image array
            self.bgr_image = image_path

        # Convert to RGB
        self.image = cv2.cvtColor(self.bgr_image, cv2.COLOR_BGR2RGB)
        self.num_colors = num_colors

    def set_final_pbn(self):
        """
        Process the image to create a paint-by-number style image
        """
        # Resize the image to a reasonable size
        h, w = self.image.shape[:2]
        max_dim = 800
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            new_size = (int(w * scale), int(h * scale))
            self.image = cv2.resize(self.image, new_size, interpolation=cv2.INTER_AREA)

        # Apply bilateral filter to smooth the image while preserving edges
        self.image = cv2.bilateralFilter(self.image, 9, 75, 75)

        # Reshape the image for K-means clustering
        pixels = self.image.reshape(-1, 3)

        # Perform K-means clustering to reduce colors
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=self.num_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)

        # Replace each pixel with its closest cluster center
        segmented_img = kmeans.cluster_centers_[kmeans.labels_].reshape(self.image.shape).astype(np.uint8)
        self.image = segmented_img

        # Add a border
        border_size = 5
        h, w, c = self.image.shape
        canvas = np.zeros((h + 2 * border_size, w + 2 * border_size, c), dtype=np.uint8)
        canvas[border_size:border_size + h, border_size:border_size + w] = self.image
        self.image = canvas

    def output_to_svg(self, svg_path, json_path=None):
        """
        Generate SVG and JSON files
        """
        h, w = self.image.shape[:2]

        # Create SVG drawing
        import svgwrite
        dwg = svgwrite.Drawing(svg_path, profile='tiny', size=(w, h), viewBox=f"0 0 {w} {h}")

        # Find unique colors
        unique_colors = np.unique(self.image.reshape(-1, 3), axis=0)

        # Create palette
        palette = []
        shape_id = 0

        # Process each color
        for idx, color in enumerate(unique_colors):
            # Create a mask for this color
            mask = np.all(self.image == color, axis=2).astype(np.uint8) * 255

            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Create data for this color
            color_data = {
                "color": str(tuple(color)),
                "shapes": []
            }

            # Process each contour
            for contour in contours:
                # Skip tiny contours
                if cv2.contourArea(contour) < 10:
                    continue

                # Get contour points
                points = contour.squeeze().tolist()
                if len(np.shape(points)) == 1:
                    # Handle single point contours
                    points = [points]

                # Create SVG group and shape
                group = dwg.g(fill="white", stroke="black", id=str(shape_id))
                shape = dwg.polygon(points)

                # Add text label (number)
                # Find center of contour
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    # Add text
                    text = dwg.text(str(idx), insert=(cx, cy), text_anchor="middle",
                                   font_size="8px", fill="black")
                    group.add(text)

                # Add shape to group and group to drawing
                group.add(shape)
                dwg.add(group)

                # Add shape ID to color data
                color_data["shapes"].append(str(shape_id))
                shape_id += 1

            # Add color data to palette
            palette.append(color_data)

        # Save SVG
        dwg.save()

        # Save palette to JSON if path provided
        if json_path:
            with open(json_path, 'w') as f:
                json.dump(palette, f)

        return palette

# Initialize session state for storing processed results
if 'svg_content' not in st.session_state:
    st.session_state.svg_content = None
if 'palette' not in st.session_state:
    st.session_state.palette = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'temp_file_path' not in st.session_state:
    st.session_state.temp_file_path = None
if 'selected_color' not in st.session_state:
    st.session_state.selected_color = None

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
        # Create a PbnGen instance
        pbn = SimplePbnGen(image_path, num_colors=num_colors)

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
            palette = pbn.output_to_svg(svg_path, json_path)

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

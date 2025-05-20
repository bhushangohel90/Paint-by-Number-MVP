import streamlit as st
import os
import tempfile
import base64
from PIL import Image
import cv2
import numpy as np
import re
import json
import traceback

# Set page config
st.set_page_config(
    page_title="Paint by Number Generator",
    page_icon="🎨",
    layout="wide"
)

# Create images directory if it doesn't exist
os.makedirs("images", exist_ok=True)

# Alternative PbnGen implementation
class AlternativePbnGen:
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
        Generate SVG and JSON files using a simpler approach
        """
        h, w = self.image.shape[:2]
        
        # Create a simplified SVG manually
        svg_content = f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">\n'
        
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
                "color": f"({color[0]},{color[1]},{color[2]})",
                "shapes": []
            }
            
            # Process each contour
            for contour in contours:
                # Skip tiny contours
                if cv2.contourArea(contour) < 50:  # Increased threshold
                    continue
                
                # Get contour points
                points = contour.squeeze().tolist()
                if len(np.shape(points)) == 1:
                    # Handle single point contours
                    continue  # Skip single points
                
                # Create SVG group and shape
                svg_content += f'<g id="{shape_id}" fill="white" stroke="black">\n'
                
                # Create polygon points string
                points_str = ""
                for point in points:
                    points_str += f"{point[0]},{point[1]} "
                
                svg_content += f'  <polygon points="{points_str}" />\n'
                
                # Add text label (number) for larger regions
                area = cv2.contourArea(contour)
                if area > 200:  # Only add numbers to regions that are large enough
                    # Find center of contour
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        # Calculate appropriate font size based on area
                        font_size = min(max(8, int(np.sqrt(area) / 10)), 14)
                        
                        # Add text
                        svg_content += f'  <text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="middle" font-size="{font_size}px" font-weight="bold" fill="black">{idx+1}</text>\n'
                
                svg_content += '</g>\n'
                
                # Add shape ID to color data
                color_data["shapes"].append(str(shape_id))
                shape_id += 1
            
            # Add color data to palette
            palette.append(color_data)
        
        # Close SVG
        svg_content += '</svg>'
        
        # Save SVG
        with open(svg_path, 'w') as f:
            f.write(svg_content)
        
        # Save palette to JSON if path provided
        if json_path:
            with open(json_path, 'w') as f:
                json.dump(palette, f)
        
        return palette

# Initialize session state
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
if 'error_message' not in st.session_state:
    st.session_state.error_message = None

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
        pbn = AlternativePbnGen(image_path, num_colors=num_colors)
        
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
        
        return svg_content, palette, None
    
    except Exception as e:
        error_trace = traceback.format_exc()
        return None, None, f"Error: {str(e)}\n\nTraceback:\n{error_trace}"

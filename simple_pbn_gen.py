import cv2
import numpy as np
from sklearn.cluster import KMeans
import svgwrite
import json
import os

# Try to import matplotlib, but it's optional
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("Matplotlib not installed. Some features may not work properly.")
    MATPLOTLIB_AVAILABLE = False

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

        # For compatibility with both PbnGen versions
        if os.path.exists(svg_path):
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            return palette
        else:
            return svg_content, palette

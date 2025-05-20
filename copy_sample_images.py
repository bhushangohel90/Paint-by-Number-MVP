import os
import shutil

def copy_sample_images():
    """
    Copy sample images from frontend/src/assets to images directory
    """
    # Create images directory if it doesn't exist
    if not os.path.exists('images'):
        os.makedirs('images')
    
    # Check if frontend assets directory exists
    assets_dir = os.path.join('frontend', 'src', 'assets')
    if os.path.exists(assets_dir):
        # Look for jpg files
        for filename in os.listdir(assets_dir):
            if filename.endswith('.jpg'):
                # Copy the file to images directory
                src_path = os.path.join(assets_dir, filename)
                dst_path = os.path.join('images', filename)
                shutil.copy2(src_path, dst_path)
                print(f"Copied {filename} to images directory")
    
    # Check if there are any images in the images directory
    image_count = len([f for f in os.listdir('images') if f.endswith(('.jpg', '.jpeg', '.png'))])
    return image_count > 0

if __name__ == "__main__":
    copy_sample_images()

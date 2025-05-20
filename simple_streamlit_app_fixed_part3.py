# Main app logic
if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption="Uploaded Image", use_container_width=True)
    
    # Save the uploaded image to a temporary file if not already saved
    if st.session_state.temp_file_path is None:
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            image.save(temp_file.name)
            st.session_state.temp_file_path = temp_file.name
    
    # Process button
    if st.sidebar.button("Generate Paint by Number", disabled=st.session_state.processing):
        # Start processing in a separate thread
        st.session_state.processing = True
        st.rerun()
    
    # If processing is in progress, show a spinner
    if st.session_state.processing:
        with st.spinner("Processing image... This may take a minute."):
            # Process the image
            st.session_state.svg_content, st.session_state.palette = process_image(st.session_state.temp_file_path, num_colors)
            st.session_state.processing = False
            # Force a rerun to update the UI
            st.rerun()
    
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
            st.rerun()
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
                cols[i].image(img, caption=img_name, use_container_width=True)
                if cols[i].button("Use this image", key=f"sample_{i}", disabled=st.session_state.processing):
                    # Process the selected sample image
                    st.session_state.processing = True
                    st.session_state.sample_index = i
                    st.rerun()
            
            # If processing is in progress for a sample image
            if st.session_state.processing and 'sample_index' in st.session_state:
                with st.spinner("Processing image... This may take a minute."):
                    img_path = os.path.join(sample_dir, sample_images[st.session_state.sample_index])
                    st.session_state.svg_content, st.session_state.palette = process_image(img_path, num_colors)
                    st.session_state.processing = False
                    # Force a rerun to update the UI
                    st.rerun()
        else:
            st.warning(f"No sample images found in the '{sample_dir}' directory.")
            
            # Add button to download sample images
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
                st.rerun()
    else:
        st.warning(f"Sample images directory '{sample_dir}' not found.")
        
        # Create the directory and add a button to download sample images
        os.makedirs(sample_dir, exist_ok=True)
        
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
            st.rerun()

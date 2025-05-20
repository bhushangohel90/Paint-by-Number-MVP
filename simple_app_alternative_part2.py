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
        # Start processing
        st.session_state.processing = True
        
        with st.spinner("Processing image... This may take a minute."):
            # Process the image
            svg_content, palette, error = process_image(st.session_state.temp_file_path, num_colors)
            st.session_state.svg_content = svg_content
            st.session_state.palette = palette
            st.session_state.error_message = error
            st.session_state.processing = False
    
    # If we have results, display them
    if st.session_state.svg_content and st.session_state.palette:
        # Display the SVG
        st.success("Paint by number generated successfully!")
        st.markdown(f"""
        <div style="width: 100%; overflow: auto; max-height: 70vh; border: 1px solid #ddd; border-radius: 5px; padding: 10px;">
            {st.session_state.svg_content}
        </div>
        """, unsafe_allow_html=True)
        
        # Create color palette UI
        st.sidebar.header("Color Palette")
        
        # Display color palette with clickable colors
        color_cols = st.sidebar.columns(3)
        for idx, color_data in enumerate(palette):
            color = color_data["color"]
            # Convert color string to RGB format - handle different formats
            try:
                # Remove any text like 'np.uint8' and just extract the numbers
                color_str = color.replace("(", "").replace(")", "")
                # Use regex to extract just the numbers
                rgb_values = re.findall(r'\d+', color_str)
                # Take the first 3 values (R, G, B)
                rgb_values = [int(rgb_values[i]) for i in range(min(3, len(rgb_values)))]
                # Ensure we have 3 values
                while len(rgb_values) < 3:
                    rgb_values.append(0)
                hex_color = "#{:02x}{:02x}{:02x}".format(*rgb_values)
            except Exception as e:
                st.warning(f"Error parsing color {color}: {e}")
                hex_color = "#000000"  # Default to black if parsing fails
            
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
        
        # Add download button for SVG
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
    
    # If there was an error, display it
    if st.session_state.error_message:
        st.error("An error occurred during processing")
        st.code(st.session_state.error_message)
else:
    st.info("Please upload an image to get started.")

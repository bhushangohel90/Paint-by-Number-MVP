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
    if st.sidebar.button("Start Over", type="secondary", key="start_over_2"):
        # Reset session state
        st.session_state.svg_content = None
        st.session_state.palette = None
        st.session_state.temp_file_path = None
        st.session_state.selected_color = None
        
        # Force a rerun to update the UI
        st.rerun()

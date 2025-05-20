# Troubleshooting Guide for Paint by Number Streamlit App

This guide provides solutions for common issues you might encounter when setting up and running the Paint by Number Streamlit app.

## Installation Issues

### 'streamlit' is not recognized as a command

**Error Message:**
```
'streamlit' is not recognized as an internal or external command, operable program or batch file.
```

**Solution:**
This happens when Python's Scripts directory is not in your system PATH.

1. Use the Python module approach instead:
   ```
   python -m streamlit run streamlit_app.py
   ```

2. Or run the updated batch file:
   ```
   run_app_only.bat
   ```

3. To fix permanently, add Python Scripts to your PATH:
   - Find your Python scripts directory (usually `C:\Python312\Scripts` or similar)
   - Add this directory to your system PATH environment variable
   - Restart your command prompt

### Missing `distutils` Error

**Error Message:**
```
ModuleNotFoundError: No module named 'distutils'
```

**Solution:**
This error occurs with Python 3.12, which no longer includes `distutils` by default.

1. Install setuptools separately first:
   ```
   pip install setuptools wheel
   ```
2. Then install the rest of the requirements:
   ```
   pip install -r streamlit_requirements.txt
   ```

### OpenCV Installation Issues

**Error Message:**
```
error: Microsoft Visual C++ 14.0 or greater is required.
```

**Solution:**
Use the pre-built OpenCV package instead:

1. Replace `opencv-python` with `opencv-python-headless` in the requirements file
2. Run:
   ```
   pip install opencv-python-headless
   ```

### Dependency Conflicts

**Solution:**
Create a fresh virtual environment:

1. Create a new virtual environment:
   ```
   python -m venv venv
   ```
2. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
3. Install the requirements:
   ```
   pip install setuptools wheel
   pip install -r streamlit_requirements.txt
   ```

## Runtime Issues

### SVG Not Displaying

**Issue:** The SVG is generated but not displayed in the Streamlit app.

**Solution:**
1. Check if the SVG file was created successfully
2. Try using a smaller or simpler image
3. Increase the memory limit for Streamlit:
   ```
   streamlit run streamlit_app.py --server.maxUploadSize=10
   ```

### Slow Processing

**Issue:** Image processing takes a very long time.

**Solution:**
1. Use smaller images (resize before uploading)
2. Reduce the number of colors in the settings
3. If using a high-resolution image, try to resize it to under 1000x1000 pixels

### JavaScript Interactivity Issues

**Issue:** The coloring functionality doesn't work properly.

**Solution:**
1. Try using a different browser (Chrome or Firefox recommended)
2. Refresh the page after the SVG is generated
3. Click the "Fill All" or "Clear All" buttons to reset the SVG state

## Environment-Specific Issues

### Windows

- If you encounter path-related errors, try using forward slashes (`/`) instead of backslashes (`\`) in file paths
- Make sure you have the latest version of pip: `python -m pip install --upgrade pip`

### Mac/Linux

- Make sure the shell script is executable: `chmod +x run_streamlit_app.sh`
- If you encounter permission issues, try running with sudo: `sudo ./run_streamlit_app.sh`

## Getting Help

If you continue to experience issues:

1. Check the Streamlit documentation: https://docs.streamlit.io/
2. Look for similar issues in the project's GitHub repository
3. Try running the original Paint by Number code without Streamlit to isolate the issue

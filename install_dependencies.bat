@echo off
echo Installing required packages...
pip install setuptools wheel
pip install streamlit numpy matplotlib opencv-python-headless scikit-learn svgwrite shapely pillow requests
echo Done!
pause

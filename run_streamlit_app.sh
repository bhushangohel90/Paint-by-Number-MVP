#!/bin/bash
echo "Installing base packages..."
pip install setuptools wheel
echo "Installing requirements..."
pip install -r streamlit_requirements.txt
echo "Starting Streamlit app..."
python -m streamlit run streamlit_app.py

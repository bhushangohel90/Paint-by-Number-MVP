@echo off
echo Combining fixed app parts...
type simple_streamlit_app_fixed.py > simple_streamlit_app_combined.py
type simple_streamlit_app_fixed_part3.py >> simple_streamlit_app_combined.py
type simple_streamlit_app_fixed_part4.py >> simple_streamlit_app_combined.py
echo Starting Streamlit app...
python -m streamlit run simple_streamlit_app_combined.py

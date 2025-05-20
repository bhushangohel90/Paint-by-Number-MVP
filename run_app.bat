@echo off
echo ===================================================
echo Paint by Number Generator - Starting Application
echo ===================================================
echo.

REM Check if the combined file exists, if not create it
if not exist simple_app_alternative_combined.py (
    echo Combining app files...
    type simple_app_alternative.py > simple_app_alternative_combined.py
    type simple_app_alternative_part2.py >> simple_app_alternative_combined.py
    echo Combined app files successfully.
)

echo Starting Paint by Number Generator...
echo.
python -m streamlit run simple_app_alternative_combined.py

echo.
echo Application closed.

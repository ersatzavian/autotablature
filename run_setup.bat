@echo off
REM AutoTablature Setup and Test Script

echo AutoTablature Setup and Test
echo ===========================
echo.

REM Run setup
echo Running setup...
python setup.py
if %ERRORLEVEL% NEQ 0 (
    echo Setup failed with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo.
echo Setup completed successfully!
echo.

REM Ask user if they want to run a quick test
set /p run_test="Would you like to run a quick test? (y/n): "

if /i "%run_test%"=="y" (
    echo.
    echo Running quick test...
    
    REM Check if sample file exists
    if exist "data\samples\guitar_sample.mp3" (
        python tests\test_basic.py -i "data\samples\guitar_sample.mp3" -o "data\output\test_output.json"
    ) else (
        echo No sample file found.
        echo Please add a sample MP3 file to data\samples\guitar_sample.mp3
        echo or run the test manually with:
        echo python tests\test_basic.py -i ^<path_to_audio_file^> -o "data\output\test_output.json"
    )
)

echo.
echo All done! Welcome to AutoTablature!
echo.

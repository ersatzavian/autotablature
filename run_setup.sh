#!/bin/bash
# AutoTablature Setup and Test Script

echo "AutoTablature Setup and Test"
echo "==========================="
echo

# Run setup
echo "Running setup..."
python3 setup.py
if [ $? -ne 0 ]; then
    echo "Setup failed with error code $?"
    exit 1
fi

echo
echo "Setup completed successfully!"
echo

# Ask user if they want to run a quick test
read -p "Would you like to run a quick test? (y/n): " run_test

if [[ $run_test == "y" || $run_test == "Y" ]]; then
    echo
    echo "Running quick test..."
    
    # Check if sample file exists
    if [ -f "data/samples/guitar_sample.mp3" ]; then
        python3 tests/test_basic.py -i "data/samples/guitar_sample.mp3" -o "data/output/test_output.json"
    else
        echo "No sample file found."
        echo "Please add a sample MP3 file to data/samples/guitar_sample.mp3"
        echo "or run the test manually with:"
        echo "python3 tests/test_basic.py -i <path_to_audio_file> -o \"data/output/test_output.json\""
    fi
fi

echo
echo "All done! Welcome to AutoTablature!"
echo

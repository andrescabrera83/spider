#!/bin/bash

# Activate the virtual environment
source /home/rdpuser/diariospdf/spider/venv/bin/activate 

# Navigate to the directory containing the Python script
cd /home/rdpuser/diariospdf/spider/

# Run the Python script
python spider.py

# Capture the exit code of the Python script
python_exit_code=$?

# Deactivate the virtual environment
deactivate

# Use pgrep to find the process IDs of chromedriver processes
chromedriver_pids=$(pgrep -f "chromedriver")

# Check if chromedriver process IDs are found
if [ -n "$chromedriver_pids" ]; then
    echo "Chromedriver process IDs found: $chromedriver_pids"
    # Kill the chromedriver processes
    echo "Killing Chromedriver processes: $chromedriver_pids"
    kill "$chromedriver_pids"
else
    echo "No matching Chromedriver processes found."
fi

# Check if the Python script exited with an error code
if [ "$python_exit_code" -eq 0 ]; then
    echo "Python script exited successfully."
else
    echo "Python script exited with an error code: $python_exit_code"
fi

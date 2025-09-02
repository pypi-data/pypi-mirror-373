import subprocess
import sys
from pathlib import Path
import os
import time

# Global Path and Timeout Definitions
widget_path = Path(__file__).parent.parent / "widgets"
OVERALL_TIMEOUT_DURATION = 60  # Timeout limit for all widget executions combined

# Global dictionary to collect results
results_summary = {}

def process_widget_output(widget, return_code, stderr_output):
    """
    Processes the error output from a widget execution.

    Parameters:
    widget (Path): Path object pointing to the widget script.
    return_code (int): The subprocess return code.
    stderr_output (str): Complete stderr data as a UTF-8 string.
    """
    global results_summary
    stderr_output = stderr_output.strip()
    contains_warning = 'warning' in stderr_output.lower()
    widget_name = widget.name

    if return_code is None:
        results_summary[widget_name] = "In Progress"
    elif return_code == 0:
        if stderr_output:
            if contains_warning:
                results_summary[widget_name] = "Warning"
            else:
                results_summary[widget_name] = "No Output"
        else:
            results_summary[widget_name] = "Success"
    else:
        error_message = f"Error Code {return_code}:\n{stderr_output}"
        if contains_warning:
            results_summary[widget_name] = f"Warning with {error_message}"
        else:
            results_summary[widget_name] = error_message

def execute_widget_as_module(widget):
    """
    Executes a single Python widget script as a module with the -m flag.

    Parameters:
    widget (Path): Path object pointing to the widget script to be run.

    Returns:
    tuple: A combination of the widget path and the initiated subprocess.
    """
    module_name = '.'.join(widget.with_suffix('').relative_to(Path(__file__).parent.parent).parts)
    
    # Execute the widget script using unbuffered output
    process = subprocess.Popen(
        [sys.executable, '-m', module_name],
        cwd=widget_path.parent,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env=dict(os.environ, PYTHONUNBUFFERED="1")
    )
    
    return widget, process

def test_all_widgets():
    """
    Executes all Python scripts in the widgets directory as modules in parallel,
    excluding '__init__.py', within a specified total execution time limit.
    """
    processes = []

    # Launch all widget processes
    for widget in widget_path.glob("*.py"):
        if widget.name != "__init__.py":
            processes.append(execute_widget_as_module(widget))
    
    # Allow all processes to run for a maximum of 60 seconds
    time.sleep(OVERALL_TIMEOUT_DURATION)

    # Collect outputs after the timeout period
    for widget, process in processes:
        if process.poll() is None:
            process.terminate()  # Terminate if still running
            process.wait()  # Ensure process has terminated properly
            process_widget_output(widget, None, "")
        else:
            _, stderr_data = process.communicate()
            stderr_output = stderr_data.decode('utf-8')
            process_widget_output(widget, process.returncode, stderr_output)

def main():
    """
    Main function to trigger widget testing and output a summary with error details.
    """
    test_all_widgets()

    # Print a separated summary of errors and warnings
    print("\n___ SUMMARY OF ERRORS AND WARNINGS ___")

    # Display only the widgets with errors or warnings
    any_issues = False
    for widget_name, issue in results_summary.items():
        if issue not in ["In Progress", "Success", "No Output"]:
            print(f"{widget_name}: {issue}")
            any_issues = True

    # Check if there were any issues; if not, print a success message
    if not any_issues:
        print("All widgets executed successfully or are in progress with no issues.")
    else:
        raise Exception("One or more widgets encountered issues during execution.")

if __name__ == "__main__":
    main()

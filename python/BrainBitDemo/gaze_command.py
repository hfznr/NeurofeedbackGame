import subprocess
import atexit

# Initialize the GazeTracking subprocess
gaze_process = None

def start_gaze_process(script_path):
    global gaze_process
    try:
        gaze_process = subprocess.Popen(
            ['python', script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        print("GazeTracking subprocess started successfully.")
    except Exception as e:
        print(f"Error starting GazeTracking subprocess: {e}")
        gaze_process = None

    # Register cleanup for the subprocess
    atexit.register(cleanup_gaze_process)

def cleanup_gaze_process():
    global gaze_process
    if gaze_process and gaze_process.poll() is None:
        try:
            gaze_process.stdin.write("exit\n")
            gaze_process.stdin.flush()
            gaze_process.wait(timeout=5)
            print("Gaze subprocess exited successfully.")
        except Exception as e:
            print(f"Error closing gaze subprocess: {e}")

def send_gaze_command(cmd):
    global gaze_process
    if gaze_process and gaze_process.poll() is None:
        try:
            gaze_process.stdin.write(cmd + '\n')
            gaze_process.stdin.flush()
            print(f"[gaze_command.py → gaze]: {cmd}")
        except Exception as e:
            print(f"Failed to send command to gaze subprocess: {e}")
    else:
        print("Gaze subprocess is not running.")
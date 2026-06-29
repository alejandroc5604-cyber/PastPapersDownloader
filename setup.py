import sys
import os
import subprocess 


if __name__ == "__main__":
    if not os.path.isfile("requirements.txt"):
        sys.exit(-1, "Requirements.txt not found")
    
    print("Installing modules")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("All packages installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during installation: {e}")
        
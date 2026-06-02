import os
import subprocess
import sys

# --- THE OMNISIGHT BUILD AGENT ---
# Purpose: Automates the PyArmor security pipeline to lock down your IP.

def run_security_pipeline():
    print("[BUILD AGENT] Initializing Security Pipeline...")
    
    # Step 1: Ensure PyArmor is installed on your machine
    try:
        import pyarmor
    except ImportError:
        print("[BUILD AGENT] Installing PyArmor...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyarmor', '--quiet'])
    
    # Step 2: Define the output folder for the locked files
    output_dir = "dist_secure"
    
    # Step 3: Run the PyArmor encryption engine
    # Note: PyArmor automatically strips all comments (minification) during this process
    print("\n[BUILD AGENT] Engaging PyArmor Obfuscation...")
    print("[BUILD AGENT] Stripping comments and encrypting logic...")
    
    try:
        # The command tells PyArmor to encrypt main.py and all local modules it touches, 
        # saving the locked versions into the 'dist_secure' folder.
        build_command = [sys.executable, "-m", "pyarmor.cli.core", "gen", "-O", output_dir, "main.py"]
        subprocess.check_call(build_command)
        
        print(f"\n[BUILD AGENT] ✅ SUCCESS: Project successfully locked!")
        print(f"[BUILD AGENT] Your encrypted, ready-to-distribute files are in the '{output_dir}' folder.")
        print("[BUILD AGENT] Warning: NEVER edit the files in the secure folder. Only edit your original files.")
        
    except Exception as e:
        print(f"\n[BUILD AGENT] ❌ FAILED: Security pipeline encountered an error: {e}")

if __name__ == "__main__":
    run_security_pipeline()
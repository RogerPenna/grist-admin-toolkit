import os
import shutil

# Files required for the toolkit to function
REQUIRED_FILES = [
    "grist_admin_toolkit.py",
    "run_toolkit.bat",
    "requirements.txt",
    "README.md",
    "audit_configs.json" # Optional template
]

DIST_DIR = "DIST_GristAdminToolkit"

def prepare():
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)
    
    print(f"Creating clean export in: {DIST_DIR}")
    
    for file in REQUIRED_FILES:
        if os.path.exists(file):
            print(f"  -> Copying {file}...")
            shutil.copy(file, DIST_DIR)
        else:
            print(f"  -- Skipping {file} (not found)")

    print("\n[SUCCESS] Your shareable folder is ready!")
    print(f"You can now ZIP the folder '{DIST_DIR}' and share it safely.")
    print("Your .env, .git, venv, and cache files were NOT included.")

if __name__ == "__main__":
    prepare()

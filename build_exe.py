import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

print("Starting build process for VietStruct FEM...")

# PyInstaller arguments
args = [
    'steeldeckfem/__main__.py',           # Entry point
    '--name=VietStructFEM',               # Name of the executable
    '--onedir',                           # Create a directory (FASTER startup)
    '--windowed',                         # No console window (for GUI apps)
    '--add-data=vn_construction_standards.json;.',  # Include TCVN data
    '--clean',                            # Clean cache
    '--noconfirm',                        # Replace output directory without asking
]

# Note: If you don't have an icon yet, remove the '--icon' argument above.
# We will check if icon exists, if not remove the arg to prevent error
if os.path.exists('assets/icon.ico'):
    args.insert(4, '--icon=assets/icon.ico')
    print("Using custom icon")
else:
    print("No icon found, building with default icon.")

PyInstaller.__main__.run(args)

print("\nBuild complete!")
print("Executable is located in: dist/VietStructFEM/VietStructFEM.exe")
print("Tip: This 'onedir' version starts much faster than 'onefile'.")

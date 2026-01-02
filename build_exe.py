import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

print("🚀 Starting build process for VietStruct FEM...")

# PyInstaller arguments
args = [
    'steeldeckfem/__main__.py',           # Entry point
    '--name=VietStructFEM',               # Name of the executable
    '--onefile',                          # Create a single executable file
    '--windowed',                         # No console window (for GUI apps)
    '--icon=assets/icon.ico',             # Icon (if you have one, otherwise remove this line)
    '--add-data=steeldeckfem;steeldeckfem', # Include package data
    '--clean',                            # Clean cache
    '--noconfirm',                        # Replace output directory without asking
]

# Note: If you don't have an icon yet, remove the '--icon' argument above.
# We will check if icon exists, if not remove the arg to prevent error
if not os.path.exists('assets/icon.ico'):
    args = [arg for arg in args if not arg.startswith('--icon')]
    print("ℹ️  No icon found at assets/icon.ico, building with default icon.")

PyInstaller.__main__.run(args)

print("\n✅ Build complete!")
print("📂 Executable is located in the 'dist' folder: dist/VietStructFEM.exe")

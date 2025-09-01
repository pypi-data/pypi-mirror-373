
from PyInstaller.utils.hooks import collect_data_files


# This adds all data files (non-python-code files) in the whole package
datas = collect_data_files("fontfinder", excludes=['__pyinstaller'])
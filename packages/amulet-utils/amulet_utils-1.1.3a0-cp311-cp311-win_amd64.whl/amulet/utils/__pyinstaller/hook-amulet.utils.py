from PyInstaller.utils.hooks import collect_data_files, collect_submodules

hiddenimports = collect_submodules("amulet.utils")
datas = collect_data_files("amulet.utils")

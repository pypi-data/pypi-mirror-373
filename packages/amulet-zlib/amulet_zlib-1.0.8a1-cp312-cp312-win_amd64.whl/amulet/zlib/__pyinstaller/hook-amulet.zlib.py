from PyInstaller.utils.hooks import collect_data_files, collect_submodules

hiddenimports = collect_submodules("amulet.zlib")
datas = collect_data_files("amulet.zlib")

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

hiddenimports = collect_submodules("amulet.game")
datas = collect_data_files("amulet.game")

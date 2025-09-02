from PyInstaller.utils.hooks import collect_data_files, collect_submodules

hiddenimports = collect_submodules("amulet.resource_pack")
datas = collect_data_files("amulet.resource_pack")

from locators import *





def subfolder_paths(path: AbsPath):
    return [ AbsPath(f.path) for f in os.scandir(folder) if f.is_dir() ].sorted()

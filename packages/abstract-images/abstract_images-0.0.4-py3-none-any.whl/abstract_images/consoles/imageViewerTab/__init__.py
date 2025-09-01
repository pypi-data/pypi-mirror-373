from abstract_gui import startConsole
from .main import imageViewerTab
def startImageViewerConsole(defaultRoot=None,mapPath=None):
    startConsole(imageViewerTab,defaultRoot=defaultRoot,mapPath=mapPath)

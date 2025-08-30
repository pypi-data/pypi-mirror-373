import sys, os, sys, platform
from os import environ

class PyVerNotSupported(Exception):
  pass

pyver = f"{sys.version_info.major}.{sys.version_info.minor}"
ossys = platform.system()
platmac = platform.machine()  

if not (pyver in ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]):
  raise PyVerNotSupported(f"TatukGIS DK doesn't support Python{pyver}.")

try:
  if ossys == "Windows":
    if (sys.maxsize > 2**32):
      os.environ['PATH'] = os.path.dirname(__file__) + r"\_lib\win64" + os.pathsep + os.environ['PATH']
      from tatukgis_pdk._lib.win64.tatukgis_pdk import *
    else:
      os.environ['PATH'] = os.path.dirname(__file__) + r"\_lib\win32" + os.pathsep + os.environ['PATH']
      from tatukgis_pdk._lib.win32.tatukgis_pdk import *
  elif ossys == "Linux":
    if "ANDROID_BOOTLOGO" in environ:       
      if (sys.maxsize > 2**32):
        from tatukgis_pdk._lib.android64.tatukgis_pdk import *
      else:
        from tatukgis_pdk._lib.android.tatukgis_pdk import *
    else:
      if platmac == "x86_64":
        from tatukgis_pdk._lib.linux64.tatukgis_pdk import *
  elif ossys == "Darwin":
    if platmac == "x86_64":
      from tatukgis_pdk._lib.osx64.tatukgis_macos import *
      from tatukgis_pdk._lib.osx64.tatukgis_pdk import *
    elif platmac == "arm64":
      from tatukgis_pdk._lib.osxarm64.tatukgis_macos import *
      from tatukgis_pdk._lib.osxarm64.tatukgis_pdk import *
except:
  raise ValueError("Unsupported platform: " + ossys + "/" + platmac)  

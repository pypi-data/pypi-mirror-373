from PyInstaller.utils.hooks import get_package_paths
import os.path

(_, root) = get_package_paths('aspose')

datas = [(os.path.join(root, 'assemblies', 'gis'), os.path.join('aspose', 'assemblies', 'gis'))]

hiddenimports = [ 'aspose', 'aspose.pydrawing', 'aspose.pyreflection', 'aspose.pyio', 'aspose.pygc', 'aspose.pycore' ]


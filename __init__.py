# -*- coding: utf-8 -*-
"""
/***************************************************************************
 pymeoPlugin
                                 A QGIS plugin
 Este plugin
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-07-31
        copyright            : (C) 2024 by CGGEO
        email                : cggeo@gestao.gov.br
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
import subprocess
import sys


dirPython = f"{sys.prefix}\\python.exe"
subprocess.check_call([dirPython, "-m", "pip", "install", "--upgrade", "pip"])

try:
    import glob
except ImportError:
    # Se o módulo não estiver instalado, instala-o
    dirPython = f"{sys.prefix}\\python.exe"
    subprocess.check_call([dirPython, "-m", "pip", "install", "glob"])

try:
    import sqlalchemy
except ImportError:
    # Se o módulo não estiver instalado, instala-o
    dirPython = f"{sys.prefix}\\python.exe"
    subprocess.check_call([dirPython, "-m", "pip", "install", "sqlalchemy"])
    
## sqlite
try:
    import sqlite3
except ImportError:
    # Se o módulo não estiver instalado, instala-o
    dirPython = f"{sys.prefix}\\python.exe"
    subprocess.check_call([dirPython, "-m", "pip", "install", "sqlite3"])
    

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load pymeoPlugin class from file pymeoPlugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .pymeo import pymeoPlugin
    return pymeoPlugin(iface)

import os
import sys

# __file__ 
#    atributo especial do python que contém o caminho do arquivo Python atual
#
# os.path.dirname(__file__) 
#   Retorna o diretório que contém o arquivo atual
#   Se o arquivo estiver em /home/user/projeto/meu_script.py retorna /home/user/projeto
#
# os.path.join(valor1, valor2)
#   Combina o valor1 com o valor2
#
# Diretório principal do plugin
# PATH = os.path.join(os.path.dirname(__file__))
# PATHARQUIVOS = os.path.abspath(os.path.join(PATH, 'arquivos'))
# PATHCOMUNS = os.path.abspath(os.path.join(PATH, 'comuns'))
# PATHCSV = os.path.abspath(os.path.join(PATH, 'csv'))
# PATHLOG = os.path.abspath(os.path.join(PATH, 'logs'))
# PATHPYTHON = f"{sys.prefix}\\python.exe"

# Diretório principal do plugin
# Pastas
PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATHARQUIVOS = os.path.abspath(os.path.join(PATH, 'pymeo\\arquivos'))
PATHCOMUNS = os.path.abspath(os.path.join(PATH, 'pymeo\comuns'))
PATHCLASSES = os.path.abspath(os.path.join(PATH, 'pymeo\classes'))
PATHCSV = os.path.abspath(os.path.join(PATH, 'pymeo\csv'))
PATHIMAGE = os.path.abspath(os.path.join(PATH, 'pymeo\images'))
PATHLOG = os.path.abspath(os.path.join(PATH, 'pymeo\logs'))
PATHUSER = os.path.expanduser('~')

# Arquivos
PATHICONE = f"{PATHIMAGE}\\pymeo.png"
PATHEXCEL = f"C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"
PATHPYTHON = f"{sys.prefix}\\python.exe"

# Outros
MENUMAIN = 'SPUGeo'
PLUGIN = 'PyMeo 1.0'

EXIBIRMSG = True
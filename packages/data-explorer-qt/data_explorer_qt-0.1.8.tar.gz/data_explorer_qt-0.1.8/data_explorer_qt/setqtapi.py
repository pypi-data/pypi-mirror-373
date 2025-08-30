# Ensures the API is correctly set. Had an issue with PyQt6 overriding this.
from matplotlib.backends import qt_compat

qt_compat.QT_API = qt_compat.QT_API_PYSIDE6

import os

import pickle
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import folium

import ee

import sys
from qgis.PyQt.QtWidgets import QApplication, QMainWindow, QSizePolicy
from qgis.PyQt.QtGui import QSizePolicy
from qgis.PyQt.QtCore import QSettings, QgsApplication
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge
from qgis.core import QgsProject, QgsVectorLayer

# Initialize QGIS
app = QApplication([], False)
QgsApplication.setPrefixPath("/path/to/qgis", True)  # Specify the path to your QGIS installation
QgsApplication.initQgis()

# Create a main window
main_window = QMainWindow()
main_window.setWindowTitle("Simple QGIS Map")

# Create a map canvas
canvas = QgsMapCanvas()
canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
canvas.setExtent(QgsProject.instance().readEntry("Gui", "/CanvasExtents", QgsRectangle())[0])

# Set the map canvas on the main window
main_window.setCentralWidget(canvas)

# Create a layer tree and map canvas bridge
layer_tree = QgsLayerTreeMapCanvasBridge(QgsProject.instance(), canvas)
layer_tree.setCanvas(canvas)

# Load a vector layer (e.g., a shapefile)
vector_layer = QgsVectorLayer("/path/to/your/shapefile.shp", "My Layer", "ogr")
if not vector_layer.isValid():
    sys.exit(f"Layer failed to load: {vector_layer.lastError().message()}")
QgsProject.instance().addMapLayer(vector_layer)

# Refresh the canvas
canvas.refresh()

# Show the main window
main_window.show()
main_window.resize(800, 600)

# Run the application event loop
sys.exit(app.exec_())

# Cleanup
QgsApplication.exitQgis()


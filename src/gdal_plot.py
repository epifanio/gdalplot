from __future__ import with_statement
import numpy as np
import sys
from PyQt4 import QtCore 
from PyQt4 import QtGui
from qtdesigner import Ui_MplMainWindow

try:
    from osgeo import osr
    from osgeo import ogr
    from osgeo import gdal
except ImportError:
    import osr
    import ogr
from numpy import zeros, vstack

class Picker:
    def __init__(self, infile):
        self.infile = infile
        self.geoinfo = DesignerMainWindow().read(self.infile)[1]
        self.gdarray = DesignerMainWindow().read(self.infile)[0]
        
    def __call__(self, event):
        if event is None: return
        lon1 = event.xdata + float(self.geoinfo['max_x'])
        lat1 = float(self.geoinfo['max_y']) - event.ydata
        lon2 = event.xdata + float(self.geoinfo['max_x'])
        lat2 = float(self.geoinfo['max_y']) - event.ydata
        self.printsomething = DesignerMainWindow().printsomething(lon1)
        print '\n - Longitude : ', event.xdata + float(self.geoinfo['max_x']), \
        '\n - Latitude : ', float(self.geoinfo['max_y']) - event.ydata, \
        '\n - Data : ', self.gdarray[int(event.ydata)][int(event.xdata)]
        
class DesignerMainWindow(QtGui.QMainWindow, Ui_MplMainWindow): 
    """Customization for Qt Designer created window""" 
    def __init__(self, parent = None):
        super(DesignerMainWindow, self).__init__(parent) 
        self.setupUi(self)
        QtCore.QObject.connect(self.mplpushButton, QtCore. SIGNAL("clicked()"), \
            self.update_graph)
        QtCore.QObject.connect(self.mplactionOpen, QtCore. SIGNAL('triggered()'), \
            self.select_file)
        QtCore.QObject.connect(self.mplactionQuit, QtCore. SIGNAL('triggered()'), \
            QtGui.qApp, QtCore.SLOT("quit()"))
        
    def select_file(self): 
        """opens a file select dialog""" 
        inputfile = QtGui.QFileDialog.getOpenFileName() 
        if inputfile:
            self.mpllineEdit.setText(inputfile)
            
    def printsomething(self,data):
        print 'mayday', data
        self.mpleast1.setText(QtCore.QString(data))
        
    def update_graph(self):
        infile = self.mpllineEdit.text()
        array = self.read(str(infile))[0]
        self.mpl_2.canvas.ax.clear()
        self.mpl_2.canvas.ax.matshow(array)
        self.mpl_2.canvas.ax.grid(True)
        self.mpl_2.canvas.draw()
        self.mpl_2.canvas.mpl_connect('button_press_event', Picker(infile))
        
    def read(self,infile):
        indataset = gdal.Open(str(infile), gdal.GA_ReadOnly)
        band = indataset.GetRasterBand(1)
        gdarray = indataset.GetRasterBand(1).ReadAsArray()
        geotransform = indataset.GetGeoTransform() 
        geoinfo = {}
        geoinfo['res_x'], geoinfo['res_y'], geoinfo['min_x'], geoinfo['max_y'],  \
            =  geotransform[1], geotransform[5], geotransform[0], geotransform[3]
        geoinfo['max_x'] = geoinfo['min_x'] + (band.XSize * geoinfo['res_x'])
        geoinfo['min_y'] = geoinfo['max_y'] - (band.YSize * geoinfo['res_y'])
        return gdarray , geoinfo
    
app = QtGui.QApplication(sys.argv) 
dmw = DesignerMainWindow() 
dmw.show() 
sys.exit(app.exec_())

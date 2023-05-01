import sys
import math
import re
import pyqtgraph
import numpy as np
import struct
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from pyqtgraph import PlotWidget

class SerialMonitor(QtWidgets.QMainWindow):
    def __init__(self):
        super(SerialMonitor, self).__init__()
        self.sendCount = 0
        self.lastData = bytearray()
        self.port = QSerialPort()
        self.serialDataGraph = SerialDataGraph(self)

        self.setCentralWidget( QtWidgets.QWidget(self) )
        layout = QtWidgets.QVBoxLayout( self.centralWidget() )
        layout.addWidget(self.serialDataGraph)
        layout.setContentsMargins(3, 3, 3, 3)
        self.setWindowTitle('Serial Graph Monitor')

        self.toolBar = ToolBar(self)
        self.addToolBar(self.toolBar)

        self.setStatusBar( QtWidgets.QStatusBar(self) )
        self.statusText = QtWidgets.QLabel(self)
        self.statusBar().addWidget( self.statusText )
        
        self.toolBar.portOpenButton.clicked.connect(self.portOpen)
        self.port.readyRead.connect(self.readData)
        self.serialDataGraph.mouseMovedSignal.connect(self.graphCrossHairChanged)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(5)
        self.timer.timeout.connect(self.sendData)

    def slipDecode(self, packet):
        return packet.replace(b'\xDB\xDC', b'\xC0').replace(b'\xDB\xDD', b'\xDB')

    def slipEncode(self, packet):
        return b''.join([ b'\xDB\xDC' if i==192 else b'\xDB\xDD' if i==219 else bytes([i]) for i in packet ]) + b'\xC0'

    def sendData(self):
        y0, y1 = int( 32767 * math.sin( 0.01 * self.sendCount ) + 32767 ), int( 32767 * math.cos( 0.01 * self.sendCount ) + 32767 )
        self.port.write( self.slipEncode( struct.pack('>H', y0) + struct.pack('>H', y1) ) )
        self.sendCount += 1

    def readData(self):
        data = self.port.readAll()
        if len(data) > 0:

            splited = data.split(b'\xC0')

            if len(splited[0]) == 0:
                splited = splited[1:]
            else:
                splited[0] = self.lastData + splited[0]

            if len(splited[-1]) == 0 or not len(splited[-1]) == 4:
                self.lastData = splited.pop(-1)

            for packet in splited:
                decoded = self.slipDecode(packet)

                try:
                    y0 = struct.unpack('>H', decoded[:2])[0]
                    y1 = struct.unpack('>H', decoded[2:])[0]
                except:
                    pass

                self.serialDataGraph.appendData(y0, 0)
                self.serialDataGraph.appendData(y1, 1)

    def graphCrossHairChanged(self, x, y0, y1):
        self.statusText.setText( str(round(x, 4)) + ', ' + str(round(y0, 4)) + ', ' + str(round(y1, 4)) )

    def portOpen(self, flag):
        if flag:
            self.port.setBaudRate( self.toolBar.baudRate() )
            self.port.setPortName( self.toolBar.portName() )
            self.port.setDataBits( self.toolBar.dataBit() )
            self.port.setParity( self.toolBar.parity() )
            self.port.setStopBits( self.toolBar.stopBit() )
            self.port.setFlowControl( self.toolBar.flowControl() )
            r = self.port.open(QtCore.QIODevice.ReadWrite)
            if not r:
                self.statusText.setText('Port open error')
                self.toolBar.portOpenButton.setChecked(False)
                self.toolBar.serialControlEnable(True)
            else:
                self.statusText.setText('Port opened')
                self.toolBar.serialControlEnable(False)
                self.timer.start()
        else:
            self.timer.stop()
            self.port.close()
            self.statusText.setText('Port closed')
            self.toolBar.serialControlEnable(True)
        
class SerialDataGraph(QtWidgets.QWidget):
    mouseMovedSignal = QtCore.pyqtSignal( float, float, float )
    def __init__(self, parent):
        super(SerialDataGraph, self).__init__(parent)
        
        self.plotWidget = pyqtgraph.PlotWidget()
        self.plotWidget.setBackground('#FFFFFFFF')
        self.plotWidget.plotItem.getAxis('bottom').setPen( pyqtgraph.mkPen(color='#000000') )
        self.plotWidget.plotItem.getAxis('left').setPen( pyqtgraph.mkPen(color='#000000') )
        self.plotWidget.plotItem.showGrid(True, True, 0.3)
        self.plotWidget.setXRange(0, 300)

        self.data = [ self.plotWidget.plotItem.plot(pen='r'), self.plotWidget.plotItem.plot(pen='b')]
        self.data[0].setData( np.zeros(300) )
        self.data[1].setData( np.zeros(300) )

        self.crossHairV = pyqtgraph.InfiniteLine(angle=90, movable=False)
        self.crossHairH = pyqtgraph.InfiniteLine(angle=0, movable=False)
        self.plotWidget.addItem(self.crossHairV, ignoreBounds=True)
        self.plotWidget.addItem(self.crossHairH, ignoreBounds=True)
        self.plotWidget.scene().sigMouseMoved.connect(self.mouseMovedEvent)

        self.setLayout( QtWidgets.QVBoxLayout() )
        self.layout().addWidget(self.plotWidget)

    def appendData(self, data, yNum):
        rolled = np.roll(self.data[yNum].yData, -1)
        rolled[-1] = data
        self.data[yNum].setData(rolled)

    def mouseMovedEvent(self, pos):
        if self.plotWidget.sceneBoundingRect().contains(pos):
            mousePoint = self.plotWidget.plotItem.getViewBox().mapSceneToView(pos)
            index = int( mousePoint.x() )
            data0, data1 = self.data[0].yData, self.data[1].yData
            if 0 <= index < data0.shape[0] and 0 <= index < data1.shape[0]:
                self.mouseMovedSignal.emit( mousePoint.x(), data0[index], data1[index] )
            self.crossHairV.setPos( mousePoint.x() )
            self.crossHairH.setPos( mousePoint.y() )

class SerialDataView(QtWidgets.QWidget):
    def __init__(self, parent):
        super(SerialDataView, self).__init__(parent)
        self.serialData = QtWidgets.QTextEdit(self)
        self.serialData.setReadOnly(True)
        self.serialData.setFontFamily('Courier New')
        self.serialData.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.serialDataHex = QtWidgets.QTextEdit(self)
        self.serialDataHex.setReadOnly(True)
        self.serialDataHex.setFontFamily('Courier New')
        self.serialDataHex.setFixedWidth(500)
        self.serialDataHex.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.label = QtWidgets.QLabel('00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F')
        self.label.setFont( QtGui.QFont('Courier New') )
        self.label.setIndent(5)

        self.setLayout( QtWidgets.QGridLayout(self) )
        self.layout().addWidget(self.serialData,    0, 0, 2, 1)
        self.layout().addWidget(self.label,         0, 1, 1, 1)
        self.layout().addWidget(self.serialDataHex, 1, 1, 1, 1)
        self.layout().setContentsMargins(2, 2, 2, 2)
        
    def appendSerialText(self, appendText, color):
        self.serialData.moveCursor(QtGui.QTextCursor.End)
        self.serialData.setFontFamily('Courier New')
        self.serialData.setTextColor(color)
        self.serialDataHex.moveCursor(QtGui.QTextCursor.End)
        self.serialDataHex.setFontFamily('Courier New')
        self.serialDataHex.setTextColor(color)

        self.serialData.insertPlainText(appendText)
        
        lastData = self.serialDataHex.toPlainText().split('\n')[-1]
        lastLength = math.ceil( len(lastData) / 3 )
        
        appendLists = []
        splitedByTwoChar = re.split( '(..)', appendText.encode().hex() )[1::2]
        if lastLength > 0:
            t = splitedByTwoChar[ : 16-lastLength ] + ['\n']
            appendLists.append( ' '.join(t) )
            splitedByTwoChar = splitedByTwoChar[ 16-lastLength : ]

        appendLists += [ ' '.join(splitedByTwoChar[ i*16 : (i+1)*16 ] + ['\n']) for i in range( math.ceil(len(splitedByTwoChar)/16) ) ]
        if len(appendLists[-1]) < 47:
            appendLists[-1] = appendLists[-1][:-1]

        for insertText in appendLists:
            self.serialDataHex.insertPlainText(insertText)
        
        self.serialData.moveCursor(QtGui.QTextCursor.End)
        self.serialDataHex.moveCursor(QtGui.QTextCursor.End)

class ToolBar(QtWidgets.QToolBar):
    def __init__(self, parent):
        super(ToolBar, self).__init__(parent)
        
        self.portOpenButton = QtWidgets.QPushButton('Open')
        self.portOpenButton.setCheckable(True)
        self.portOpenButton.setMinimumHeight(32)

        self.portNames = QtWidgets.QComboBox(self)
        self.portNames.addItems([ port.portName() for port in QSerialPortInfo().availablePorts() ])
        self.portNames.setMinimumHeight(30)

        self.baudRates = QtWidgets.QComboBox(self)
        self.baudRates.addItems([
            '110', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200', '28800', 
            '31250', '38400', '51200', '56000', '57600', '76800', '115200', '128000', '230400', '256000', '921600'
        ])
        self.baudRates.setCurrentText('115200')
        self.baudRates.setMinimumHeight(30)

        self.dataBits = QtWidgets.QComboBox(self)
        self.dataBits.addItems(['5 bit', '6 bit', '7 bit', '8 bit'])
        self.dataBits.setCurrentIndex(3)
        self.dataBits.setMinimumHeight(30)

        self._parity = QtWidgets.QComboBox(self)
        self._parity.addItems(['No Parity', 'Even Parity', 'Odd Parity', 'Space Parity', 'Mark Parity'])
        self._parity.setCurrentIndex(0)
        self._parity.setMinimumHeight(30)

        self.stopBits = QtWidgets.QComboBox(self)
        self.stopBits.addItems(['One Stop', 'One And Half Stop', 'Two Stop'])
        self.stopBits.setCurrentIndex(0)
        self.stopBits.setMinimumHeight(30)

        self._flowControl = QtWidgets.QComboBox(self)
        self._flowControl.addItems(['No Flow Control', 'Hardware Control', 'Software Control'])
        self._flowControl.setCurrentIndex(0)
        self._flowControl.setMinimumHeight(30)

        self.addWidget( self.portOpenButton )
        self.addWidget( self.portNames)
        self.addWidget( self.baudRates)
        self.addWidget( self.dataBits)
        self.addWidget( self._parity)
        self.addWidget( self.stopBits)
        self.addWidget( self._flowControl)

    def serialControlEnable(self, flag):
        self.portNames.setEnabled(flag)
        self.baudRates.setEnabled(flag)
        self.dataBits.setEnabled(flag)
        self._parity.setEnabled(flag)
        self.stopBits.setEnabled(flag)
        self._flowControl.setEnabled(flag)
        
    def baudRate(self):
        return int(self.baudRates.currentText())

    def portName(self):
        return self.portNames.currentText()

    def dataBit(self):
        return int(self.dataBits.currentIndex() + 5)

    def parity(self):
        return self._parity.currentIndex()

    def stopBit(self):
        return self.stopBits.currentIndex()

    def flowControl(self):
        return self._flowControl.currentIndex()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SerialMonitor()
    window.show()
    app.exec()
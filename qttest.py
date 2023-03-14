from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import pandas as pd
import glob
import numpy as np
from model_test import get_result

class WindowLength:
    x_axis = 400

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 603)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_ECG = QtWidgets.QLabel(self.centralwidget)
        self.label_ECG.setGeometry(QtCore.QRect(0, 0, 71, 21))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(16)
        self.label_ECG.setFont(font)
        self.label_ECG.setObjectName("label_ECG")
        
        self.label_PPG = QtWidgets.QLabel(self.centralwidget)
        self.label_PPG.setGeometry(QtCore.QRect(0, 260, 71, 21))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(16)
        self.label_PPG.setFont(font)
        self.label_PPG.setObjectName("label_PPG")
        
        #sbp value
        self.label_SBP = QtWidgets.QLabel(self.centralwidget)
        self.label_SBP.setGeometry(QtCore.QRect(0, 525, 71, 21))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(16)
        self.label_SBP.setFont(font)
        self.label_SBP.setObjectName("label_SBP")
        
        #dbp value
        self.label_DBP = QtWidgets.QLabel(self.centralwidget)
        self.label_DBP.setGeometry(QtCore.QRect(0, 555, 71, 21))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(16)
        self.label_DBP.setFont(font)
        self.label_DBP.setObjectName("label_DBP")
        
        self.label_status = QtWidgets.QLabel(self.centralwidget)
        self.label_status.setGeometry(QtCore.QRect(360, 520, 81, 51))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體 Light")
        font.setPointSize(26)
        self.label_status.setFont(font)
        self.label_status.setObjectName("label_status")
        
        #status light
        self.StdWlrStstus = QtWidgets.QLabel(self.centralwidget)
        self.StdWlrStstus.setGeometry(QtCore.QRect(320, 535, 20, 20))
        self.StdWlrStstus.setStyleSheet("border-radius:10px;background-color:green")
        font = QtGui.QFont()
        font.setFamily("微軟正黑體 Light")
        font.setPointSize(1)
        self.StdWlrStstus.setFont(font)
        self.StdWlrStstus.setObjectName("StdWlrStstus")
        
        self.InformButton = QtWidgets.QPushButton(self.centralwidget)
        self.InformButton.setGeometry(QtCore.QRect(690, 530, 91, 31))
        self.InformButton.setObjectName("InformButton")
        
        #self.ecg, self.ppg, self.first_diff, self.second_diff = self.read_csv_file()
        self.ecg, self.ppg = self.read_csv_file()
        self.ecg = self.ecg.to_numpy()
        self.ppg = self.ppg.to_numpy()
        
        self.count = 0
        
        pen = pg.mkPen(color=(225, 125, 0))
        self.x1 = np.arange(WindowLength.x_axis)  # time points
        
        #INIT ECG Y VALUE
        self.y1 = self.ecg[0:WindowLength.x_axis]  # data points
        self.ecg = self.ecg[WindowLength.x_axis:]  # Remove the first window size
        
        self.graphicsView = PlotWidget(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(0, 20, 801, 241))
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setBackground('w')
        self.graphicsView.showGrid(x=True, y=True)
        
        #畫
        self.data_line1 =  self.graphicsView.plot(self.x1, self.y1, name="test", pen=pen)
        
        #INIT PPG Y VALUE
        self.x2 = np.arange(WindowLength.x_axis)
        self.y2 = self.ppg[0:WindowLength.x_axis]
        self.ppg = self.ppg[WindowLength.x_axis:]  # Remove the first window size
        
        self.graphicsView_2 = PlotWidget(self.centralwidget)
        self.graphicsView_2.setGeometry(QtCore.QRect(0, 280, 801, 241))
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.graphicsView_2.setBackground('w')
        self.graphicsView_2.showGrid(x=True, y=True)
        #畫
        self.data_line2 =  self.graphicsView_2.plot(self.x2, self.y2, name="test2", pen=pen)
        
        #數據更新計時器
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10) #0.01秒(數據為100HZ)
        self.timer.timeout.connect(self.update_data)
        self.timer.start()
        
        #模型結果更新計時器
        self.timer_model = QtCore.QTimer()
        self.timer_model.setInterval(60000) #60秒
        self.timer_model.timeout.connect(self.StdStatusLightSet)
        self.timer_model.start()
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        mean_sbp, mean_dbp = get_result(self.count)
        
        print('mean_sbp:', mean_sbp)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_ECG.setText(_translate("MainWindow", "ECG"))
        self.label_PPG.setText(_translate("MainWindow", "PPG"))
        
        self.label_SBP.setText(_translate("MainWindow", "SBP:"))
        self.label_DBP.setText(_translate("MainWindow", "DBP:"))
        
        
        self.StdWlrStstus.setText(_translate("MainWindow", "O"))
        self.label_status.setText(_translate("MainWindow", "狀態"))
        self.InformButton.setText(_translate("MainWindow", "通知"))
        
    def update_plot_data(self):
        self.x1 = np.insert(self.x1,len(self.x1) , self.x1[-1] + 1)
        self.x1 = self.x1[1:]  # Remove the first y element.

        self.y1 = self.y1[1:]  # Remove the first
        self.y1 = np.insert(self.y1,len(self.y1) , self.ecg[0])
        self.ecg = self.ecg[1:]

        self.data_line1.setData(self.x1, self.y1)  # Update the data.
        
    def update_plot_data2(self):
        self.x2 = np.insert(self.x2,len(self.x2) , self.x2[-1] + 1)
        self.x2 = self.x2[1:]  # Remove X0.

        self.y2 = self.y2[1:]  # Remove the first element in y0
        self.y2 = np.insert(self.y2,len(self.y2) , self.ppg[0])
        self.ppg = self.ppg[1:]

        self.data_line2.setData(self.x2, self.y2)  # Update the data.
        
    def update_plot_data_first(self):
        self.first_in_window = self.first_in_window[1:]  # Remove the first element in y0
        self.first_in_window = np.insert(self.first_in_window,len(self.first_in_window) , self.first_diff[0])
        self.first_diff = self.first_diff[1:]
        
    def update_plot_data_second(self):
        self.second_in_window = self.second_in_window[1:]  # Remove the first element in y0
        self.second_in_window = np.insert(self.second_in_window,len(self.second_in_window) , self.second_diff[0])
        self.second_diff = self.second_diff[1:]
        
    def read_csv_file(self):
        csv_files = glob.glob("D:/BPP/test/datexpsql2018_06_29_" "*.csv")
         
        df = pd.concat((pd.read_csv(file, usecols=['II','PLETH', 'first', 'second'], dtype={ 'II': float, 'PLETH':float, 'first':float, 'second':float}) for file in csv_files), ignore_index=True)
        
        return df['II'], df['PLETH']#, df['first'], df['second']
    
    def update_data(self):
        self.update_plot_data()
        self.update_plot_data2()
        
    def StdStatusLightSet(self):
        sheetStrHead = "border-radius:10px;background-color:"
        self.count += 1
        count = self.count
        mean_sbp, mean_dbp = get_result(count)
        
        if mean_sbp > 160 or mean_dbp < 80:
            status = "red"
        
        self.StdWlrStstus.setStyleSheet(sheetStrHead + status)
        self.label_SBP.setText(("SBP:" + str(mean_sbp)))
        self.label_DBP.setText(("DBP:" + str(mean_dbp)))
                
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

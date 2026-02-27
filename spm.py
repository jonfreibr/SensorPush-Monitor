#!/usr/bin/python3
"""
Program :   SensorPush Monitor
Author  :   Jon Freivald <jfreivald@brmedical.com>
        :   Copyright © Blue Ridge Medical Center, 2026
        :   License: GNU GPL Version 3
Date    :   2026-02-26
Purpose :   To provide a display of current sensor reading without using the web site.
"""

import os
import sys
from pysensorpush import PySensorPush

from PySide6.QtGui import (
    QFont,
    QIcon,
    QPixmap,
)

from PySide6 import (
    QtCore,
)

from PySide6.QtCore import (
    Qt,
    QTimer,
    QSettings,
    QPoint,
    QSize,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QDialog,
    QTextEdit,
    QApplication,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QDialogButtonBox,
)

progver = "0.1a"
batmin = 2.3 # volts
sensors = []

brmc_dark_blue = '#00446a'
brmc_medium_blue = '#73afb6'
brmc_gold = '#ffcf01'
brmc_rust = '#ce7067'
brmc_warm_grey = '#9a8b7d'

class Sensor():
    def __init__(self, id, name, t_calibration, h_calibration, volts, temp, humid, a_t, a_tmax, a_tmin, a_h):
        
        self.id = id
        self.name = name
        self.t_calibration = t_calibration
        self.h_calibration = h_calibration
        self.volts = volts
        self.temp = temp
        self.humid = humid
        self.a_t = a_t
        self.a_tmax = a_tmax
        self.a_tmin = a_tmin
        self.a_h = a_h
        self.cal_temp = self.temp + self.t_calibration
        self.cal_humid = self.humid + self.h_calibration

    def get_sensor_id(self):
        return self.id

    def get_sensor(self):
        return QLabel(self.name+"\n"+str(round(self.cal_temp, 1))+"°F, "+str(round(self.cal_humid, 1))+"%\n"+str(round(self.volts, 2)+"v"))
    
    def get_sensor_name(self):
        font = QFont()
        font.setItalic(True)
        self.name_label = QLabel(self.name)
        self.name_label.setStyleSheet("color: black;")
        self.name_label.setFont(font)
        return self.name_label
    
    def get_temp(self):
        self.temp_label = QLabel(str(round(self.cal_temp, 1))+"°F")
        if self.a_t:
            if self.cal_temp >= self.a_tmax or self.cal_temp <= self.a_tmin:
                self.temp_label.setStyleSheet("color: red;")
            else:
                self.temp_label.setStyleSheet("color: darkgreen;")
        return self.temp_label
    
    def get_humid(self):
        self.humd_label = QLabel(str(round(self.cal_humid, 1))+"%")
        self.humd_label.setStyleSheet("color: black;")
        return self.humd_label
    
    def get_bat(self):
        msg = ""
        if self.volts <= batmin:
            msg = " (Replace Battery!)"
        self.bat_label = QLabel(str(round(self.volts, 2))+"v"+msg)
        if self.volts > batmin:
            self.bat_label.setStyleSheet("color: darkgreen;")
        else:
            self.bat_label.setStyleSheet("color: red;")
        return self.bat_label
    
    def sensor_update(self, t_calibration, h_calibration, volts, temp, humid, a_t, a_tmax, a_tmin, a_h):
        self.t_calibration = t_calibration
        self.h_calibration = h_calibration
        self.volts = volts
        self.temp = temp
        self.humid = humid
        self.a_t = a_t
        self.a_tmax = a_tmax
        self.a_tmin = a_tmin
        self.a_h = a_h
        self.cal_temp = self.temp + self.t_calibration
        self.cal_humid = self.humid + self.h_calibration
        self.temp_label.setText(str(round(self.cal_temp,1)))
        if self.a_t:
            if self.cal_temp >= self.a_tmax or self.cal_temp <= self.a_tmin:
                self.temp_label.setStyleSheet("color: red;")
            else:
                self.temp_label.setStyleSheet("color: darkgreen;")
        self.temp_label.repaint()
        self.humd_label.setText(str(round(self.cal_humid,1)))
        self.temp_label.repaint()
        msg = ""
        if self.volts <= batmin:
            msg = " (Replace Battery!)"
        self.bat_label.setText(str(round(self.volts, 2))+"v"+msg)
        if self.volts > batmin:
            self.bat_label.setStyleSheet("color: darkgreen;")
        else:
            self.bat_label.setStyleSheet("color: red;")
        self.bat_label.repaint()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f'SensorPush Monitor v{progver}')
        self.settings = QSettings("Blue Ridge Medical Center", "SensorPush Monitor")
        self.resize(self.settings.value('MainWindowSize', QSize(450, 50)))
        self.move(self.settings.value('MainWindowPos', QPoint(50, 50)))
        self.setStyleSheet(f'background-color: {brmc_medium_blue}')
        self.container = QWidget()
        layout = QGridLayout()

        user = os.getenv('SENSORPUSH_USER', None)
        password = os.getenv('SENSORPUSH_PASSWORD', None)

        if None in (user, password):
            print(
                'ERROR! Must define env variables SENSORPUSH_USER and SENSORPUSH_PASSWORD'
            )
            raise SystemExit
    
        self.sensorpush = PySensorPush(user, password)

        s = self.sensorpush.sensors
        r = self.sensorpush.samples(1)
        # print(s)
        for i in s:
            # print(i)
            id = s[i]["id"]
            name = s[i]['name']
            volts = s[i]["battery_voltage"]
            t_calibration = s[i]["calibration"]["temperature"]
            h_calibration = s[i]["calibration"]["humidity"]
            a_t = s[i]["alerts"]["temperature"]["enabled"]
            a_tmax = s[i]["alerts"]["temperature"]["max"]
            a_tmin = s[i]["alerts"]["temperature"]["min"]
            a_h = s[i]["alerts"]["humidity"]["enabled"]
            temp = r["sensors"][id][0]["temperature"]
            humid = r["sensors"][id][0]["humidity"]
            
            sensors.append(Sensor(id, name, t_calibration, h_calibration, volts, temp, humid, a_t, a_tmax, a_tmin, a_h))

        font = QFont()
        font.setBold(True)
        font.setUnderline(True)
        sensor_label = QLabel("Sensor")
        sensor_label.setFont(font)
        temp_label = QLabel("Temp")
        temp_label.setFont(font)
        humid_label = QLabel("Humidity")
        humid_label.setFont(font)
        bat_label = QLabel("Battery")
        bat_label.setFont(font)
        
        layout.addWidget(sensor_label, 0, 0)
        layout.addWidget(temp_label, 0, 1)
        layout.addWidget(humid_label, 0, 2)
        layout.addWidget(bat_label, 0, 3)
        y = 1
        for j in sensors:
            layout.addWidget(j.get_sensor_name(), y, 0)
            layout.addWidget(j.get_temp(), y, 1)
            layout.addWidget(j.get_humid(), y, 2)
            layout.addWidget(j.get_bat(), y, 3)
            y += 1
            
        self.container.setLayout(layout)
        self.setCentralWidget(self.container)

        timer = QTimer(self)
        timer.timeout.connect(self.do_update)
        timer.start(300000) # milliseconds

    def do_update(self):
        s = self.sensorpush.sensors
        r = self.sensorpush.samples(1)
        for i in sensors:
            id = i.get_sensor_id()
            volts = s[id]["battery_voltage"]
            t_calibration = s[id]["calibration"]["temperature"]
            h_calibration = s[id]["calibration"]["humidity"]
            a_t = s[id]["alerts"]["temperature"]["enabled"]
            a_tmax = s[id]["alerts"]["temperature"]["max"]
            a_tmin = s[id]["alerts"]["temperature"]["min"]
            a_h = s[id]["alerts"]["humidity"]["enabled"]
            temp = r["sensors"][id][0]["temperature"]
            humid = r["sensors"][id][0]["humidity"]
            i.sensor_update(t_calibration, h_calibration, volts, temp, humid, a_t, a_tmax, a_tmin, a_h)

    def closeEvent(self, a0):
        self.settings.setValue("MainWindowSize", self.size())
        self.settings.setValue("MainWindowPos", self.pos())
        return super().closeEvent(a0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

"""
v 0.1       :   20260226        : Initial version.
v 0.1a      :   20260227        : Fixed display rounding issue
"""
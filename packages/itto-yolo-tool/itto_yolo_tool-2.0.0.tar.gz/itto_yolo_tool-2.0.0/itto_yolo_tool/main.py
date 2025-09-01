from PyQt5 import QtCore, QtWidgets
from itto_yolo_tool.ui_function.main_menu_function import Ui_MainWindow_function
import sys

def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow_function()
    ui.setupUi(MainWindow)
    ui.setupfunction(MainWindow=MainWindow, main_path=__file__)
    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
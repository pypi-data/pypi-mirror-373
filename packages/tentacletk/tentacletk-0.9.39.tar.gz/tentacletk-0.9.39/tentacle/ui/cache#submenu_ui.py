# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cache#submenu.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QSizePolicy,
    QTabWidget, QWidget)

class Ui_QtUi(object):
    def setupUi(self, QtUi):
        if not QtUi.objectName():
            QtUi.setObjectName(u"QtUi")
        QtUi.setEnabled(True)
        QtUi.resize(600, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(QtUi.sizePolicy().hasHeightForWidth())
        QtUi.setSizePolicy(sizePolicy)
        QtUi.setMinimumSize(QSize(0, 0))
        QtUi.setMaximumSize(QSize(600, 600))
        QtUi.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        QtUi.setToolButtonStyle(Qt.ToolButtonIconOnly)
        QtUi.setTabShape(QTabWidget.Triangular)
        QtUi.setDockNestingEnabled(True)
        QtUi.setDockOptions(QMainWindow.AllowNestedDocks|QMainWindow.AllowTabbedDocks|QMainWindow.AnimatedDocks|QMainWindow.ForceTabbedDocks)
        self.widget = QWidget(QtUi)
        self.widget.setObjectName(u"widget")
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.i040 = QPushButton(self.widget)
        self.i040.setObjectName(u"i040")
        self.i040.setGeometry(QRect(260, 290, 66, 21))
        self.i040.setMinimumSize(QSize(0, 21))
        self.i040.setMaximumSize(QSize(66, 21))
        QtUi.setCentralWidget(self.widget)

        self.retranslateUi(QtUi)

        QMetaObject.connectSlotsByName(QtUi)
    # setupUi

    def retranslateUi(self, QtUi):
#if QT_CONFIG(accessibility)
        self.i040.setAccessibleName(QCoreApplication.translate("QtUi", u"cache", None))
#endif // QT_CONFIG(accessibility)
        self.i040.setText(QCoreApplication.translate("QtUi", u"Cache", None))
        pass
    # retranslateUi


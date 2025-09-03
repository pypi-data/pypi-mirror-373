# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'animation.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QVBoxLayout, QWidget)

from uitk.widgets.header.Header import Header
from widgets.pushbutton import PushButton

class Ui_QtUi(object):
    def setupUi(self, QtUi):
        if not QtUi.objectName():
            QtUi.setObjectName(u"QtUi")
        QtUi.setEnabled(True)
        QtUi.resize(200, 262)
        QtUi.setTabShape(QTabWidget.Triangular)
        QtUi.setDockNestingEnabled(True)
        QtUi.setDockOptions(QMainWindow.AllowNestedDocks|QMainWindow.AllowTabbedDocks|QMainWindow.AnimatedDocks|QMainWindow.ForceTabbedDocks)
        self.central_widget = QWidget(QtUi)
        self.central_widget.setObjectName(u"central_widget")
        self.central_widget.setMinimumSize(QSize(200, 0))
        self.verticalLayout_2 = QVBoxLayout(self.central_widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.header = Header(self.central_widget)
        self.header.setObjectName(u"header")
        self.header.setMinimumSize(QSize(0, 20))
        font = QFont()
        font.setBold(True)
        self.header.setFont(font)

        self.verticalLayout.addWidget(self.header)

        self.face = QGroupBox(self.central_widget)
        self.face.setObjectName(u"face")
        self.face.setBaseSize(QSize(0, 0))
        self.verticalLayout_6 = QVBoxLayout(self.face)
        self.verticalLayout_6.setSpacing(1)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.tb000 = PushButton(self.face)
        self.tb000.setObjectName(u"tb000")
        self.tb000.setMinimumSize(QSize(0, 20))
        self.tb000.setMaximumSize(QSize(16777215, 20))
        self.tb000.setCheckable(False)

        self.verticalLayout_6.addWidget(self.tb000)

        self.tb002 = PushButton(self.face)
        self.tb002.setObjectName(u"tb002")
        self.tb002.setMinimumSize(QSize(0, 20))
        self.tb002.setMaximumSize(QSize(16777215, 20))
        self.tb002.setCheckable(False)

        self.verticalLayout_6.addWidget(self.tb002)

        self.tb001 = PushButton(self.face)
        self.tb001.setObjectName(u"tb001")
        self.tb001.setMinimumSize(QSize(0, 20))
        self.tb001.setMaximumSize(QSize(16777215, 20))
        self.tb001.setCheckable(False)

        self.verticalLayout_6.addWidget(self.tb001)

        self.tb003 = PushButton(self.face)
        self.tb003.setObjectName(u"tb003")
        self.tb003.setMinimumSize(QSize(0, 20))
        self.tb003.setMaximumSize(QSize(16777215, 20))
        self.tb003.setCheckable(False)

        self.verticalLayout_6.addWidget(self.tb003)

        self.tb005 = PushButton(self.face)
        self.tb005.setObjectName(u"tb005")
        self.tb005.setMinimumSize(QSize(0, 20))
        self.tb005.setMaximumSize(QSize(16777215, 20))
        self.tb005.setCheckable(False)

        self.verticalLayout_6.addWidget(self.tb005)

        self.tb006 = PushButton(self.face)
        self.tb006.setObjectName(u"tb006")
        self.tb006.setMinimumSize(QSize(0, 20))
        self.tb006.setMaximumSize(QSize(16777215, 20))
        self.tb006.setCheckable(False)

        self.verticalLayout_6.addWidget(self.tb006)

        self.tb004 = PushButton(self.face)
        self.tb004.setObjectName(u"tb004")
        self.tb004.setMinimumSize(QSize(0, 20))
        self.tb004.setMaximumSize(QSize(16777215, 20))
        self.tb004.setCheckable(False)

        self.verticalLayout_6.addWidget(self.tb004)

        self.b000 = QPushButton(self.face)
        self.b000.setObjectName(u"b000")
        self.b000.setEnabled(True)
        self.b000.setMinimumSize(QSize(0, 20))
        self.b000.setMaximumSize(QSize(16777215, 20))
        self.b000.setIconSize(QSize(18, 18))

        self.verticalLayout_6.addWidget(self.b000)


        self.verticalLayout.addWidget(self.face)

        self.groupBox = QGroupBox(self.central_widget)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setSpacing(1)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.b002 = QPushButton(self.groupBox)
        self.b002.setObjectName(u"b002")
        self.b002.setEnabled(True)
        self.b002.setMinimumSize(QSize(0, 20))
        self.b002.setMaximumSize(QSize(16777215, 20))
        self.b002.setIconSize(QSize(18, 18))

        self.gridLayout.addWidget(self.b002, 1, 1, 1, 1)

        self.b001 = QPushButton(self.groupBox)
        self.b001.setObjectName(u"b001")
        self.b001.setEnabled(True)
        self.b001.setMinimumSize(QSize(0, 20))
        self.b001.setMaximumSize(QSize(16777215, 20))
        self.b001.setIconSize(QSize(18, 18))

        self.gridLayout.addWidget(self.b001, 0, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        QtUi.setCentralWidget(self.central_widget)

        self.retranslateUi(QtUi)

        QMetaObject.connectSlotsByName(QtUi)
    # setupUi

    def retranslateUi(self, QtUi):
        self.header.setText(QCoreApplication.translate("QtUi", u"ANIMATION", None))
        self.face.setTitle(QCoreApplication.translate("QtUi", u"Keyframes", None))
#if QT_CONFIG(tooltip)
        self.tb000.setToolTip(QCoreApplication.translate("QtUi", u"<html><head/><body><p>Set the current frame on the timeslider.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.tb000.setText(QCoreApplication.translate("QtUi", u"Go to Frame", None))
#if QT_CONFIG(tooltip)
        self.tb002.setToolTip(QCoreApplication.translate("QtUi", u"Add or remove spacing between all keys at a given time for any currently selected objects.", None))
#endif // QT_CONFIG(tooltip)
        self.tb002.setText(QCoreApplication.translate("QtUi", u"Adjust Spacing", None))
#if QT_CONFIG(tooltip)
        self.tb001.setToolTip(QCoreApplication.translate("QtUi", u"<html><head/><body><p>Duplicate any selected keyframes and paste them inverted at the given time.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.tb001.setText(QCoreApplication.translate("QtUi", u"Invert Selected Keys", None))
#if QT_CONFIG(tooltip)
        self.tb003.setToolTip(QCoreApplication.translate("QtUi", u"Stagger the keyframes of selected objects such that the keyframes of each subsequent object start after the previous object.", None))
#endif // QT_CONFIG(tooltip)
        self.tb003.setText(QCoreApplication.translate("QtUi", u"Stagger Keys", None))
#if QT_CONFIG(tooltip)
        self.tb005.setToolTip(QCoreApplication.translate("QtUi", u"Stagger the keyframes of selected objects such that the keyframes of each subsequent object start after the previous object.", None))
#endif // QT_CONFIG(tooltip)
        self.tb005.setText(QCoreApplication.translate("QtUi", u"Add Intermediate Keys", None))
#if QT_CONFIG(tooltip)
        self.tb006.setToolTip(QCoreApplication.translate("QtUi", u"<html><head/><body><p>Move the selected keyframes to the current time with the selected option, </p><p>Else move all keyframes of the selected objects.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.tb006.setText(QCoreApplication.translate("QtUi", u"Move Keys", None))
#if QT_CONFIG(tooltip)
        self.tb004.setToolTip(QCoreApplication.translate("QtUi", u"Transfer keyframes from the first selected object to the subsequent objects.", None))
#endif // QT_CONFIG(tooltip)
        self.tb004.setText(QCoreApplication.translate("QtUi", u"Transfer Keys", None))
#if QT_CONFIG(tooltip)
        self.b000.setToolTip(QCoreApplication.translate("QtUi", u"<html><head/><body><p>Deletes <span style=\" font-weight:600;\">ALL</span> keyframes for the currently selected object(s).</p><p>If specific attributes are selected in the channel box, only keyframes for those attributes will be deleted.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.b000.setText(QCoreApplication.translate("QtUi", u"Delete Keys", None))
        self.groupBox.setTitle(QCoreApplication.translate("QtUi", u"Channel Box", None))
#if QT_CONFIG(tooltip)
        self.b002.setToolTip(QCoreApplication.translate("QtUi", u"<html><head/><body><p>Sets keys matching any previously stored attributes at the current time.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.b002.setText(QCoreApplication.translate("QtUi", u"Paste Keys", None))
#if QT_CONFIG(tooltip)
        self.b001.setToolTip(QCoreApplication.translate("QtUi", u"<html><head/><body><p>Stores the current values of any selected attributes in Maya's channel box for the currently selected scene objects.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.b001.setText(QCoreApplication.translate("QtUi", u"Copy Keys", None))
        pass
    # retranslateUi


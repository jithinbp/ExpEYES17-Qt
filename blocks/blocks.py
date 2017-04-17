#!/usr/bin/python
# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-

from __future__ import print_function

license="""\
  Copyright (C) 2017 Georges Khaznadar <georgesk@debian.org>

  Application Expeyes-Blocks

  This application may be used under the terms of the
  GNU General Public License version 3.0 as published by
  the Free Software Foundation, or, at your preference,
   any later verion of the same.

  Expeyes-Blocks is built upon Qt4 GUI libraries, see "About Qt".

  This application is provided AS IS with NO WARRANTY OF ANY KIND,
  INCLUDING THE WARRANTY OF DESIGN, MERCHANTABILITY AND
  FITNESS FOR A PARTICULAR PURPOSE.
"""

version="0.4"

import copy, re
from os.path import basename

from PyQt4.QtCore import QPoint, QRect, Qt, QSize, QString, \
	QTimer, QFileInfo, SIGNAL, QByteArray

from PyQt4.QtGui import QMainWindow, QApplication, \
	QMessageBox, QFileDialog

from templates.ui_blocks import Ui_MainWindow
from component import Component, InputComponent
from timecomponent import TimeComponent
from modifcomponent import ModifComponent
from channelcomponent import ChannelComponent


class BlockMainWindow(QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):
		QMainWindow.__init__(self, parent)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)
		self.loadComponents()
		self.connectSignals()
		self.fileName=None
		self.dirty="" # may become "*"
		return

	def loadComponents(self, path=None):
		self.widget.clear()
		cList=Component.listFromRC()
		for c in cList:
			self.componentsList.newComponent(c)
		return

	def connectSignals(self):
		"""
		connecting signals to methods
		"""
		self.action_Quit.triggered.connect(self.close)
		self.actionSave.triggered.connect(self.save)
		self.actionSave_as.triggered.connect(self.saveAs)
		self.action_Open.triggered.connect(self.load)
		self.action_About.triggered.connect(self.about)
		self.actionAbout_Qt.triggered.connect(self.aboutQt)
		self.widget.blocksChanged.connect(self.makeDirty)
		
	def about(self):
		"""
		brings up the About dialog
		"""
		QMessageBox.about(self,"About", license)
		return
		
	def aboutQt(self):
		"""
		brings up the About dialog
		"""
		QMessageBox.aboutQt(self,"About Qt")
		return
		
	versionPattern=re.compile(r"^Expeyes-Blocks version ([\.\d]+)$")
	classPattern  =re.compile(r"^Class Name \((\d+) bytes\)$")
	blobPattern   =re.compile(r"^Blob \((\d+) bytes\)$")
		
	def load(self):
		"""
		Loads a component composition
		"""
		fileName=QFileDialog.getOpenFileName(self,
			"Open a file",
			filter="Expeyes-Blocks:  *.eyeblk (*.eyeblk);;All files: * (*)"
		)
		ok=False
		cur=0
		with open(fileName,"rb") as instream:
			s=instream.readline()
			thisVersion=self.versionPattern.match(s).group(1)
			# take a decision about thisVersion
			components=[]
			nameSize = instream.readline()
			while nameSize:
				size=int(self.classPattern.match(nameSize).group(1))
				className=instream.readline().strip()
				if len(className) != size:
					raise Exception("Error size: %s does not match %s" %(size, className))
				s=instream.readline()
				blobSize=int(self.blobPattern.match(s).group(1))
				blob=QByteArray(instream.read(blobSize))
				obj, dataStream, className = eval("%s.unserialize(blob)" %className)
				components.append(obj)
				# prepare next iteration
				nameSize = instream.readline()
			if components:
				ok=True
				self.widget.components=components
				self.widget.update()
				for c in components:
					self.componentsList.hideItem(c)
		if ok: 
			self.fileName=fileName
			self.dirty=False
			self.setWindowTitle(self.currentTitle())
		return
		
	def save(self):
		"""
		Saves the current component composition
		"""
		if self.fileName:
			with open(self.fileName,"wb") as outstream:
				outstream.write("Expeyes-Blocks version %s\n" %version)
				for c in self.widget.components:
					c.save(outstream)
			self.dirty=""
			self.setWindowTitle(self.currentTitle())
		else:
			self.saveAs()
		return
		
	def saveAs(self, fileName=None):
		"""
		Saves the current component composition in a new file
		@param fileName name of the file, defaults to None
		"""
		if fileName: self.fileName=fileName
		if not self.fileName:
			self.fileName = "untitled.eyeblk"
		self.fileName=QFileDialog.getSaveFileName(
			self, "Save to file", self.fileName,
			filter = "Expeyes-Blocks:  *.eyeblk (*.eyeblk);;All files: * (*)"
		)
		if self.fileName:
			self.save()
		return
		
	def makeDirty(self):
		self.dirty="*"
		self.setWindowTitle(self.currentTitle())
		return
		
	def closeEvent(self, event):
        ok = True
        if self.dirty:
			ok=QMessageBox.question(
				self, "Please confirm", """\
The current work is not yet saved,
do you really want to quit the application?
""",
				QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes
        if ok:
			QMainWindow.closeEvent(self,event)
            event.accept() # let the window close
        else:
            event.ignore()
        return

	def currentTitle(self):
		"""
		@return curren title of the main window, taking in account
		the file name and a dirty flag
		"""
		return "Blocks (%s)%s" %(basename(str(self.fileName)), self.dirty)
		
		
if __name__ == '__main__':

	import sys

	app = QApplication(sys.argv)
	window = BlockMainWindow()
	window.show()
	sys.exit(app.exec_())

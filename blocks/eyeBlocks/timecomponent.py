# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
############################################################################
#
#  Copyright (C) 2017 Georges Khaznadar <georgesk@debian.org>
#
#
#  This file may be used under the terms of the GNU General Public
#  License version 3.0 as published by the Free Software Foundation,
#  or, at your preference, any later verion of the same.
#
#  This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
#  WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import print_function

from PyQt4 import QtCore, QtGui
from component import InputComponent, Component

def _translate(context, text, disambig):
	return QtGui.QApplication.translate(context, unicode(text), disambig)
        

class TimeComponent(InputComponent):
	"""
	A component to implement a time base for an oscilloscope
	"""
	# standard numbers of points
	np = [11, 101, 501, 1001, 2001]

	def __init__(*args,**kw):
		InputComponent.__init__(*args,**kw)
		self=args[0]
		self.initDefaults()
		for a in ("npoints","delay","duration"):
			if a in kw:
				setattribute(self, a, kw[a])
				
	def __str__(self):
		result=super(self.__class__,self).__str__()
		result+="\n  npoints = %s delay = %s duration = %s" %(self.npoints, self.delay, self.duration)
		return result

	def initDefaults(self):
		self.npoints = TimeComponent.np[2]
		self.delay   = 1000 # µs
		self.duration = (self.npoints-1)*self.delay


	def draw(self, painter):
		super(TimeComponent, self).draw(painter)
		lh=12 # lineheight
		x=10;y=15
		pos=self.rect.topLeft()
		titlePos=pos+QtCore.QPoint(x,y)
		x=15; y+=lh
		delayPos=pos+QtCore.QPoint(x,y)
		y+=lh
		durationPos=pos+QtCore.QPoint(x,y)
		y+=lh
		pointsPos=pos+QtCore.QPoint(x,y)
		painter.drawText(titlePos,_translate("eyeBlocks.timecomponent","Time Base",None))
		painter.drawText(delayPos,_translate("eyeBlocks.timecomponent","delay: %1 s",None).arg(self.delay/1e6))
		painter.drawText(durationPos,_translate("eyeBlocks.timecomponent","duration: %1 s",None) .arg(self.duration/1e6))
		painter.drawText(pointsPos,_translate("eyeBlocks.timecomponent","(%1 points)",None).arg(self.npoints))

	def getMoreData(self, dataStream):
		delay=QtCore.QVariant()
		duration=QtCore.QVariant()
		npoints=QtCore.QVariant()
		dataStream >> delay >> duration >> npoints
		self.delay, report=delay.toInt()
		self.duration, report=delay.toInt()
		self.npoints, report=npoints.toInt()
		return

	def putMoreData(self, dataStream):
		dataStream << QtCore.QVariant(self.delay) << QtCore.QVariant(self.duration) << QtCore.QVariant(self.npoints)
		return

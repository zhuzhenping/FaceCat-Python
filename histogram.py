# -*- coding:utf-8 -*-
#! python3

# FaceCat-Python-Wasm(OpenSource)
#Shanghai JuanJuanMao Information Technology Co., Ltd 

import win32gui
import win32api
from win32con import *
import math
import time
from facecat import *
import facecat
import timer
import random
try:
    import thread
except ImportError:
    import _thread as thread

#更新悬浮状态
#views:视图集合
def updateView(views):
	for i in range(0,len(views)):
		view = views[i]
		if(view.m_dock == "fill"):
			if(view.m_parent != None and view.m_parent.m_type != "split"):
				view.m_location = FCPoint(0, 0)
				view.m_size = FCSize(view.m_parent.m_size.cx, view.m_parent.m_size.cy)
		if(view.m_type == "split"):
			resetSplitLayoutDiv(view)
		elif(view.m_type == "tabview"):
			updateTabLayout(view)
		elif(view.m_type == "layout"):
			resetLayoutDiv(view)
		if(view.m_name == "price"):
			view.m_columns[0].m_width = view.m_size.cx
		subViews = view.m_views
		if(len(subViews) > 0):
			updateView(subViews)

#绘制视图
#view:视图
#paint:绘图对象
#clipRect:区域
def onViewPaint(view, paint, clipRect):
	if(view.m_type == "radiobutton"):
		drawRadioButton(view, paint, clipRect)
	elif(view.m_type == "checkbox"):
		drawCheckBox(view, paint, clipRect)
	elif(view.m_type == "chart"):
		resetChartVisibleRecord(view)
		checkChartLastVisibleIndex(view)
		onCalculateChartMaxMin(view)
		drawChart(view, paint, clipRect)
	elif(view.m_type == "grid"):
		drawDiv(view, paint, clipRect)
		drawGrid(view, paint, clipRect)
	elif(view.m_type == "tree"):
		drawDiv(view, paint, clipRect)
		drawTree(view, paint, clipRect)
	elif(view.m_type == "label"):
		if(view.m_textColor != "none"):
			tSize = paint.textSize(view.m_text, view.m_font)
			paint.drawText(view.m_text, view.m_textColor, view.m_font, 0, (view.m_size.cy - tSize.cy) / 2)
	elif(view.m_type == "div" or view.m_type =="tabpage" or view.m_type =="tabview" or view.m_type =="layout"):
		drawDiv(view, paint, clipRect)
	else:
		drawButton(view, paint, clipRect)

#绘制视图边线
#view:视图
#paint:绘图对象
#clipRect:区域
def onViewPaintBorder(view, paint, clipRect):
	if(view.m_type == "grid"):
		drawGridScrollBar(view, paint, clipRect)
	elif(view.m_type == "tree"):
		drawTreeScrollBar(view, paint, clipRect)
	elif(view.m_type == "div" or view.m_type =="tabpage" or view.m_type =="tabview" or view.m_type =="layout"):
		drawDivScrollBar(view, paint, clipRect)
		drawDivBorder(view, paint, clipRect)

#视图的鼠标移动方法
#view 视图
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
def onViewMouseMove(view, mp, buttons, clicks, delta):
	firstTouch = FALSE
	secondTouch = FALSE
	firstPoint = mp
	secondPoint = mp
	if (buttons == 1):
		firstTouch = TRUE
	if (view.m_type == "grid"):
		mouseMoveGrid(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif (view.m_type == "tree"):
		mouseMoveTree(view, firstTouch, secondTouch, firstPoint, secondPoint)
	elif(view.m_type == "chart"):
		mouseMoveChart(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "div" or view.m_type =="layout"):
		mouseMoveDiv(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "button"):
		invalidateView(view, view.m_paint)
		
#视图的鼠标按下方法
#view 视图
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
def onViewMouseDown(view, mp, buttons, clicks, delta):
	global m_addingPlot_Chart
	firstTouch = FALSE
	secondTouch = FALSE
	firstPoint = mp
	secondPoint = mp
	if (buttons == 1):
		firstTouch = TRUE
	if (view.m_type == "grid"):
		mouseDownGrid(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif (view.m_type == "tree"):
		mouseDownTree(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "chart"):
		view.m_selectShape = ""
		view.m_selectShapeEx = ""
		facecat.m_mouseDownPoint_Chart = mp;
		if (view.m_sPlot == None):
			selectShape(view, mp)
	elif(view.m_type == "div" or view.m_type =="layout"):
		mouseDownDiv(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "button"):
		invalidateView(view, view.m_paint)

#视图的鼠标抬起方法
#view 视图
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
def onViewMouseUp(view, mp, buttons, clicks, delta):
	firstTouch = FALSE
	secondTouch = FALSE
	firstPoint = mp
	secondPoint = mp
	if (buttons == 1):
		firstTouch = TRUE
	if (view.m_type == "grid"):
		mouseUpGrid(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif (view.m_type == "tree"):
		mouseUpTree(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif (view.m_type == "div" or view.m_type =="layout"):
		mouseUpDiv(view, firstTouch, secondTouch, firstPoint, secondPoint)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "chart"):
		facecat.m_firstTouchIndexCache_Chart = -1
		facecat.m_secondTouchIndexCache_Chart = -1
		invalidateView(view, view.m_paint)
	elif(view.m_type == "button"):
		invalidateView(view, view.m_paint)

#视图的鼠标点击方法
#view 视图
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
def onViewClick(view, mp, buttons, clicks, delta):
	global m_addingPlot_Chart
	if(view.m_type == "radiobutton"):
		clickRadioButton(view, mp)
		if(view.m_parent != None):
			invalidateView(view.m_parent, view.m_parent.m_paint)
		else:
			invalidateView(view, view.m_paint)
	elif(view.m_type == "checkbox"):
		clickCheckBox(view, mp)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "tabbutton"):
		tabView = view.m_parent
		for i in range(0, len(tabView.m_tabPages)):
			if(tabView.m_tabPages[i].m_headerButton == view):
				selectTabPage(tabView, tabView.m_tabPages[i])
		invalidateView(tabView, tabView.m_paint)

#视图的鼠标滚动方法
#view 视图
#mp 坐标
#buttons 按钮 0未按下 1左键 2右键
#clicks 点击次数
#delta 滚轮值
def onViewMouseWheel(view, mp, buttons, clicks, delta):
	if (view.m_type == "grid"):
		mouseWheelGrid(view, delta)
		invalidateView(view, view.m_paint)
	elif (view.m_type == "tree"):
		mouseWheelTree(view, delta)
		invalidateView(view, view.m_paint)
	elif (view.m_type == "div" or view.m_type =="layout"):
		mouseWheelDiv(view, delta)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "chart"):
		if(delta > 0):
			zoomOutChart(view);
		elif(delta < 0):
			zoomInChart(view);
		invalidateView(view, view.m_paint)
	if(view.m_type == "ldata"):
		mouseWheelDiv(view.m_parent, delta)
		invalidateView(view.m_parent, view.m_parent.m_paint)

#重新计算最大最小值
def onCalculateChartMaxMin(chart):
	chart.m_candleMax = 0
	chart.m_candleMin = 0
	chart.m_volMax = 0
	chart.m_volMin = 0
	chart.m_indMin = 0
	chart.m_indMin = 0
	if (chart.m_data != None and len(chart.m_data) > 0):
		lastValidIndex = chart.m_lastVisibleIndex
		if(chart.m_lastValidIndex != -1):
			lastValidIndex = chart.m_lastValidIndex
		for i in range(chart.m_firstVisibleIndex, lastValidIndex + 1):
			total = chart.m_data[i].m_data1 + chart.m_data[i].m_data2 + chart.m_data[i].m_data3 + chart.m_data[i].m_data4 + chart.m_data[i].m_data5 + chart.m_data[i].m_data6
			if (i == chart.m_firstVisibleIndex):
				chart.m_candleMax = total
				chart.m_candleMin = 0
			else:
				if (chart.m_candleMax < total):
					chart.m_candleMax = total

#绘制K线
#chart:K线
#paint:绘图对象
#clipRect:裁剪区域
def onPaintChartStock(chart, paint, clipRect):
	global m_drawColors
	if (chart.m_data != None and len(chart.m_data) > 0):
		lastValidIndex = chart.m_lastVisibleIndex;
		if(chart.m_lastValidIndex != -1):
			lastValidIndex = chart.m_lastValidIndex
		for i in range(chart.m_firstVisibleIndex, lastValidIndex + 1):
			x = getChartX(chart, i)
			y1 = getChartY(chart, 0, chart.m_data[i].m_data1)
			zeroY =  getChartY(chart, 0, 0)
			dWidth = chart.m_hScalePixel / 3
			paint.fillRect(m_drawColors[0], x - dWidth, y1, x + dWidth, zeroY)
			y2 = getChartY(chart, 0, chart.m_data[i].m_data1 + chart.m_data[i].m_data2)
			paint.fillRect(m_drawColors[1], x - dWidth, y2, x + dWidth, y1)
			y3 = getChartY(chart, 0, chart.m_data[i].m_data1 + chart.m_data[i].m_data2 + chart.m_data[i].m_data3)
			paint.fillRect(m_drawColors[2], x - dWidth, y3, x + dWidth, y2)
			y4 = getChartY(chart, 0, chart.m_data[i].m_data1 + chart.m_data[i].m_data2 + chart.m_data[i].m_data3 + chart.m_data[i].m_data4)
			paint.fillRect(m_drawColors[3], x - dWidth, y4, x + dWidth, y3)
			y5 = getChartY(chart, 0, chart.m_data[i].m_data1 + chart.m_data[i].m_data2 + chart.m_data[i].m_data3 + chart.m_data[i].m_data4 + chart.m_data[i].m_data5)
			paint.fillRect(m_drawColors[4], x - dWidth, y5, x + dWidth, y4)
			y6 = getChartY(chart, 0, chart.m_data[i].m_data1 + chart.m_data[i].m_data2 + chart.m_data[i].m_data3 + chart.m_data[i].m_data4 + chart.m_data[i].m_data5  + chart.m_data[i].m_data6)
			paint.fillRect(m_drawColors[5], x - dWidth, y6, x + dWidth, y5)
			if (chart.m_paint.m_defaultUIStyle == "dark"):
				paint.drawRect("rgb(255,255,255)", 1, 0, x - dWidth, y6, x + dWidth, zeroY)
			elif (chart.m_paint.m_defaultUIStyle == "light"):
				paint.drawRect("rgb(0,0,0)", 1, 0, x - dWidth, y6, x + dWidth, zeroY)

#绘制十字线
#chart:K线
#paint:绘图对象
#clipRect:裁剪区域
def onPaintChartCrossLine(chart, paint, clipRect):
	global m_drawColors
	if (chart.m_data != None and len(chart.m_data) > 0):
		candleDivHeight = getCandleDivHeight(chart)
		volDivHeight = getVolDivHeight(chart)
		indDivHeight = getIndDivHeight(chart)
		crossLineIndex = chart.m_crossStopIndex
		if (crossLineIndex == -1):
			crossLineIndex = chart.m_lastVisibleIndex
		drawTitles = []
		drawTitles.append("项目1 " + toFixed(chart.m_data[crossLineIndex].m_data1, chart.m_candleDigit))
		drawTitles.append("项目2 " + toFixed(chart.m_data[crossLineIndex].m_data2, chart.m_candleDigit))
		drawTitles.append("项目3 " + toFixed(chart.m_data[crossLineIndex].m_data3, chart.m_candleDigit))
		drawTitles.append("项目4 " + toFixed(chart.m_data[crossLineIndex].m_data4, chart.m_candleDigit))
		drawTitles.append("项目5 " + toFixed(chart.m_data[crossLineIndex].m_data5, chart.m_candleDigit))
		drawTitles.append("项目6 " + toFixed(chart.m_data[crossLineIndex].m_data6, chart.m_candleDigit))

		iLeft = chart.m_leftVScaleWidth + 5
		for i in range(0, len(drawTitles)):
			tSize = paint.textSize(drawTitles[i], chart.m_font)
			paint.drawText(drawTitles[i], m_drawColors[i], chart.m_font, iLeft, 5 + tSize.cy / 2)
			iLeft += tSize.cx + 5

m_paint = FCPaint() #创建绘图对象
facecat.m_paintCallBack = onViewPaint 
facecat.m_paintBorderCallBack = onViewPaintBorder 
facecat.m_mouseDownCallBack = onViewMouseDown 
facecat.m_mouseMoveCallBack = onViewMouseMove 
facecat.m_mouseUpCallBack = onViewMouseUp
facecat.m_mouseWheelCallBack = onViewMouseWheel
facecat.m_clickCallBack = onViewClick
facecat.m_calculteMaxMin = onCalculateChartMaxMin
facecat.m_paintChartStock = onPaintChartStock
facecat.m_paintChartCrossLine = onPaintChartCrossLine

def WndProc(hwnd,msg,wParam,lParam):
	if msg == WM_DESTROY:
		win32gui.PostQuitMessage(0)
	if(hwnd == m_paint.m_hWnd):
		if msg == WM_ERASEBKGND:
			return 1
		elif msg == WM_SIZE:
			rect = win32gui.GetClientRect(m_paint.m_hWnd)
			m_paint.m_size = FCSize(rect[2] - rect[0], rect[3] - rect[1])
			for view in m_paint.m_views:
				if view.m_dock == "fill":
					view.m_size = FCSize(m_paint.m_size.cx, m_paint.m_size.cy)
			updateView(m_paint.m_views)
			invalidate(m_paint)
		elif msg == WM_LBUTTONDOWN:
			mx, my = win32api.GetCursorPos()
			ccx, ccy = win32gui.ScreenToClient(hwnd, (mx, my))
			mp = FCPoint(ccx, ccy)
			onMouseDown(mp, 1, 1, 0, m_paint)
		elif msg == WM_LBUTTONUP:
			mx, my = win32api.GetCursorPos()
			ccx, ccy = win32gui.ScreenToClient(hwnd, (mx, my))
			mp = FCPoint(ccx, ccy)
			onMouseUp(mp, 1, 1, 0, m_paint)
		elif msg == WM_MOUSEWHEEL:
			mx, my = win32api.GetCursorPos()
			ccx, ccy = win32gui.ScreenToClient(hwnd, (mx, my))
			mp = FCPoint(ccx, ccy)
			if(wParam > 4000000000):
				onMouseWheel(mp, 0, 0, -1, m_paint)
			else:
				onMouseWheel(mp, 0, 0, 1, m_paint)
		elif msg == WM_MOUSEMOVE:
			mx, my = win32api.GetCursorPos()
			ccx, ccy = win32gui.ScreenToClient(hwnd, (mx, my))
			mp = FCPoint(ccx, ccy)
			if(wParam == 1):
				onMouseMove(mp, 1, 1, 0, m_paint)
			elif(wParam == 2):
				onMouseMove(mp, 2, 1, 0, m_paint)
			else:
				onMouseMove(mp, 0, 0, 0, m_paint)
		elif msg == WM_PAINT:
			rect = win32gui.GetClientRect(m_paint.m_hWnd)
			m_paint.m_size = FCSize(rect[2] - rect[0], rect[3] - rect[1])
			for view in m_paint.m_views:
				if view.m_dock == "fill":
					view.m_size = FCSize(m_paint.m_size.cx, m_paint.m_size.cy)
			updateView(m_paint.m_views)
			invalidate(m_paint)
	return win32gui.DefWindowProc(hwnd,msg,wParam,lParam)

wc = win32gui.WNDCLASS()
wc.hbrBackground = COLOR_BTNFACE + 1
wc.hCursor = win32gui.LoadCursor(0,IDI_APPLICATION)
wc.lpszClassName = "facecat-py"
wc.lpfnWndProc = WndProc
reg = win32gui.RegisterClass(wc)
hwnd = win32gui.CreateWindow(reg,'facecat-py',WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN,CW_USEDEFAULT,CW_USEDEFAULT,CW_USEDEFAULT,CW_USEDEFAULT,0,0,0,None)
m_paint.m_hWnd = hwnd

m_drawColors = []
m_drawColors.append("rgb(59,174,218)")
m_drawColors.append("rgb(185,63,150)")
m_drawColors.append("rgb(219,68,83)")
m_drawColors.append("rgb(246,187,67)")
m_drawColors.append("rgb(216,112,173)")
m_drawColors.append("rgb(140,192,81)")
m_drawColors.append("rgb(233,87,62)")
m_drawColors.append("rgb(150,123,220)")
m_drawColors.append("rgb(75,137,220)")
m_drawColors.append("rgb(170,178,189)")

m_histogram = FCChart()
m_histogram.m_dock = "fill"
m_histogram.m_leftVScaleWidth = 70
m_histogram.m_rightVScaleWidth = 0
m_histogram.m_vScaleDistance = 60
m_histogram.m_hScalePixel = 50
m_histogram.m_hScaleHeight = 30
m_histogram.m_candleDivPercent = 1
m_histogram.m_volDivPercent = 0
m_histogram.m_indDivPercent = 0
m_histogram.m_cycle = "tick"
m_histogram.m_scaleColor = "rgb(100,100,100)"
m_histogram.m_crossTipColor = "rgb(50,50,50)"
m_histogram.m_crossLineColor = "rgb(100,100,100)"
m_histogram.m_gridColor = "rgba(100,100,100,0.5)"
m_histogram.m_textColor = "rgb(255,255,255)"
addView(m_histogram, m_paint)

#检查CTP的数据
def checkNewData(a='', b=''):
	global m_paint
	global m_histogram
	data = SecurityData()
	data.m_close = 0
	data.m_date = len(m_histogram.m_data)
	data.m_data1 = random.randint(0,100) - 50
	data.m_data2 = random.randint(0,100) - 50
	data.m_data3 = random.randint(0,100) - 50
	data.m_data4 = random.randint(0,100) - 50
	data.m_data5 = random.randint(0,100) - 50
	data.m_data6 = random.randint(0,100) - 50
	if(data.m_data1 < 0):
		data.m_data1 = 0
	if(data.m_data2 < 0):
		data.m_data2 = 0
	if(data.m_data3 < 0):
		data.m_data3 = 0
	if(data.m_data4 < 0):
		data.m_data4 = 0
	if(data.m_data5 < 0):
		data.m_data5 = 0
	if(data.m_data6 < 0):
		data.m_data6 = 0
	m_histogram.m_data.append(data)
	resetChartVisibleRecord(m_histogram)
	checkChartLastVisibleIndex(m_histogram)
	onCalculateChartMaxMin(m_histogram)
	invalidate(m_paint)

timer.set_timer(50, checkNewData)

rect = win32gui.GetClientRect(hwnd)
m_paint.m_size = FCSize(rect[2] - rect[0], rect[3] - rect[1])
for view in m_paint.m_views:
	if view.m_dock == "fill":
		view.m_size = FCSize(m_paint.m_size.cx, m_paint.m_size.cy)
updateView(m_paint.m_views)
win32gui.ShowWindow(hwnd,SW_SHOWNORMAL)
win32gui.UpdateWindow(hwnd)
win32gui.PumpMessages()
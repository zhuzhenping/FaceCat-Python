# -*- coding:utf-8 -*-
#! python3

# FaceCat-Python-Wasm(OpenSource)
#Shanghai JuanJuanMao Information Technology Co., Ltd 

import win32gui
import win32api
from win32con import *
from xml.etree import ElementTree as ET
import math
import requests
import time
from requests.adapters import HTTPAdapter
from facecat import *
import facecat

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
		subViews = view.m_views
		if(len(subViews) > 0):
			updateView(subViews)

#绘制视图
#view:视图
#paint:绘图对象
#drawRect:区域
def onViewPaint(view, paint, drawRect):
	if(view.m_type == "radiobutton"):
		drawRadioButton(view, paint, drawRect)
	elif(view.m_type == "checkbox"):
		drawCheckBox(view, paint, drawRect)
	elif(view.m_type == "chart"):
		resetChartVisibleRecord(view)
		checkChartLastVisibleIndex(view)
		calculateChartMaxMin(view)
		drawChart(view, paint, drawRect)
	elif(view.m_type == "grid"):
		drawDiv(view, paint, drawRect)
		drawGrid(view, paint, drawRect)
	elif(view.m_type == "tree"):
		drawDiv(view, paint, drawRect)
		drawTree(view, paint, drawRect)
	elif(view.m_type == "label"):
		if(view.m_textColor != "none"):
			tSize = paint.textSize(view.m_text, view.m_font)
			paint.drawText(view.m_text, view.m_textColor, view.m_font, 0, (view.m_size.cy - tSize.cy) / 2)
	elif(view.m_type == "div" or view.m_type =="tabpage" or view.m_type =="tabview"):
		drawDiv(view, paint, drawRect)
	else:
		drawButton(view, paint, drawRect)

#绘制视图边线
#view:视图
#paint:绘图对象
#drawRect:区域
def onViewPaintBorder(view, paint, drawRect):
	if(view.m_type == "grid"):
		drawGridScrollBar(view, paint, drawRect)
	elif(view.m_type == "tree"):
		drawTreeScrollBar(view, paint, drawRect)
	elif(view.m_type == "div" or view.m_type =="tabpage" or view.m_type =="tabview"):
		drawDivScrollBar(view, paint, drawRect)
		drawDivBorder(view, paint, drawRect)

m_addingPlot_Chart = ""

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
	elif(view.m_type == "div"):
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
		if(len(m_addingPlot_Chart) > 0):
			if (mp.y < getCandleDivHeight(view)):
				touchIndex = getChartIndex(view, mp)
				if (touchIndex >= view.m_firstVisibleIndex and touchIndex <= view.m_lastVisibleIndex):
					if(m_addingPlot_Chart == "FiboTimezone"):
						fIndex = touchIndex
						fDate = getChartDateByIndex(view, fIndex)
						y = getCandleDivValue(view, mp)
						newPlot = FCPlot()
						if(view.m_paint.m_defaultUIStyle == "light"):
							newPlot.m_lineColor = "rgb(0,0,0)"
							newPlot.m_pointColor = "rgba(0,0,0,0.5)"
						newPlot.m_key1 = fDate
						newPlot.m_value1 = y
						newPlot.m_plotType = m_addingPlot_Chart
						view.m_plots.append(newPlot)
						view.m_sPlot = selectPlot(view, mp)
					elif (m_addingPlot_Chart == "Triangle" or m_addingPlot_Chart == "CircumCycle" or m_addingPlot_Chart == "ParalleGram" or m_addingPlot_Chart == "AngleLine" or m_addingPlot_Chart == "Parallel" or m_addingPlot_Chart == "SymmetricTriangle"):
						eIndex = touchIndex;
						bIndex = eIndex - 5;
						if (bIndex >= 0):
							fDate = getChartDateByIndex(view, bIndex)
							sDate = getChartDateByIndex(view, eIndex)
							y = getCandleDivValue(view, mp)
							newPlot = FCPlot()
							if(view.m_paint.m_defaultUIStyle == "light"):
								newPlot.m_lineColor = "rgb(0,0,0)"
								newPlot.m_pointColor = "rgba(0,0,0,0.5)"
							newPlot.m_key1 = fDate
							newPlot.m_value1 = y
							newPlot.m_key2 = sDate
							newPlot.m_value2 = y
							newPlot.m_key3 = sDate
							newPlot.m_value3 = view.m_candleMin + (view.m_candleMax - view.m_candleMin) / 2
							newPlot.m_plotType = m_addingPlot_Chart
							view.m_plots.append(newPlot)
							view.m_sPlot = selectPlot(view, mp)
					else:
						eIndex = touchIndex
						bIndex = eIndex - 5
						if (bIndex >= 0):
							fDate = getChartDateByIndex(view, bIndex)
							sDate = getChartDateByIndex(view, eIndex)
							y = getCandleDivValue(view, mp)
							newPlot = FCPlot()
							if(view.m_paint.m_defaultUIStyle == "light"):
								newPlot.m_lineColor = "rgb(0,0,0)"
								newPlot.m_pointColor = "rgba(0,0,0,0.5)"
							newPlot.m_key1 = fDate
							newPlot.m_value1 = y
							newPlot.m_key2 = sDate
							newPlot.m_value2 = y
							newPlot.m_plotType = m_addingPlot_Chart
							view.m_plots.append(newPlot)
							view.m_sPlot = selectPlot(view, mp)
			m_addingPlot_Chart = ""
		view.m_sPlot = selectPlot(view, mp)
		if (view.m_sPlot == None):
			selectShape(view, mp)
	elif(view.m_type == "div"):
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
	elif (view.m_type == "div"):
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
	elif(view.m_type == "plot"):
		m_addingPlot_Chart = view.m_text
	elif(view.m_type == "indicator"):
		if (view.m_text == "BOLL" or view.m_text == "MA"):
			m_chart.m_mainIndicator = view.m_text
		else:
			m_chart.m_showIndicator = view.m_text
		calcChartIndicator(m_chart)
		invalidateView(m_chart, m_chart.m_paint)

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
	elif (view.m_type == "div"):
		mouseWheelDiv(view, delta)
		invalidateView(view, view.m_paint)
	elif(view.m_type == "chart"):
		if(delta > 0):
			zoomOutChart(view);
		elif(delta < 0):
			zoomInChart(view);
		invalidateView(view, view.m_paint)

m_paint = FCPaint() #创建绘图对象
facecat.m_paintCallBack = onViewPaint 
facecat.m_paintBorderCallBack = onViewPaintBorder 
facecat.m_mouseDownCallBack = onViewMouseDown 
facecat.m_mouseMoveCallBack = onViewMouseMove 
facecat.m_mouseUpCallBack = onViewMouseUp
facecat.m_mouseWheelCallBack = onViewMouseWheel
facecat.m_clickCallBack = onViewClick

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
m_split = FCSplitLayoutDiv()
m_split.m_dock = "fill"
m_split.m_paint = m_paint
m_split.m_size = FCSize(400, 400)
m_paint.m_views.append(m_split)
m_chart = FCChart()
m_chart.m_leftVScaleWidth = 80
m_chart.m_textColor = "rgb(255,255,255)"
m_chart.m_paint = m_paint
m_chart.m_parent = m_split
m_chart.m_mainIndicator = "MA" 
m_chart.m_showIndicator = "MACD" 
m_split.m_views.append(m_chart)
m_layout = FCView()
m_layout.m_paint = m_paint
m_layout.m_type = "div"
m_layout.m_parent = m_split
m_layout.m_showHScrollBar = TRUE
m_layout.m_showVScrollBar = TRUE
m_layout.m_allowDragScroll = TRUE
m_layout.m_scrollSize = 0
m_split.m_views.append(m_layout)
m_splitter = FCView()
m_splitter.m_location = FCPoint(0, 340)
m_splitter.m_size = FCSize(400, 1)
m_splitter.m_paint = m_paint
m_splitter.m_parent = m_split
m_split.m_views.append(m_splitter)
m_split.m_firstView = m_layout
m_split.m_secondView = m_chart
m_split.m_splitter = m_splitter
m_split.m_layoutStyle = "bottomtotop"
m_split.m_oldSize = FCSize(400, 400)
plots = []
plots.append("Line")
plots.append("Segment")
plots.append("Ray")
plots.append("Triangle")
plots.append("Rect")
plots.append("Cycle")
plots.append("CircumCycle")
plots.append("Ellipse")
plots.append("AngleLine")
plots.append("ParalleGram")
plots.append("SpeedResist")
plots.append("FiboFanline")
plots.append("FiboTimezone")
plots.append("Percent")
plots.append("BoxLine")
plots.append("TironeLevels")
plots.append("Parallel")
plots.append("GoldenRatio")
plots.append("LRLine")
plots.append("LRChannel")
plots.append("LRBand")
for i in range(0, len(plots)):
	subView = FCView()
	subView.m_type = "plot"
	subView.m_text = plots[i]
	subView.m_name = plots[i]
	subView.m_location = FCPoint(i * 100 + 1, 1)
	subView.m_size = FCSize(98, 28)
	subView.m_paint = m_paint
	subView.m_parent = m_layout
	subView.m_allowDrag = TRUE
	m_layout.m_views.append(subView)
	if(subView.m_paint.m_defaultUIStyle == "dark"):
		subView.m_backColor = "rgb(0,0,0)"
		subView.m_borderColor = "rgb(100,100,100)"
		subView.m_textColor = "rgb(255,255,255)"
	elif(subView.m_paint.m_defaultUIStyle == "light"):
		subView.m_backColor = "rgb(255,255,255)"
		subView.m_borderColor = "rgb(150,150,150)"
		subView.m_textColor = "rgb(0,0,0)"
indicators = []
indicators.append("MA")
indicators.append("BOLL")
indicators.append("MACD")
indicators.append("KDJ")
indicators.append("BIAS")
indicators.append("ROC")
indicators.append("WR")
indicators.append("DMA")
indicators.append("RSI")
indicators.append("BBI")
indicators.append("CCI")
indicators.append("TRIX")
for i in range(0, len(indicators)):
	subView = FCView()
	subView.m_type = "indicator"
	subView.m_text = indicators[i]
	subView.m_name = indicators[i]
	subView.m_location = FCPoint(i * 100 + 1, 30)
	subView.m_size = FCSize(98, 28)
	subView.m_paint = m_paint
	subView.m_allowDrag = TRUE
	subView.m_parent = m_layout
	m_layout.m_views.append(subView)
	if(subView.m_paint.m_defaultUIStyle == "dark"):
		subView.m_backColor = "rgb(0,0,0)"
		subView.m_borderColor = "rgb(100,100,100)"
		subView.m_textColor = "rgb(255,255,255)"
	elif(subView.m_paint.m_defaultUIStyle == "light"):
		subView.m_backColor = "rgb(255,255,255)"
		subView.m_borderColor = "rgb(150,150,150)"
		subView.m_textColor = "rgb(0,0,0)"
resetSplitLayoutDiv(m_split)
try:
	s = requests.Session()
	s.mount('http://', HTTPAdapter(max_retries=3))
	response = s.get('http://quotes.money.163.com/service/chddata.html?code=0000001', timeout=5)
	text = response.text
	strs = text.split("\r\n")
	strLen = len(strs)
	pos = strLen - 2
	for i in range(0, strLen - 3):
		subStrs = strs[pos].split(",")
		if(len(subStrs) > 8):
			data = SecurityData()
			data.m_date = i
			data.m_close = float(subStrs[3])
			data.m_high = float(subStrs[4])
			data.m_low = float(subStrs[5])
			data.m_open = float(subStrs[6])
			data.m_volume = float(subStrs[11])
			m_chart.m_data.append(data)
		pos = pos - 1
except requests.exceptions.RequestException as e:
	print(e)
calcChartIndicator(m_chart)

rect = win32gui.GetClientRect(hwnd)
m_paint.m_size = FCSize(rect[2] - rect[0], rect[3] - rect[1])
for view in m_paint.m_views:
	if view.m_dock == "fill":
		view.m_size = FCSize(m_paint.m_size.cx, m_paint.m_size.cy)
updateView(m_paint.m_views)
win32gui.ShowWindow(hwnd,SW_SHOWNORMAL)
win32gui.UpdateWindow(hwnd)
win32gui.PumpMessages()
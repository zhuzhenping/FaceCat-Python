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
	elif(view.m_type == "div" or view.m_type =="tabpage" or view.m_type =="tabview" or view.m_type =="layout"):
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
	elif(view.m_type == "div" or view.m_type =="tabpage" or view.m_type =="tabview" or view.m_type =="layout"):
		drawDivScrollBar(view, paint, drawRect)
		drawDivBorder(view, paint, drawRect)

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

#创建列
#grid:表格
def createGridColumn(grid):
	gridColumn = FCGridColumn()
	if (grid.m_paint.m_defaultUIStyle == "dark"):
		gridColumn.m_backColor = "rgb(0,0,0)"
		gridColumn.m_borderColor = "rgb(150,150,150)"
		gridColumn.m_textColor = "rgb(255,255,255)"
	elif (grid.m_paint.m_defaultUIStyle == "light"):
		gridColumn.m_backColor = "rgb(200,200,200)"
		gridColumn.m_borderColor = "rgb(100,100,100)"
		gridColumn.m_textColor = "rgb(0,0,0)"
	return gridColumn
    
#创建列
#grid:表格
def createGridCell(grid):
	gridCell = FCGridCell()
	if (grid.m_paint.m_defaultUIStyle == "dark"):
		gridCell.m_backColor = "rgb(0,0,0)"
		gridCell.m_borderColor = "rgb(150,150,150)"
		gridCell.m_textColor = "rgb(255,255,255)"
	elif (grid.m_paint.m_defaultUIStyle == "light"):
		gridCell.m_backColor = "rgb(255,255,255)"
		gridCell.m_borderColor = "rgb(100,100,100)"
		gridCell.m_textColor = "rgb(0,0,0)"
	return gridCell

m_grid = FCGrid()
m_grid.m_paint = m_paint
if (m_grid.m_paint.m_defaultUIStyle == "dark"):
	m_grid.m_backColor = "rgb(0,0,0)"
	m_grid.m_borderColor = "rgb(100,100,100)"
	m_grid.m_textColor = "rgb(255,255,255)"
elif(m_grid.m_paint.m_defaultUIStyle == "light"):
	m_grid.m_backColor = "rgb(255,255,255)"
	m_grid.m_borderColor = "rgb(150,150,150)"
	m_grid.m_textColor = "rgb(0,0,0)"
        
m_grid.m_dock = "fill"
m_paint.m_views.append(m_grid)

column1 = createGridColumn(m_grid)
column1.m_text = "id"
column1.m_frozen = TRUE
column1.m_width = 90
m_grid.m_columns.append(column1)

column2 = createGridColumn(m_grid)
column2.m_text = "rank"
column2.m_width = 100
column2.m_frozen = TRUE
m_grid.m_columns.append(column2)

column3 = createGridColumn(m_grid)
column3.m_text = "symbol"
column3.m_width = 100
column3.m_frozen = TRUE
m_grid.m_columns.append(column3)

column4 = createGridColumn(m_grid)
column4.m_text = "name"
column4.m_width = 60
m_grid.m_columns.append(column4)

column10 = createGridColumn(m_grid)
column10.m_text = "changePercent24Hr"
m_grid.m_columns.append(column10)
column10.m_width = 140

column11 = createGridColumn(m_grid)
column11.m_text = "vwap24Hr"
m_grid.m_columns.append(column11)
column11.m_width = 140

column5 = createGridColumn(m_grid)
column5.m_text = "supply"
m_grid.m_columns.append(column5)

column6 = createGridColumn(m_grid)
column6.m_text = "maxSupply"
m_grid.m_columns.append(column6)

column7 = createGridColumn(m_grid)
column7.m_text = "marketCapUsd"
m_grid.m_columns.append(column7)

column8 = createGridColumn(m_grid)
column8.m_text = "volumeUsd24Hr"
m_grid.m_columns.append(column8)

column9 = createGridColumn(m_grid)
column9.m_text = "priceUsd"
m_grid.m_columns.append(column9)

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
			lastClose = 0
			if(subStrs[7] != "None"):
				lastClose = float(subStrs[7])
			if(m_grid != None):
				row = FCGridRow()
				m_grid.m_rows.append(row)
				for c in range(0, len(m_grid.m_columns)):
					cell = FCGridCell()
					if (m_grid.m_paint.m_defaultUIStyle == "dark"):
						cell.m_backColor = "rgb(0,0,0)"
					elif(m_grid.m_paint.m_defaultUIStyle == "light"):
						cell.m_backColor = "rgb(255,255,255)"
					if(c < len(subStrs)):
						cell.m_value = subStrs[c]
					row.m_cells.append(cell)
					if(cell.m_value != None):
						if(c >= 3 and c <= 6):
							if(float(cell.m_value) >= lastClose):
								cell.m_textColor = "rgb(219,68,83)"
							else:
								cell.m_textColor = "rgb(15,193,118)"
						elif(c == 0):
							cell.m_textColor = "rgb(255,255,0)"
						elif(c == 1):
							cell.m_textColor = "rgb(0,255,255)"
		pos = pos - 1
except requests.exceptions.RequestException as e:
	print(e)

rect = win32gui.GetClientRect(hwnd)
m_paint.m_size = FCSize(rect[2] - rect[0], rect[3] - rect[1])
for view in m_paint.m_views:
	if view.m_dock == "fill":
		view.m_size = FCSize(m_paint.m_size.cx, m_paint.m_size.cy)
updateView(m_paint.m_views)
win32gui.ShowWindow(hwnd,SW_SHOWNORMAL)
win32gui.UpdateWindow(hwnd)
win32gui.PumpMessages()
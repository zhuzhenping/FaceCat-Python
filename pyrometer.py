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
import websocket
#pip install websocket-client 
import json
import timer
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
		calculateChartMaxMin(view)
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
	elif (view.m_type == "pyrometer"):
		drawDiv(view, paint, clipRect)
	elif (view.m_type == "pdata"):
		backColor = "none"
		borderColor = "none"
		if (view.m_parent.m_paint.m_defaultUIStyle == "dark"):
			if(view.m_data["price"] >= view.m_firstPrice):
				backColor = "rgb(219,68,83)"
			else:
				backColor = "rgb(15,193,118)"
			borderColor = "rgb(0,0,0)"
		elif(view.m_parent.m_paint.m_defaultUIStyle == "light"):
			if(view.m_data["price"] >= view.m_firstPrice):
				backColor = "rgb(255,255,255)"
			else:
				backColor = "rgb(255,255,255)"
			borderColor = "rgb(255,255,255)"
		paint.fillRect(backColor, 0, 0, view.m_size.cx, view.m_size.cy)
		paint.drawRect(borderColor, 1, 0, 0, 0, view.m_size.cx, view.m_size.cy)
		fontSize1 = int(min(view.m_size.cx, view.m_size.cy) / 5)
		if(fontSize1 > 1):
			baseUpper = view.m_data["base"].upper()
			font1 = str(fontSize1) + "px Arial"
			tSize = paint.textSize(baseUpper, font1)
			while(tSize.cx > view.m_size.cx - 10):
				fontSize1 = fontSize1 - 1
				if(fontSize1 < 1):
					return
				font1 = str(fontSize1) + "px Arial"
				tSize = paint.textSize(baseUpper, font1)   
			quoteUpper = view.m_data["quote"].upper()
			font2 = str(fontSize1 / 2) + "px Arial"
			tSize2 = paint.textSize(quoteUpper, font2)
			if (view.m_parent.m_paint.m_defaultUIStyle == "dark"):
				paint.drawText(baseUpper, "rgb(255,255,255)", font1, (view.m_size.cx - tSize.cx) / 2, view.m_size.cy / 2 - tSize.cy)
				paint.drawText(quoteUpper, "rgb(255,255,255)", font2, (view.m_size.cx - tSize2.cx) / 2, view.m_size.cy / 2)
			elif (view.m_parent.m_paint.m_defaultUIStyle == "light"):
				paint.drawText(baseUpper, "rgb(0,0,0)", font1, (view.m_size.cx - tSize.cx) / 2, view.m_size.cy / 2 - tSize.cy)
				paint.drawText(quoteUpper, "rgb(0,0,0)", font2, (view.m_size.cx - tSize2.cx) / 2, view.m_size.cy / 2)
			strPrice = toFixed(view.m_data["price"], 6)
			font3 = str(fontSize1 * 2 / 3) + "px Arial"
			tSize5 = paint.textSize(strPrice, font3)
			if (view.m_parent.m_paint.m_defaultUIStyle == "dark"):
				paint.drawText(strPrice, "rgb(255,255,255)", font3, (view.m_size.cx - tSize5.cx) / 2, view.m_size.cy / 2 + tSize.cy)
			elif(view.m_parent.m_paint.m_defaultUIStyle == "light"):
				paint.drawText(strPrice, "rgb(0,0,0)", font3, (view.m_size.cx - tSize5.cx) / 2, view.m_size.cy / 2 + tSize.cy)
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

#面积图数据
class PyrometerData(FCView):
	def __init__(self):
		super().__init__()
		self.m_value = 0 #数值
		self.m_key = None
		self.m_firstPrice = None
		self.m_data = None
		self.m_type = "pdata"

#面积图
class PyrometerDiv(FCView):
	def __init__(self):
		super().__init__()
		self.m_useAnimation = FALSE #是否使用动画
		self.m_type = "pyrometer" #类型
		self.INF = 0x3f3f3f; #无效数据
		self.Rwidth = 0
		self.Rheight = 0;
	pass

def layoutrow(pyrometer, R, w):
	width = pyrometer.m_size.cx
	height = pyrometer.m_size.cy
	lx = width - pyrometer.Rwidth
	ly = height - pyrometer.Rheight
	direction = 0;  # 0: horizontal;  1: vertical

	# refresh Rwidth, Rheight
	sumValue = 0
	for x in range(0, len(R)):
		sumValue = sumValue + R[x]
	ext = sumValue / w
	if (abs(w - pyrometer.Rwidth) <= 1e-6):
		pyrometer.Rheight = pyrometer.Rheight - ext
		direction = 0
	else:
		pyrometer.Rwidth = pyrometer.Rwidth - ext
		direction = 1

	# store
	for x in range(0, len(R)):
		r = R[x]
		if (direction == 0):
			hh = ext
			ww = r / ext
			newRect = FCRect(0, 0, 0, 0)
			newRect.left = lx;
			newRect.top = ly;
			newRect.right = lx + ww;
			newRect.bottom = ly + hh;
			pyrometer.m_rects.append(newRect)
			# refresh
			lx = lx + ww
		else:
			ww = ext
			hh = r / ext
			newRect = FCRect(0, 0, 0, 0)
			newRect.left = lx;
			newRect.top = ly;
			newRect.right = lx + ww;
			newRect.bottom = ly + hh;
			pyrometer.m_rects.append(newRect)
			# refresh
			ly = ly + hh;

def rWidth(pyrometer, R, w):
	return min(pyrometer.Rwidth, pyrometer.Rheight)

def worst(pyrometer, R, w):
	if (len(R) == 0):
		return pyrometer.INF
	rmx = 0
	rmn = pyrometer.INF
	s = 0
	for x in range(0, len(R)):
		r = R[x]
		s = s + r
		if (r > rmx):
			rmx = r
		if (r < rmn):
			rmn = r
	pw = math.pow(w, 2)
	sw = math.pow(s, 2)
	return max(pw * rmx / sw, sw / (pw * rmn))

def onPyrometerTime(pyrometer):
	paint2 = FALSE
	if(pyrometer.m_useAnimation):
		for i in range(0, len(pyrometer.m_rects)):
			subView = pyrometer.m_views[i]
			targetRect = pyrometer.m_rects[i]
			nowRect = FCRect(subView.m_location.x, subView.m_location.y, subView.m_location.x + subView.m_size.cx, subView.m_location.y + subView.m_size.cy)
			if (1 == 1):
				if (nowRect.left > targetRect.left):
					nowRect.left -= (nowRect.left - targetRect.left) / 4
					if (nowRect.left - targetRect.left < 10):
						nowRect.left = targetRect.left
					paint2 = TRUE
				elif (nowRect.left < targetRect.left):
					nowRect.left += (targetRect.left - nowRect.left) / 4
					if (targetRect.left - nowRect.left < 10):
						nowRect.left = targetRect.left
					paint2 = TRUE
			if (1 == 1):
				if (nowRect.top > targetRect.top):
					nowRect.top -= (nowRect.top - targetRect.top) / 4
					if (nowRect.top - targetRect.top < 10):
						nowRect.top = targetRect.top
					paint2 = TRUE
				elif (nowRect.top < targetRect.top):
					nowRect.top += (targetRect.top - nowRect.top) / 4
					if (targetRect.top - nowRect.top < 10):
						nowRect.top = targetRect.top
					paint2 = TRUE
			if (1 == 1):
				if (nowRect.right > targetRect.right):
					nowRect.right -= (nowRect.right - targetRect.right) / 4
					if (nowRect.right - targetRect.right < 10):
						nowRect.right = targetRect.right
					paint2 = TRUE
				elif (nowRect.right < targetRect.right):
					nowRect.right += (targetRect.right - nowRect.right) / 4
					if (targetRect.right - nowRect.right < 10):
						nowRect.right = targetRect.right
					paint2 = TRUE
			if (1 == 1):
				if (nowRect.bottom > targetRect.bottom):
					nowRect.bottom -= (nowRect.bottom - targetRect.bottom) / 4
					if (nowRect.bottom - targetRect.bottom < 10):
						nowRect.bottom = targetRect.bottom
					paint2 = TRUE
				elif (nowRect.bottom < targetRect.bottom):
					nowRect.bottom += (targetRect.bottom - nowRect.bottom) / 4
					if (targetRect.bottom - nowRect.bottom < 10):
						nowRect.bottom = targetRect.bottom
					paint2 = TRUE
			subView.m_location = FCPoint(nowRect.left, nowRect.top)
			subView.m_size = FCSize(nowRect.right - nowRect.left, nowRect.bottom - nowRect.top)
	else:
		for i in range(0, len(pyrometer.m_rects)):
			subView = pyrometer.m_views[i]
			targetRect = pyrometer.m_rects[i]
			subView.m_location = FCPoint(targetRect.left, targetRect.top)
			subView.m_size = FCSize(targetRect.right - targetRect.left, targetRect.bottom - targetRect.top)
	if(paint2):
		invalidateView(pyrometer, pyrometer.m_paint)

def updatePyromoter(pyrometer):
	pyrometer.m_rects = []
	totalAmount = 0
	for i in range(0, len(pyrometer.m_views)):
		totalAmount += pyrometer.m_views[i].m_value
	rates = []
	for i in range(0, len(pyrometer.m_views)):
		rates.append(pyrometer.m_views[i].m_value / totalAmount)
	pyrometer.Rwidth = pyrometer.m_size.cx
	pyrometer.Rheight = pyrometer.m_size.cy
	areas = []
	for i in range(0, len(rates)):
		areas.append(rates[i] * pyrometer.m_size.cx * pyrometer.m_size.cy)
	children = areas
	row = []
	w = min(pyrometer.Rwidth, pyrometer.Rheight)
	while (1 == 1):
		if(len(pyrometer.m_rects) > len(pyrometer.m_views)):
			break
		if (w <= 0):
			break
		if (len(children) == 0):
			if (len(row) > 0):
				layoutrow(pyrometer, row, w)  #output current row
			break
		c = children[0]
		if (c == 0):
			break
		newrow = []
		for x in range(0, len(row)):
			newrow.append(row[x])
		newrow.append(c);
		if (worst(pyrometer, row, w) >= worst(pyrometer, newrow, w)):
			# can be placed in this row
			#cout << " add: " << c << endl;
			tmp = []
			for x in range(1, len(children)):
				tmp.append(children[x])
			children = tmp
			row = newrow
		else:
			#placed in a empty new row
			#cout << " new: " << c << endl;
			layoutrow(pyrometer, row, w);  # output current row
			row = []
			w = rWidth(pyrometer, row, int(w))

def on_message(ws, message):
	global m_pyrometer
	global m_paint
	newData = json.loads(message)
	key = newData["base"] + "," + newData["quote"]
	hasData = FALSE
	viewsSize = len(m_pyrometer.m_views)
	for i in range(0,viewsSize):
		thisCell = m_pyrometer.m_views[i]
		if(thisCell.m_key == key):
			hasData = TRUE
			thisCell.m_data = newData
			thisCell.m_value = thisCell.m_value + newData["volume"] * newData["price"]
			break
	if(hasData == FALSE):
		pData = PyrometerData()
		pData.m_key = key
		pData.m_text = key
		pData.m_data = newData
		pData.m_value = newData["volume"] * newData["price"]
		pData.m_size = FCSize(0, 0)
		pData.m_location = FCPoint(m_pyrometer.m_size.cx, m_pyrometer.m_size.cy)
		pData.m_firstPrice = newData["price"]
		pData.m_backColor = "none"
		pData.m_borderColor = "rgb(0,0,0)"
		pData.m_visible = TRUE
		pData.m_parent = m_pyrometer
		pData.m_paint = m_paint
		addViewToParent(pData, m_pyrometer)
	m_pyrometer.m_views = sorted(m_pyrometer.m_views, key=attrgetter('m_value'), reverse=True)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("closed")

def on_open(ws):
    print("start")

def startWebSocket():
	websocket.enableTrace(True)
	ws = websocket.WebSocketApp("wss://ws.coincap.io/trades/binance",
								on_open=on_open,
								on_message=on_message,
								on_error=on_error,
								on_close=on_close)

	ws.run_forever()

wc = win32gui.WNDCLASS()
wc.hbrBackground = COLOR_BTNFACE + 1
wc.hCursor = win32gui.LoadCursor(0,IDI_APPLICATION)
wc.lpszClassName = "facecat-py"
wc.lpfnWndProc = WndProc
reg = win32gui.RegisterClass(wc)
hwnd = win32gui.CreateWindow(reg,'facecat-py',WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN,CW_USEDEFAULT,CW_USEDEFAULT,CW_USEDEFAULT,CW_USEDEFAULT,0,0,0,None)
m_paint.m_hWnd = hwnd

m_pyrometer = PyrometerDiv()
m_pyrometer.m_dock = "fill"
addView(m_pyrometer, m_paint)

#检查CTP的数据
def checkNewData(a='', b=''):
	global m_paint
	global m_pyrometer
	updatePyromoter(m_pyrometer)
	onPyrometerTime(m_pyrometer)
	invalidate(m_paint)

def run(*args):
	startWebSocket()
thread.start_new_thread(run, ())
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
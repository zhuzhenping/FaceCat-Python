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
	elif(view.m_type == "ldata"):
		a = 0
	else:
		drawButton(view, paint, clipRect)
	if(view.m_name == "list"):
		for i in range(0, len(view.m_views)):
			if(view.m_views[i].m_isMove == FALSE):
				drawListItem(view.m_views[i], paint, clipRect)

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
	elif(view.m_type == "ldata"):
		a = 0
	if(view.m_name == "list"):
		for i in range(0, len(view.m_views)):
			if(view.m_views[i].m_isMove):
				drawListItem(view.m_views[i], paint, clipRect)

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
class ListData(FCView):
	def __init__(self):
		super().__init__()
		self.m_value = 0 #数值
		self.m_key = None
		self.m_firstPrice = None
		self.m_data = None
		self.m_type = "ldata"
		self.m_isMove = FALSE

#绘制数据项
def drawListItem(view, paint, clipRect):
	scrollV = view.m_parent.m_scrollV
	if(view.m_location.y + view.m_size.cy - scrollV >= 0 and view.m_location.y - scrollV < view.m_parent.m_size.cy):
		totalValue = view.m_parent.m_totalValue
		diffRange = toFixed((view.m_data["price"] - view.m_firstPrice) / view.m_data["price"] * 100, 2) + "%"
		rtRight = (view.m_size.cx - 130) * view.m_value / totalValue
		if(view.m_backColor != "none"):
			paint.fillRect(view.m_backColor, 0, 10 - scrollV + view.m_location.y, rtRight, view.m_size.cy - 10 - scrollV + view.m_location.y)
		if(view.m_borderColor != "none"):
			paint.drawRect(view.m_borderColor, 1, 0, 0, 10 - scrollV + view.m_location.y, rtRight, view.m_size.cy - 10 - scrollV + view.m_location.y)
		rtRight += 10
		fontSize1 = int(min(view.m_size.cx, view.m_size.cy) / 4);
		if(fontSize1 > 1):
			baseUpper = view.m_data["base"].upper()
			font1 = str(fontSize1) + "px Arial"
			tSize = paint.textSize(baseUpper, font1)	           
			quoteUpper = view.m_data["quote"].upper()
			font2 = str(fontSize1 / 2) + "px Arial"
			tSize2 = paint.textSize(quoteUpper, font2)
	            
			if (view.m_paint.m_defaultUIStyle == "dark"):
				paint.drawText(baseUpper, "rgb(255,255,255)", font1, rtRight, view.m_size.cy / 2 - tSize.cy + 2 - scrollV + view.m_location.y - tSize.cy / 2)
				paint.drawText(quoteUpper, "rgb(255,255,255)", font2, rtRight, view.m_size.cy / 2 + 2 - scrollV + view.m_location.y - tSize.cy / 2)
			elif (view.m_paint.m_defaultUIStyle == "light"):
				paint.drawText(baseUpper, "rgb(0,0,0)", font1, rtRight, view.m_size.cy / 2 - tSize.cy + 2 - scrollV + view.m_location.y - tSize.cy / 2)
				paint.drawText(quoteUpper, "rgb(0,0,0)", font2, rtRight, view.m_size.cy / 2 + 2 - scrollV + view.m_location.y - tSize.cy / 2)
	            
			strPrice = toFixed(view.m_data["price"], 6)
			font3 = str(fontSize1 * 2 / 3) + "px Arial"
			tSize5 = paint.textSize(strPrice, font3)
			if (view.m_paint.m_defaultUIStyle == "dark"):
				paint.drawText(strPrice, "rgb(255,255,255)", font3, rtRight, view.m_size.cy / 2 + tSize.cy + 2 - scrollV + view.m_location.y - tSize.cy / 2)
			elif (view.m_paint.m_defaultUIStyle == "light"):
				paint.drawText(strPrice, "rgb(0,0,0)", font3, rtRight, view.m_size.cy / 2 + tSize.cy + 2 - scrollV + view.m_location.y - tSize.cy / 2)
	
def updateList(dynaList):
	dynaList.m_rects = []
	viewsSize = len(dynaList.m_views)
	for i in range(0, viewsSize):
		thisCell = dynaList.m_views[i]
		dynaList.m_rects.append(FCRect(0, i * dynaList.m_itemHeight, dynaList.m_size.cx - dynaList.m_scrollSize, (i + 1) * dynaList.m_itemHeight));

def onListTime(dynaList):
	paint2 = FALSE
	if(dynaList.m_useAnimation):
		for i in range(0, len(dynaList.m_rects)):
			subView = dynaList.m_views[i]
			targetRect = dynaList.m_rects[i]
			nowRect = FCRect(subView.m_location.x, subView.m_location.y, subView.m_location.x + subView.m_size.cx, subView.m_location.y + subView.m_size.cy)
			isMove = FALSE
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
					isMove = TRUE
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
			subView.m_isMove = isMove;
			subView.m_location = FCPoint(nowRect.left, nowRect.top)
			subView.m_size = FCSize(nowRect.right - nowRect.left, nowRect.bottom - nowRect.top)
	else:
		for i in range(0, len(dynaList.m_rects)):
			subView = dynaList.m_views[i]
			targetRect = dynaList.m_rects[i]
			subView.m_location = FCPoint(targetRect.left, targetRect.top)
			subView.m_size = FCSize(targetRect.right - targetRect.left, targetRect.bottom - targetRect.top)
	if(paint2):
		invalidateView(dynaList, dynaList.m_paint)

def on_message(ws, message):
	global m_list
	global m_paint
	global m_listColors
	newData = json.loads(message)
	key = newData["base"] + "," + newData["quote"]
	hasData = FALSE
	viewsSize = len(m_list.m_views)
	for i in range(0,viewsSize):
		thisCell = m_list.m_views[i]
		if(thisCell.m_key == key):
			hasData = TRUE
			thisCell.m_data = newData
			thisCell.m_value = thisCell.m_value + newData["volume"] * newData["price"]
			break
	if(hasData == FALSE):
		pData = ListData()
		pData.m_key = key
		pData.m_text = key
		pData.m_data = newData
		pData.m_value = newData["volume"] * newData["price"]
		pData.m_size = FCSize(m_list.m_size.cx, m_list.m_itemHeight)
		pData.m_location = FCPoint(0, len(m_list.m_views) * m_list.m_itemHeight)
		pData.m_firstPrice = newData["price"]
		pData.m_backColor = m_listColors[len(m_list.m_views) % len(m_listColors)]
		pData.m_allowDraw = FALSE
		if (m_list.m_paint.m_defaultUIStyle == "dark"):
			pData.m_borderColor = "rgb(255,255,255)"
		elif(m_list.m_paint.m_defaultUIStyle == "light"):
			pData.m_borderColor = "rgb(0,0,0)"
		addViewToParent(pData, m_list)
	totalValue = 0; 
	viewsSize = len(m_list.m_views)
	for i in range(0, viewsSize):
	    thisCell = m_list.m_views[i]
	    if(totalValue < thisCell.m_value):
	        totalValue = thisCell.m_value
	m_list.m_totalValue = totalValue
	m_list.m_views = sorted(m_list.m_views, key=attrgetter('m_value'), reverse=True)

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

m_listColors = []
m_listColors.append("rgb(59,174,218)")
m_listColors.append("rgb(185,63,150)")
m_listColors.append("rgb(219,68,83)")
m_listColors.append("rgb(246,187,67)")
m_listColors.append("rgb(216,112,173)")
m_listColors.append("rgb(140,192,81)")
m_listColors.append("rgb(233,87,62)")
m_listColors.append("rgb(150,123,220)")
m_listColors.append("rgb(75,137,220)")
m_listColors.append("rgb(170,178,189)")

m_list = FCView()
m_list.m_type = "div"
m_list.m_name = "list"
m_list.m_dock = "fill"
m_list.m_itemHeight = 60
m_list.m_rects = []
m_list.m_useAnimation = TRUE
m_list.m_showVScrollBar = TRUE
addView(m_list, m_paint)
print(m_list.m_scrollV)

#检查CTP的数据
def checkNewData(a='', b=''):
	global m_paint
	global m_list
	updateList(m_list)
	onListTime(m_list)
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
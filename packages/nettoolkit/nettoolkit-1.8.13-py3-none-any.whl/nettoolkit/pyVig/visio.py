
# ------------------------------------------------------------------------------
#  IMPORTS
# ------------------------------------------------------------------------------
try:
	import win32com.client
	from win32com.client import constants
except:
	print("[-] Please install the win32com client using - pip install pywin32")
import traceback
from random import randint

from nettoolkit.pyVig.static import *
from nettoolkit.pyVig.common import get_filename

# ------------------------------------------------------------------------------
#  VisioObject class
# ------------------------------------------------------------------------------
class VisioObject():
	"""Creates a Visio Object. 

	Args:
		stencils (list, optional): List of stencils. Defaults to None.
		outputFile (str, optional): output filename. Defaults to None.

	Returns:
		_type_: _description_
	"""	

	# stencils dictionary
	stn = {}

	# object initializer
	def __init__(self, stencils=None, outputFile=None):
		"""Initialize Visio Object by starting Visio Application, 
		Opens a blank Visio Document/Page inside it.
		open all stencils mentioned

		"""		
		self.page_number = 0
		self.no_of_icons = 0
		self.icons = {}
		self.outputFile = outputFile
		self._startVisio
		self._openBlankVisioDoc()
		if all([stencils is not None, 
				self.visio is not None,
				self.doc is not None,
				# self.page is not None,
				]):
			for value in stencils:
				v = get_filename(value)
				self.stn[v] = self.openStencil(value)

	# context Load
	def __enter__(self):
		return self

	# context end
	def __exit__(self, exc_type, exc_value, tb):
		save_success = self._saveVisio(self.outputFile)
		if save_success:
			self._closeVisio()
		else:
			print(f"[-] Information:\tVisio file save did not happen, please save and close visio manually")
		#
		if exc_type is not None:
			traceback.print_exception(exc_type, exc_value, tb)

	# Object Representation
	def __repr__(self):
		return f'VisioObject: {self.outputFile}'

	# --------------------------------------------------------------------------
	#  Internal
	# --------------------------------------------------------------------------

	# save visio output file
	def _saveVisio(self, file):
		try: 
			print(f"[+] Information:\tattempting to save file as {file}... ", end='\t')
			self.doc.SaveAs(file)
			print(f"Success ")
			return True
		except: 
			print(f"Failed")
			return False

	# close visio application
	def _closeVisio(self):
		try:
			print(f"[+] Information:\tattempting to close/quite visio... ", end='\t')
			self.doc.Close()
			self.visio.Quit()
			print(f"Success ")
		except:
			print(f"Failed")

	# Internal use only: starts a new Visio Application
	@property
	def _startVisio(self):
		try:
			print(f"[+] Information:\tstarting visio application..", end='\t')
			self.visio = win32com.client.Dispatch("Visio.Application")
			print(f"success..",)
		except Exception as e:
			print(f"fail..",)
			print(f"[-] Critical:\tVisio application load failed, retry after clearing temp, verify macros all allowed with vBA access, verify visio application installation..",)
			print(f"[-] Debug:\t\t{e}",)
			self.visio = None

	# Internal use only: Open a blank visio page inside opened Visio Application
	def _openBlankVisioDoc(self):
		try:
			print(f"[+] Information:\tadding a new blank page on visio application..", end='\t')
			# self.doc = self.visio.Documents.Add('Basic Diagram.vst')
			self.doc = self.visio.Documents.Add('')
			print(f"success..",)
		except Exception as e:
			print(f"fail..",)
			print(f"[-] Critical:\tadding a new blank page on visio application failed..",)

	def insert_new_page(self, name=None):
		self.page_number += 1
		try:
			print(f"[+] Information:\tappending a new page on visio application..", end='\t')
			self.page = self.doc.Pages.Add()
			self.page = self.doc.Pages.Item(self.page_number)
			if name: 
				self.page.Name = name
				print(f"renamed to {name}..", end='\t')
			print(f"success..",)
		except Exception as e:
			print(f"fail..",)
			print(f"[+] Critical:\tappending a new page on visio application failed..",)

	# Return item from Stencil
	def _selectItemfromStencil(self, item, stencil):
		try:
			return self.stn[stencil].Masters.Item(item)
		except:
			print(f"Error:\t\titem `{item}` not found in stencil `{stencil}`.., You may see a text box instead")

	# Drops 'item' on visio page at given position index ( posX and posY )
	def _dropItemtoPage(self, item, posX, posY):
		try: 
			itemProp = self.page.Drop(item, posY, posX)
			return itemProp
		except Exception as e:
			print(f"[-] Error:\t\tItem Drop failed for {item}, verify stencil, item icon available in stencil",)
			print(f"[-] Debug:\t\t{e}",)

	@staticmethod
	def _border(item, borderLineColor=None, borderLinePattern=None,
		borderLineWeight=0) :
		if borderLineColor is not None:
			item.Cells( 'LineColor' ).FormulaU = borderLineColor
		if borderLinePattern is not None and isinstance(borderLinePattern, int):
			item.Cells( 'LinePattern' ).FormulaU = borderLinePattern
		if borderLineWeight > 0:
			item.Cells( 'LineWeight' ).FormulaU = borderLineWeight

	@staticmethod
	def _fill(item, fillColor=None, fillTransparency=None):
		if fillColor is not None:
			item.Cells( 'Fillforegnd' ).FormulaU = fillColor
		if fillTransparency is not None:
			if isinstance(fillTransparency, int):
				fillTransparency = str(fillTransparency) + "%"
			item.CellsSRC(visSectionObject, visRowFill, visFillForegndTrans).FormulaU = fillTransparency
			item.CellsSRC(visSectionObject, visRowFill, visFillBkgndTrans).FormulaU = fillTransparency

	@staticmethod
	def _text(item, text=None, textColor=None, textSize=0, vAlign=1, hAlign=0, style=None):
		if text is not None:
			item.Text = text
		if textColor is not None:
			item.CellsSRC(visSectionCharacter, 0, visCharacterColor).FormulaU = textColor
		if textSize > 0 and isinstance(textSize, int):
			item.Cells( 'Char.size' ).FormulaU = textSize
		if isinstance(vAlign, int) and (vAlign>=0 and vAlign<=2):
			item.Cells( 'VerticalAlign' ).FormulaU = vAlign
		if isinstance(hAlign, int) and (hAlign>=0 and hAlign<=2):
			item.CellsSRC(visSectionParagraph, 0, visHorzAlign).FormulaU = hAlign
		if style is not None:
			if isinstance(style, str):
				item.CellsSRC(visSectionCharacter, 0, visCharacterStyle).FormulaU = visCharStyle[style]
			elif isinstance(style, (list, tuple)):
				for x in style:
					item.CellsSRC(visSectionCharacter, 0, visCharacterStyle).FormulaU = visCharStyle[x]

	### FORMATTING ###	
	def _format(self, icon,
		text=None, textColor=None, textSize=0, vAlign=1, hAlign=0, style=None,
		fillColor=None, fillTransparency=None,
		borderLineColor=None, borderLinePattern=None, borderLineWeight=0,
		iconHeight=0, iconWidth=0  
		):
		''' Formatting Parameters '''
		self._border(icon, borderLineColor, borderLinePattern, borderLineWeight)
		self._fill(icon, fillColor, fillTransparency)
		self._text(icon, text, textColor, textSize, vAlign, hAlign, style)
		self._resize(icon, iconWidth, iconHeight)
		self.no_of_icons += 1
		self.icons[self.no_of_icons] = icon

	@staticmethod
	def _resize(item, width, height):
		try:
			if width:
				item.CellsSRC(visSectionObject, visRowXFormOut, visXFormWidth).FormulaU = f"{width} in"
			if height:
				item.CellsSRC(visSectionObject, visRowXFormOut, visXFormHeight).FormulaU = f"{height} in"
		except:
			print(f"[-] Error:\t\tResizing of item {item} not allowed for gaurded stencil items. Match text box size manually")

	# --------------------------------------------------------------------------
	#  External
	# --------------------------------------------------------------------------

	# Internal + External : Open mentioned stencil in opened visio application. 
	def openStencil(self, stencil):
		"""open a stencil in visio document

		Args:
			stencil (str): stencil file

		Returns:
			visioStencil: visio stencil object
		"""		
		stencil = stencil.replace("/", "\\")
		try:
			print(f"[+] Information:\tattempting to open visio stencil {stencil}..", end='\t')
			s = self.visio.Documents.Open(stencil)
			print("success..")
			return s
		except Exception as e:
			print("fail..")
			print(f"[-] Error:\t\tUnable to open visio stencil {stencil}, verify stencil existance",)
			print(f"[-] Debug:\t\t{e}",)

	def selectNdrop(self, stencil, item, posX, posY, **format):
		"""Selects item `item` from provided stencil `stencil` for selected visio object.
		And drops that item on visio Object at given position index ( posX and posY )
		usage: icon = visObj.selectNdrop(stencil,item,posX,posY)
		format = shape formatting (see _format() for type of formats available)
		
		Args:
			stencil (str): name of stencil
			item (str, int): icon name or number from stencil
			posX (int): plane x-coordinate
			posY (int): plane y-coordinate

		Returns:
			iconObject: dropped icon object
		"""
		#
		defaults = {
			'iconWidth': 2.5,
			'iconHeight': 1,
			# add more as and when need.
		}
		#
		for k, v in defaults.items():
			if k not in format :
				format[k] = v
		#
		itm = self._selectItemfromStencil(item, stencil)
		if itm is not None:
			icon = self._dropItemtoPage(itm, posX, posY)
			self._format(icon=icon, **format)
			return icon

	def shapeDrow(self, shape, lx, lr, rx, rr, **format):
		"""Drops provided shape to visio page.
		Usage: shape = visObj.shapeDrow(shape, lx, lr, rx, rr, format)
		format = shape formatting (see _format() for type of formats available)

		Args:
			shape (str): [description]
			lx (int): x1 - coordinate
			lr (int): y1 - coordinate
			rx (int): x2 - coordinate
			rr (int): y2 - coordinate

		Returns:
			shapeObject: shape object from visio
		"""		
		shaping = True
		if shape.lower() == "rectangle":
			rect = self.page.DrawRectangle(lx, lr, rx, rr)
		elif shape.lower() == "ellipse":
			rect = self.page.DrawOval(lx, lr, rx, rr)
		elif shape.lower() == "arc":
			rect = self.page.DrawQuarterArc(lx, lr, rx, rr, visArcSweepFlagConvex)
		elif shape.lower() == "line":
			rect = self.page.DrawLine(lx, lr, rx, rr)
		else:
			shaping =False

		if shaping:
			self._format(icon=rect, **format)
			return rect

	def join(self, connector, shpObj1, shpObj2):
		"""use Connector object to join two shapes (Device objects)

		Args:
			connector (Connector): Connector object
			shpObj1 (Device): Device Object 1
			shpObj2 (Device): Device Object 2
		"""		
		try:
			connector.obj.Cells("BeginX").GlueTo(shpObj1.obj.Cells("PinX"))
		except:
			x, y = shpObj1.x, shpObj1.y
			connector.obj.CellsSRC(visSectionObject, visRowXForm1D, vis1DBeginX).FormulaU = f"{x} in"
			connector.obj.CellsSRC(visSectionObject, visRowXForm1D, vis1DBeginY).FormulaU = f"{y} in"
		try:
			connector.obj.Cells("EndX").GlueTo(shpObj2.obj.Cells("PinX"))		
		except:
			x, y = shpObj2.x, shpObj2.y
			connector.obj.CellsSRC(visSectionObject, visRowXForm1D, vis1DEndX).FormulaU = f"{x} in"
			connector.obj.CellsSRC(visSectionObject, visRowXForm1D, vis1DEndY).FormulaU = f"{y} in"


	def fit_to_draw(self, height, width):
		"""resize visio page to fit the page to drawing.

		Args:
			height (int)): page height to be resized (inch)
			width (int): page width to be resized (inch)
		"""		
		self.page.PageSheet.CellsSRC(visSectionObject, visRowPage, visPageWidth).FormulaU = f"{width} in"
		self.page.PageSheet.CellsSRC(visSectionObject, visRowPage, visPageHeight).FormulaU = f"{height} in"
		self.page.PageSheet.CellsSRC(visSectionObject, visRowPage, visPageDrawSizeType).FormulaU = "1"
		self.page.PageSheet.CellsSRC(visSectionObject, visRowPage, 38).FormulaU = "2"


# ------------------------------------------------------------------------------
# A Single Connector Class defining connector properties and methods.
# ------------------------------------------------------------------------------
class Connector():
	'''s1_s2_Connector = self.connector(), Drops a connector to visio page.

	Args:
		visObj (visObj): visio object
		connector_type (str, optional): connector type. Defaults to None.
	'''

	def __init__(self, visObj, connector_type=None):
		"""connector
		"""		
		self.visObj = visObj
		self.connector_type = connector_type

	def drop(self, connector_type=None):
		"""drops a connector to visio page.

		Args:
			connector_type (str, optional): connector tpe (valid options are:  angled, straight, curved). Defaults to None=angled.

		Returns:
			connectorObj: Connector Object from visio
		"""		
		item = self.visObj.page.Drop(self.visObj.visio.ConnectorToolDataObject, randint(1, 50), randint(1, 50))
		if self.connector_type == "straight":
			item.CellsSRC(visSectionObject, visRowShapeLayout, visSLOLineRouteExt).FormulaU = "1"
			item.CellsSRC(visSectionObject, visRowShapeLayout, visSLORouteStyle).FormulaU = "16"
		elif self.connector_type == "curved":
			item.CellsSRC(visSectionObject, visRowShapeLayout, visSLOLineRouteExt).FormulaU = "2"
			item.CellsSRC(visSectionObject, visRowShapeLayout, visSLORouteStyle).FormulaU = "1"
		else:
			item.CellsSRC(visSectionObject, visRowShapeLayout, visSLOLineRouteExt).FormulaU = "1"
			item.CellsSRC(visSectionObject, visRowShapeLayout, visSLORouteStyle).FormulaU = "1"
		self.obj = item
		return item

	def add_a_port_info(self, aport_info, at_angle, connector_type, indent=True):
		"""add port information for (a-side interface) on connector

		Args:
			aport_info (str): port information
			at_angle (int): rotate information at angle
			connector_type (str): connector type ( angled, straight, curved )
			indent (bool, optional): indent text or not. Defaults to True.
		"""		
		self.description(aport_info)
		if connector_type and connector_type != "angled":
			self.text_rotate(at_angle)
		if indent: self.text_indent()

	def format_line(self, color=None, weight=None, pattern=None):
		"""formatting of line

		Args:
			color (str, optional): set color of line (blue, red, gray etc.). Defaults to None=black.  see line_color for all available options.
			weight (int, optional): thickness of line. Defaults to None=1.
			pattern (int, optional): line patterns. Defaults to solid line.
		"""		
		if color: self.line_color(color)
		if weight: self.line_weight(weight)
		if pattern: self.line_pattern(pattern)

	@property
	def object(self):
		"""visio object

		Returns:
			visioObject: visio object
		"""		
		return self.obj

	def text_rotate(self, degree=90):
		"""Rotation of text at given angle

		Args:
			degree (int, optional): angle to be rotate to. Defaults to 90.
		"""		
		self.obj.CellsSRC(visSectionObject, visRowTextXForm, visXFormAngle).FormulaU = f"{degree} deg"

	def text_indent(self):
		"""Indention to be done on oject
		"""		
		inch = self.obj.LengthIU / 2 
		self.obj.CellsSRC(visSectionParagraph, 0, visIndentLeft).FormulaU = f"{inch} in"

	def description(self, remarks):
		"""description to be add to object.

		Args:
			remarks (str, memo): description
		"""		
		try:
			self.obj.Characters.Text = remarks
		except:
			print(f"[-] Error:\t\tDescription set for object failed `{remarks}` ")

	def line_color(self, color=None):
		"""color of a line object

		Args:
			color (str tuple, optional): color of line. Defaults to black. valid string options are (red, green, blue, gray, lightgray, darkgray ). Other option is to provide RGB color in tuple ex: (10, 10, 10)

		Returns:
			None: None
		"""	
		clr = "THEMEGUARD(RGB(0,0,0))"
		if isinstance(color, str):
			if color.lower() == "white": clr = "THEMEGUARD(RGB(255,255,255))"
			if color.lower() == "black": clr = "THEMEGUARD(RGB(0,0,0))"
			if color.lower() == "red": clr = "THEMEGUARD(RGB(255,0,0))"
			if color.lower() == "orange": clr = "THEMEGUARD(RGB(255,192,0))"
			if color.lower() == "green": clr = "THEMEGUARD(RGB(0,255,0))"
			if color.lower() == "skyblue": clr = "THEMEGUARD(RGB(0,176,240))"
			if color.lower() == "blue": clr = "THEMEGUARD(RGB(0,0,255))"
			if color.lower() == "yellow": clr = "THEMEGUARD(RGB(255,255,0))"
			if color.lower() == "gray": clr = "THEMEGUARD(RGB(127,127,127))"
			if color.lower() == "lightgray": clr = "THEMEGUARD(RGB(55,55,55))"
			if color.lower() == "darkgray": clr = "THEMEGUARD(RGB(200,200,200))"
		elif isinstance(color, (list, tuple)) and len(color) == 3:
			clr = f"THEMEGUARD(RGB({color[0]},{color[1]},{color[2]}))"
		else:
			return None
		try:
			self.obj.CellsSRC(visSectionObject, visRowLine, visLineColor).FormulaU = clr
		except:
			pass
			print(f"[-] Error:\t\tLine color formatting failed, `{visRowLine}`, for color `{color}`")

	def line_weight(self, weight=None):
		"""set weight/thickness of a line

		Args:
			weight (int, optional): thickness of line. Defaults to None=1.
		"""
		try:
			self.obj.CellsSRC(visSectionObject, visRowLine, visLineWeight).FormulaU = f"{weight} pt"
		except:
			pass

	def line_pattern(self, pattern=None):
		"""set line pattern

		Args:
			pattern (int, optional): pattern number. Defaults to solid line.
		"""		
		try:
			self.obj.CellsSRC(visSectionObject, visRowLine, visLinePattern).FormulaU = pattern
		except:
			pass

# ------------------------------------------------------------------------------
# A Single Visio Item Class defining its properties and methods.
# ------------------------------------------------------------------------------
class Device():
	"""A Device Object

	Args:
		visObj (Visio): visio object
		x (int): x-coordinate
		y (int): y-coordinate
	"""		

	def __init__(self, visObj, x, y, **kwargs):
		"""Initialize Device Object
		"""		
		self.visObj = visObj
		self.x = x
		self.y = y
		self.kwargs = kwargs

	def drop_from(self, stencil):
		"""drop an item from stencil, if item not found in stencil then it will drop a rectangle.

		Args:
			stencil (str): stencil name
		"""		
		if stencil and self.kwargs['item']:
			self.obj = self.visObj.selectNdrop(
				posX=self.y, posY=self.x, 
				textSize=.8, 
				**self.kwargs
			)
			self.is_rectangle = False
		else:
			self.obj = self.visObj.shapeDrow('rectangle', 
				self.x, self.y, self.x+2.7, self.y+1.7,
				vAlign=1, hAlign=1)
			self.is_rectangle = True

	@property
	def object(self):
		"""self object

		Returns:
			self.obj: self object
		"""		
		return self.obj

	def connect(self, 
		remote, 
		connector_type=None, 
		angle=0, 
		aport="",
		color=None,
		weight=None,
		pattern=None,
		):
		"""connects self object with remote object using connector.

		Args:
			remote (Device): remote Device object
			connector_type (str, optional): connector type. Defaults to None='angled'.
			angle (int, optional): a-port info rotate at. Defaults to 0.
			aport (str, optional): line a-port info. Defaults to "".
			color (str, optional): line color. Defaults to None.
			weight (int, optional): line weight. Defaults to None.
			pattern (int, optional): line pattern. Defaults to None.
		"""				
		connector = Connector(self.visObj, connector_type)
		connector.drop()
		self.visObj.join(connector, self, remote)
		connector.add_a_port_info(aport, angle, connector_type, indent=False)
		connector.format_line(color, weight, pattern)

	def description(self, remarks):
		"""set description/remark of current object.

		Args:
			remarks (str, memo): remark for the object.
		"""		
		try:
			if not self.is_rectangle:
				remarks = "\n" * len(remarks.split("\n")) + remarks
			self.obj.Characters.Text = remarks
		except:
			dev = device(						# drop rectangle
				stencil=None, 
				visObj=self.visObj, 
				item="",
				x=self.x-1,
				y=self.y-1)
			dev.description(remarks)


# ------------------------------------------------------------------------------
# Device class object return by dropping it to given position
# ------------------------------------------------------------------------------
def device(visObj, x, y, **kwargs):
	"""Drop an item from stencil given to visio object at given x,y co-ordinates.

	Args:
		visObj (Visio): Visio Object
		x (int): x coordinate
		y (int): y coordinate
		**kwargs (kwargs): keyword arguments

	Returns:
		Device: Device Object
	"""	
	D = Device(visObj, x, y, **kwargs)
	D.drop_from(kwargs['stencil'])
	return D


# ------------------------------------------------------------------------------

class ExcelObject():
	"""Interact with Microsoft Excel files (MS Windows only) 

	Args:
		file (str): file name of excel file.
	"""    		

	def __init__(self, file):
		win32c = win32com.client.constants
		self.xl = win32com.client.gencache.EnsureDispatch('Excel.Application')
		self.xl.Visible = True
		self.open(file)

	def open(self, file):
		"""opens the provided file in MS-Excel (default, while initializing)

		Args:
			file (str): file name of excel file.
		"""    		
		self.wb = self.xl.Workbooks.Open(file)

	@property
	def workbook(self):
		"""return workbook object of opened excel file.

		Returns:
			object: excel workbook object
		"""    		
		return self.wb

	@property
	def excel(self):
		"""return excel object of opened excel file.

		Returns:
			object: excel object
		"""    		
		return self.xl



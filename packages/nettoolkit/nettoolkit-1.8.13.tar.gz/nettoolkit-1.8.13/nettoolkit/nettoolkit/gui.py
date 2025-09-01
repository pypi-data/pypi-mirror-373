
# ---------------------------------------------------------------------------------------
#
from .forms.gui_template import GuiTemplate
from .forms.formitems import *


# ---------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Generalized Class to Prepare GUI UserForm using template 
# -----------------------------------------------------------------------------

class NGui(GuiTemplate):
	"""class to define a custom GUI window

	Args:
		header (str, optional): Header on GUI Window. Defaults to "Set Your private Header".
		banner (str, optional): Banner in Window. Defaults to "Set Your private Banner".
		form_width (int, optional): width of form. Defaults to 1440.
		form_height (int, optional): height of form. Defaults to 700.
		frames_dict (dict, optional): dictionary of frames. Defaults to {}.
		event_catchers (dict, optional): dictionary of event catchers and its events. Defaults to {}.
		event_updaters (set, optional): set of event updators. Defaults to set().
		event_item_updaters (set, optional): set of an event item updators. Defaults to set().
		retractables (set, optional): set of retractable fields. Defaults to set().
		button_pallete_dic (dict, optional): button pallete dictionary. Defaults to {}.
	"""	

	def __init__(self, * ,
		header="",
		banner="",
		form_width=1440,
		form_height=700,
		frames_dict={},
		event_catchers={},
		event_updaters=set(),
		event_item_updaters=set(),
		retractables=set(),
		button_pallete_dic={},
		):
		super().__init__(
			header, banner, form_width, form_height,
			frames_dict, event_catchers, event_updaters, 
			event_item_updaters, retractables, button_pallete_dic,
		)
		self.event_catchers.update({v['key']: None for k, v in self.button_pallete_dic.items()})
		self.button_pallete_updaters = {v['key'] for k, v in self.button_pallete_dic.items()}

	def __call__(self, initial_frame=None):
		if self.hide_button_pallete_buttons:
			initial_frame = None
		if not self.tabs_dic: self.collate_frames()
		super().__call__(initial_frame) 

	def update_set(self, name, value):
		if self.__dict__.get(name): 
			self.__dict__[name] = self.__dict__[name].union(value)
		else:
			self.__dict__[name] = value


	def update_dict(self, name, value):
		if self.__dict__.get(name): 
			self.__dict__[name].update(value)
		else:
			self.__dict__[name] = value

	@property
	def cleanup_fields(self):
		return self.retractables

	def collate_frames(self):
		for short_name, dic in self.button_pallete_dic.items():
			self.tabs_dic.update(dic['frames'])




# ------------------------------------------------------------------------------
# Main Function
# ------------------------------------------------------------------------------
if __name__ == '__main__':
	pass
# ------------------------------------------------------------------------------

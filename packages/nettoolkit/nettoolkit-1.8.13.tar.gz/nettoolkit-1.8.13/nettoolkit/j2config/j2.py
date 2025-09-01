import jinja2
from inspect import getmembers, isfunction, isclass, isroutine

from .data_collect import DeviceDetails
from .cmn import common_fn as cmn
from . import func as func
from .func import Vrf, Vlan, Physical, Bgp, Aggregated, Loopback, Ospf, Static
from .general import *
from .read_conditions import JinjaVarCheck

# =======================================================================================================

class PrepareConfig():
	"""boiler plate code class for start configuration preparation

	Args:
		data_file (str): Excel database
		jtemplate_file (str): Jinja Template
		output_folder (str, optional): output path. Defaults to ".".
		regional_file (str, optional): custom static regional variable file. Defaults to None. (overrides device var)
		regional_class (class, optional): custom class returning frames to be merge with device var . Defaults to None.

	Raises:
		Exception: Raise for Custom class insertion
		Exception: Raise for Custom module insertion
	"""	

	# -----------------------------------------
	# IMPORT FILTERS FOR JINJA VARIABLES
	# -----------------------------------------
	filters = {}
	filters.update({'Vrf': Vrf, 'Bgp': Bgp,
		'Vlan': Vlan, 'Physical': Physical, 'Aggregated': Aggregated, 'Loopback': Loopback, 		
		'Ospf': Ospf, 'Static': Static,
	})
	filters.update(dict(getmembers(cmn, isfunction)))
	filters.update(dict(getmembers(Vrf, lambda x:not(isroutine(x))))['__dict__'] )
	filters.update(dict(getmembers(Vlan, lambda x:not(isroutine(x))))['__dict__'] )
	filters.update(dict(getmembers(Physical, lambda x:not(isroutine(x))))['__dict__'] )
	filters.update(dict(getmembers(Bgp, lambda x:not(isroutine(x))))['__dict__'] )
	filters.update(dict(getmembers(Aggregated, lambda x:not(isroutine(x))))['__dict__'] )
	filters.update(dict(getmembers(Loopback, lambda x:not(isroutine(x))))['__dict__'] )
	filters.update(dict(getmembers(Static, lambda x:not(isroutine(x))))['__dict__'] )
	filters.update(dict(getmembers(Ospf, lambda x:not(isroutine(x))))['__dict__'] )
	filters.update(dict(getmembers(func, isfunction)))

	def __init__(self,
		data_file,
		jtemplate_file,
		output_folder=".",
		regional_file=None,
		regional_class=None,
		):
		"""Object Initializer
		"""		
		self.data_file = data_file
		self.jtemplate_file = jtemplate_file.replace("\\", '/')
		self.output_folder = output_folder
		self.regional_file = regional_file
		self.regional_class = regional_class
		self.check_jinja_var_tab_variables()

	def check_jinja_var_tab_variables(self):
		JVC = JinjaVarCheck(jinja_file=self.jtemplate_file, clean_file=self.data_file, global_file=self.regional_file)
		JVC()
		if JVC.xl_var_missing:
			print(f"\n[-] There found Jinja variable(s) missing in your input excel database(s) `var` tab. please validate."
				f"\n[-] Missing Variables: ({', '.join(JVC.xl_var_missing)})")

	def custom_class_add_to_filter(self, **kwargs):
		"""add custom classes and its methods as jinja filters. External callable.
		"""
		for filtername, _cls in kwargs.items():
			try:
				self.filters.update({filtername: _cls})
				pre = self.filters.keys()
				self.filters.update(dict(getmembers(_cls, lambda x:not(isroutine(x))))['__dict__'] )
				post = self.filters.keys()
			except Exception as e:
				raise Exception(f"[-] Class Insertion Failed for filter {filtername}\n{e}")

	def custom_module_methods_add_to_filter(self, *modules):
		"""add custom methods from module(s) as jinja filters. External callable.
		"""
		for module in modules:
			try:
				self.filters.update(dict(getmembers(module, isfunction)))
			except Exception as e:
				raise Exception(f"[-] Module Insertion Failed {module}\n{e}")

	def start(self):
		"""kick start generation
		"""
		# ## LOAD - DATA
		DD = DeviceDetails(self.data_file)
		frames = []
		try:
			RCD = self.regional_class(DD.device_details, self.regional_file)
			frames = RCD.frames
		except:
			pass
		DD.merge_with_var_frames(frames)
		DD.read_table()

		# ## LOAD - JINJA TEMPLATE AND ENVIRONMENT
		templateLoader = jinja2.FileSystemLoader(searchpath='')
		templateEnv = jinja2.Environment(loader=templateLoader, 
			extensions=['jinja2.ext.loopcontrols', 'jinja2.ext.do',])
		for key, value in self.filters.items():
			templateEnv.filters[key] = value

		# ## TEMPLATE FILE		
		template = templateEnv.get_template(self.jtemplate_file)
		outputText = template.render(DD.data)#, undefined=jinja2.StrictUndefined) # Enable undefined for strict variable check

		# ## WRITE OUT
		model, template_ver = get_model_template_version(self.jtemplate_file)
		op_file = f"{self.output_folder}/{DD.data['var']['hostname']}-{model}-{template_ver}-j2Gen.cfg"
		with open(op_file, 'w') as f:
			f.write(outputText)


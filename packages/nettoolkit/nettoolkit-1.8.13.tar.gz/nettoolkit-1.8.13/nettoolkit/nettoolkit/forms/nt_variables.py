
# ---------------------------------------------------------------------------------------
#   Imports
# ---------------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.capture_it.forms.execs   import CAPTUREIT_EVENT_UPDATERS,   CAPTUREIT_ITEM_UPDATERS,   CAPTUREIT_RETRACTABLES,   CATPUREIT_EVENT_FUNCS
from nettoolkit.facts_finder.forms.execs import FACTSFINDER_EVENT_UPDATERS, FACTSFINDER_ITEM_UPDATERS, FACTSFINDER_RETRACTABLES, FACTSFINDER_EVENT_FUNCS
from nettoolkit.j2config.forms.execs     import J2CONFIG_EVENT_UPDATERS,    J2CONFIG_ITEM_UPDATERS,    J2CONFIG_RETRACTABLES,    J2CONFIG_EVENT_FUNCS
from nettoolkit.pyVig.forms.execs        import PYVIG_EVENT_UPDATERS,       PYVIG_ITEM_UPDATERS,       PYVIG_RETRACTABLES,       PYVIG_EVENT_FUNCS
from nettoolkit.configure.forms.execs    import CONFIGURE_EVENT_UPDATERS,   CONFIGURE_ITEM_UPDATERS,   CONFIGURE_RETRACTABLES,   CONFIGURE_EVENT_FUNCS
from nettoolkit.addressing.forms.execs   import ADDRESSING_EVENT_UPDATERS,  ADDRESSING_ITEM_UPDATERS,  ADDRESSING_RETRACTABLES,  ADDRESSING_EVENT_FUNCS
from nettoolkit.pyJuniper.forms.execs    import JUNIPER_EVENT_UPDATERS,     JUNIPER_ITEM_UPDATERS,     JUNIPER_RETRACTABLES,     JUNIPER_EVENT_FUNCS
from nettoolkit.pyNetCrypt.forms.execs   import CRYPT_EVENT_UPDATERS,       CRYPT_ITEM_UPDATERS,       CRYPT_RETRACTABLES,       CRYPT_EVENT_FUNCS

from nettoolkit.capture_it.forms.frames import CAPTUREIT_FRAMES
from nettoolkit.facts_finder.forms.frames import FACTSFINDER_FRAMES
from nettoolkit.j2config.forms.frames import J2CONFIG_FRAMES
from nettoolkit.pyVig.forms.frames import PYVIG_FRAMES
from nettoolkit.configure.forms.frames import CONFIGURE_FRAMES
from nettoolkit.addressing.forms.frames import ADDRESSING_FRAMES
from nettoolkit.pyJuniper.forms.frames import JUNIPER_FRAMES
from nettoolkit.pyNetCrypt.forms.frames import CRYPT_FRAMES

# ---------------------------------------------------------------------------------------
#   sets of event updator variables    -- exec_fn(i)
# ---------------------------------------------------------------------------------------
EVENT_UPDATORS = set()
EVENT_UPDATORS = EVENT_UPDATORS.union(CRYPT_EVENT_UPDATERS)
EVENT_UPDATORS = EVENT_UPDATORS.union(ADDRESSING_EVENT_UPDATERS)
EVENT_UPDATORS = EVENT_UPDATORS.union(JUNIPER_EVENT_UPDATERS)
EVENT_UPDATORS = EVENT_UPDATORS.union(CAPTUREIT_EVENT_UPDATERS)
EVENT_UPDATORS = EVENT_UPDATORS.union(FACTSFINDER_EVENT_UPDATERS)
EVENT_UPDATORS = EVENT_UPDATORS.union(J2CONFIG_EVENT_UPDATERS)
EVENT_UPDATORS = EVENT_UPDATORS.union(PYVIG_EVENT_UPDATERS)
EVENT_UPDATORS = EVENT_UPDATORS.union(CONFIGURE_EVENT_UPDATERS)		
# ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
#   sets of event updator variables    -- exec_fn(obj, i)
# ---------------------------------------------------------------------------------------
EVENT_ITEM_UPDATORS = set()
EVENT_ITEM_UPDATORS = EVENT_ITEM_UPDATORS.union(CRYPT_ITEM_UPDATERS)
EVENT_ITEM_UPDATORS = EVENT_ITEM_UPDATORS.union(ADDRESSING_ITEM_UPDATERS)
EVENT_ITEM_UPDATORS = EVENT_ITEM_UPDATORS.union(JUNIPER_ITEM_UPDATERS)
EVENT_ITEM_UPDATORS = EVENT_ITEM_UPDATORS.union(CAPTUREIT_ITEM_UPDATERS)
EVENT_ITEM_UPDATORS = EVENT_ITEM_UPDATORS.union(FACTSFINDER_ITEM_UPDATERS)
EVENT_ITEM_UPDATORS = EVENT_ITEM_UPDATORS.union(J2CONFIG_ITEM_UPDATERS)
EVENT_ITEM_UPDATORS = EVENT_ITEM_UPDATORS.union(PYVIG_ITEM_UPDATERS)
EVENT_ITEM_UPDATORS = EVENT_ITEM_UPDATORS.union(CONFIGURE_ITEM_UPDATERS)		
# ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
#   sets of variables needs cleanup 
# ---------------------------------------------------------------------------------------
RETRACTABLES = set()
RETRACTABLES = RETRACTABLES.union(CRYPT_RETRACTABLES)
RETRACTABLES = RETRACTABLES.union(ADDRESSING_RETRACTABLES)
RETRACTABLES = RETRACTABLES.union(JUNIPER_RETRACTABLES)
RETRACTABLES = RETRACTABLES.union(CAPTUREIT_RETRACTABLES)
RETRACTABLES = RETRACTABLES.union(FACTSFINDER_RETRACTABLES)
RETRACTABLES = RETRACTABLES.union(J2CONFIG_RETRACTABLES)
RETRACTABLES = RETRACTABLES.union(PYVIG_RETRACTABLES)
RETRACTABLES = RETRACTABLES.union(CONFIGURE_RETRACTABLES)
# -------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
#   Frames dict
# ---------------------------------------------------------------------------------------
FRAMES = {}
FRAMES.update(CRYPT_FRAMES)
FRAMES.update(ADDRESSING_FRAMES)
FRAMES.update(JUNIPER_FRAMES)
FRAMES.update(CAPTUREIT_FRAMES)
FRAMES.update(FACTSFINDER_FRAMES)
FRAMES.update(J2CONFIG_FRAMES)
FRAMES.update(PYVIG_FRAMES)
FRAMES.update(CONFIGURE_FRAMES)
# ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
#   Button Pallete dict
# ---------------------------------------------------------------------------------------
BUTTUN_PALLETE_DICT = {
	'addressing': {'key': 'btn_addressing', 'frames': ADDRESSING_FRAMES,  "button_name": "Addressing",},
	'captureit':  {'key': 'btn_captureit',  'frames': CAPTUREIT_FRAMES,   "button_name": "Capture-IT",},
	'configure':  {'key': 'btn_configure',  'frames': CONFIGURE_FRAMES,   "button_name": "Configure", },
	'configgen':  {'key': 'btn_j2config',   'frames': J2CONFIG_FRAMES,    "button_name": "Config Gen",},
	'crypt':      {'key': 'btn_cryptology', 'frames': CRYPT_FRAMES,       "button_name": "Crypt",     },
	'facts':      {'key': 'btn_factsfinder','frames': FACTSFINDER_FRAMES, "button_name": "Facts",     },
	'juniper':    {'key': 'btn_juniper' ,   'frames': JUNIPER_FRAMES,     "button_name": "Juniper",   },
	'visiogen':   {'key': 'btn_pyvig',      'frames': PYVIG_FRAMES,       "button_name": "Visio Gen", },
}

# ---------------------------------------------------------------------------------------
#   event functions dict
# ---------------------------------------------------------------------------------------
EVENT_FUNCTIONS = {}
EVENT_FUNCTIONS.update(CRYPT_EVENT_FUNCS)
EVENT_FUNCTIONS.update(ADDRESSING_EVENT_FUNCS)
EVENT_FUNCTIONS.update(JUNIPER_EVENT_FUNCS)
EVENT_FUNCTIONS.update(CATPUREIT_EVENT_FUNCS)
EVENT_FUNCTIONS.update(FACTSFINDER_EVENT_FUNCS)
EVENT_FUNCTIONS.update(J2CONFIG_EVENT_FUNCS)
EVENT_FUNCTIONS.update(PYVIG_EVENT_FUNCS)
EVENT_FUNCTIONS.update(CONFIGURE_EVENT_FUNCS)

# ---------------------------------------------------------------------------------------



__all__ = [
	EVENT_UPDATORS, EVENT_ITEM_UPDATORS,  RETRACTABLES, 
	EVENT_FUNCTIONS, 
	FRAMES, BUTTUN_PALLETE_DICT,
]


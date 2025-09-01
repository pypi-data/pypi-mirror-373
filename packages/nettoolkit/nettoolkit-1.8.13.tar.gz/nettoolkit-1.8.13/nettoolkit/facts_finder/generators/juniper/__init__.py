"""Juniper Specific Command Parser Functions/Classes
"""



# // HERE IS ALL PARSER FUNCTIONS //
from ._cmd_parse_lldp import get_lldp_neighbour
from ._cmd_parse_int_description import get_int_description
from ._cmd_parse_chassis_hardware import get_chassis_hardware, get_chassis_serial
from ._cmd_parse_arp_table import get_arp_table
from ._cmd_parse_running_interfaces import get_interfaces_running
from ._cmd_parse_version import get_version
from ._cmd_parse_running_system import get_running_system
from ._cmd_parse_running_routing_instances import get_instances_running
from ._cmd_parse_running_bgp import get_instances_bgps
from ._cmd_parse_running_ospf import get_instances_ospfs
from ._cmd_parse_running_routes import get_system_running_routes
from ._cmd_parse_running_prefix_lists import get_system_running_prefix_lists
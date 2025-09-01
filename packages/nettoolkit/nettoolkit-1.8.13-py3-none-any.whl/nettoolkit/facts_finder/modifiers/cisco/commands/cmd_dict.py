"""
# =========================================================================
#  THIS FILE CONTAINS THE COLUMN MAPPINGS FROM THE FILE WHICH GOT GENERATED 
#  FROM CAPTURE_IT USING TEXTFSM AND
#  RELATIVE REQUIRED FIELD VALUES. 
# =========================================================================
"""
from collections import OrderedDict

#
# ---------- VAR
#
cmd_lst_var = {
    'show ipv6 interface brief': {'ipaddr': '//h2b-h3b'},

    'show route-map': {'set_clauses': '//reso'},

    'show version': {'hardware': 'hardware',
                'hostname': 'hostname',
                'mac': 'mac',
                'running_image': 'bootvar',
                'serial': 'serial',
                'version': 'ios_version'}
}

#
# ---------- INTERFACES
#
cmd_lst_int = OrderedDict()
cmd_lst_int.update({
    'show etherchannel summary': {'group': 'int_number',
                            'interfaces': '//po_to_interface',
                            'po_name': 'interface'},

    'show interfaces': {'description': 'description',
                    'duplex': 'duplex',
                    'hardware_type': '//filter',
                    'interface': 'interface',
                    'ip_address': '//subnet',
                    'link_status': 'link_status',
                    'media_type': 'media_type',
                    'protocol_status': 'protocol_status',
                    'speed': 'speed'},

    'show interfaces switchport': {'access_vlan': 'access_vlan',
                                'admin_mode': 'admin_mode',
                                'interface': 'interface',
                                'mode': '//interface_mode',
                                'native_vlan': 'native_vlan',
                                'switchport': 'switchport',
                                'switchport_negotiation': 'switchport_negotiation',
                                'trunking_vlans': '//vlan_members',
                                'voice_vlan': 'voice_vlan'},

    'show ip vrf interfaces': {'interface': 'interface', 'vrf': 'intvrf'},

    'show ipv6 interface brief': {'intf': 'interface', 'ipaddr': '//h4block'},
})
cmd_lst_int['show cdp neighbors detail'] = {'destination_host': '//nbr_hostname',
                                            'local_port': 'interface',
                                            'management_ip': 'nbr_ip',
                                            'platform': 'nbr_platform',
                                            'remote_port': 'nbr_interface'}
cmd_lst_int['show lldp neighbors detail'] = {'local_interface': 'interface',
                                            'management_ip': 'nbr_ip',
                                            'neighbor': '//nbr_hostname',
                                            'neighbor_port_id': 'nbr_interface',
                                            'serial': 'nbr_serial',
                                            'vlan': 'nbr_vlan'}

#
# ---------- VRF
#
cmd_lst_vrf = {
    'show vrf': {'name': 'vrf'},
}

#
# ---------- BGP
#
cmd_lst_bgp = {
    'show ip bgp all summary': {'addr_family': 'bgp_vrf',
                            'bgp_neigh': 'bgp_peer_ip'},
    'show ip bgp vpnv4 all neighbors': {'peer_group': 'bgp_peergrp',
                                    'remote_ip': 'bgp_peer_ip'},
}

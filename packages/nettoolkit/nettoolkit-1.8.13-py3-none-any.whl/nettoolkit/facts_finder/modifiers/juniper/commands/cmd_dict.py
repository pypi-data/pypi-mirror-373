"""
# ---------------------------------------------------------------------------
#  THIS FILE CONTAINS THE COLUMN MAPPINGS FROM THE FILE WHICH GOT GENERATED 
#  FROM CAPTURE_IT USING TEXTFSM AND
#  RELATIVE REQUIRED FIELD VALUES. 
# ---------------------------------------------------------------------------
"""
#
# ---------- VAR
#
cmd_lst_var = {
    'show version': {'hostname': 'hostname',
                            'junos_version': 'ios_version',
                            'model': 'hardware',
                            'serial_number': 'serial'}
}

#
# ---------- INTERFACES
#
cmd_lst_int = {
    'show interfaces': {'admin_state': 'link_status',
                                'description': 'description',
                                'destination': '//subnet',
                                'hardware_type': 'GRE',
                                'interface': 'interface',
                                'link_status': 'protocol_status',
                                'local': '//subnet1'},
    'show lldp neighbors': {'local_interface': 'interface',
                               'port_info': 'nbr_interface',
                               'system_name': '//nbr_hostname'}
}

#
# ---------- VRF
#
cmd_lst_vrf = {

}

#
# ---------- BGP
#
cmd_lst_bgp = {


}

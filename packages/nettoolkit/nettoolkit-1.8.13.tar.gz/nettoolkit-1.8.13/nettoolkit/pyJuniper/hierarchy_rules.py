


###
### NOTE: PROVIDED LIST/SETS ARE NOT COMPLETE, IT MAY NEED EDIT/ADDS AS FOUND MORE
###

candidates_require_suffix = {
	'family', 
	'filter', 
	'term', 
	'source-port',
	'destination-port', 
	'ip-protocol',
	'forwarding-class',
	'loss-priority',
	'count',
	'ether-type',
	'host-name',
	'domain-name',
	'time-zone',
	'aging-timer',
	'no-tcp-reset',
	'authentication-order',
	'console', 'auxiliary',
	'encrypted-password', 'secret', 
	'timeout', 
	'source-address',
	'events',
	'announcement', 'message',
	'tries-before-disconnect',
	'class', 'user', 'uid', 'full-name', 
	'idle-timeout', 'connection-limit', 'rate-limit',
	'permissions',
	'allow-commands',
	'root-login',
	'protocol-version',
	'key-exchange',
	'any',
	'interactive-commands',
	'change-log',
	'match',
	'facility-override',
	'host', 
	'file',
	'authorization',
	'daemon', 'kernel', 
	'commit',
	# 'server',
	'device-count',
	'link-down',
	'interface-range',
	'member',
	'description',
	'unit',
	'802.3ad',
	'mtu',
	'address',
	'interface-mode',
	# 'members',
	'storm-control',
	'recovery-timeout',
	'link-speed',
	'periodic',
	'vrrp-group',
	'virtual-address',
	'priority',
	'fast-interval',
	'hold-time',
	'priority-hold-time',
	'interface',
	'priority-cost',
	'input',
	'output',
	'location',
	'contact',
	'authorization',
	'client-list-name',
	'trap-group',
	'version',
	'interval',
	'rising-threshold',
	'falling-threshold',
	'storm-control-profiles',
	'bandwidth-level',
	'group',
	'router-id',
	'autonomous-system',
	'export',
	'import',
	'preference',
	'minimum-hold-time',
	'type',
	'neighbor',
	'delay',
	'holddown',
	'rapid-runs',
	'external-preference',
	'reference-bandwidth',
	'area',
	'interface-type',
	'metric',
	'simple-password',
	'egress-policy',
	'label-withdrawal-delay',
	'transport-address',
	'keepalive-interval',
	'keepalive-timeout',
	'igp-synchronization', 'holddown-interval',
	'hello-interval',
	'failover-delay',
	'startup-silent-period',
	'global-mac-table-aging-time',
	'management-address',
	'port-id-subtype',
	'bridge-priority',
	'max-age',
	'forward-delay',
	'mode',
	'prefix-list',
	'authentication-key',
	'local-address',
	'vlan',
	'policy-statement',
	'load-balance',
	'rib',
	'origin',
	'community',
	'next',
	'tag',
	'policy',
	'local-preference',
	'firewall',
	'as-path',
	'dscp',
	'low',
	'loss-priority',
	'prefix-list-filter',
	'exp',
	'scheduler-map',
	'percent',
	'buffer-size',
	'guaranteed-rate',
	'transmit-rate',
	'output-traffic-control-profile',
	# 'scheduler',
	'ttl',
	'instance-type',
	'route-distinguisher',
	'route',
	'next-hop',
	'vlan-id',
	'l3-interface',

	'archive',			# Multiple words following archive
	'member-range'


	}

candidates_require_suffix_include_members = {

}
candidates_require_suffix_exclude_members = {
	'filter': ('input', 'output'),
	'interactive-commands': ('interactive-commands',),
	'vlan': ('members'),
	'firewall': ('family', ),
	# 'nc': ('loss-priority', )


}

candidates_distributed_to_multi_lines = {
	'set',
	'add',
	'community',
}
candidates_distributed_to_multi_lines_exclude = {
	
}
candidates_distributed_to_multi_lines_include = {
	'community': ('add', 'set'),
}


candidates_can_club_members = {
	'source-port',
	'destination-port', 
	'events',
	'permissions',
	'members',
	'apply-path',
	'protocol',
	'code-points', 
	'code-point',
	'icmp-type',
	'apply-groups',
	'vrf-export',
	'next-hop',
	'import',


	}

candidates_not_expand_if_single = set()
candidates_not_expand_in_anycase = set()


# EXCEPTIONAL_WORDS = {
# 	'firewall',

# }

description_strings = {
	'description',
	'secret',
	'announcement',
	'message',
	'allow-commands',
	'encrypted-password',
	'authentication-key',
	'simple-password',
	'full-name',
	'match',
	'apply-path',
	'archive',
	'member-range',
	'location',
	'contact',
	'as-path',
}


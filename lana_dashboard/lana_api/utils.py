from functools import reduce


def reduce_networks(networks):
	def reducer(previous, current):
		# If current is a subnetwork of any previous network, skip it.
		if any(current.network_address in k and current.prefixlen > k.prefixlen for k in previous):
			return previous

		# Remove all previous subnetworks of current.
		keep = [k for k in previous if k.network_address not in current or k.prefixlen <= current.prefixlen]
		return keep + [current]
	return reduce(reducer, networks, [])

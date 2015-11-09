from __future__ import unicode_literals
from bisect import bisect_left, bisect_right
from functools import total_ordering
from socket import inet_aton, inet_ntoa
from struct import Struct


ipv4_struct = Struct('!I')


def ipv4_to_int(ip, unpack=ipv4_struct.unpack, inet_aton=inet_aton):
    return unpack(inet_aton(ip))[0]


def ipv4_from_int(ip_int, pack=ipv4_struct.pack, inet_ntoa=inet_ntoa):
    return inet_ntoa(pack(ip_int))


def ipv4_mask(length, ALL_ONES=(1 << 32) - 1):
    if not (0 <= length <= 32):
        raise ValueError('Invalid length: {}'.format(length))

    return ALL_ONES ^ (ALL_ONES >> length)


@total_ordering
class IPv4Network(object):
    __slots__ = ['net_int', 'bcast_int', 'length', 'data']

    def __init__(self, cidr, data=None):
        cidr = cidr.split('/')
        if len(cidr) == 1:
            length = 32
        elif len(cidr) == 2:
            length = int(cidr[1])
        else:
            raise ValueError('Invalid IPv4 CIDR notation: {}'.format(cidr))

        net = cidr[0]
        mask_int = ipv4_mask(length)
        span = (1 << (32 - length)) - 1

        self.length = length
        self.net_int = ipv4_to_int(net) & mask_int
        self.bcast_int = self.net_int + span
        self.data = data

    @property
    def network_address(self):
        return ipv4_from_int(self.net_int)

    @property
    def broadcast_address(self):
        return ipv4_from_int(self.bcast_int)

    def __eq__(self, other):
        return (
            self.net_int == other.net_int and
            self.length == other.length
        )

    def __lt__(self, other):
        if self.net_int < other.net_int:
            return True

        if self.net_int > other.net_int:
            return False

        return self.length < other.length

    def __contains__(self, other):
        return (
            self.net_int <= other.net_int <= other.bcast_int <= self.bcast_int
        )

    def __repr__(self):
        return '{}/{}'.format(self.network_address, self.length)


class NetworkFinder(object):
    def __init__(self):
        self._network_list = []

    def add(self, cidr):
        """
        Inserts the network described by `cidr`. Returns the inserted
        network object. Does not insert duplicate networks.
        """
        network = IPv4Network(cidr)

        # If the network is already present, don't add another instance
        i = bisect_right(self._network_list, network)
        if i and network == self._network_list[i - 1]:
            return network

        self._network_list.insert(i, network)
        return network

    def delete(self, cidr):
        """
        Deletes the network described by `cidr`. Raises KeyError if the network
        is not found.
        """
        network = IPv4Network(cidr)
        i = bisect_right(self._network_list, network)
        if i and network == self._network_list[i - 1]:
            del self._network_list[i - 1]
        else:
            raise KeyError('{} not found'.format(network))

    def search_exact(self, cidr):
        """
        Finds the network described by `cidr`. Returns None if there is no
        match.
        """
        network = IPv4Network(cidr)
        i = bisect_right(self._network_list, network)
        if i:
            found = self._network_list[i - 1]
            if network == found:
                return found

        return None

    def search_best(self, cidr):
        """
        Finds the network with the longest prefix that matches the network
        described by `cidr`. Returns None if there is no match.
        """
        network = IPv4Network(cidr)
        i = bisect_right(self._network_list, network)
        while i:
            found = self._network_list[i - 1]
            if network in found:
                return found
            i -= 1

        return None

    def search_worst(self, cidr):
        """
        Finds the network with the shortest prefix that matches the network
        described by `cidr`. Returns None if there is no match.
        """
        network = IPv4Network(cidr)
        i = bisect_right(self._network_list, network)
        ret = None
        while i:
            found = self._network_list[i - 1]
            if network in found:
                ret = found
            i -= 1

        return ret

    def search_covered(self, cidr):
        """
        Finds the networks that are contained by the network described by
        `cidr`. Returns an empty list if there are none.
        """
        network = IPv4Network(cidr)
        i = bisect_left(self._network_list, network)
        ret = []
        while i != len(self._network_list):
            found = self._network_list[i]
            if found in network:
                ret.append(found)
            i += 1

        return ret

    def search_covering(self, cidr):
        """
        Finds the networks that are have a matching prefix with the network
        described by `cidr`. Returns an empty list if there are none.
        """
        network = IPv4Network(cidr)
        i = bisect_right(self._network_list, network)
        ret = []
        while i:
            found = self._network_list[i - 1]
            if network in found:
                ret.append(found)
            i -= 1

        return ret

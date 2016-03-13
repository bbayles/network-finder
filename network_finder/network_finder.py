from __future__ import unicode_literals
from bisect import bisect_left, bisect_right
from functools import total_ordering
from socket import AF_INET6, inet_aton, inet_ntoa, inet_ntop, inet_pton
from struct import Struct
from sys import version_info

integer_types = (int, long) if (version_info[0] == 2) else (int,)  # noqa
ipv4_struct = Struct(b'!I')
ipv6_struct = Struct(b'!QQ')


def ip_mask(length, bits):
    if not (0 <= length <= bits):
        raise ValueError('Invalid length: {}'.format(length))

    all_ones = (1 << bits) - 1
    return all_ones ^ (all_ones >> length)


@total_ordering
class BaseIPNetwork(object):
    __slots__ = ['net_int', 'bcast_int', 'length', '_data']

    def __init__(self, cidr, data=None):
        if isinstance(cidr, integer_types):
            net_int = cidr
            length = self.bits
        else:
            cidr = cidr.split('/')
            if len(cidr) == 1:
                length = self.bits
            elif len(cidr) == 2:
                length = int(cidr[1])
            else:
                raise ValueError('Invalid CIDR notation: {}'.format(cidr))

            net_int = self.ip_to_int(cidr[0])

        if (data is not None) and (not isinstance(data, dict)):
            raise ValueError('data argument must be a dict')

        mask_int = self.mask_cache[length]
        span = (1 << (self.bits - length)) - 1

        self.length = length
        self.net_int = net_int & mask_int
        self.bcast_int = self.net_int + span
        self._data = data

    @property
    def network_address(self):
        return self.ip_from_int(self.net_int)

    @property
    def broadcast_address(self):
        return self.ip_from_int(self.bcast_int)

    def __hash__(self):
        return hash((self.net_int, self.length))

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

    def __getattr__(self, attr):
        try:
            return self._data[attr]
        except (TypeError, KeyError):
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        try:
            return super(BaseIPNetwork, self).__setattr__(attr, value)
        except AttributeError:
            if self._data is None:
                self._data = {}
            self._data[attr] = value

    def __repr__(self):
        return "{}('{}/{}')".format(
            self.__class__.__name__, self.network_address, self.length
        )

    def __str__(self):
        return '{}/{}'.format(self.network_address, self.length)

    __unicode__ = __str__


class IPv4Network(BaseIPNetwork):
    __slots__ = []
    bits = 32
    mask_cache = {length: ip_mask(length, 32) for length in range(32 + 1)}

    @staticmethod
    def ip_to_int(ip, unpack=ipv4_struct.unpack, inet_aton=inet_aton):
        return unpack(inet_aton(ip))[0]

    @staticmethod
    def ip_from_int(ip_int, pack=ipv4_struct.pack, inet_ntoa=inet_ntoa):
        return inet_ntoa(pack(ip_int))


class IPv6Network(BaseIPNetwork):
    __slots__ = []
    bits = 128
    mask_cache = {length: ip_mask(length, 128) for length in range(128 + 1)}

    @staticmethod
    def ip_to_int(
        ip, unpack=ipv6_struct.unpack, inet_pton=inet_pton, af=AF_INET6,
    ):
        unpacked = unpack(inet_pton(af, ip))
        return (unpacked[0] << 64) | unpacked[1]

    @staticmethod
    def ip_from_int(ip_int, pack=ipv6_struct.pack, af=AF_INET6):
        return inet_ntop(af, pack(ip_int >> 64, ip_int & 0xffffffffffffffff))


class NetworkFinder(object):
    def __init__(self, IPNetwork=IPv4Network):
        self._network_list = []
        self.IPNetwork = IPNetwork

    def add(self, cidr, data=None, bisect_right=bisect_right):
        """
        Inserts the network described by `cidr`. Returns the inserted
        network object. Does not insert duplicate networks.
        """
        network = self.IPNetwork(cidr, data)

        # If the network is already present, don't add another instance
        i = bisect_right(self._network_list, network)
        if i and network == self._network_list[i - 1]:
            existing = self._network_list[i - 1]
            if data and existing._data:
                existing._data.update(data)
            elif data:
                existing._data = data
            return existing

        self._network_list.insert(i, network)
        return network

    def delete(self, cidr, bisect_right=bisect_right):
        """
        Deletes the network described by `cidr`. Raises KeyError if the network
        is not found.
        """
        network = self.IPNetwork(cidr)
        i = bisect_right(self._network_list, network)
        if i and network == self._network_list[i - 1]:
            del self._network_list[i - 1]
        else:
            raise KeyError('{} not found'.format(network))

    def search_exact(self, cidr, bisect_right=bisect_right):
        """
        Finds the network described by `cidr`. Returns None if there is no
        match.
        """
        network = self.IPNetwork(cidr)
        i = bisect_right(self._network_list, network)
        if i:
            found = self._network_list[i - 1]
            if network == found:
                return found

        return None

    def search_best(self, cidr, bisect_right=bisect_right):
        """
        Finds the network with the longest prefix that matches the network
        described by `cidr`. Returns None if there is no match.
        """
        network = self.IPNetwork(cidr)
        i = bisect_right(self._network_list, network)
        while i:
            found = self._network_list[i - 1]
            if network in found:
                return found
            i -= 1

        return None

    def search_worst(self, cidr, bisect_right=bisect_right):
        """
        Finds the network with the shortest prefix that matches the network
        described by `cidr`. Returns None if there is no match.
        """
        network = self.IPNetwork(cidr)
        i = bisect_right(self._network_list, network)
        ret = None
        while i:
            found = self._network_list[i - 1]
            if network in found:
                ret = found
            i -= 1

        return ret

    def search_covered(self, cidr, bisect_left=bisect_left):
        """
        Finds the networks that are contained by the network described by
        `cidr`. Returns an empty list if there are none.
        """
        network = self.IPNetwork(cidr)
        i = bisect_left(self._network_list, network)
        ret = []
        while i != len(self._network_list):
            found = self._network_list[i]
            if found in network:
                ret.append(found)
            i += 1

        return ret

    def search_covering(self, cidr, bisect_right=bisect_right):
        """
        Finds the networks that are have a matching prefix with the network
        described by `cidr`. Returns an empty list if there are none.
        """
        network = self.IPNetwork(cidr)
        i = bisect_right(self._network_list, network)
        ret = []
        while i:
            found = self._network_list[i - 1]
            if network in found:
                ret.append(found)
            i -= 1

        return ret

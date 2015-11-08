from __future__ import unicode_literals
from bisect import bisect_left, bisect_right
from ipaddress import ip_network


class NetworkFinder(object):
    def __init__(self, items=None, strict=False):
        self._network_list = []

    def add(self, item, strict=False):
        """
        Inserts the network described by `item`. Returns the inserted network
        object. Does not insert duplicate networks.
        `item` and `strict` are passed to the ipaddress.ip_network constructor.
        """
        network = ip_network(item, strict)

        # If the network is already present, don't add another instance
        i = bisect_right(self._network_list, network)
        if i and network == self._network_list[i - 1]:
            return network

        self._network_list.insert(i, network)
        return network

    def delete(self, item, strict=False):
        """
        Deletes the network described by `item`.
        Raises KeyError if the network is not found.
        """
        network = ip_network(item, strict)
        i = bisect_right(self._network_list, network)
        if i and network == self._network_list[i - 1]:
            del self._network_list[i - 1]
        else:
            raise KeyError('{} not found'.format(network))

    def search_exact(self, item, strict=False):
        """
        Finds the network described by `item`. Returns None if there is no
        match.
        """
        network = ip_network(item, strict)
        i = bisect_right(self._network_list, network)
        if i:
            found = self._network_list[i - 1]
            if network == found:
                return found

        return None

    def search_best(self, item, strict=False):
        """
        Finds the network with the longest prefix that matches the network
        described by `item`. Returns None if there is no match.
        """
        network = ip_network(item, strict)
        i = bisect_right(self._network_list, network)
        while i:
            found = self._network_list[i - 1]
            if network.network_address in found:
                return found
            i -= 1

        return None

    def search_worst(self, item, strict=False):
        """
        Finds the network with the shortest prefix that matches the network
        described by `item`. Returns None if there is no match.
        """
        network = ip_network(item, strict)
        i = bisect_right(self._network_list, network)
        ret = None
        while i:
            found = self._network_list[i - 1]
            if network.network_address in found:
                ret = found
            i -= 1

        return ret

    def search_covered(self, item, strict=False):
        """
        Finds the networks that are contained by the network described by
        `item`. Returns an empty list if there are none.
        """
        network = ip_network(item, strict)
        i = bisect_left(self._network_list, network)
        ret = []
        while i != len(self._network_list):
            found = self._network_list[i]
            if found.network_address in network:
                ret.append(found)
            i += 1

        return ret

    def search_covering(self, item, strict=False):
        """
        Finds the networks that are have a matching prefix with the network
        described by `item`. Returns an empty list if there are none.
        """
        network = ip_network(item, strict)
        i = bisect_right(self._network_list, network)
        ret = []
        while i:
            found = self._network_list[i - 1]
            if network.network_address in found:
                ret.append(found)
            i -= 1

        return ret

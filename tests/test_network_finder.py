from __future__ import unicode_literals
from unittest import TestCase
from network_finder import NetworkFinder
from network_finder.network_finder import ip_mask, IPv4Network, IPv6Network

# Python 2 does not have TestCase.assertCountEqual
try:
    TestCase.assertCountEqual = TestCase.assertItemsEqual
except AttributeError:
    pass


class IPNetworkTests(TestCase):
    def test_ip_mask_v4(self):
        ipv4_masks = [
            (0, 0x00000000),
            (1, 0x80000000),
            (2, 0xc0000000),
            (3, 0xe0000000),
            (4, 0xf0000000),
            (5, 0xf8000000),
            (6, 0xfc000000),
            (7, 0xfe000000),
            (8, 0xff000000),
            (9, 0xff800000),
            (10, 0xffc00000),
            (11, 0xffe00000),
            (12, 0xfff00000),
            (13, 0xfff80000),
            (14, 0xfffc0000),
            (15, 0xfffe0000),
            (16, 0xffff0000),
            (17, 0xffff8000),
            (18, 0xffffc000),
            (19, 0xffffe000),
            (20, 0xfffff000),
            (21, 0xfffff800),
            (22, 0xfffffc00),
            (23, 0xfffffe00),
            (24, 0xffffff00),
            (25, 0xffffff80),
            (26, 0xffffffc0),
            (27, 0xffffffe0),
            (28, 0xfffffff0),
            (29, 0xfffffff8),
            (30, 0xfffffffc),
            (31, 0xfffffffe),
            (32, 0xffffffff),
        ]
        for length, mask_int in ipv4_masks:
            self.assertEqual(ip_mask(length, bits=32), mask_int)

        with self.assertRaises(ValueError):
            ip_mask(-1, bits=32)
            ip_mask(33, bits=32)

    def test_ip_mask_v6(self):
        # See: https://en.wikipedia.org/wiki/IPv6_subnetting_reference
        ipv6_masks = [
            (12, 0xfff00000000000000000000000000000),
            (20, 0xfffff000000000000000000000000000),
            (24, 0xffffff00000000000000000000000000),
            (28, 0xfffffff0000000000000000000000000),
            (32, 0xffffffff000000000000000000000000),
            (36, 0xfffffffff00000000000000000000000),
            (48, 0xffffffffffff00000000000000000000),
            (52, 0xfffffffffffff0000000000000000000),
            (56, 0xffffffffffffff000000000000000000),
            (60, 0xfffffffffffffff00000000000000000),
            (64, 0xffffffffffffffff0000000000000000),
            (127, 0xfffffffffffffffffffffffffffffffe),
            (128, 0xffffffffffffffffffffffffffffffff),
        ]
        for length, mask_int in ipv6_masks:
            self.assertEqual(ip_mask(length, bits=128), mask_int)

        with self.assertRaises(ValueError):
            ip_mask(-1, bits=128)
            ip_mask(129, bits=128)

    def test_init_v4(self):
        for host_addr in ('192.0.2.1', 3221225985):
            host = IPv4Network(host_addr, {'name': 'RFC 5737 host'})
            self.assertEqual(host.net_int, 3221225985)
            self.assertEqual(host.bcast_int, 3221225985)
            self.assertEqual(host.length, 32)
            self.assertEqual(host._data, {'name': 'RFC 5737 host'})
            self.assertEqual(host.network_address, '192.0.2.1')
            self.assertEqual(host.broadcast_address, '192.0.2.1')

        net = IPv4Network('192.0.2.1/24', {'name': 'RFC 5737 net'})
        self.assertEqual(net.net_int, 3221225984)
        self.assertEqual(net.bcast_int, 3221226239)
        self.assertEqual(net.length, 24)
        self.assertEqual(net._data, {'name': 'RFC 5737 net'})
        self.assertEqual(net.network_address, '192.0.2.0')
        self.assertEqual(net.broadcast_address, '192.0.2.255')

        for bad_arg in (
            '192..2', '192.0.2.256', '192.0.2.1/33', '192.0.2.0/24/24'
        ):
            with self.assertRaises(Exception):
                IPv4Network(bad_arg)

        with self.assertRaises(ValueError):
            IPv4Network('192.0.2.0/24', 'something')

    def test_init_v6(self):
        for host_addr in (
            '2001:0db8::',
            0x20010db8000000000000000000000000,
        ):
            host = IPv6Network(host_addr)
            self.assertEqual(host.net_int, 0x20010db8000000000000000000000000)
            self.assertEqual(
                host.bcast_int, 0x20010db8000000000000000000000000
            )
            self.assertEqual(host.length, 128)
            self.assertEqual(host.network_address, '2001:db8::')
            self.assertEqual(host.broadcast_address, '2001:db8::')

        net = IPv6Network('2001:0db8::/32')
        self.assertEqual(net.net_int, 0x20010db8000000000000000000000000)
        self.assertEqual(net.bcast_int, 0x20010db8ffffffffffffffffffffffff)
        self.assertEqual(net.length, 32)
        self.assertEqual(net.network_address, '2001:db8::')
        self.assertEqual(
            net.broadcast_address, '2001:db8:ffff:ffff:ffff:ffff:ffff:ffff'
        )

        with self.assertRaises(ValueError):
            IPv6Network('2001:0db8::/32', 'something')

    def test_hash(self):
        v4_net_set = {
            IPv4Network('192.0.2.0'),
            IPv4Network('192.0.2.0/32'),
            IPv4Network('192.0.2.0/24'),
        }
        self.assertEqual(len(v4_net_set), 2)

        v6_net_set = {
            IPv6Network('2001:db8::'),
            IPv6Network('2001:db8::/128'),
            IPv6Network('2001:db8:0123::/32'),
        }
        self.assertEqual(len(v6_net_set), 2)

    def test_eq(self):
        self.assertEqual(
            IPv4Network('192.0.2.0'), IPv4Network('192.0.2.0/32')
        )
        self.assertNotEqual(
            IPv4Network('192.0.2.0/24'), IPv4Network('192.0.2.0/25')
        )

        self.assertEqual(
            IPv6Network('2001:db8::'), IPv6Network('2001:db8::/128')
        )
        self.assertNotEqual(
            IPv6Network('2001:db8::/32'), IPv6Network('2001:db8::/64')
        )

    def test_sorting(self):
        v4_net_list = [
            IPv4Network('192.0.2.0/24'),
            IPv4Network('192.0.2.0/25'),
            IPv4Network('192.0.2.128/25'),
            IPv4Network('192.0.2.0/26'),
            IPv4Network('192.0.2.64/26'),
            IPv4Network('192.0.2.128/26'),
            IPv4Network('192.0.2.192/26'),
        ]
        v4_net_list.sort()
        actual = [str(x) for x in v4_net_list]
        expected = [
            '192.0.2.0/24',
            '192.0.2.0/25',
            '192.0.2.0/26',
            '192.0.2.64/26',
            '192.0.2.128/25',
            '192.0.2.128/26',
            '192.0.2.192/26',
        ]
        self.assertEqual(actual, expected)

        v6_net_list = [
            IPv6Network('2001:db8::/64'),
            IPv6Network('2001:db8::/32'),
            IPv6Network('2001:db8::/128'),
        ]
        v6_net_list.sort()
        actual = [str(x) for x in v6_net_list]
        expected = [
            '2001:db8::/32', '2001:db8::/64', '2001:db8::/128',
        ]
        self.assertEqual(actual, expected)

    def test_contains(self):
        v4_cases = [
            ('192.0.2.0', '192.0.2.0/24', True),
            ('192.0.2.1', '192.0.2.0/24', True),
            ('192.0.2.255', '192.0.2.0/24', True),
            ('192.0.2.129', '192.0.2.0/25', False),
            ('192.0.2.128/25', '192.0.2.0/24', True),
            ('192.0.2.128/25', '192.0.2.0/26', False),
        ]
        for needle, haystack, result in v4_cases:
            self.assertTrue(
                (IPv4Network(needle) in IPv4Network(haystack)) == result
            )

        v6_cases = [
            ('2001:db8::', '2001:db8::/32', True),
            ('2001:db8::', '2001:db8:ffff::/64', False),
            ('2001:db8::/48', '2001:db8::/32', True),
            ('2001:db8::/48', '2001:db8::/64', False),
        ]
        for needle, haystack, result in v6_cases:
            self.assertTrue(
                (IPv6Network(needle) in IPv6Network(haystack)) == result
            )

    def test_ip_to_int(self):
        v4_cases = [
            ('192.0.2.0', 3221225984),
            ('192.0.2.1', 3221225985),
            ('192.0.2.255', 3221226239),
        ]
        for ip_str, ip_int in v4_cases:
            self.assertEqual(IPv4Network.ip_to_int(ip_str), ip_int)
            self.assertEqual(IPv4Network.ip_from_int(ip_int), ip_str)

        v6_cases = [
            ('2001:db8::', 0x20010db8000000000000000000000000),
            ('2001:db8::1', 0x20010db8000000000000000000000001),
            (
                '2001:db8:ffff:ffff:ffff:ffff:ffff:ffff',
                0x20010db8ffffffffffffffffffffffff,
            ),
        ]
        for ip_str, ip_int in v6_cases:
            self.assertEqual(IPv6Network.ip_to_int(ip_str), ip_int)
            self.assertEqual(IPv6Network.ip_from_int(ip_int), ip_str)

    def test_getattr(self):
        v4_net = IPv4Network('192.0.2.0/24', data={'key_1': 'value_1'})
        self.assertEqual(v4_net.length, 24)
        self.assertEqual(v4_net.key_1, 'value_1')
        with self.assertRaises(AttributeError):
            v4_net.key_2

        v6_net = IPv6Network('2001:db8::/32', data={'key_1': 'value_1'})
        self.assertEqual(v6_net.length, 32)
        self.assertEqual(v6_net.key_1, 'value_1')
        with self.assertRaises(AttributeError):
            v6_net.key_2

        empty_net = IPv4Network('198.51.100.0/24')
        with self.assertRaises(AttributeError):
            empty_net.key_1

    def test_setattr(self):
        v4_net = IPv4Network('192.0.2.0/24', data={'key_1': 'value_1'})
        v4_net.key_2 = 'value_2'
        self.assertEqual(v4_net.key_2, 'value_2')

        v6_net = IPv6Network('2001:db8::/32', data={'key_1': 'value_1'})
        v6_net.key_2 = 'value_2'
        self.assertEqual(v6_net.key_2, 'value_2')

        empty_net = IPv4Network('198.51.100.0/24')
        empty_net.key = 'value'
        self.assertEqual(empty_net.key, 'value')

    def test_repr(self):
        v4_net = IPv4Network('192.0.2.0/24')
        v4_str = repr(v4_net)
        self.assertEqual(v4_net, eval(v4_str))

        v6_net = IPv6Network('2001:db8::/32')
        v6_str = repr(v6_net)
        self.assertEqual(v6_net, eval(v6_str))


class NetworkFinderTests(TestCase):
    def setUp(self):
        self.inst = NetworkFinder()

    def test_add(self):
        # The list of networks should maintain sorted order
        slash_16 = self.inst.add('10.0.0.0/16', data={1: 2})
        self.assertEqual(self.inst._network_list, [slash_16])

        slash_8 = self.inst.add('10.0.0.0/8')
        self.assertEqual(self.inst._network_list, [slash_8, slash_16])

        slash_24 = self.inst.add('10.0.0.0/24')
        self.assertEqual(
            self.inst._network_list, [slash_8, slash_16, slash_24]
        )

        # Duplicates are not allowed, but existing data should not be destroyed
        node = self.inst.add('10.0.0.0/16')
        self.assertEqual(
            self.inst._network_list, [slash_8, slash_16, slash_24]
        )
        self.assertEqual(node._data, {1: 2})

        # Additional data should be stored for a duplicate
        node = self.inst.add('10.0.0.0/16', data={3: 4})
        self.assertEqual(
            self.inst._network_list, [slash_8, slash_16, slash_24]
        )
        self.assertEqual(node._data, {1: 2, 3: 4})

        # Additional data should be stored for a duplicate
        node = self.inst.add('10.0.0.0/24', data={5: 6})
        self.assertEqual(
            self.inst._network_list, [slash_8, slash_16, slash_24]
        )
        self.assertEqual(node._data, {5: 6})

    def test_delete(self):
        slash_8 = self.inst.add('10.0.0.0/8')
        slash_24 = self.inst.add('10.0.0.0/24')

        self.inst.add('10.0.0.0/16')
        self.inst.delete('10.0.0.0/16')
        self.assertEqual(self.inst._network_list, [slash_8, slash_24])

        with self.assertRaises(KeyError):
            self.inst.delete('10.0.0.0/16')

    def test_user_data(self):
        # You should be able to store data on ip_network objects
        network = self.inst.add('192.0.2.1')
        network._data = {'key': 'value'}
        found = self.inst.search_exact('192.0.2.1')
        self.assertEqual(found._data['key'], 'value')

    def test_search_exact(self):
        slash_8 = self.inst.add('10.0.0.0/8')
        slash_16 = self.inst.add('10.0.0.0/16')
        slash_24 = self.inst.add('10.0.0.0/24')

        self.assertEqual(self.inst.search_exact('10.0.0.0/8'), slash_8)
        self.assertEqual(self.inst.search_exact('10.0.0.0/16'), slash_16)
        self.assertEqual(self.inst.search_exact('10.0.0.0/24'), slash_24)
        self.assertIsNone(self.inst.search_exact('10.0.0.0'))
        self.assertIsNone(self.inst.search_exact('192.0.2.1'))

    def test_search_best(self):
        slash_8 = self.inst.add('10.0.0.0/8')
        slash_13 = self.inst.add('10.0.0.0/13')
        slash_16 = self.inst.add('10.0.0.0/16')
        slash_24 = self.inst.add('10.0.0.0/24')

        self.assertEqual(self.inst.search_best('10.0.0.0'), slash_24)
        self.assertEqual(self.inst.search_best('10.0.0.0/24'), slash_24)
        self.assertEqual(self.inst.search_best('10.0.1.0/15'), slash_13)
        self.assertEqual(self.inst.search_best('10.0.1.0/24'), slash_16)
        self.assertEqual(self.inst.search_best('10.128.0.0'), slash_8)
        self.assertIsNone(self.inst.search_best('192.0.2.1'))

        slash_0 = self.inst.add('0.0.0.0/0')
        self.assertEqual(self.inst.search_best('192.0.2.1'), slash_0)

    def test_search_worst(self):
        slash_8 = self.inst.add('10.0.0.0/8')
        self.inst.add('10.0.0.0/13')
        self.inst.add('10.0.0.0/16')

        self.assertEqual(self.inst.search_worst('10.0.0.0/24'), slash_8)
        self.assertIsNone(self.inst.search_worst('100.0.1.0/15'))

    def test_search_covered(self):
        self.inst.add('10.0.0.0/8')
        self.inst.add('10.0.0.0/13')
        self.inst.add('10.0.0.0/31')
        self.inst.add('11.0.0.0/16')
        self.inst.add('27.0.100.0/24')
        self.inst.add('27.0.101.0/24')
        self.inst.add('193.178.156.0/24')
        self.inst.add('193.178.157.0/24')

        cases = [
            ('10.0.0.0/8', ['10.0.0.0/8', '10.0.0.0/13', '10.0.0.0/31']),
            ('10.0.0.0/9', ['10.0.0.0/13', '10.0.0.0/31']),
            ('11.0.0.0/8', ['11.0.0.0/16']),
            ('21.0.0.0/8', []),
            ('31.3.104.0/21', []),
            ('193.178.152.0/21', ['193.178.156.0/24', '193.178.157.0/24']),
            ('0.0.0.0/0', [str(x) for x in self.inst._network_list]),
        ]
        for arg, expected in cases:
            actual = [str(x) for x in self.inst.search_covered(arg)]
            self.assertEqual(actual, expected)

    def test_search_covering(self):
        self.inst.add('0.0.0.0/2')
        self.inst.add('8.9.0.1/32')
        self.inst.add('8.9.0.0/16')
        self.inst.add('3.178.156.0/24')
        self.inst.add('3.178.157.0/24')

        cases = [
            ('8.9.0.1/32', ['8.9.0.1/32', '8.9.0.0/16', '0.0.0.0/2']),
            ('5.5.5.0/24', ['0.0.0.0/2']),
            ('3.178.152.0/21', ['0.0.0.0/2']),
            ('205.0.1.0/24', []),
        ]
        for arg, expected in cases:
            actual = [str(x) for x in self.inst.search_covering(arg)]
            self.assertCountEqual(actual, expected)

    def test_v6(self):
        inst = NetworkFinder(IPv6Network)

        slash_16 = inst.add('fd00:0000:0000:0000::/16')
        slash_32 = inst.add('fd00:0000:0000:0000::/32')
        slash_48 = inst.add('fd00:0000:0000:0000::/48')
        slash_64 = inst.add('fd00:0000:0000:0000::/64')
        self.assertEqual(
            inst._network_list, [slash_16, slash_32, slash_48, slash_64]
        )

        inst.delete('fd00::/32')
        self.assertEqual(
            inst._network_list, [slash_16, slash_48, slash_64]
        )

        self.assertEqual(inst.search_exact('fd00::/64'), slash_64)
        self.assertIsNone(inst.search_exact('fd00:0001::/64'))

        self.assertEqual(inst.search_best('fd00::/64'), slash_64)
        self.assertEqual(
            inst.search_best('fd00:0000:0000:0001::/64'), slash_48
        )

        self.assertEqual(inst.search_worst('fd00::/64'), slash_16)
        self.assertEqual(
            inst.search_worst('fd00:0000:0000:0001::/64'), slash_16
        )

        self.assertEqual(
            inst.search_covered('fd00::/32'), [slash_48, slash_64]
        )

        self.assertCountEqual(
            inst.search_covering('fd00::/48'), [slash_16, slash_48]
        )

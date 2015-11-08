from __future__ import unicode_literals
from unittest import TestCase
from network_finder import NetworkFinder

# Python 2 does not have TestCase.assertCountEqual
try:
    TestCase.assertCountEqual = TestCase.assertItemsEqual
except AttributeError:
    pass


class NetworkFinderTestCase(TestCase):
    def setUp(self):
        self.inst = NetworkFinder()

    def test_add(self):
        # The list of networks should maintain sorted order
        slash_16 = self.inst.add('10.0.0.0/16')
        self.assertEqual(self.inst._network_list, [slash_16])

        slash_8 = self.inst.add('10.0.0.0/8')
        self.assertEqual(self.inst._network_list, [slash_8, slash_16])

        slash_24 = self.inst.add('10.0.0.0/24')
        self.assertEqual(
            self.inst._network_list, [slash_8, slash_16, slash_24]
        )

        # Duplicates are not allowed
        self.inst.add('10.0.0.0/16')
        self.assertEqual(
            self.inst._network_list, [slash_8, slash_16, slash_24]
        )

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
        network.data = {'key': 'value'}
        found = self.inst.search_exact('192.0.2.1')
        self.assertEqual(found.data['key'], 'value')

    def test_search_exact(self):
        slash_8 = self.inst.add('10.0.0.0/8')
        slash_16 = self.inst.add('10.0.0.0/16')
        slash_24 = self.inst.add('10.0.0.0/24')

        self.assertEqual(self.inst.search_exact('10.0.0.0/8'), slash_8)
        self.assertEqual(self.inst.search_exact('10.0.0.0/24'), slash_24)
        self.assertIsNone(self.inst.search_exact('10.0.0.0'))
        self.assertEqual(self.inst.search_exact('10.0.0.0/16'), slash_16)
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
        slash_16 = self.inst.add('fd00:0000:0000:0000::/16')
        slash_32 = self.inst.add('fd00:0000:0000:0000::/32')
        slash_48 = self.inst.add('fd00:0000:0000:0000::/48')
        slash_64 = self.inst.add('fd00:0000:0000:0000::/64')
        self.assertEqual(
            self.inst._network_list, [slash_16, slash_32, slash_48, slash_64]
        )

        self.inst.delete('fd00::/32')
        self.assertEqual(
            self.inst._network_list, [slash_16, slash_48, slash_64]
        )

        self.assertEqual(self.inst.search_exact('fd00::/64'), slash_64)
        self.assertIsNone(self.inst.search_exact('fd00:0001::/64'))

        self.assertEqual(self.inst.search_best('fd00::/64'), slash_64)
        self.assertEqual(
            self.inst.search_best('fd00:0000:0000:0001::/64'), slash_48
        )

        self.assertEqual(self.inst.search_worst('fd00::/64'), slash_16)
        self.assertEqual(
            self.inst.search_worst('fd00:0000:0000:0001::/64'), slash_16
        )

        self.assertEqual(
            self.inst.search_covered('fd00::/32'), [slash_48, slash_64]
        )

        self.assertCountEqual(
            self.inst.search_covering('fd00::/48'), [slash_16, slash_48]
        )

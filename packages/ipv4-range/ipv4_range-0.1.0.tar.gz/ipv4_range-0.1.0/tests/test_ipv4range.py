from ipaddress import IPv4Address, AddressValueError, NetmaskValueError, IPv4Network

from ipv4_range import IPv4Range
from contextlib import nullcontext as does_not_raise
import pytest


class TestIpv4Range:

    @pytest.mark.parametrize(
            ('item', 'expected'),
            (
                    ('10.0.0.0-10.0.0.100', does_not_raise()),
                    ('10.1.0.0-10.0.0.100', pytest.raises(ValueError)),
                    ('10.1.as.0-10.0.0.100', pytest.raises(AddressValueError)),
                    ('10.1.as.0-10.0.as.100', pytest.raises(AddressValueError)),
                    ('10.1.0.0-10.0.as.100', pytest.raises(AddressValueError)),
            )
    )
    def test_init(self, item, expected):
        with expected:
            IPv4Range(item)

    @pytest.mark.parametrize(
            ('ips', 'result', 'expected'),
            (
                (
                    ['10.0.0.101', '10.0.0.102', '10.0.0.104', '10.0.0.105', '10.0.0.106'],
                    [IPv4Range('10.0.0.101-10.0.0.102'), IPv4Range('10.0.0.104-10.0.0.106')],
                    does_not_raise()
                ),
                (
                    ['10.0.0.101', '10.0.0.102', '10.0.0.104', '10.0.0.106', '10.0.0.107'],
                    [IPv4Range('10.0.0.101-10.0.0.102'), IPv4Address('10.0.0.104'), IPv4Range('10.0.0.106-10.0.0.107')],
                    does_not_raise()
                ),
                (
                    ['10.0.0.101', '10.0.0.104', '10.0.0.106', '10.0.0.107'],
                    [IPv4Address('10.0.0.101'), IPv4Address('10.0.0.104'), IPv4Range('10.0.0.106-10.0.0.107')],
                    does_not_raise()
                ),
                (
                    ['10.0.0.253', '10.0.0.254', '10.0.0.255', '10.0.1.0'],
                    [IPv4Range('10.0.0.253-10.0.1.0')],
                    does_not_raise()
                ),
                (
                    [IPv4Address('10.0.0.253'), IPv4Address('10.0.0.254'), IPv4Address('10.0.0.255'), '10.0.1.0'],
                    [IPv4Range('10.0.0.253-10.0.1.0')],
                    does_not_raise()
                ),
                (
                    ['10.sdf.0.253', '10.0.0.254', '10.0.0.255', '10.0.1.0'],
                    [],
                    pytest.raises(AddressValueError)
                ),
                (
                    [],
                    [],
                    does_not_raise()
                )
            )
    )
    def test_from_ips(self, ips, result, expected):
        with expected:
            assert IPv4Range.from_ips(ips) == result

    @pytest.mark.parametrize(
            ('network', 'result', 'expected'),
            (
                ('10.0.0.0/31', IPv4Range('10.0.0.0-10.0.0.1'), does_not_raise()),
                ('10.0.0.0/24', IPv4Range('10.0.0.0-10.0.0.255'), does_not_raise()),
                ('10.0.0.0/16', IPv4Range('10.0.0.0-10.0.255.255'), does_not_raise()),
                ('10.0.0.0/8', IPv4Range('10.0.0.0-10.255.255.255'), does_not_raise()),
                ('10.0.0.16/31', IPv4Range('10.0.0.16-10.0.0.17'), does_not_raise()),
                (IPv4Network('10.0.0.16/31'), IPv4Range('10.0.0.16-10.0.0.17'), does_not_raise()),
                ('10.0.0.16', IPv4Range('10.0.0.16-10.0.0.17'), pytest.raises(ValueError)),
                ('10.sf.0.16', IPv4Range('10.0.0.16-10.0.0.17'), pytest.raises(AddressValueError)),
                ('10.sf.0.16/34', IPv4Range('10.0.0.16-10.0.0.17'), pytest.raises(AddressValueError)),
            )
    )
    def test_from_network(self, network, result, expected):
        with expected:
            assert IPv4Range.from_network(network) == result

    @pytest.mark.parametrize(
            ('start', 'end', 'result', 'expected'),
            (
                    ('10.0.0.0', '10.0.0.100', IPv4Range('10.0.0.0-10.0.0.100'), does_not_raise()),
                    ('10.1.0.0', '10.0.0.100', None, pytest.raises(ValueError)),
                    (IPv4Address('10.0.0.0'), IPv4Address('10.0.0.100'), IPv4Range('10.0.0.0-10.0.0.100'), does_not_raise()),
                    (IPv4Address('10.1.0.0'), None, IPv4Address('10.0.0.100'), pytest.raises(ValueError)),
                    ('10.1.as.0', '10.0.0.100', None, pytest.raises(AddressValueError)),
                    ('10.1.as.0', '10.0.as.100', None, pytest.raises(AddressValueError)),
                    ('10.1.0.0', '10.0.as.100', None, pytest.raises(AddressValueError)),
            )
    )
    def test_from_start_end(self, start, end, result, expected):
        with expected:
            assert IPv4Range.from_start_and_end(start, end) == result


    @pytest.mark.parametrize(
            ('rng', 'result'),
            (
                (IPv4Range('10.0.0.0-10.0.0.255'), True),
                (IPv4Range('10.0.0.0-10.0.0.250'), False),
                (IPv4Range('10.0.0.0-10.0.0.127'), True),
                (IPv4Range('10.0.0.128-10.0.0.255'), True),
                (IPv4Range('10.0.0.0-10.0.0.1'), True),
                (IPv4Range('10.0.0.0-10.0.0.2'), False),
            )
    )
    def test_is_network(self, rng, result):
        assert rng.is_network == result

    @pytest.mark.parametrize(
            ('item', 'result', 'expected'),
            (
                (IPv4Range('10.0.0.0-10.0.0.255'), IPv4Network('10.0.0.0/24'), does_not_raise()),
                (IPv4Range('10.0.0.0-10.0.255.255'), IPv4Network('10.0.0.0/16'), does_not_raise()),
                (IPv4Range('10.0.0.0-10.0.0.2'), None, pytest.raises(ValueError)),
            )
    )
    def test_to_network(self, item, result, expected):
        with expected:
            assert IPv4Range.to_network(item) == result

    @pytest.mark.parametrize(
            ('a', 'b', 'result', 'expected'),
            (
                (IPv4Range('10.0.0.0-10.0.0.101'), IPv4Range('10.0.0.0-10.0.0.101'), True, does_not_raise()),
                (IPv4Range('10.0.0.0-10.0.0.100'), IPv4Range('10.0.0.0-10.0.0.101'), False, does_not_raise()),
                (IPv4Range('10.0.0.0-10.0.0.102'), IPv4Range('10.0.0.0-10.0.0.101'), False, does_not_raise()),
                (IPv4Range('10.0.0.0-10.0.0.255'), IPv4Network('10.0.0.0/24'), True, does_not_raise()),
                (IPv4Range('10.0.0.0-10.0.0.255'), '123', False, pytest.raises(TypeError)),
            )
    )
    def test_equals(self, a, b, result, expected):
        with expected:
            assert (a == b) == result

    @pytest.mark.parametrize(
            ('rng', 'item', 'result', 'expected'),
            (
                (
                    IPv4Range('10.0.0.0-10.0.0.100'),
                    IPv4Address('10.0.0.0'),
                    True,
                    does_not_raise()
                ),
                (
                    IPv4Range('10.0.0.0-10.0.0.100'),
                    IPv4Address('10.0.0.100'),
                    True,
                    does_not_raise()
                ),
                (
                    IPv4Range('10.0.0.0-10.0.0.100'),
                    IPv4Address('10.0.0.101'),
                    False,
                    does_not_raise()
                ),
                (
                    IPv4Range('10.0.0.1-10.0.0.100'),
                    IPv4Address('10.0.0.0'),
                    False,
                    does_not_raise()
                ),
                (
                    IPv4Range('10.0.0.0-10.0.0.100'),
                    '10.0.0.0',
                    True,
                    does_not_raise()
                ),
                (
                    IPv4Range('10.0.0.0-10.0.0.100'),
                    '10.0.0.100',
                    True,
                    does_not_raise()
                ),
                (
                    IPv4Range('10.0.0.0-10.0.0.100'),
                    '10.0.0.101',
                    False,
                    does_not_raise()
                ),
                (
                    IPv4Range('10.0.0.1-10.0.0.100'),
                    '10.0.0.0',
                    False,
                    does_not_raise()
                ),
                (
                    IPv4Range('10.0.0.1-10.0.0.100'),
                    '10.0.sd.0',
                    False,
                    pytest.raises(AddressValueError)
                ),
                (
                    IPv4Range('10.0.0.1-10.0.0.100'),
                    23.4,
                    False,
                    pytest.raises(TypeError)
                ),

            )
    )
    def test_contains(self, rng, item, result, expected):
        with expected:
            assert (item in rng) == result

    @pytest.mark.parametrize(
            ('item', 'result'),
            (
                (IPv4Range('10.0.0.0-10.0.0.100'), 101),
                (IPv4Range('10.0.0.0-10.0.0.255'), 256),
                (IPv4Range('10.0.0.0-10.0.0.5'), 6),
            )
    )
    def test_len(self, item, result):
        assert len(item) == result

    @pytest.mark.parametrize(
            ('item', 'result'),
            (
                (
                    IPv4Range('10.0.0.100-10.0.0.102'),
                    (IPv4Address('10.0.0.100'), IPv4Address('10.0.0.101'), IPv4Address('10.0.0.102'))
                ),
            )
    )
    def test_iter(self, item, result):
        for i, v in enumerate(item):
            assert v == result[i]


    @pytest.mark.parametrize(
            ('args', 'result', 'expected'),
            (
                (
                    (IPv4Address('10.0.0.101'), IPv4Address('10.0.0.102')),
                    True,
                    does_not_raise()
                ),
                (
                    (IPv4Address('10.0.0.102'), IPv4Address('10.0.0.101')),
                    False,
                    does_not_raise()
                ),
                (
                    (IPv4Address('10.0.0.101'), IPv4Address('10.0.0.101')),
                    False,
                    does_not_raise()
                ),
                (
                    ('10.0.0.0-10.0.0.100', ),
                    True,
                    does_not_raise()
                ),
                (
                    ('10.0.0.101-10.0.0.100', ),
                    False,
                    does_not_raise()
                ),
                (
                    tuple(),
                    False,
                    pytest.raises(ValueError)
                ),
                (
                    ('10.0.0.0-10.0.0.100', '123'),
                    False,
                    does_not_raise()
                ),
                (
                    ('10.0.0.0-10.0.0.100', '123', '123'),
                    False,
                    pytest.raises(ValueError)
                ),
            )
    )
    def test_is_ipv4_range(self, args, result, expected):
        with expected:
            assert IPv4Range.is_ip_range(*args) == result




import math
from ipaddress import IPv4Address, IPv4Network, AddressValueError
from typing import Collection, Iterable, Sequence, Union, overload


class IPv4Range(Collection):
    """
    Implementation ranges of mikrotik

    Examples:
        10.0.0.0-10.0.0.101

    Usage:
        ```python
        rng = IPv4Range('10.0.0.0-10.0.0.101')
        rng.to_network()
        ```

    :param ip_range: ip range string Example: '10.0.0.0-10.0.0.101'
    :raises AddressValueError: If one of two string is not a valid IPv4 address.
    :raises ValueError: if start IP great then end ip
    """
    def __init__(self, ip_range: str) -> None:
        [start_ip_str, end_ip_str] = ip_range.split("-")

        self.start_ip = IPv4Address(start_ip_str)
        self.end_ip = IPv4Address(end_ip_str)
        self._len = None
        self._network_mask = None

        if self.start_ip >= self.end_ip:
            raise ValueError('start_ip must be greater than end_ip')

    @classmethod
    def from_start_and_end(cls, ip_start: IPv4Address | str, ip_end: IPv4Address | str) -> "IPv4Range":
        """Create IPv4Range from start and end IP addresses

        :param ip_start: start IP address
        :param ip_end: end IP address
        :type ip_start: IPv4Address | str
        :type ip_end: IPv4Address | str
        :rtype: IPv4Range
        :return: IPv4Range from start and end IP addresses
        """
        return IPv4Range(f'{ip_start}-{ip_end}')

    @classmethod
    def from_ips(cls, *ips: Iterable[IPv4Address | str]) -> Sequence[Union['IPv4Range', IPv4Address]]:
        """Create IPv4Range or IPv4Address list if list ip not has ranges

        :param ips: Iterable of IPv4Address or str
        :type ips: Iterable[IPv4Address | str]
        :return: sequence of IPv4Range or IPv4Address
        :rtype: Sequence[IPv4Range | IPv4Address]
        """
        sorted_ips: list[int] = sorted(map(lambda x: int(IPv4Address(x)), *ips))
        result: list[IPv4Range | IPv4Address] = []

        start, end = None, None
        for current_ip in sorted_ips:
            if start is None:
                start, end = current_ip, current_ip
                continue

            if current_ip - 1 == end:
                end = current_ip
                continue

            if start == end:
                result.append(IPv4Address(start))
                start, end = current_ip, current_ip
                continue

            result.append(IPv4Range.from_start_and_end(IPv4Address(start), IPv4Address(end)))
            start, end = current_ip, current_ip

        if start is None and end is None:
            return result

        if start == end:
            result.append(IPv4Address(start))
            return result

        result.append(IPv4Range.from_start_and_end(IPv4Address(start), IPv4Address(end)))
        return result

    @classmethod
    @overload
    def from_network(cls, ip_network: IPv4Network) -> "IPv4Range": ...
    @classmethod
    @overload
    def from_network(cls, ip_network: str) -> "IPv4Range": ...

    @classmethod
    def from_network(cls, ip_network) -> "IPv4Range":
        """Create IPv4Range from IPv4Network

        :param ip_network: IPv4Network or string like be IPv4Network
        :type ip_network: str | IPv4Network
        :return: IPv4Range from IPv4Network
        :rtype: IPv4Range
        :raises ValueError: if IPv4Network has mask 32
        """
        current_network = IPv4Network(ip_network)
        if current_network.num_addresses == 1:
            raise ValueError('IPv4Range has only more one address')
        start = current_network.network_address
        end = IPv4Address(int(current_network.network_address) + current_network.num_addresses - 1)
        return IPv4Range.from_start_and_end(start, end)


    @classmethod
    @overload
    def is_ip_range(cls, ip_range: str, /) -> bool: ...

    @classmethod
    @overload
    def is_ip_range(cls, start: IPv4Address, end: IPv4Address, /) -> bool: ...

    @classmethod
    @overload
    def is_ip_range(cls, start: str, end: str, /) -> bool: ...

    @classmethod
    def is_ip_range(cls, *args) -> bool:
        """Check is ip range
        :return: True if ip range
        """
        args_len = len(args)

        if args_len == 1:
            if '-' not in args[0]:
                return False
            [start, end] = args[0].split('-')
        elif args_len == 2:
            [start, end] = args
        else:
            raise ValueError('is_ip_range() takes exactly 2 arguments')

        try:
            ip_start = IPv4Address(start)
            ip_end = IPv4Address(end)
        except AddressValueError:
            return False

        if ip_start >= ip_end:
            return False

        return True

    @property
    def is_network(self) -> bool:
        """Является ли range сетью с маской от 0-31

        :rtype: bool
        :return: True if IPv4Range is network address
        """
        if self._network_mask is not None:
            return True
        number = math.log2(len(self))

        if not number.is_integer():
            return False

        number = int(number)
        real_mask = 32 + (-number)

        if not f"{int(self.start_ip):b}".endswith('0' * number):
            return False

        self._network_mask = real_mask
        return True

    def to_network(self):
        """IPv4Range to IPv4Network

        :return: IPv4Range to IPv4Network
        :rtype: IPv4Network
        :raises ValueError: if ip range is not in network
        """
        if not self.is_network:
            raise ValueError('IPv4Range does not is a network')

        return IPv4Network(f'{self.start_ip}/{self._network_mask}')

    def __eq__(self, other):
        other_rng = other
        if isinstance(other, IPv4Network):
            other_rng = IPv4Range.from_network(other)

        if isinstance(other_rng, IPv4Range):
            return self.start_ip == other_rng.start_ip and self.end_ip == other_rng.end_ip

        raise TypeError('IPv4Range can compare only with IPv4Range and IPv4Network')

    def __contains__(self, x, /):
        if isinstance(x, str) or isinstance(x, IPv4Address) or isinstance(x, int):
            ip_address = IPv4Address(x)
            return int(self.start_ip) <= int(ip_address) <= int(self.end_ip)

        raise TypeError('Contains only str like IPv4Address or IPv4Address or int of IPv4Address')

    def __iter__(self):
        for ip_int in range(int(self.start_ip), int(self.end_ip) + 1):
            yield IPv4Address(ip_int)

    def __len__(self):
        if self._len is not None:
            return self._len
        self._len = int(self.end_ip) - int(self.start_ip) + 1
        return self._len

    def __repr__(self):
        return f'<IPv4Range {self.start_ip}-{self.end_ip}>'

    def __str__(self):
        return f'{self.start_ip}-{self.end_ip}'




if __name__ == '__main__':
    for i in IPv4Range('10.0.0.100-10.0.0.102'):
        print(i)

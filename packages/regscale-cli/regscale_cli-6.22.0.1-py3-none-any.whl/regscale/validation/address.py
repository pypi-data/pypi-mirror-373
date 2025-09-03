import ipaddress
import re


def validate_ip_address(ip_str: str) -> bool:
    """Validate IPv4 or IPv6 address

    :param str ip_str: String to validate
    :return: bool
    :rtype: bool
    """
    try:
        ipaddress.IPv4Address(ip_str)
        return True
    except ipaddress.AddressValueError:
        try:
            ipaddress.IPv6Address(ip_str)
            return True
        except ipaddress.AddressValueError:
            return False


def validate_mac_address(mac_address: str) -> bool:
    """
    Simple validation of a mac address input
    :param str mac_address: mac address
    :return: Whether mac address is valid or not
    :rtype: bool
    """
    if not mac_address:
        return False
    return bool(
        re.match(
            "[0-9a-f]{2}(:?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$",
            mac_address.lower(),
        )
    )

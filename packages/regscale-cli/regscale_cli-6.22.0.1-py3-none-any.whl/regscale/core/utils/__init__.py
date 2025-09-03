"""Utility functions for the application"""

from typing import Union, Optional

UDP = "UDP"
TCP = "TCP"
TCP_UDP = "TCP/UDP"


def snakify(name: str) -> str:
    """
    Convert a string to snake_case

    :param str name: String to convert
    :returns: String in snake_case
    :rtype: str
    """
    return name.lower().replace(" ", "_")


def get_protocol_from_port(port: Union[int, str]) -> Optional[str]:
    """
    Determines the protocol from a port number for well known ports

    :param Union[int, str] port: Port number (int or str)
    :returns: Protocol name or None if not found
    :rtype: Optional[str]
    """
    port_to_protocol = {
        20: "FTP",  # File Transfer Protocol (FTP) Data Transfer
        21: "FTP",  # File Transfer Protocol (FTP) Command Control
        22: "SSH",  # Secure Shell (SSH)
        23: "Telnet",  # Telnet protocol
        25: "SMTP",  # Simple Mail Transfer Protocol (SMTP)
        53: "DNS",  # Domain Name System (DNS)
        67: "DHCP",  # Dynamic Host Configuration Protocol (DHCP) Server
        68: "DHCP",  # Dynamic Host Configuration Protocol (DHCP) Client
        80: "HTTP",  # Hypertext Transfer Protocol (HTTP)
        110: "POP3",  # Post Office Protocol v3 (POP3)
        123: "NTP",  # Network Time Protocol (NTP)
        143: "IMAP",  # Internet Message Access Protocol (IMAP)
        161: "SNMP",  # Simple Network Management Protocol (SNMP)
        162: "SNMP",  # Simple Network Management Protocol (SNMP) Trap
        443: "HTTPS",  # Hypertext Transfer Protocol Secure (HTTPS)
        445: "SMB",  # Server Message Block (SMB)
        465: "SMTPS",  # Simple Mail Transfer Protocol Secure (SMTPS)
        993: "IMAPS",  # Internet Message Access Protocol Secure (IMAPS)
        995: "POP3S",  # Post Office Protocol 3 Secure (POP3S)
        1433: "MSSQL",  # Microsoft SQL Server
        3306: "MySQL",  # MySQL Database Service
        3389: "RDP",  # Remote Desktop Protocol (RDP)
        5432: "PostgreSQL",  # PostgreSQL Database
        5672: "AMQP",  # Advanced Message Queuing Protocol (AMQP)
        5900: "VNC",  # Virtual Network Computing (VNC)
        6379: "Redis",  # Redis Key-Value Store
        8080: "HTTP-ALT",  # Alternative HTTP
        8443: "HTTPS-ALT",  # Alternative HTTPS
        27017: "MongoDB",  # MongoDB Database
    }

    port = int(port)  # Ensure port is an integer

    return port_to_protocol.get(port, None)


def get_base_protocol_from_port(port: Union[int, str]) -> str:
    """
    Returns the well-known base protocol for a port such as TCP, UDP, both TCP/UDP, or other based on the port number
    :param Union[int, str] port: Port number
    :returns: Protocol category
    :rtype: str
    """
    port = int(port)  # Ensure port is an integer

    both_tcp_udp_ports = [
        20,
        21,
        22,
        23,
        25,
        53,
        80,
        110,
        123,
        143,
        161,
        162,
        443,
        465,
        993,
        995,
        1433,
        3306,
        3389,
        5432,
        5672,
        5900,
        6379,
        8080,
        8443,
        27017,
    ]
    well_known_udp_ports = [7, 9, 19, 49, 67, 68, 69, 123, 161, 162, 514]
    well_known_tcp_ports = list(set(range(0, 1024)) - set(well_known_udp_ports) - set(both_tcp_udp_ports))

    if port in well_known_udp_ports:
        return UDP  # Well-known ports for UDP
    elif port in both_tcp_udp_ports:
        return TCP_UDP  # Ports used for both TCP and UDP
    elif port in well_known_tcp_ports:
        return TCP  # Well-known ports for TCP
    elif 1024 <= port <= 49151:
        return TCP_UDP  # Registered ports for both TCP and UDP
    elif 49152 <= port <= 65535:
        return TCP_UDP  # Dynamic or private ports for both TCP and UDP
    else:
        return "Other"  # Ports that don't fit into the standard categories

from update_ip.ip_getters.base import BaseIpGetter


class DynDns(BaseIpGetter):
    NAME = "dyndns.org"
    URL = "http://checkip.dyndns.org"


class IfconfigMe(BaseIpGetter):
    NAME = "ifconfig.me"
    URL = "http://ifconfig.me/ip"


class IPEchoNet(BaseIpGetter):
    NAME = "ipecho.net"
    URL = "http://ipecho.net/plain"


class IP4Me(BaseIpGetter):
    NAME = "ip4.me"
    URL = "http://ip4.me/"


class WhatIsMyPublicIP(BaseIpGetter):
    NAME = "whatismypublicip.com"
    URL = "http://www.whatismypublicip.com/"


class WhatIsMyIP(BaseIpGetter):
    NAME = "whatismyip.com"
    URL = "https://www.whatismyip.com/what-is-my-public-ip-address/"


'''
class JsonIp(BaseIpGetter):
    NAME="jsonip.com"
    URL="http://jsonip.com"
'''


'''
class IpChicken(BaseIpGetter):
    NAME= "ipchicken.com"
    URL= "http://ipchicken.com/"
'''

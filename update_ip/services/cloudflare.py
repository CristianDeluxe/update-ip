import json
import urllib2

import tld

from update_ip.services.base import BaseDNSService, DNSServiceError


class CloudflareService(BaseDNSService):
    name = 'Cloudflare'

    def __init__(self, email, api_key, dns_type, **kwargs):
        """Init the Cloudflare class
        :param email: Cloudflare login email
        :param api_key: Cloudflare Global API Key
        :param domain: Domain to update
        :param dns_type: Domain type (A: for IPv4, AAAA: for IPv6...)
        """
        if not email or not api_key:
            raise DNSServiceError('Email and "Global API key" are required for use the Cloudflare service.')

        # Updates the known TLD names
        tld.utils.update_tld_names()

        # Cloudflare API URL
        self.api_url = 'https://api.cloudflare.com/client/v4/'

        # HTTP request and opener variables
        self.request = None
        self.opener = urllib2.build_opener(urllib2.HTTPHandler)

        # Cloudflare data
        self.email = email
        self.api_key = api_key

        # Domain Data
        self.domain = None
        self.dns_record = None

        # DNS Type
        self.record_type = dns_type

        # Cloudflare internal data
        self.zone_id = None
        self.record_id = None

    def update(self, domain, ip):
        """Parse the given domain and extract the TLD
        :param domain: Domain (or subdomain) to update
        :param ip: IP address to update
        """
        self.parse_domain(domain)
        self.update_ip(ip)

    def find_domains(self, ip):
        """Not implemented, since in cloudflare you can have multiple domains, subdomains, dns-records ... it would
        not be safe to try to update them all
        :param ip: IP address to update
        """
        raise NotImplementedError

    def parse_domain(self, domain):
        """Parse the given domain and extract the TLD
        :param domain: Full domain
        """
        self.domain = tld.get_tld('http://' + domain)  # Convert from "any.sub.domain.tld" to "domain.tld"
        self.dns_record = domain

    def parse_result(self, data):
        """Parse the JSON result and return a dict/list with data
        :param data: JSON data to parse
        """
        return json.loads(data)

    def update_ip(self, ip, second_try=False):
        """Get the DNS Record info for selected sub-domain
        :param ip: IP address to update
        :param second_try: If Record_ID is empty try to get it, if everything fails in a second attempt, we throw an
                            exception.
        """
        if self.record_id is None:
            if second_try:
                raise DNSServiceError(
                    'Record ID is empty, we tried to find it, but it was not possible'
                )
            self.get_dns_record()
            self.update_ip(ip, True)
            return

        self.create_request(self.generate_update_url(),
                            json.dumps({'name': self.dns_record, 'type': self.record_type, 'content': ip})
                            )

        self.request.get_method = lambda: 'PUT'
        result = self.opener.open(self.request)
        # data = self.parse_result(result.read())

    def get_zones(self):
        """Get the zone info for selected domain
        """
        self.create_request(self.generate_zones_list_url())
        result = urllib2.urlopen(self.request)
        data = self.parse_result(result.read())
        if len(data[u'result']) > 0:
            self.zone_id = data[u'result'][0][u'id']
        else:
            raise DNSServiceError('No info found for domain: ' + self.domain)

    def get_dns_record(self, second_try=False):
        """Get the DNS Record info for selected sub-domain
        :param second_try: If Zone_ID is empty try to get it, if everything fails in a second attempt, we throw an
                            exception.
        """
        if self.zone_id is None:
            if second_try:
                raise DNSServiceError(
                    'Zone ID is empty, we tried to find it, but it was not possible'
                )
            self.get_zones()
            self.get_dns_record(True)
            return

        self.create_request(self.generate_dns_list_url())
        result = urllib2.urlopen(self.request)
        data = self.parse_result(result.read())

        if len(data[u'result']) > 0:
            self.record_id = data[u'result'][0][u'id']
        else:
            raise DNSServiceError(
                'No info found for DNS Record: "' + self.dns_record + '" with DNS type: "' + self.record_type + '"'
            )

    def create_request(self, url, data=None):
        """Creates the HTTP request and add headers
        :param url: API URL with the petition.
        :param data: Request Data
        """
        if data is None:
            self.request = urllib2.Request(url)
        else:
            self.request = urllib2.Request(url, data)
        self.add_url_headers()

    def add_url_headers(self):
        """Add headers to petition with auth data and other needed headers"""
        self.request.add_header('Content-Type', 'application/json')
        self.request.add_header('X-Auth-Key', self.api_key)
        self.request.add_header('X-Auth-Email', self.email)

    def generate_zones_list_url(self):
        """Generate the URL for get the Zone List info"""
        return self.api_url + \
               'zones' + \
               '?name=' + self.domain

    def generate_dns_list_url(self):
        """Generate the URL for get the DNS List info"""
        return self.api_url + \
               'zones/' + \
               self.zone_id + '/' + \
               'dns_records' + \
               '?name=' + self.dns_record + \
               '&type=' + self.record_type

    def generate_update_url(self):
        """Generate the URL for update the DNS Record"""
        return self.api_url + \
               'zones/' + \
               self.zone_id + '/' + \
               'dns_records/' + \
               self.record_id


service = CloudflareService

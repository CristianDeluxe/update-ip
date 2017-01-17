import logging

import tld
import pynfsn

from update_ip.services.base import BaseDNSService, DNSServiceError

log = logging.getLogger('update_ip.services.nfsn')

ALLOW_INEXISTENT = True  # If this is false, I'll refuse to proceed if the domain record doesn't already exist


class NearlyFreeSpeechService(BaseDNSService):
    name = 'NearlyfreeSpeech'
    TTL = 300  # 5 minutes of dns record ttl

    def __init__(self, username, api_key, **kwargs):
        if not username or not api_key:
            raise DNSServiceError('Username and api_key are required for the NearlyFreeSpeech service.')
        self.nfsn = pynfsn.NFSN(username, api_key)

        # Updates the known TLD names
        tld.utils.update_tld_names()

    def update(self, whole_domain, ip):
        tld_info = tld.get_tld('http://' + whole_domain, as_object=True)
        dns = self.nfsn.dns(tld_info.domain)
        try:
            current_records = dns.listRRs(name=tld_info.subdomain, type="A")
            current_records = filter(lambda x: x['name'] == tld_info.subdomain, current_records)
        except Exception as e:
            raise DNSServiceError("failed to get current records: " + str(e))
        if len(current_records) > 1:
            raise DNSServiceError("Found more than one existing record with the given name: " + tld_info.subdomain)
        inexistent = len(current_records) == 0
        if inexistent and not ALLOW_INEXISTENT:
            raise DNSServiceError("Found no existing record with the given name: " + tld_info.subdomain)
        if inexistent:
            log.warning("domain " + whole_domain + " did not exist - creating it")
        else:
            record = current_records[0]
            if record.get("type") != "A":
                raise DNSServiceError('Not an "A" record')
            if record.get("name") != tld_info.subdomain:
                raise DNSServiceError("Got a diferent record than expected")
            record_ip = record.get("data")
            # if record_ip==self.current_ip:
            #    #"Record already up to date."
            #    return
            try:
                dns.removeRR(name=tld_info.subdomain, type=record.get("type"), data=record.get("data"))
            except Exception as e:
                raise DNSServiceError("failed to remove: " + str(e))
        try:
            dns.addRR(name=tld_info.subdomain, type='A', data=ip, ttl=self.TTL)
        except Exception as e:
            raise DNSServiceError("failed to add: " + str(e))


service = NearlyFreeSpeechService

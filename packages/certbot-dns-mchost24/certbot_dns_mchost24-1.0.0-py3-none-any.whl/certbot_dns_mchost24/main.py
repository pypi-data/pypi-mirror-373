import logging

from certbot import errors
from certbot.plugins import dns_common

from mchost24.api import DomainRecordType, MCHost24API, MCHost24APIError

logger = logging.getLogger(__name__)

class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for MCHost24
    
    Uses the MCHost24 API to fullfill a dns-01 challenge
    """
    
    description = 'Obtain certificates using a DNS TXT record for MCHost24.'
    
    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None
    
    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds = 60
        )
        add("credentials", help="MCHost24 credentials INI file.")
    
    def more_info(self):
        return (
            "This plugin configures a DNS TXT record to respond to a dns-01 "
            "challenge using the MCHost24 API."
        )
    
    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            "credentials",
            "MCHost24 API credentials INI file. Only API token "
            "authentication is supported",
            {"api_token": "API token for the MCHost24 API"},
        )
    
    def _perform(self, domain, validation_name, validation):
        MCH24APIWrapper(self.credentials.conf("api_token")).add_txt_record(
            domain,
            validation_name.replace("." + domain, ""),
            validation
        )
    
    def _cleanup(self, domain, validation_name, validation):
        MCH24APIWrapper(self.credentials.conf("api_token")).del_txt_record(
            domain,
            validation_name.replace("." + domain, ""),
            validation
        )

class MCH24APIWrapper(object):
    
    def __init__(self, api_token: str):
        logger.debug("[dns-mchost24] Creating API wrapper")
        self.api_client = MCHost24API(token = api_token)
    
    def _get_domains(self):
        try:
            res = self.api_client.get_domains()
        
            if not res.success:
                raise errors.PluginError(f"Couldn't get list of domains from API: {res.message}")
            
            return res.data
        except MCHost24APIError as e:
            raise errors.PluginError(f"Error while getting list of domains.") from e
    
    def _get_dns_records(self, domain_id: int):
        try:
            res = self.api_client.get_domain_info(domain_id)
        
            if not res.success:
                raise errors.PluginError(f"Couldn't get domain info from API: {res.message}")
            
            return res.data.records
        except MCHost24APIError as e:
            raise errors.PluginError(f"Error while getting list of dns records for domain.") from e
    
    def _get_domain_id(self, domain: str):
        components = domain.split('.')
        
        if len(components) < 2:
            raise errors.PluginError(f"Domain has too few components: {len(components)}")
        
        id = None
        for d in self._get_domains():
            if (components[-1] == d.tld) and (components[-2] == d.sld):
                id = d.id
        
        if id is None:
            raise errors.PluginError(f"Unknown domain: {components[-2]}.{components[-1]}")
        
        return id, components[:-2]
    
    def add_txt_record(self, domain: str, record_name: str, record_content: str):
        domain_id, subcomponents = self._get_domain_id(domain)
        
        record_name_components = [record_name] + subcomponents
        
        logger.debug(f"[dns-mchost24] Adding TXT record with name '{'.'.join(record_name_components)}' for domain '{domain}'...")
        
        try:
            res = self.api_client.create_domain_dns_record(domain_id, '.'.join(record_name_components), DomainRecordType.TXT, record_content)
            
            if not res:
                raise errors.PluginError(f"Creating DNS record failed: {res.message}")
        except MCHost24APIError as e:
            raise errors.PluginError("Error while creating DNS record.") from e
    
    def del_txt_record(self, domain: str, record_name: str, record_content: str):
        domain_id, subcomponents = self._get_domain_id(domain)
        records = self._get_dns_records(domain_id)
        
        full_record_name = '.'.join([record_name] + subcomponents)
        
        logger.debug(f"[dns-mchost24] Trying to delete TXT record with name '{full_record_name}' for domain '{domain}'...")
        
        id = None
        for r in records:
            if (r.sld == full_record_name) and (r.target == record_content):
                id = r.id
        
        if id is None:
            # No record found to delete
            return
        
        try:
            res = self.api_client.delete_domain_dns_record(domain_id, id)
        
            if not res.success:
                logger.error(f"Couldn't delete DNS record: {res.message}")
        except MCHost24APIError as e:
            logger.error(f"{e.__class__.__name__}:{e.message}")
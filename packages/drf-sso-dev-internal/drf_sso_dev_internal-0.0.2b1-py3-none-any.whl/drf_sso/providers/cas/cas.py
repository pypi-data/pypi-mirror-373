import requests
import xml.etree.ElementTree as ET
import json
from pathlib import Path
from logging import getLogger

logger = getLogger(__name__)

class CAS:
    def __init__(self, conf: Path | dict):
        if isinstance(conf, Path):
            with open(conf, 'r') as file:
                self._load_conf(json.load(file))
        else:
            self._load_conf(conf)
            
    def _load_conf(self, conf: dict):
        self.login_url = conf['login_url']
        self.validate_url = conf['validate_url']
        self.service_url = conf['service_url']
        self.use_json = conf.get('use_json', True)
        
    def get_login_url(self):
        return f"{self.login_url}?service={self.service_url}"
    
    def _get_response(self, ticket = None):
        if ticket is None:
                raise Exception("CAS Ticket is invalid.")
            
        params = {
            'ticket': ticket,
            'service': self.service_url,
            'format': "json" if self.use_json else "xml"
        }
        response = requests.get(self.validate_url, params=params, timeout=5)
        response.raise_for_status()
        
        return response
    
    def _parse_xml(self, response):
        root = ET.fromstring(response.text)
        ns = {'cas': 'http://www.yale.edu/tp/cas'}

        auth_success = root.find('.//cas:authenticationSuccess', ns)
        if auth_success is None:
            raise Exception("CAS Auth failed.")
        
        user = auth_success.find('cas:user', ns).text
        attributes = auth_success.find('cas:attributes', ns)
        
        atr_dict = {}
        for attr in attributes:
            tag = attr.tag.split("}")[-1]
            if tag in atr_dict:
                if isinstance(atr_dict[tag], list):
                    atr_dict[tag].append(attr.text)
                else:
                    atr_dict[tag] = [atr_dict[tag], attr.text]
            else:
                atr_dict[tag] = attr.text
        atr_dict['username'] = user
        return atr_dict
    
    def _parse_json(self, response):
        try:
            return response.json()['serviceResponse']['authenticationSuccess']
        except KeyError:
            raise Exception("CAS Auth failed.")
            
    def validate_ticket(self, ticket = None):
        try:
            response = self._get_response(ticket)
            if self.use_json:
                return self._parse_json(response) 
            else:
                return self._parse_xml(response)
        except Exception as e:
            logger.error(e)
            return None
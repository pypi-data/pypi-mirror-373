import base64
import jwt
import lxml.etree as ET
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone
from .config import NAMESPACES, SPConfig, IdPConfig
from .xmlsign_utils import XmlSignUtils

class SAMLResponse:
    def __init__(self, b64_response: str, sp: SPConfig, idp: IdPConfig, relay_state: Optional[str] = None):
        self.sp = sp
        self.idp = idp
        self.xml = base64.b64decode(b64_response.encode())
        self.root = ET.fromstring(self.xml)
        self.assertion = self.root.find(".//saml:Assertion", NAMESPACES)
        self.subject = None
        self.attributes = {}
        self.conditions = {}
        self.session_index = None
        self._parse(relay_state=relay_state)

    def _parse(self, relay_state: Optional[str] = None):
        self.relay_state = relay_state
        
        self.in_response_to = self.root.attrib.get("InResponseTo")
        
        nameid_elem = self.assertion.find(".//saml:Subject/saml:NameID", NAMESPACES)
        self.subject = nameid_elem.text if nameid_elem is not None else None

        for attr in self.assertion.findall(".//saml:Attribute", NAMESPACES):
            name = attr.attrib.get("Name")
            values = [v.text for v in attr.findall("saml:AttributeValue", NAMESPACES)]
            self.attributes[name] = values if len(values) > 1 else values[0] if values else None

        conditions = self.assertion.find(".//saml:Conditions", NAMESPACES)
        if conditions is not None:
            self.conditions = {
                "not_before": conditions.attrib.get("NotBefore"),
                "not_on_or_after": conditions.attrib.get("NotOnOrAfter")
            }

        authn_stmt = self.assertion.find(".//saml:AuthnStatement", NAMESPACES)
        if authn_stmt is not None:
            self.session_index = authn_stmt.attrib.get("SessionIndex")

    def is_valid(self) -> bool:
        # Basic checks
        if self.subject is None or not self.attributes:
            return False
        
        # Relay state JWT check
        try:
            payload = jwt.decode(self.relay_state, self.sp.public_key, algorithms=["RS256"], options={"require": ["exp", "iat"]})
            if not payload.get("sp_entity_id") == self.sp.entity_id:
                return False
            if not payload.get("idp_entity_id") == self.idp.entity_id:
                return False
            if not self.in_response_to or payload.get("request_id") != self.in_response_to:
                return False
        except Exception as e:
            return False
        
        # Conditions validation
        if not self._validate_condition():
            return False

        # Signature validation
        if self.sp.want_assertions_signed:
            if not XmlSignUtils.verify(self.xml.decode(), self.idp):
                return False
    
    def _validate_condition(self) -> bool:
        now = datetime.now(timezone.utc)
        not_before = self.conditions.get("not_before")
        not_on_or_after = self.conditions.get("not_on_or_after")

        if not_before:
            try:
                if now < datetime.fromisoformat(not_before):
                    return False
            except Exception:
                return False

        if not_on_or_after:
            try:
                if now >= datetime.fromisoformat(not_on_or_after):
                    return False
            except Exception:
                return False

        return True

    def get_attributes(self) -> dict:
        return self.attributes

    def get_subject(self) -> Optional[str]:
        return self.subject

    def get_session_index(self) -> Optional[str]:
        return self.session_index

    def get_conditions(self) -> dict:
        return self.conditions
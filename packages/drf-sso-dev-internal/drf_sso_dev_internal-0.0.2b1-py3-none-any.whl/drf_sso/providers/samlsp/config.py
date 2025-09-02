import lxml.etree as ET
from pathlib import Path
from enum import Enum

NAMESPACES = {
    "saml": "urn:oasis:names:tc:SAML:2.0:assertion",
    "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
    "md": "urn:oasis:names:tc:SAML:2.0:metadata",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
}

class Binding(Enum):
    HTTP_REDIRECT = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    HTTP_POST = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    HTTP_POST_SIMPLE_SIGN = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST-SimpleSign"
    SOAP = "urn:oasis:names:tc:SAML:2.0:bindings:SOAP"

class DigestAlgorithm(Enum):
    SHA1 = "http://www.w3.org/2000/09/xmldsig#sha1"
    SHA256 = "http://www.w3.org/2001/04/xmlenc#sha256"
    SHA512 = "http://www.w3.org/2001/04/xmlenc#sha512"
    
    @property
    def signxml_name(self):
        return self.name.lower()

class SignatureAlgorithm(Enum):
    RSA_SHA1 = "http://www.w3.org/2000/09/xmldsig#rsa-sha1"
    RSA_SHA256 = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
    RSA_SHA512 = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha512"
    
    @property
    def signxml_name(self):
        return self.name.lower().replace("_", "-")

class SPConfig:
    def __init__(self, data: dict):
        self.entity_id = data["entity_id"]
        self.acs_url = data["acs_url"]
        self.sls_url = data.get("sls_url")
        self.signing_cert_path = Path(data["signing_cert"])
        self.private_key_path = Path(data["private_key"])
        self.public_key_path = Path(data["public_key"]) #TODO: Extract from signing_cert?
        self.want_assertions_signed = data.get("want_assertions_signed", True)
        self.authn_requests_signed = data.get("authn_requests_signed", True)
        self.digest_method = data.get("digest_method", DigestAlgorithm.SHA256)
        self.signature_method = data.get("signature_method", SignatureAlgorithm.RSA_SHA256)

        self.signing_cert = self.signing_cert_path.read_text()
        self.private_key = self.private_key_path.read_text()
        self.public_key = self.public_key_path.read_text()

    @classmethod
    def from_file(cls, path: Path):
        import json
        return cls(json.loads(path.read_text()))


class IdPConfig:
    def __init__(self, metadata_xml: str):
        self.entity_id = None
        self.sso_services = {}  # Binding -> URL
        self.sls_services = {}  # Binding -> URL
        self.signing_cert = None
        self.encryption_cert = None
        self.want_authn_requests_signed = False
        self._parse(metadata_xml)

    def _parse(self, xml_str: str):
        root = ET.fromstring(xml_str.encode())
        self.entity_id = root.attrib.get("entityID")
        
        idp_descriptor = root.find(".//md:IDPSSODescriptor", NAMESPACES)
        if idp_descriptor is not None:
            self.want_authn_requests_signed = idp_descriptor.attrib.get("WantAuthnRequestsSigned", "false").lower() == "true"

        for sso in root.findall(".//md:IDPSSODescriptor/md:SingleSignOnService", NAMESPACES):
            binding = sso.attrib.get("Binding")
            location = sso.attrib.get("Location")
            if binding and location:
                self.sso_services[binding] = location

        for sls in root.findall(".//md:IDPSSODescriptor/md:SingleLogoutService", NAMESPACES):
            binding = sls.attrib.get("Binding")
            location = sls.attrib.get("Location")
            if binding and location:
                self.sls_services[binding] = location

        certs = root.findall(".//md:IDPSSODescriptor/md:KeyDescriptor", NAMESPACES)
        for cert in certs:
            use = cert.attrib.get("use", "signing")
            x509 = cert.find(".//ds:X509Certificate", NAMESPACES)
            if x509 is not None:
                if use == "signing":
                    self.signing_cert = x509.text.strip()
                elif use == "encryption":
                    self.encryption_cert = x509.text.strip()

    def get_sso_url(self, preferred: Binding = Binding.HTTP_REDIRECT):
        return self.sso_services.get(preferred.value)

    def get_sls_url(self, preferred: Binding = Binding.HTTP_REDIRECT):
        return self.sls_services.get(preferred.value)

    def is_valid(self) -> bool:
        return self.entity_id is not None and bool(self.sso_services) and self.signing_cert is not None

    @classmethod
    def from_file(cls, path: Path):
        with open(path, "r") as f:
            return cls(f.read())

    @classmethod
    def from_url(cls, url: str):
        import requests
        response = requests.get(url)
        response.raise_for_status()
        return cls(response.text)
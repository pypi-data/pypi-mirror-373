from signxml import XMLVerifier, XMLSigner
import lxml.etree as ET
from .config import SPConfig, IdPConfig

class XmlSignUtils:    
    @staticmethod
    def sign(xml: str, sp: SPConfig) -> str:
        digest_algorithm = sp.digest_method.signxml_name
        signature_algorithm = sp.signature_method.signxml_name
        private_key = sp.private_key
        cert = sp.signing_cert
        
        signer = XMLSigner(
            digest_algorithm=digest_algorithm,
            signature_algorithm=signature_algorithm,
            c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"
        )
        dom = ET.fromstring(xml.encode())
        signed = signer.sign(dom, key=private_key.encode(), cert=cert.encode())
        return ET.tostring(signed).decode()
    
    @staticmethod
    def verify(xml: str, idp: IdPConfig) -> bool:
        cert = idp.signing_cert
        dom = ET.fromstring(xml.encode())
        try:
            XMLVerifier().verify(dom, x509_cert=cert.encode())
            return True
        except:
            return False
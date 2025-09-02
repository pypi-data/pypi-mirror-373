import uuid
import zlib
import base64
import jwt
from datetime import datetime
from urllib.parse import urlencode

from .config import SPConfig, IdPConfig, Binding
from .xmlsign_utils import XmlSignUtils

AUTHN_REQUEST_TEMPLATE = """
<samlp:AuthnRequest
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="{destination}"
    ProtocolBinding="{protocol_binding}"
    AssertionConsumerServiceURL="{acs_url}"
    >
    <saml:Issuer>{entity_id}</saml:Issuer>
</samlp:AuthnRequest>
"""

class AuthnRequest:
    def __init__(self, sp: SPConfig, idp: IdPConfig, binding: Binding = Binding.HTTP_REDIRECT):
        self.sp = sp
        self.idp = idp
        self.binding = binding
        self.id = f"_{uuid.uuid4().hex}"
        self.issue_instant = datetime.now().isoformat()
        self.destination = idp.get_sso_url(binding)
        self._raw_xml = self._build_xml()
        self._signed_xml = None
        
    def _build_secure_relay_state(self) -> str:
        now = datetime.now().timestamp()
        return jwt.encode(
            payload={
                "sp_entity_id": self.sp.entity_id,
                "idp_entity_id": self.idp.entity_id,
                "request_id": self.id,
                "iat": now,
                "exp": now + 120,
            },
            key=self.sp.private_key,
            algorithm="RS256"
        )

    def _build_xml(self) -> str:
        return AUTHN_REQUEST_TEMPLATE.format(
            request_id=self.id,
            issue_instant=self.issue_instant,
            destination=self.destination,
            protocol_binding=self.binding.value,
            acs_url=self.sp.acs_url,
            entity_id=self.sp.entity_id
        )

    def _should_sign(self) -> bool:
        idp_requires = self.idp.want_authn_requests_signed
        sp_wants = self.sp.authn_requests_signed
        return idp_requires or sp_wants

    def _sign_xml(self, xml_str: str) -> str:
        return XmlSignUtils.sign(xml=xml_str, sp=self.sp)

    def get_request_xml(self) -> str:
        if self._should_sign():
            if not self._signed_xml:
                self._signed_xml = self._sign_xml(self._raw_xml)
            return self._signed_xml
        return self._raw_xml

    def get_encoded(self) -> str:
        raw = self.get_request_xml().encode()
        if self.binding == Binding.HTTP_REDIRECT:
            deflated = zlib.compress(raw, level=9)[2:-4]
            return base64.b64encode(deflated).decode()
        elif self.binding == Binding.HTTP_POST:
            return base64.b64encode(raw).decode()
        raise NotImplementedError(f"Binding {self.binding} not supported")

    def to_http_redirect(self) -> str:
        b64 = self.get_encoded()
        return f"{self.destination}?{urlencode({'SAMLRequest': b64, 'RelayState': self._build_secure_relay_state()})}"

    def to_http_post_form(self) -> str:
        b64 = self.get_encoded()
        return f"""
        <form method='post' action='{self.destination}'>
            <input type='hidden' name='SAMLRequest' value='{b64}'/>
            <input type='hidden' name='RelayState' value='{self._build_secure_relay_state()}'/>
            <input type='submit' value='Continue'/>
        </form>
        <script>document.forms[0].submit();</script>
        """

    def render(self) -> str:
        if self.binding == Binding.HTTP_REDIRECT:
            return self.to_http_redirect()
        elif self.binding == Binding.HTTP_POST:
            return self.to_http_post_form()
        raise NotImplementedError(f"Binding {self.binding} not supported")


def create_authn_request(sp: SPConfig, idp: IdPConfig, binding: Binding = Binding.HTTP_REDIRECT) -> tuple[str, str, AuthnRequest]:
    req = AuthnRequest(sp, idp, binding)
    return req.destination, req.render(), req

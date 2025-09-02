from .config import SPConfig, Binding
from pathlib import Path

SP_METADATA_TEMPLATE = """<EntityDescriptor entityID="{entity_id}" xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  <SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol" AuthnRequestsSigned="{authn_signed}" WantAssertionsSigned="{assertion_signed}">
    <KeyDescriptor use="signing">
      <KeyInfo xmlns="http://www.w3.org/2000/09/xmldsig#">
        <X509Data>
          <X509Certificate>{cert}</X509Certificate>
        </X509Data>
      </KeyInfo>
    </KeyDescriptor>
    <AssertionConsumerService Binding="{binding}" Location="{acs_url}" index="1" />
    {sls_block}
  </SPSSODescriptor>
</EntityDescriptor>
"""

SLS_TEMPLATE = """
    <SingleLogoutService Binding="{binding}" Location="{sls_url}" />
"""

def generate_metadata(sp: SPConfig, binding: Binding = Binding.HTTP_POST) -> str:
    cert_clean = sp.signing_cert.replace("-----BEGIN CERTIFICATE-----", "").replace("-----END CERTIFICATE-----", "").replace("\n", "")
    sls_block = ""
    if sp.sls_url:
        sls_block = SLS_TEMPLATE.format(binding=binding.value, sls_url=sp.sls_url)
    return SP_METADATA_TEMPLATE.format(
        entity_id=sp.entity_id,
        authn_signed=str(sp.authn_requests_signed).lower(),
        assertion_signed=str(sp.want_assertions_signed).lower(),
        cert=cert_clean,
        acs_url=sp.acs_url,
        binding=binding.value,
        sls_block=sls_block
    )

def write_metadata_to_file(sp: SPConfig, path: Path, binding: Binding = Binding.HTTP_POST):
    xml_str = generate_metadata(sp, binding)
    path.write_text(xml_str)
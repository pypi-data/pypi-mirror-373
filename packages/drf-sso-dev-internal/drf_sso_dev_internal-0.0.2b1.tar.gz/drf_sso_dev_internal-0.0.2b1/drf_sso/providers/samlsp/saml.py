from .config import SPConfig, IdPConfig, Binding
from .request import create_authn_request, AuthnRequest
from .response import SAMLResponse
from pathlib import Path

class SAMLSP:
    def __init__(self, sp_config: SPConfig | Path | str, idp_config: IdPConfig | str):
        if isinstance(sp_config, Path):
            self.sp = SPConfig.from_file(sp_config)
        elif isinstance(sp_config, str):
            self.sp = SPConfig.from_file(Path(sp_config))
        elif isinstance(sp_config, dict):
            self.sp = SPConfig(sp_config)
        else:
            self.sp = sp_config
        
        if isinstance(idp_config, str):
            self.idp = IdPConfig.from_url(idp_config)
        else:
            self.idp = idp_config
            
    def get_login_request(self, binding: Binding = Binding.HTTP_REDIRECT) -> tuple[str, str, AuthnRequest]:
        return create_authn_request(self.sp, self.idp, binding)

    def parse_response(self, b64_response: str, relay_state=None) -> SAMLResponse:
        return SAMLResponse(b64_response, self.sp, self.idp, relay_state=relay_state)

    def get_metadata_xml(self, binding: Binding = Binding.HTTP_POST) -> str:
        from .metadata import generate_metadata
        return generate_metadata(self.sp, binding)

    def write_metadata(self, path, binding: Binding = Binding.HTTP_POST):
        from .metadata import write_metadata_to_file
        write_metadata_to_file(self.sp, path, binding)
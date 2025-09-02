from pathlib import Path
from django.core.management import BaseCommand
from drf_sso.providers import get_providers
from drf_sso.providers.saml_provider import SAMLProvider

saml_providers = [provider for provider in get_providers() if provider.__class__ == SAMLProvider]

class Command(BaseCommand):
    help = "Generate metadata for all SAML Service Providers registered"
    
    def add_arguments(self, parser):
        parser.add_argument("out", type=str, help="Chemin du dossier de sortie")
    
    def handle(self, *args, **options):
        out_dir = Path(options["out"])
        out_dir.mkdir(exist_ok=True)
        
        for provider in saml_providers:
            out_file = out_dir / f"{provider.name}.xml"
            provider.provider.write_metadata(out_file)
            
        self.stdout.write("Les metadata des SP ont bien été générées.")
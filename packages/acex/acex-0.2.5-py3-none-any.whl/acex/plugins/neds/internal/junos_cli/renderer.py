
from acex.plugins.neds.core import RendererBase
from typing import Any, Dict, Optional
from pathlib import Path

from jinja2 import Environment, FileSystemLoader



class JunosCLIRenderer(RendererBase):

    def _load_template_file(self) -> str:
        """Load a Jinja2 template file."""
        template_name = "template.j2"
        path = Path(__file__).parent
        env = Environment(loader=FileSystemLoader(path))
        template = env.get_template(template_name)
        return template

    def render(self, configuration: Dict[str, Any]) -> Any:
        """Render the configuration model for Junos CLI devices."""
        template = self._load_template_file()
        return template.render(configuration=configuration)
        
from jinja2 import TemplateRuntimeError, TemplateSyntaxError
from jinja2.ext import Extension
from jinja2.nodes import Const, Name, Keyword, CallBlock

from edri.api.handlers import HTTPHandler
from edri.utility.function import format_url


class URLExtension(Extension):
    tags = {"url"}

    def parse(self, parser):
        # Skip the name of tag - there is only one candidate
        lineno = next(parser.stream).lineno

        # Skip the first argument, which is the event name
        event_name = parser.parse_expression()

        # Parse the optional keyword arguments
        kwargs = []
        while parser.stream.current.type != "block_end":
            token = parser.stream.current
            if token.type in ("string", "name") and parser.stream.look().type == "assign":
                key = parser.parse_expression()
                if isinstance(key, Const):
                    key = key.value
                elif isinstance(key, Name):
                    key = key.name
                parser.stream.skip()  # Skip over the "="
                value = parser.parse_expression()
                kwargs.append(Keyword(key, value))
            elif token.type == "comma":
                parser.stream.skip()
            else:
                raise TemplateSyntaxError("Only keyword arguments are allowed", lineno=lineno, filename=parser.filename)

        return CallBlock(self.call_method("_render_url", [event_name], kwargs), [], [], {}).set_lineno(lineno)

    @staticmethod
    def _render_url(event_name, **kwargs):
        event_type = HTTPHandler.event_type_names.get(event_name)
        try:
            extensions = HTTPHandler.event_type_extensions[event_type]
        except KeyError:
            raise TemplateRuntimeError(f"Event {event_name} was not found")

        try:
            return format_url(extensions["url"], **kwargs)
        except KeyError:
            raise TemplateRuntimeError(f"Event {event_name} was not found")

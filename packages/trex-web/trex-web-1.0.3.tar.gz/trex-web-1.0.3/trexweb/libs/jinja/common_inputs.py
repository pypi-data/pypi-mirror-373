'''
Created on 21 May 2020

@author: jacklok
'''
import jinja2

class ShowTodayDate(jinja2.ext.Extension):
    """
    This will give us a {% today_date %} tag.
    """

    template = '%s'
    tags = set(['check_active'])

    def _render_tag(self, context, caller):
        return jinja2.Markup(self.template % context['active'])

    def parse(self, parser):
        ctx_ref = jinja2.nodes.ContextReference()
        lineno = next(parser.stream).lineno
        node = self.call_method('_render_tag', [ctx_ref], lineno=lineno)
        return jinja2.nodes.CallBlock(node, [], [], [], lineno=lineno)

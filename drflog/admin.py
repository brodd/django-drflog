from django.contrib import admin
from drflog.models import Entry
from django.utils.safestring import mark_safe
from django.template.defaultfilters import truncatechars
import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

STYLE = 'friendly'
HTML_FORMATTER = HtmlFormatter(style=STYLE)
JSON_LEXER = JsonLexer()

def prettify(field):
    r = json.dumps(field, sort_keys=True, indent=4)
    return mark_safe(highlight(r, JSON_LEXER, HTML_FORMATTER))

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ip', 'short_user_agent', 'time_initialized',
                    'time_ms', 'method', 'path', 'status')
    search_fields = ('=user__id', '=user__email', 'user__artist_name')

    fields = ('user', 'ip', 'user_agent', 'time_initialized', 'time_ms',
              'method', 'status', 'path',
              'query_params_prettified', 'request_data_prettified', 'response_data_prettified')
    readonly_fields = fields

    def short_user_agent(self, instance):
        return truncatechars(instance.user_agent, 20)

    def query_params_prettified(self, instance):
        return prettify(instance.query_params)

    def request_data_prettified(self, instance):
        return prettify(instance.request_data)

    def response_data_prettified(self, instance):
        return prettify(instance.response_data)

    class Media:
        css = {
            'all': ('drflog/css/drflog.css',
                    'drflog/css/%s.css' % STYLE)
        }

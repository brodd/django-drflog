import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.template.defaultfilters import truncatechars
from drflog.models import Entry

STYLE = 'friendly'
HTML_FORMATTER = HtmlFormatter(style=STYLE)
JSON_LEXER = JsonLexer()

class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice

class UserFilter(InputFilter):
    parameter_name = 'user'
    title = 'User (ID, Email)'

    def queryset(self, request, queryset):
        if self.value() is not None:
            if self.value().isdigit():
                return queryset.filter(user_id=int(self.value()))
            else:
                return queryset.filter(user__email__iexact=self.value())

class PathFilter(InputFilter):
    parameter_name = 'path'
    title = 'Path'

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(path__iexact=self.value())

class IPFilter(InputFilter):
    parameter_name = 'ip'
    title = 'IP Address'

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(ip=self.value().strip())

class StatusFilter(InputFilter):
    parameter_name = 'status'
    title = 'Status Code'

    def queryset(self, request, queryset):
        if self.value() is not None and self.value().isdigit():
            return queryset.filter(status=int(self.value()))

def prettify(field):
    r = json.dumps(field, sort_keys=True, indent=4)
    return mark_safe(highlight(r, JSON_LEXER, HTML_FORMATTER))

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ip', 'short_user_agent', 'time_initialized',
                    'time_ms', 'method', 'path', 'status')

    fields = ('user', 'ip', 'user_agent', 'time_initialized', 'time_ms',
              'method', 'status', 'path',
              'query_params_prettified', 'request_data_prettified', 'response_data_prettified')
    readonly_fields = fields

    list_filter = (UserFilter, PathFilter, IPFilter, StatusFilter)

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

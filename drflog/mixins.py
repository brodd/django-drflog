import re
from django.utils.timezone import now
from .models import Entry

class LogMixin(object):

    FILTERED_PLACEHOLDER = '[Filtered]'
    FILTERED_FIELDS = re.compile('api|token|key|secret|password|signature', re.I)

    def parse_client_ip(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR', None)
        return ip.split(',')[0].strip() if ip else request.META.get('REMOTE_ADDR', '')

    def parse_user_agent(self, request):
        return request.META.get('HTTP_USER_AGENT', None)

    def clean_data(self, data):
        if isinstance(data, list):
            return [self.clean_data(d) for d in data]
        if isinstance(data, dict):
            data = dict(data)
            for key, value in data.items():
                if isinstance(value, list) or isinstance(value, dict):
                    data[key] = self.clean_data(value)
                if self.FILTERED_FIELDS.search(key):
                    data[key] = self.FILTERED_PLACEHOLDER
        return data


    def initial(self, request, *args, **kwargs):

        self.request.drflog = Entry.objects.create(
            user=request.user if not request.user.is_anonymous else None,
            ip=self.parse_client_ip(request),
            host=request.get_host(),
            path=request.path,
            method=request.method,
            user_agent=request.META.get('HTTP_USER_AGENT', 'N/A')[:200],
            query_params=self.clean_data(request.query_params.dict()),
            request_data=self.clean_data(request.data)
        )
        super(LogMixin, self).initial(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super(LogMixin, self).finalize_response(request, response, *args, **kwargs)
        if hasattr(self.request, 'drflog'):
            self.request.drflog.response_data = self.clean_data(response.data)
            self.request.drflog.status = response.status_code
            self.request.drflog.time_finalized = now()
            self.request.drflog.save()
        return response

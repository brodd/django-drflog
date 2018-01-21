from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField

class Entry(models.Model):

    @property
    def time_ms(self):
        if not self.time_finalized or not self.time_initialized:
            return None
        return int((self.time_finalized - self.time_initialized).total_seconds() * 1000)

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True)

    ip = models.GenericIPAddressField()

    host = models.URLField()
    path = models.CharField(max_length=200)

    method = models.CharField(max_length=10)
    status = models.PositiveSmallIntegerField(null=True)

    user_agent = models.CharField(max_length=200)
    query_params = JSONField(null=True)
    request_data = JSONField(null=True)
    response_data = JSONField(null=True)

    time_initialized = models.DateTimeField(auto_now_add=True)
    time_finalized = models.DateTimeField(null=True)

    class Meta:
        verbose_name_plural = 'Entries'

from __future__ import annotations

from datetime import datetime

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def as_date(timestamp):
    date = datetime.fromisoformat(timestamp)
    return date.strftime("%H:%M:%S — %d/%m/%Y")

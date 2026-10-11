import re
from django import template

register = template.Library()

@register.filter
def phone_format(phone):
    if not phone:
        return ""

    phone = re.sub(r'\D', '', str(phone))

    if len(phone) == 12 and phone.startswith("998"):
        return f"+998({phone[3:5]}) {phone[5:8]}-{phone[8:10]}-{phone[10:12]}"

    return phone
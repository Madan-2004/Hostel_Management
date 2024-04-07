from django import template

from datetime import date, timedelta

register = template.Library()

@register.simple_tag(name="todays_date")
def get_current_date():
    now = date.today().isoformat() 
    return now

@register.simple_tag(name="max_date")
def get_current_date():
    max = (date.today()+timedelta(days=60)).isoformat()  
    return max

@register.simple_tag(name="tomorrow")
def get_current_date():
    max = (date.today()+timedelta(days=1)).isoformat()  
    return max



@register.filter
def percentage(value1,value2=100):
    
    return int(value1)/int(value2)*100

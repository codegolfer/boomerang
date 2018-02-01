"""
sendgrid python api
"""

import json
import re

import requests

# Helpers


def _url(path):
    return 'https://api.sendgrid.com/v3' + path


def _fix_at(at):
    at_prefix = 'Bearer '
    if not re.match(at_prefix, at):
        return 'Bearer ' + at
    else:
        return at

# POST Requests


def send_email(at, from_name, from_email, to_email, subject, body):
    """
    send email
    """
    headers = {'Authorization': _fix_at(
        at), 'content-type': 'application/json'}
    payload = {'personalizations': [{'to': [{'email': to_email}]}], 'from': {
        'email': from_email, 'name': from_name}, 'subject': subject, 'content': [{'type': 'text/plain', 'value': body}]}
    requests.post(url=_url('/mail/send'), json=payload, headers=headers)
    return True

"""
bot implementation.
"""
import os

import boto3
from botocore.exceptions import ClientError

import sendgrid
import ciscospark

# Sets config values from the config file
ACCESS_TOKEN_SPARK = "Bearer " + os.environ['access_token_spark']
MYSELF = os.environ['my_person_id']
SENDGRID_API_TOKEN = os.environ['sendgrid_api_token']

AWS_REGION = "us-west-2"
CHARSET = "UTF-8"
SENDER = 'boomerang.spark@aol.com'
SENDER_NAME = 'boomerang'


def mask_email(email):
    """
    masks important part of email
    """
    at_index = email.find('@')
    email_substring_to_mask = email[1:at_index]
    masked_email = email.replace(
        email_substring_to_mask, '*' * len(email_substring_to_mask))
    return masked_email


def send_email(subject, plaintext_email, recipient):
    """
    sends email via Sendgrid
    """
    sendgrid.send_email(SENDGRID_API_TOKEN, SENDER_NAME,
                        SENDER, recipient, subject, plaintext_email)


def send_email_ses(subject, plaintext_email, recipient):
    """
    sends email via SES
    """

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': plaintext_email,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print e.response['Error']['Message']
    else:
        print "Email sent! Message ID:",
        print response['ResponseMetadata']['RequestId']


def handler(event, context):
    """
    boomerang
    """
    # print "Event is {0}".format(event)

    person_email = None
    try:
        room_id = event['data']['roomId']
        message_id = event['data']['id']
        person_id = event['data']['personId']
        person_email = event['data']['personEmail']
        print "Consumer: {}".format(person_email)
    except KeyError as error:
        print "Duh - key error %r" % error
        return False

    if person_id == MYSELF:
        return False

    if person_email is None:
        return False

    message = ciscospark.get_message(ACCESS_TOKEN_SPARK, message_id)
    user_message = message.get('text', "None")
    # print "Message: {}".format(user_message)

    if user_message is None:
        return False

    if user_message.lower().startswith('boomerang'):
        user_message = user_message[9:]

    # print "Query (final): {}".format(user_message)

    if "help" in user_message[:6].lower():
        ciscospark.post_message_rich(
            ACCESS_TOKEN_SPARK, room_id, "Supported commands: help, or just add your note")
        return True

    subject = 'boomerang: {}...'.format(user_message[:30])
    # print 'subject: {}'.format(subject)
    # print 'body: {}'.format(user_message)
    send_email(subject, user_message, person_email)

    masked_email = mask_email(person_email)
    ciscospark.post_message_rich(
        ACCESS_TOKEN_SPARK, room_id, 'boom...the message is on it\'s way to ``{}``'.format(masked_email))
    return True

"""
AWS Manager for Client Desktop

Class for manage all communications with AWS.

Author: Ruben Perez Vaz for Lab Assignment 1.
"""

import uuid
import boto3
import time
import logging
import yaml
import urllib.request as urllib2
import base64
import M2Crypto
import hashlib

secret = "technology_applications_18_19"


def generate_session_id(num_bytes):
    return base64.b64encode(M2Crypto.m2.rand_bytes(num_bytes))


class Manager:
    def __init__(self):
        self.sqs = boto3.resource('sqs')
        self.queue_inbox = self.sqs.get_queue_by_name(QueueName='inbox')
        self.queue_outbox = self.sqs.get_queue_by_name(QueueName='outbox')
        self.user_id = str(uuid.UUID(bytes=M2Crypto.m2.rand_bytes(16)))

        key = self.user_id + secret
        hash_object = hashlib.md5(key.encode())
        self.hash_user = str(hash_object.hexdigest())

        logging.info('User ID: %s, hash: "%s"', str(self.user_id), str(self.hash_user))

        return

    '''
        Used for send messages to a specific queue.
        :return
            > SQS.Message() [see boto3 SQS.Message]
    '''

    def send_message(self, type_message, message, queue_name):
        logging.info('Entering send_message(), arguments [type = "%s", message = "%s", queue_name = "%s"]',
                     type_message,
                     message,
                     queue_name)

        if queue_name is 'inbox':
            logging.info('  Send new message to queue "inbox".')
            queue = self.queue_inbox
        else:
            if queue_name is 'outbox':
                logging.info('  Send new message to queue "outbox".')

                queue = self.queue_outbox
            else:
                logging.ERROR(' Queue not valid, exit!')

                return -1

        response = queue.send_message(MessageAttributes={
            str(type_message): {
                'DataType': 'String',
                'StringValue': str(type_message)
            },
            str('user_hash'): {
                'DataType': 'String',
                'StringValue': str(self.hash_user)
            },
            str('user_id'): {
                'DataType': 'String',
                'StringValue': str(self.user_id)
            }
        }, MessageBody=str(message))

        logging.info('  Message send.')
        logging.info("Leaving send_message()")

        return response

    '''
        Used for receive a message from a queue using a list of filters in order to gets only the correct messages.
        :return
            > SQS.Message() [see boto3 SQS.Message]
    '''

    def receive_message(self, queue_name):
        logging.info('Entering receive_message(), arguments [queue_name = "%s"]', queue_name)

        if queue_name is 'inbox':
            logging.info('  Waiting for new message from queue "inbox".')

            queue = self.queue_inbox
        else:
            if queue_name is 'outbox':
                logging.info('  Waiting for new message from queue "outbox".')

                queue = self.queue_outbox
            else:
                logging.ERROR(' Queue not valid, exit!')

                return -1

        while True:
            for response in queue.receive_messages(MessageAttributeNames=[self.user_id], MaxNumberOfMessages=1,
                                                   VisibilityTimeout=100):
                if response.message_attributes is not None:
                    logging.info('      Receive new message:')
                    logging.info('          > body: "%s".', response.body)
                    logging.info('          > message_id: "%s".', response.message_id)
                    response.delete()
                    logging.info("Leaving receive_message()")

                    return response
                else:
                    response.change_visibility(VisibilityTimeout=0)
                    time.sleep(5)

    def print_response(self, response):
        if response.message_attributes[self.user_id]['StringValue'] == 'False':
            response = str(response.body)
            print(response)
        else:
            echos = yaml.load(urllib2.urlopen(str(response.body)))

            for echo in echos:
                print('- ' + echo)

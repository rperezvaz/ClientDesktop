import aws_manager
import logging
import os
import signal
import sys

logging.basicConfig(format='[%(asctime)s] [%(levelname)8s] --- %(message)s', level=logging.CRITICAL)


def sigint_handler(signum, frame):
    print('\n\nStop pressing CTRL+C.')
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)
client_aws = aws_manager.Manager()

while True:
    os.system('clear')
    print('TECHNOLOGY APPLICATIONS, LAB ASSIGNMENT 1.\n')
    print('     1. ECHO.')
    print('     2. SEARCH.\n')

    try:
        option = int(input('     SELECT AN OPTION [1,2]: '))
        if option == 1:
            os.system('clear')

            while True:
                message = str(input('CLIENT MESSAGE: '))

                client_aws.send_message(type_message='echo', message=message, queue_name='inbox')
                response = client_aws.receive_message(queue_name='outbox')
                print(response.body + '\n')

                if message.upper() == 'END':
                    input("\n\nPRESS ENTER TO BACK TO MENU...")
                    break

        if option == 2:
            os.system('clear')

            client_aws.send_message(type_message='search', message='search', queue_name='inbox')
            response = client_aws.receive_message(queue_name='outbox')
            client_aws.print_response(response)

            input("\n\nPRESS ENTER TO BACK TO MENU...")
    except ValueError as error:
        continue

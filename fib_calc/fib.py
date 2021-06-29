#docker build -t fib .
#docker run -it --rm -e QUEUE_NAME='my-queue' -e AMQP_HOST='host.docker.internal' fib
#

import pika
import os
import sys
import time

host = os.environ.get('AMQP_HOST')
in_queue = os.environ.get('IN_QUEUE_NAME')
out_queue = os.environ.get('OUT_QUEUE_NAME')
connection_params = pika.ConnectionParameters(host=host)
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()



def fib(n):
    a = 0
    b = 1
    c = None
    for i in range(1, n):
        c = a + b
        a = b 
        b = c
    return c

#send fib(n) for message n on in-queue, then send to out-queue
def on_message(ch, method, properties, body):
    message = body.decode('UTF-8')
    try:
        fib_n = fib(int(message))
    except ValueError: #if message can't be parsed as a base 10 int
        fib_n = -1
    channel.queue_declare(queue=out_queue)
    channel.basic_publish(exchange='',
                    routing_key=out_queue,
                    body=str(fib_n))
    print(fib_n)


def main():
    #consume in-queue
    channel.queue_declare(queue=in_queue)
    channel.basic_consume(queue=in_queue, on_message_callback=on_message, auto_ack=True)

    print('Subscribed to ' + in_queue + ', waiting for messages...')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            connection.close()
            sys.exit(0)
        except SystemExit:
            os._exit(0)
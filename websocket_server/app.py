#from flask import Flask,render_template,request,send_from_directory
#from flask_socketio import SocketIO
import os
import sys
import time
import socketio
import aio_pika
from aiohttp import web
from functools import partial




time.sleep(20) #wait for rabbitmq to spin up
print("Online", flush=True)

## creates a new Async Socket IO Server
sio = socketio.AsyncServer(cors_allowed_origins=['http://localhost:5000'])
## Creates a new Aiohttp Web Application
app = web.Application()
# Binds our Socket.IO server to our Web App
## instance
sio.attach(app)
#using print statements to log for now, should be using a logger
print("Connected", flush=True)


# Send the consumed message to a socket
async def process_message(message: aio_pika.IncomingMessage, sid=None):
    async with message.process():
        msg = message.body.decode("utf-8")
        print(f"Sending message on socket: {msg}, sid: {sid}", flush=True)
        await sio.emit('message', msg, room=sid)

    
#connect and consume messages
@sio.event
async def connect(sid, environ):
    print(f"connection from sid {sid}", flush=True)
    await sio.emit('message', "fib_n output goes here", broadcast=True)


    connection = await aio_pika.connect(host=os.environ.get('AMQP_HOST'))
    queue_name = os.environ.get('OUT_QUEUE_NAME')
    channel = await connection.channel()
    queue = await channel.declare_queue(queue_name)
    #I tried sending to different sid's but there are extra precautions I would have to take
    #if i wanted to do that
    await queue.consume(partial(process_message, sid=None)) #acts as broadcast with sid=None


# Used only to verify a connection message from our client
@sio.on('message')
async def print_message(sid, message):
    ## When we receive a new event of type
    ## 'message' through a socket.io connection
    ## we print the socket ID and the message
    print(f"Socket ID: {sid}", flush=True)
    print(message, flush=True)


## We kick off our server
if __name__ == '__main__':
    web.run_app(app, host=sys.argv[1], port=sys.argv[2])
from flask import Flask,render_template,request,send_from_directory
import os
import time
import pika
import atexit




print("Online", flush=True)
time.sleep(20) #wait for rabbitmq to spin up
host = os.environ.get('AMQP_HOST')
in_queue = os.environ.get('IN_QUEUE_NAME')
connection_params = pika.ConnectionParameters(host=host)
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
#don't think this actually works without catching some exception, 
#but the sleep works well enough
while not channel.is_open: 
    print("Channel not open, retrying", flush=True)
    time.sleep(5)
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
channel.queue_declare(queue=in_queue)
print("Connected", flush=True)


def OnExitApp(user):
    print(user, " exit Flask application", flush=True)
    print("Closing connection", flush=True)
    connection.close()


app = Flask(__name__)
#http://localhost:5000/


#return the index page on get req
@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template("index.html")

#send the (str) number along the message queue (in-queue) for processing
@app.route('/fib', methods=['POST'])
def fib():
    if request.method == 'POST':
        #send to message queue
        #receive from message queue
        
        channel.basic_publish(exchange='',
                      routing_key=in_queue,
                      body=request.form['fib_n'])
        
        return ('', 204)

#was getting favicon errors, probably unrelated though
@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


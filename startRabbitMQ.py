#!/usr/bin/env python3

import pika
import sys

def start_rabbitMQ_server():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    print("RabbitMQ server started")
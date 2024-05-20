#!/usr/bin/env python3

import multiprocessing
from startRedis import start_redis_server
from startRabbitMQ import start_rabbitMQ_server

#aixó es per iniciar el servidor de redis

server_processRedis = multiprocessing.Process(target=start_redis_server)
server_processRedis.start()


server_processRabbitMQ = multiprocessing.Process(target=start_rabbitMQ_server)
server_processRabbitMQ.start()

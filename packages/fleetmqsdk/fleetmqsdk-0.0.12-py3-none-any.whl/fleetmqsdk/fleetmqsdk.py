from . import Message_pb2
import zmq

tcpPrefix = "tcp://0.0.0.0:"
ipcPrefix = "ipc:///tmp/feeds/"

def _getAddress(port, ipc):
    if ipc:
        return ipcPrefix + port
    else:
        return tcpPrefix + port

class FleetMQ:
    def __init__(self):
        print("FleetMQ SDK")
        self._context = zmq.Context()
        self._rpcSocket = self._initRpcReq()
        self._publishers = {}
        self._subscribers = {}

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self._rpcSocket.close()
        for publisher in self._publishers.values():
            publisher.close()
        for subscriber in self._subscribers.values():
            subscriber.close()

    def _initRpcReq(self, rpcReqPort="5558"):
        address = 'tcp://localhost:' + rpcReqPort
        try:
            rpcReqInterface = self._context.socket(zmq.REQ)
            rpcReqInterface.connect(address)
            print("Connected to RPC request address: " + address)
        except zmq.ZMQError as e:
            print(f"Failed to open RPC request socket on port {rpcReqPort}: {e}")
            exit(1)
        return rpcReqInterface    
    
    def _createPublisherFromConfig(self, port, topic, source_type, ipc=False):       
        if topic in self._publishers:
            # Publisher already exists
            print("Publisher for topic " + topic + " already exists")
            return
        self._publishers[topic] = _Publisher(self._context, port, topic, ipc)    
    
    def _createSubscriberFromConfig(self, port, topic, sink_type, ipc=False):
        if topic in self._subscribers:
            # Subscriber already exists
            print("Subscriber for topic " + topic + " already exists")
            return
        self._subscribers[topic] = _Subscriber(self._context, port, topic, ipc)
    
    def _createConfigState(self, config, ports):
        for topic in config.send_topics:
            if topic not in ports:
                print("Error: send topic " + topic + " not found in ports, won't create publisher")
                continue
            self._createPublisherFromConfig(ports[topic], topic, config.send_topics[topic].source.source)
        for topic in config.receive_topics:
            if topic not in ports:
                print("Error: receive topic " + topic + " not found in ports, won't create subscriber")
                continue
            self._createSubscriberFromConfig(ports[topic], topic, config.receive_topics[topic].sink.sink)

    def _receiveConfig(self):
        try:
            configBytes = self._rpcSocket.recv_multipart()
            if len(configBytes) != 2:
                print("Error getting config from datastreamer, expected 2 frames, got " + str(len(configBytes)))
                return None, None
            
            # Parse received config data into ABConnectMessage.
            msg = Message_pb2.ABConnectMessage()
            msg.ParseFromString(configBytes[0])

            # Evaluate the message type.
            if msg.HasField("device_config"):
                print("Received config response from datastreamer")
            elif msg.HasField("error"):            
                print("Received Error from datastreamer: " + msg.error.error_message)
                return None, None
            else:
                print("Unexpected message type received from datastreamer: " + msg)
                exit(1)

        except zmq.ZMQError as e:
            print(f"Failed to receive config: {e}")
            exit(1)

        
        portsString = configBytes[1].decode()
        print("Ports: " + portsString)    
        
        print("Device config:")
        print(msg.device_config)        

        return msg.device_config, eval(portsString)        

    def getConfig(self, createConfigState=False):
        req = Message_pb2.ABConnectMessage()
        req.config_request.SetInParent()
        print("Sending config request to datastreamer...")    
        try:
            self._rpcSocket.send(req.SerializeToString())
        except zmq.ZMQError as e:
            print(f"Failed to receive config: {e}")
            exit(1)

        # Wait for response
        config, addresses = self._receiveConfig()
        if config is None or addresses is None:
            print("Failed to get config from datastreamer")
            exit(1)

        if createConfigState:
            self._createConfigState(config, addresses)

        return config, addresses
    
    # CreatePublisher creates a publisher for the given topic, executing an rpc to the datastreamer
    # to provision a zmq port.    
    def createPublisher(self, topic, source_type):    
        if topic in self._publishers:
            # Publisher already exists
            print("Publisher for topic " + topic + " already exists")
            return        
             
        req = Message_pb2.ABConnectMessage()
        req.create_publisher.topic = topic
        req.create_publisher.source.source = source_type
        print("Sending create publisher request to datastreamer...")    
        try:
            self._rpcSocket.send(req.SerializeToString())
        except zmq.ZMQError as e:
            print(f"Failed to send CreatePublisher request to datastreamer: {e}")
            exit(1)

        config, ports = self._receiveConfig()
        if config is None or ports is None:
            print("Failed to create publisher")
            exit(1)
        self._createConfigState(config, ports)

        if topic not in self._publishers:
            print("Internal error, publisher for topic " + topic + " not created")
            exit(1)
    
    # CreateSubscriber creates a subscriber for the given topic, executing an rpc to the
    # datastreamer to provision a zmq port.    
    def createSubscriber(self, topic, sink_type):
        if topic in self._subscribers:
            # Subscriber already exists
            print("Subscriber for topic " + topic + " already exists")
            return
        
        req = Message_pb2.ABConnectMessage()
        req.create_subscription.topic = topic
        req.create_subscription.sink.sink = sink_type
        print("Sending create subscriber request to datastreamer...")
        try:
            self._rpcSocket.send(req.SerializeToString())
        except zmq.ZMQError as e:
            print(f"Failed to send CreateSubscriber request to datastreamer: {e}")
            exit(1)
        
        config, ports = self._receiveConfig()
        if config is None or ports is None:
            print("Failed to create subscriber")
            exit(1)
        self._createConfigState(config, ports)

        if topic not in self._subscribers:
            print("Internal error, subscriber for topic " + topic + " not created")
            exit(1)    

    def publish(self, topic, data):
        if topic not in self._publishers:
            print("Publisher for topic " + topic + " does not exist")
            return
        
        self._publishers[topic].publish(data)

    def receive(self, topic):
        if topic not in self._subscribers:
            print("Subscriber for topic " + topic + " does not exist")
            return

        self._subscribers[topic].receive()


class _Publisher:
    def __init__(self, context, port, topic, ipc=False):        
        self._topic = topic
        self._topicBytes = topic.encode()
        self._publisherSocket = context.socket(zmq.PUB)
        address = _getAddress(port, ipc)
        try:
            self._publisherSocket.bind(address)
        except zmq.ZMQError as e:
            print(f"Failed to open publish socket on address {address} error: {e}")
            exit(1)    
        print(f"Bound to publish socket on address {address} for topic {topic}")

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self._publisherSocket.close()
    
    def publish(self, msg):
        if type(msg) == type(""):
            msgData = msg.encode()
        else:
            msgData = msg
        self._publisherSocket.send_multipart([self._topicBytes, msgData])

class _Subscriber:
    def __init__(self, context, port, topic, ipc=False):            
        self._topic = topic
        self._subscriberSocket = context.socket(zmq.SUB)
        address = _getAddress(port, ipc)
        try:
            self._subscriberSocket.connect(address)
        except zmq.ZMQError as e:
            print(f"Failed to open subscribe socket on address {address} error: {e}")
            exit(1)    
        self._subscriberSocket.setsockopt(zmq.SUBSCRIBE, topic.encode())        
        print(f"Bound to subscribe socket on address {address} for topic {topic}")        

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self._subscriberSocket.close()

    def receive(self):
        return self._subscriberSocket.recv_multipart()[1].decode()
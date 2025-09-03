import zmq
import threading
import time
from .utils import _getAddress
        
class Logger:
    _instance = None

    MAX_MESSAGE_BUFFER = 100

    def __new__(cls, context, sendToDatastreamer, flushInterval, rateLimitInterval, port, ipc=False):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._sendToDatastreamer = sendToDatastreamer
            cls._topic = "sdk-logger"
            cls._topicBytes = cls._topic.encode()

            # Initialize rate limiting counter
            cls._rateLimitCounter = 0
            cls._rateLimitInterval = rateLimitInterval
            cls._rateLimitLock = threading.Lock()
            
            if cls._sendToDatastreamer:
                cls._pushSocket = context.socket(zmq.PUSH)
                address = _getAddress(port, ipc)
                try:
                    cls._pushSocket.connect(address)
                    print(f"Bound to logging socket: {address}")
                except zmq.ZMQError as e:
                    print(f"Failed to open logging socket: {e}")
                    exit(1)

                # Initialize buffer for msgs to send to datastreamer and timer
                cls._messageBuffer = []
                cls._bufferLock = threading.Lock()
                cls._lastFlushTime = time.time()
                cls._flushInterval = flushInterval

                cls._flushThread = threading.Thread(target=cls._instance._flushBufferPeriodically, daemon=True)
                cls._flushThread.start()                
            else:
                cls._pushSocket = None
                
        return cls._instance
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        if hasattr(self, '_pushSocket') and self._pushSocket:
            self._flushBuffer()  # Flush any remaining messages
            self._pushSocket.close()

    def _flushBufferPeriodically(self):
        """Background thread that flushes the buffer every 3 seconds"""
        while True:
            time.sleep(self._flushInterval)
            self._flushBuffer()

    def _flushBuffer(self):
        """Send all buffered messages at once"""
        if not self._sendToDatastreamer or not self._messageBuffer:
            return
            
        with self._bufferLock:
            if not self._messageBuffer:
                return
                
            # Send all buffered messages
            for message in self._messageBuffer:
                self._pushSocket.send_multipart([self._topicBytes, message.encode()])
            
            # Clear the buffer
            self._messageBuffer.clear()
            self._lastFlushTime = time.time()

    def _formatMessage(self, message, args=None):
        if args is None:
            pass
        elif isinstance(args, (list, tuple)):
            message = message.format(*args)
        else:
            message = message.format(args)
        return message

    def writeLine(self, message, args=None):
        message = self._formatMessage(message, args)
        print(message)
        
        if self._sendToDatastreamer:
            with self._bufferLock:
                self._messageBuffer.append(message)
                
                # Check if we should flush immediately (if buffer is getting large)
                if len(self._messageBuffer) >= self.MAX_MESSAGE_BUFFER:
                    self._flushBuffer()
    
    def writeRateLimited(self, message, args=None):
        message = self._formatMessage(message, args)
        
        with self._rateLimitLock:
            self._rateLimitCounter += 1
            # Only print and send to datastreamer every rateLimitInterval calls
            if self._rateLimitCounter % self._rateLimitInterval == 0:
                print(f"Rate limited with interval: {self._rateLimitInterval}: {message}")
                if self._sendToDatastreamer:
                    with self._bufferLock:
                        self._messageBuffer.append(message)
                        
                        # Check if we should flush immediately (if buffer is getting large)
                        if len(self._messageBuffer) >= self.MAX_MESSAGE_BUFFER:
                            self._flushBuffer()
        
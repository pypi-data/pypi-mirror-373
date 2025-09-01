import redis
import time
import threading
import json
import datetime



class RedisConnectionManager:
    """Manages Redis connections with automatic reconnection and health monitoring."""
    
    def __init__(self, host, port, db, password, message_handler, list_channels, bool_verbose=False):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.message_handler = message_handler
        self.bool_verbose = bool_verbose
        
        # Connection state
        self.redis_client = None
        self.pubsub = None
        self.connected = False
        self.last_message_time = time.time()
        self.connection_time = None
        self.message_count = 0
        
        # Threading
        self.running = False
        self.worker_thread = None
        self.health_thread = None
        
        # Channels to subscribe to
        self.channels = list_channels
        
        print(f"Redis Manager initialized for {host}:{port}, channels: {self.channels}")
    
    def connect(self):
        """Establish Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                socket_timeout=2.0,
                socket_connect_timeout=5.0,
                socket_keepalive=True,
                decode_responses=True
            )
            
            # Test connection
            self.redis_client.ping()
            
            self.connected = True
            self.connection_time = time.time()
            self.last_message_time = time.time()
            
            print(f"✅ Redis connected to {self.host}:{self.port} at {datetime.datetime.fromtimestamp(self.connection_time).strftime('%H:%M:%S')}")
            
            # Start worker threads
            self.start_worker_threads()
            
            return True
            
        except Exception as e:
            self.connected = False
            print(f"❌ Redis connection failed to {self.host}:{self.port}: {e}")
            return False
    
    def start_worker_threads(self):
        """Start worker threads for message handling and health monitoring."""
        if not self.running:
            self.running = True
            
            # Start message handling thread
            self.worker_thread = threading.Thread(target=self._message_worker, daemon=True)
            self.worker_thread.start()
            
            # Start health monitoring thread
            self.health_thread = threading.Thread(target=self._health_monitor, daemon=True)
            self.health_thread.start()
            
            print(f"🔄 Redis worker threads started")
    
    def _message_worker(self):
        """Worker thread for handling Redis messages."""
        while self.running:
            try:
                if not self.connected:
                    time.sleep(1)
                    continue
                
                # Create pubsub if not exists
                if self.pubsub is None:
                    self.pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)
                    for channel in self.channels:
                        self.pubsub.subscribe(channel)
                        print(f"📡 Subscribed to channel: {channel}")
                
                # Get message with timeout
                message = self.pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    self.last_message_time = time.time()
                    self.message_count += 1
                    
                    # Forward to message handler
                    channel = message['channel']
                    data = message['data']
                    self.message_handler(channel, data)
                    
                    # Print message stats every 100 messages
                    if self.message_count % 100 == 0:
                        print(f"📊 Redis messages processed: {self.message_count}")
                
            except Exception as e:
                print(f"⚠️ Redis message worker error: {e}")
                self._handle_connection_error()
                time.sleep(1)
    
    def _health_monitor(self):
        """Health monitoring thread."""
        while self.running:
            try:
                if self.connected:
                    # Check if we're still receiving messages
                    time_since_last_message = time.time() - self.last_message_time
                    if time_since_last_message > 30:  # No messages for 30 seconds

                        if self.bool_verbose:
                            print(f"⚠️ No Redis messages for {time_since_last_message:.1f}s, checking connection...")
                        
                        # Test connection
                        try:
                            self.redis_client.ping()
                        except:
                            print("❌ Redis connection lost, attempting reconnection...")
                            self._handle_connection_error()
                
                time.sleep(10)  # Health check every 10 seconds
                
            except Exception as e:
                print(f"⚠️ Health monitor error: {e}")
                time.sleep(10)
    
    def _handle_connection_error(self):
        """Handle connection errors and attempt reconnection."""
        self.connected = False
        if self.pubsub:
            try:
                self.pubsub.close()
            except:
                pass
            self.pubsub = None
        
        print(f"🔄 Attempting Redis reconnection to {self.host}:{self.port}...")
        
        # Non-stop reconnection attempts
        reconnection_attempts = 0
        while not self.connected and self.running:
            reconnection_attempts += 1
            try:
                print(f"🔄 Reconnection attempt {reconnection_attempts}...")
                if self.connect():
                    print(f"✅ Reconnection successful after {reconnection_attempts} attempts")
                    break
                else:
                    print(f"🔄 Reconnection failed, retrying in 2 seconds...")
                    time.sleep(2)
            except Exception as e:
                print(f"🔄 Reconnection error (attempt {reconnection_attempts}): {e}")
                time.sleep(2)
    
    def publish(self, channel, message):
        """Publish a message to Redis channel."""
        if not self.connected:
            print(f"⚠️ Cannot publish to {channel}: not connected")
            return False
        
        try:
            self.redis_client.publish(channel, message)
            return True
        except Exception as e:
            print(f"❌ Failed to publish to {channel}: {e}")
            self._handle_connection_error()
            return False
    
    def get(self, key):
        """Get value from Redis key."""
        if not self.connected:
            print(f"⚠️ Cannot get {key}: not connected")
            return None
        
        try:
            return self.redis_client.get(key)
        except Exception as e:
            print(f"❌ Failed to get {key}: {e}")
            self._handle_connection_error()
            return None
    
    def set(self, key, value):
        """Set value to Redis key."""
        if not self.connected:
            print(f"⚠️ Cannot set {key}: not connected")
            return False
        
        try:
            self.redis_client.set(key, value)
            return True
        except Exception as e:
            print(f"❌ Failed to set {key}: {e}")
            self._handle_connection_error()
            return False
    
    def get_connection_status(self):
        """Get detailed connection status."""
        if not self.connected:
            return {
                'status': 'Disconnected',
                'host': f"{self.host}:{self.port}",
                'last_connected': None,
                'messages_processed': self.message_count,
                'last_message': None
            }
        
        return {
            'status': 'Connected',
            'host': f"{self.host}:{self.port}",
            'last_connected': datetime.datetime.fromtimestamp(self.connection_time).strftime('%H:%M:%S'),
            'messages_processed': self.message_count,
            'last_message': datetime.datetime.fromtimestamp(self.last_message_time).strftime('%H:%M:%S'),
            'uptime': f"{(time.time() - self.connection_time) / 60:.1f} minutes"
        }
    
    def stop(self):
        """Stop the Redis connection manager."""
        print(f"🛑 Stopping Redis connection manager for {self.host}:{self.port}")
        self.running = False
        
        if self.pubsub:
            try:
                self.pubsub.close()
            except:
                pass
        
        if self.redis_client:
            try:
                self.redis_client.close()
            except:
                pass
        
        # Wait for threads to finish
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
        
        if self.health_thread and self.health_thread.is_alive():
            self.health_thread.join(timeout=2.0)
        
        print(f"✅ Redis connection manager stopped for {self.host}:{self.port}")


if __name__ == "__main__":
    redis_connection_manager = RedisConnectionManager(
        host="livewithjoyday.com",
        port=6379,
        db=0,
        password="5k4g4redisau4a83",
        message_handler=lambda channel, data: print(f"Received message on channel {channel}: {data}"),
        list_channels=["test"]
    )

    redis_connection_manager.connect()

    redis_connection_manager.publish("test", "Hello, Redis!")

    redis_connection_manager.stop()

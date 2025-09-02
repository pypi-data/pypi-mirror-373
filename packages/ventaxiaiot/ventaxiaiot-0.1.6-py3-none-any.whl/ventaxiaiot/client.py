# File: ventaxiaiot/client.py
import asyncio
import ssl
import sys
import logging

_LOGGER = logging.getLogger(__name__)

has_native_psk = sys.version_info >= (3, 13)

if not has_native_psk:
    raise RuntimeError("Native PSK requires Python 3.13+")

class AsyncNativePskClient:
    def __init__(self, wifi_device_id, identity, psk_key, host, port, loop=None,connection_lost_callback=None):
        self.identity = identity
        self.psk_key = psk_key.encode('utf-8')
        self.host = host
        self.port = port
        self.wifi_device_id = wifi_device_id
        self.loop = loop or asyncio.get_event_loop()
        self.reader = None
        self.writer = None
        self._message_queue = asyncio.Queue()
        self._reader_task = None
        self._running = False
        self.connection_lost_callback = connection_lost_callback
        self._closing = False 

    def psk_callback(self, hint):
        return self.identity, self.psk_key
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if not self._running:
            raise StopAsyncIteration
        try:
            msg = await self._message_queue.get()
            return msg
        except asyncio.CancelledError:
            raise StopAsyncIteration

    async def connect(self, timeout=30.0):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.set_ciphers("PSK-AES128-CBC-SHA")
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.set_psk_client_callback(self.psk_callback)

        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port, ssl=context),
                timeout=timeout,
            )
            self._running = True
            self._reader_task = asyncio.create_task(self._reader_loop())
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")

    async def send(self, message):
        if self.writer is None:
            raise ConnectionError("Not connected")
        self.writer.write((message + '\0').encode('utf-8'))
        await self.writer.drain()      
       
    async def _reader_loop(self):
        buffer = b""
        try:
            while not self.reader.at_eof(): # type: ignore
                chunk = await self.reader.read(1024) # type: ignore
                if not chunk:
                    break
                buffer += chunk
                while b'\0' in buffer:
                    msg_bytes, buffer = buffer.split(b'\0', 1)
                    msg = msg_bytes.decode('utf-8').strip()
                    await self._message_queue.put(msg)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _LOGGER.error(f"Reader loop error: {e}")
        finally:
            if self._running:  # If _running was still True when we exited
                self._running = False
                if not self._closing and self.connection_lost_callback:
                    _LOGGER.warning("Connection lost — calling callback")
                    await self.connection_lost_callback()
    
    async def close(self):
        if self._closing:
            return  # Already closing
        self._running = False
        self._closing = True

        try:
            # Cancel the reader task if running
            if self._reader_task and not self._reader_task.done():
                self._reader_task.cancel()
                try:
                    await self._reader_task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    # Log and suppress to avoid shutdown errors
                    _LOGGER.warning("Reader task error during shutdown: %s", e)

            # Try to close the TLS connection, suppress bad shutdown behavior
            if self.writer:
                try:
                    self.writer.close()
                    await self.writer.wait_closed()
                except ConnectionResetError as e:
                    _LOGGER.debug("Connection reset by peer during close() - ignoring: %s", e)
                except ssl.SSLError as e:
                    if "application data after close notify" in str(e):
                        _LOGGER.debug(" Ignored non-compliant TLS shutdown: %s", e)
                    else:
                        _LOGGER.warning("TLS error during shutdown: %s", e)
                except Exception as e:
                    _LOGGER.error("Unexpected error during close(): %s", e)                
        finally:
            self._closing = False
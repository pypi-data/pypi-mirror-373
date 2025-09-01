import asyncio
import websockets
import json
import sys
import os
import base64
from typing import Optional, Dict, Any
import logging
import mimetypes
from pathlib import Path
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

try:
    from .config import Config
except ImportError:
    from config import Config

logging.basicConfig(level=getattr(logging, Config.get_log_level()))
logger = logging.getLogger(__name__)

class TerminalChatClient:
    def __init__(self):
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.username: str = ""
        self.channel_code: str = ""
        self.server_uri: str = ""
        self.is_connected: bool = False
        self.reconnect_attempts: int = 0
        self.max_reconnect_attempts: int = Config.get_max_reconnect_attempts()
        self.websocket_config = Config.get_websocket_config()
        self.last_received_image: Optional[Dict[str, Any]] = None
        # Image settings from config
        try:
            self.supported_image_formats = Config.get_supported_image_formats()
            self.max_image_size = Config.get_max_image_size()
        except Exception as e:
            # Fallback values if config fails
            print(f"Warning: Failed to load image config: {e}")
            self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
            self.max_image_size = 5 * 1024 * 1024

    def derive_key(self, passphrase: str) -> bytes:
        # Use a static salt for simplicity; for real security, use a random salt and share it
        salt = b'gupsup-static-salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
            backend=default_backend()
        )
        return kdf.derive(passphrase.encode())

    def encrypt_message(self, plaintext: str) -> str:
        key = self.derive_key(self.channel_code)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, plaintext.encode(), None)
        return base64.b64encode(nonce + ct).decode()

    def decrypt_message(self, ciphertext_b64: str) -> Optional[str]:
        try:
            key = self.derive_key(self.channel_code)
            aesgcm = AESGCM(key)
            data = base64.b64decode(ciphertext_b64)
            nonce, ct = data[:12], data[12:]
            pt = aesgcm.decrypt(nonce, ct, None)
            return pt.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None

    def encode_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Encode image file to base64 with metadata"""
        try:
            path = Path(image_path)
            
            # Check if file exists
            if not path.exists():
                print(f"🔴 Image file not found: {image_path}")
                return None
            
            # Check file extension
            if path.suffix.lower() not in self.supported_image_formats:
                print(f"🔴 Unsupported image format. Supported: {', '.join(self.supported_image_formats)}")
                return None
            
            # Check file size
            file_size = path.stat().st_size
            if file_size > self.max_image_size:
                print(f"🔴 Image too large ({file_size / 1024 / 1024:.1f}MB). Max size: {self.max_image_size / 1024 / 1024}MB")
                return None
            
            # Read and encode image
            with open(path, 'rb') as f:
                image_data = f.read()
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(path))
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = 'image/jpeg'  # Default fallback
            
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            return {
                'type': 'image',
                'filename': path.name,
                'mime_type': mime_type,
                'size': file_size,
                'data': encoded_image
            }
        except Exception as e:
            print(f"🔴 Error encoding image: {e}")
            return None

    def display_image_info(self, image_data: Dict[str, Any], sender: str) -> None:
        """Display image information in terminal"""
        filename = image_data.get('filename', 'unknown')
        size = image_data.get('size', 0)
        mime_type = image_data.get('mime_type', 'unknown')
        
        size_str = f"{size / 1024:.1f}KB" if size < 1024 * 1024 else f"{size / 1024 / 1024:.1f}MB"
        
        print(f"{sender} sent an image:")
        print(f"   └─ File: {filename}")
        print(f"   └─ Type: {mime_type}")
        print(f"   └─ Size: {size_str}")
        print(f"   └─ Use '/save [path-to-folder]/[desired-filename]' to save this image")

    def save_received_image(self, image_data: Dict[str, Any], save_path: Optional[str] = None) -> bool:
        """Save received image to local filesystem"""
        try:
            filename = image_data.get('filename', 'received_image.jpg')
            if save_path:
                save_path = Path(save_path)
            else:
                save_path = Path.cwd() / filename
            
            image_bytes = base64.b64decode(image_data['data'])
            
            with open(save_path, 'wb') as f:
                f.write(image_bytes)
            
            print(f"Image saved to: {save_path}")
            return True
        except Exception as e:
            print(f"🔴 Error saving image: {e}")
            return False

    def get_server_config(self) -> str:
        """Get server configuration from environment or user input"""
        default_server = Config.get_server_address()
        
        print("gupsup - Secure Communication Channel")
        return default_server
    
    def get_channel_code(self) -> str:
        """Get or generate channel code"""
        choice = input("Channel code (or 'new' to create): ").strip()
        if choice.lower() == "new":
            import random, string
            code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            print(f"Channel created: {code}")
            print(f"Share code '{code}' with others to join")
            return code
        else:
            return choice
    
    def get_username(self) -> str:
        """Get username from user"""
        while True:
            username = input("Username: ").strip()
            if username:
                return username
            print("Username required. Try again.")
    
    def build_websocket_uri(self, server: str, code: str) -> str:
        """Build WebSocket URI based on server address"""
        if server.startswith("localhost") or server.startswith("127.0.0.1"):
            return f"ws://{server}/ws/{code}"
        else:
            return f"wss://{server}/ws/{code}"
    
    async def connect(self) -> bool:
        """Establish WebSocket connection with retry logic"""
        try:
            print("Establishing connection...")
            print("Note: Initial connection may take longer if server is sleeping")
            
            self.websocket = await websockets.connect(
                self.server_uri,
                **self.websocket_config
            )
            self.is_connected = True
            self.reconnect_attempts = 0
            print(f"🟢 Connected to channel: {self.channel_code}")
            print("Commands:")
            print("  - Type messages to send")
            print("  - '/image <path>' to send image")
            print("  - '/save [filename]' to save last received image")
            print("  - 'quit' to exit\n")
            return True
        except asyncio.TimeoutError:
            print(f"🔴 Connection timeout - server may be starting up")
            print("Retry recommended - server should be ready now")
            return False
        except Exception as e:
            print(f"🔴 Connection failed: {e}")
            return False
    
    async def reconnect(self) -> bool:
        """Attempt to reconnect to the server"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print(f"🔴 Max reconnection attempts reached ({self.max_reconnect_attempts}). Aborting.")
            return False
        
        self.reconnect_attempts += 1
        print(f"Reconnecting... (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        delay = min(2 ** self.reconnect_attempts, 30) 
        await asyncio.sleep(delay)
        return await self.connect()
    
    async def receive_messages(self):
        """Handle incoming messages (decrypt)"""
        while self.is_connected:
            try:
                if self.websocket:
                    message = await self.websocket.recv()
                    plaintext = self.decrypt_message(message)
                    if plaintext is None:
                        continue
                    
                    if plaintext.startswith(f"{self.username}: "):
                        continue
                    
                    if "[IMAGE:" in plaintext and "]" in plaintext:
                        try:
                            parts = plaintext.split(": [IMAGE:", 1)
                            if len(parts) == 2:
                                sender = parts[0]
                                image_json_part = parts[1].rsplit("]", 1)[0]
                                image_data = json.loads(image_json_part)
                                
                                self.last_received_image = image_data
                                print(f"\r", end="") 
                                self.display_image_info(image_data, sender)
                                print(f"{self.username}: ", end="", flush=True)
                                continue
                        except (json.JSONDecodeError, IndexError) as e:
                            logger.debug(f"Failed to parse image message: {e}")
                    
                    print(f"\r{plaintext}")
                    print(f"{self.username}: ", end="", flush=True)
            except websockets.exceptions.ConnectionClosedError:
                if self.is_connected:
                    print("\nConnection lost. Reconnecting...")
                    self.is_connected = False
                    if await self.reconnect():
                        continue
                    else:
                        break
            except websockets.exceptions.ConnectionClosedOK:
                self.is_connected = False
                break
            except Exception as e:
                if self.is_connected: 
                    logger.error(f"Error receiving message: {e}")
                break
    
    async def send_messages(self):
        """Handle outgoing messages (encrypt)"""
        while self.is_connected:
            try:
                prompt = f"{self.username}: "
                message = await asyncio.get_event_loop().run_in_executor(None, input, prompt)
                
                if message.lower() in ['quit', 'exit', '/quit', '/exit']:
                    print("Terminating session.")
                    self.is_connected = False
                    break
                
                # Handle image command
                if message.startswith('/image '):
                    image_path = message[7:].strip()
                    if not image_path:
                        print("🔴 Usage: /image <path_to_image>")
                        continue
                    
                    print("Processing image...")
                    image_data = self.encode_image(image_path)
                    if image_data and self.websocket:
                        image_message_text = f"{self.username}: [IMAGE:{json.dumps(image_data)}]"
                        
                        if len(image_message_text) > 3 * 1024 * 1024:  # 3MB raw text limit
                            print("🔴 Image too large after encoding. Please use a smaller image (max ~2MB).")
                            continue
                            
                        encrypted = self.encrypt_message(image_message_text)
                        
                        # Final size check after encryption
                        if len(encrypted.encode('utf-8')) > 6 * 1024 * 1024:  # 6MB encrypted limit
                            print("🔴 Encrypted message too large. Please use a smaller image.")
                            continue
                            
                        await self.websocket.send(encrypted)
                        print(f"Image sent: {image_data['filename']}")
                    continue
                
                # Handle save command
                if message.startswith('/save'):
                    if not self.last_received_image:
                        print("🔴 No image to save. Receive an image first.")
                        continue
                    
                    parts = message.split(' ', 1)
                    save_filename = parts[1].strip() if len(parts) > 1 else None
                    self.save_received_image(self.last_received_image, save_filename)
                    continue
                
                # Regular text message
                if message.strip():
                    if self.websocket:
                        formatted_message = f"{self.username}: {message}"
                        encrypted = self.encrypt_message(formatted_message)
                        await self.websocket.send(encrypted)
                        
            except KeyboardInterrupt:
                print("\nSession interrupted.")
                self.is_connected = False
                break
            except Exception as e:
                print(f"🔴 Error sending message: {e}")
                break
    
    async def chat(self):
        """Main chat loop"""
        try:
            await asyncio.gather(
                self.receive_messages(),
                self.send_messages()
            )
        except KeyboardInterrupt:
            print("\nSession terminated.")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources"""
        self.is_connected = False
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass

def run_client():
    """Main entry point for the terminal chat client"""
    client = TerminalChatClient()
    
    try:
        server = client.get_server_config()
        client.channel_code = client.get_channel_code()
        client.username = client.get_username()
        client.server_uri = client.build_websocket_uri(server, client.channel_code)
        
        async def connect_with_retry():
            max_initial_attempts = 2
            for attempt in range(max_initial_attempts):
                if await client.connect():
                    return True
                elif attempt < max_initial_attempts - 1:
                    print(f"Retrying connection... (attempt {attempt + 2}/{max_initial_attempts})")
                    await asyncio.sleep(3)
            return False
        
        async def main():
            if not await connect_with_retry():
                print("🔴 Connection failed after multiple attempts.")
                print("Check network connection and retry.")
                return
            await client.chat()
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\nExiting.")
    except Exception as e:
        print(f"🔴 System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_client()
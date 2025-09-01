<div align="center">

# gupsup

<em>A secure terminal-based chat application with image sharing for real-time communication — right from your terminal.</em>

[![PyPI Downloads](https://static.pepy.tech/badge/gupsup)](https://pepy.tech/projects/gupsup)
[![PyPI version](https://img.shields.io/pypi/v/gupsup)](https://pypi.org/project/gupsup/)
[![Python version](https://img.shields.io/pypi/pyversions/gupsup)](https://pypi.org/project/gupsup/)

Learn more and explore detailed info at [gupsup-cli](https://gupsup-cli.vercel.app/)

Looking for the server? See [gupsup-server](https://github.com/iamRahul21/terminalchat-server)
</div>



## ⚡ Quick Start

```bash
pip install gupsup
gupsup
```

[![PyPI](https://img.shields.io/pypi/v/gupsup?label=Install%20from%20PyPI)](https://pypi.org/project/gupsup/)

That's it! Start chatting instantly.

## Features

- **Zero-friction setup** - Just run `gupsup` and start chatting instantly
- **End-to-end encryption** - AES-256-GCM encryption with PBKDF2 key derivation
- **Image sharing** - Send and receive images (PNG, JPG, GIF, BMP, WebP) up to 2MB
- **Secure channels** - Create private rooms with shareable 6-character codes  
- **Auto-reconnection** - Handles network issues gracefully with smart retry logic
- **Cross-platform** - Works seamlessly on Windows, macOS, Linux
- **No account required** - Completely anonymous, no sign-up needed
- **Smart image handling** - Automatic format detection, metadata preservation

## Usage

```bash
# Install once
pip install gupsup

# Run anywhere
gupsup
```

### Example Session
```
gupsup - Secure Communication Channel
Channel code (or 'new' to create): new
Channel created: a4b2c1
Share code 'a4b2c1' with others to join
Username: qwerty

Establishing connection...
🟢 Connected to channel: a4b2c1
Commands:
  - Type messages to send
  - '/image <path>' to send image
  - '/save [filename]' to save last received image
  - 'quit' to exit

qwerty: Hello world!
mrrobot: Hey there!
qwerty: /image photo.jpg
Processing image...
Image sent: photo.jpg
alice sent an image:
   └─ File: vacation.png
   └─ Type: image/png
   └─ Size: 245.3KB
   └─ Use '/save vacation.png' to save this image
qwerty: /save my_vacation.png
Image saved to: e:\downloads\my_vacation.png
qwerty: quit
Terminating session.
```

## How It Works

1. **Create or join** a secure channel with a 6-character code
2. **Share the code** with people you want to chat with
3. **Chat securely** - messages are only sent to your channel
4. **No persistence** - messages disappear when you disconnect

## Security & Privacy

- **Military-grade encryption** - AES-256-GCM with authenticated encryption
- **Secure key derivation** - PBKDF2 with 100,000 iterations and SHA-256
- **Channel isolation** - Each channel has its own unique encryption key
- **Zero server knowledge** - Server cannot decrypt messages or images
- **Ephemeral messaging** - No message storage, everything is real-time only
- **Complete anonymity** - No accounts, no tracking, no data collection
- **Perfect forward secrecy** - Unique nonces ensure message security

### Encryption Technical Details
- **Algorithm**: AES-256-GCM (Galois/Counter Mode)
- **Key Size**: 256-bit encryption keys
- **Nonce**: 96-bit random nonce per message
- **Authentication**: Built-in message authentication
- **Key Derivation**: PBKDF2-HMAC-SHA256 with 100k iterations

### Development Install
```bash
# Clone the repository
git clone https://github.com/iamRahul21/gupsup.git
cd gupsup

# Install in development mode
pip install -e .

# Run the application
gupsup
```

### Server Setup (Optional)
```bash
# For hosting your own server
git clone https://github.com/iamRahul21/gupsup-server.git
cd gupsup-server
pip install -r requirements.txt
python main.py
```

## Available Commands

### Chat Commands
- **Send message**: Simply type your message and press Enter
- **Exit**: `quit`, `exit`, `/quit`, or `/exit`
- **Force quit**: Press `Ctrl+C`

### Image Commands
- **Send image**: `/image <path>` 
  - Example: `/image ~/Pictures/photo.jpg`
  - Example: `/image C:\Users\Me\Desktop\image.png`
- **Save received image**: `/save [custom_filename]`
  - Example: `/save` (uses original filename)
  - Example: `/save my_photo.jpg` (custom filename)

### Image Support Details

| Feature | Details |
|---------|---------|
| **Formats** | PNG, JPG/JPEG, GIF, BMP, WebP |
| **Size Limit** | 2MB per image (optimized for reliability) |
| **Encryption** | Full end-to-end encryption like text messages |
| **Metadata** | Filename, size, and MIME type preserved |
| **Validation** | Automatic format detection and size checking |

#### Image Usage Examples
```bash
# Send images
/image path/photo.png

# Save received images
/save                    # Save with original name
/save my_image.jpg       # Save with custom name
/save folder/image.png   # Save to specific path
```

## 🛠️ Troubleshooting

<details>
<summary><strong>Connection Issues</strong></summary>

**Symptoms**: Connection timeouts, frequent disconnects
- First connection may be slow (server waking up)
- Retry connection - should be faster on subsequent attempts
- Check your internet connection
- Verify the server is accessible

</details>

<details>
<summary><strong>Image Problems</strong></summary>

**Large images failing**: 
- Ensure image is under 2MB
- Use image compression tools if needed
- Supported formats: PNG, JPG, GIF, BMP, WebP

**Can't save images**:
- Check file permissions in save directory
- Ensure sufficient disk space
- Try saving to a different location

</details>

<details>
<summary><strong>Encryption Issues</strong></summary>

**Messages appear garbled**:
- Ensure all users have the same channel code
- Verify everyone is using the latest version
- Try creating a new channel

**Can't see messages**:
- Confirm you're in the correct channel
- Check if other users are actually connected
- Restart the application

</details>

<details>
<summary><strong>Platform-Specific Issues</strong></summary>

**Windows**: 
- Use PowerShell or Command Prompt
- Ensure Python 3.8+ is installed

**macOS/Linux**:
- Use Terminal application
- May need to install Python development headers
- Check file path permissions for images

</details>

## 📦 Package Information

| Detail | Information |
|--------|-------------|
| **Package Name** | `gupsup` on PyPI |
| **CLI Command** | `gupsup` |
| **Python Version** | 3.8+ required |
| **Dependencies** | `websockets>=11.0`, `cryptography>=3.0.0` |
| **Size** | Ultra-lightweight (~50KB) |
| **License** | MIT License |
| **Latest Version** | 1.1.0 (with image support) |

## Architecture

```
┌─────────────────┐    WebSocket     ┌──────────────────┐    Channel    ┌─────────────────┐
│  Terminal       │ ←─────────────→  │  FastAPI         │ ←──────────→  │  Channel        │
│  Client         │  (Encrypted)     │  Server          │   Management  │  Manager        │
│  (gupsup)       │                  │                  │               │                 │
└─────────────────┘                  └──────────────────┘               └─────────────────┘
        ↑                                      ↑
   AES-256-GCM                         Relay Only
   Encryption                        (Cannot Decrypt)
```

### How Messages Flow:
1. **Client A** encrypts message with channel key
2. **Server** receives encrypted message (cannot decrypt)
3. **Server** relays encrypted message to **Client B**
4. **Client B** decrypts message with same channel key

---

<div align="center">

**Simple. Secure. Terminal-native.**

MIT License - use freely, contribute back. 

**[Rahul Deka](https://rahul-deka.vercel.app/)**

</div>
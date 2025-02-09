# Joker Web Terminal

A modern web-based terminal that works on both VPS (Linux) and Windows systems. Access your terminal through any web browser!

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## VPS Installation (Linux)

1. Update your system and install Python:
```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip git screen -y

# For CentOS/RHEL
sudo yum update
sudo yum install python3 python3-pip git screen -y
```

2. Clone the repository:
```bash
git clone https://github.com/ormanaq/joker-Web-Terminal.git
cd joker-Web-Terminal
```

3. Install dependencies:
```bash
pip3 install -r requirements.txt
```

4. Run The App:
```bash

python3 main.py

```

Or create a systemd service (for automatic startup):
```bash
sudo nano /etc/systemd/system/joker-terminal.service
```

Add this content:
```ini
[Unit]
Description=Joker Web Terminal
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/joker-Web-Terminal
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:
```bash
sudo systemctl enable joker-terminal
sudo systemctl start joker-terminal
```

## Windows Installation

1. Install Python 3.7+ from [python.org](https://www.python.org/downloads/)

2. Download the repository:
   - Click the green "Code" button above
   - Select "Download ZIP"
   - Extract the ZIP file

3. Open PowerShell as Administrator in the extracted folder and run:
```powershell
pip install -r requirements.txt
python main.py
```

## Access the Terminal

Open your web browser and go to:
- VPS: `http://your_server_ip:8001`
- Windows: `http://localhost:8001`

## Security Setup

For VPS deployment, it's recommended to:

1. Set up a firewall:
```bash
# Ubuntu/Debian
sudo ufw allow 8001
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8001/tcp
sudo firewall-cmd --reload
```

2. Use HTTPS:
   - Get a free SSL certificate from Let's Encrypt
   - Set up Nginx/Apache as a reverse proxy

3. Add authentication:
   - Implement user login
   - Use environment variables for credentials

## Features

- Real-time terminal access via web browser
- Cross-platform support (Windows/Linux)
- Full keyboard support including special keys
- Responsive design
- Modern UI with xterm.js
- WebSocket communication
- Dynamic terminal resizing

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [xterm.js](https://xtermjs.org/) for the terminal emulator
- [FastAPI](https://fastapi.tiangolo.com/) for the backend
- [WebSocket](https://websockets.readthedocs.io/) for real-time communication

## Support

If you have any questions or issues, please open an issue on GitHub.

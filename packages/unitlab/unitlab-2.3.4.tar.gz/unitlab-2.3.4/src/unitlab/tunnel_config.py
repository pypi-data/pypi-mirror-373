"""
Cloudflare Tunnel Configuration using Service Token
No user login required - uses pre-generated service token
"""

import os
import subprocess
import socket
import time
import logging

logger = logging.getLogger(__name__)


class CloudflareTunnel:
    def __init__(self, base_domain, device_id):  # base_domain kept for compatibility
        """
        Initialize tunnel with service token
        No login or credential files needed
        """
        # Configuration
        self.base_domain = "1scan.uz"  # Hardcoded domain
        self.device_id = device_id
        self.hostname = socket.gethostname()
        
        # Service token - replace with your actual token from cloudflared tunnel token command
        # This token can ONLY run the tunnel, cannot modify or delete it
        # To generate: cloudflared tunnel token unitlab-shared
        self.service_token = os.getenv(
            "CLOUDFLARE_TUNNEL_TOKEN",
            "eyJhIjoiYzkxMTkyYWUyMGE1ZDQzZjY1ZTA4NzU1MGQ4ZGM4OWIiLCJzIjoiZmdnSHowbFJFRnBHa05TZzIzV3JKMVBiaDVROGVUd0oyYWtJWThXdjhtTT0iLCJ0IjoiYjMzZGFhOGYtMmNjMy00Y2FkLWEyMjgtOTdlMDYwNzBlNjAwIn0="  # Replace this with your actual token from step 1
        )
        
        if self.service_token == "YOUR_SERVICE_TOKEN_HERE":
            logger.warning(
                "⚠️  No service token configured. "
                "Set CLOUDFLARE_TUNNEL_TOKEN env var or update the token in tunnel_config.py"
            )
        
        # Subdomain names
        self.jupyter_subdomain = f"jupyter-{device_id}"
        self.ssh_subdomain = f"ssh-{device_id}"
        
        # Full URLs
        self.jupyter_url = f"https://{self.jupyter_subdomain}.{self.base_domain}"
        self.ssh_url = f"https://{self.ssh_subdomain}.{self.base_domain}"
        
        self.tunnel_process = None

    def check_cloudflared_installed(self):
        """Check if cloudflared is installed"""
        try:
            result = subprocess.run(
                ["cloudflared", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def install_cloudflared(self):
        """Auto-install cloudflared if not present"""
        import platform
        
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        print("📦 Installing cloudflared...")
        
        try:
            if system == "linux":
                # Determine architecture
                if machine in ["x86_64", "amd64"]:
                    arch = "amd64"
                elif machine in ["aarch64", "arm64"]:
                    arch = "arm64"
                else:
                    arch = "386"
                
                # Download and install
                url = f"https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-{arch}"
                
                commands = [
                    f"curl -L {url} -o /tmp/cloudflared",
                    "chmod +x /tmp/cloudflared",
                    "sudo mv /tmp/cloudflared /usr/local/bin/cloudflared 2>/dev/null || "
                    "mkdir -p ~/.local/bin && mv /tmp/cloudflared ~/.local/bin/cloudflared"
                ]
                
                for cmd in commands:
                    subprocess.run(cmd, shell=True, check=False)
                
                # Add ~/.local/bin to PATH if needed
                local_bin = os.path.expanduser("~/.local/bin")
                if local_bin not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = f"{local_bin}:{os.environ['PATH']}"
                
                return self.check_cloudflared_installed()
                
            elif system == "darwin":
                # Try homebrew first
                result = subprocess.run(["brew", "install", "cloudflared"], capture_output=True)
                if result.returncode != 0:
                    # Fallback to direct download
                    url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz"
                    subprocess.run(f"curl -L {url} | tar xz", shell=True)
                    subprocess.run("sudo mv cloudflared /usr/local/bin/", shell=True)
                
                return self.check_cloudflared_installed()
                
            elif system == "windows":
                print("⚠️  Please install cloudflared manually on Windows")
                print("   Download from: https://github.com/cloudflare/cloudflared/releases")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install cloudflared: {e}")
            return False

    def setup(self, jupyter_port):  # jupyter_port kept for compatibility
        """
        Setup and start tunnel with service token
        No login required!
        """
        print("🚀 Setting up Cloudflare tunnel with service token...")
        
        # Check if cloudflared is installed
        if not self.check_cloudflared_installed():
            print("cloudflared not found, attempting to install...")
            if not self.install_cloudflared():
                print("❌ Failed to install cloudflared. Please install it manually:")
                print("   https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")
                return None
        
        # Start tunnel with service token
        return self.start_tunnel_with_token()

    def start_tunnel_with_token(self):
        """
        Start the tunnel using service token
        This is much simpler than the credential file approach
        """
        try:
            print("🚀 Starting Cloudflare tunnel...")
            
            # Simple command with service token
            cmd = [
                "cloudflared",
                "tunnel",
                "--no-autoupdate",  # Prevent auto-updates during run
                "run",
                "--token",
                self.service_token
            ]
            
            # Start the tunnel process
            self.tunnel_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Wait for tunnel to establish
            print("⏳ Waiting for tunnel to connect...")
            time.sleep(5)
            
            # Check if process is still running
            if self.tunnel_process.poll() is None:
                print("✅ Tunnel is running!")
                print(f"📌 Jupyter URL: {self.jupyter_url}")
                print(f"📌 SSH URL: {self.ssh_url}")
                return self.tunnel_process
            else:
                # Read any error output
                output = self.tunnel_process.stdout.read()
                print("❌ Tunnel failed to start")
                print(f"Error output: {output}")
                return None
                
        except Exception as e:
            print(f"❌ Error starting tunnel: {e}")
            return None

    def stop(self):
        """Stop the tunnel if running"""
        if self.tunnel_process and self.tunnel_process.poll() is None:
            print("Stopping tunnel...")
            self.tunnel_process.terminate()
            self.tunnel_process.wait(timeout=5)
            print("Tunnel stopped")

    # Removed all the old methods that are no longer needed:
    # - login() - not needed with service token
    # - create_tunnel() - tunnel already exists
    # - configure_dns() - already configured
    # - create_config_file() - not needed with service token
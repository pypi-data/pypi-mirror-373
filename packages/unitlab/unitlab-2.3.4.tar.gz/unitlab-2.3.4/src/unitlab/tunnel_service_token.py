"""
Service Token implementation for Cloudflare Tunnel
More secure than embedding full credentials
"""

import os
import subprocess
import time
from pathlib import Path


class ServiceTokenTunnel:
    """
    Use Cloudflare Service Token instead of credentials file
    This is more secure and doesn't require login
    """
    
    # Embed the service token (generated once by admin)
    # This token can ONLY run the tunnel, cannot modify it
    DEFAULT_SERVICE_TOKEN = "eyJhIjoiYzkxMTkyYWUyMGE1ZDQzZjY1ZTA4NzU1MGQ4ZGM4OWIiLCJzIjoiZmdnSHowbFJFRnBHa05TZzIzV3JKMVBiaDVROGVUd0oyYWtJWThXdjhtTT0iLCJ0IjoiYjMzZGFhOGYtMmNjMy00Y2FkLWEyMjgtOTdlMDYwNzBlNjAwIn0="
    
    def __init__(self, device_id, service_token=None):
        self.device_id = device_id
        # Allow override via environment variable or parameter
        self.service_token = (
            service_token or 
            os.getenv("CLOUDFLARE_TUNNEL_TOKEN") or 
            self.DEFAULT_SERVICE_TOKEN
        )
        
        # With service token, we don't need credential files
        # The token contains all necessary information
        
    def start_tunnel_with_token(self):
        """
        Start tunnel using service token
        No login, no credential files needed
        """
        print("🚀 Starting tunnel with service token...")
        
        # Service token method - super simple!
        cmd = [
            "cloudflared", 
            "tunnel", 
            "run",
            "--token",
            self.service_token
        ]
        
        try:
            # Start the tunnel
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for tunnel to establish
            time.sleep(3)
            
            if process.poll() is None:
                print("✅ Tunnel running with service token")
                return process
            else:
                print("❌ Failed to start tunnel")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_tunnel_info(self):
        """
        Service tokens use predetermined URLs
        The admin sets these up when creating the tunnel
        """
        # These URLs are configured when creating the tunnel
        base_domain = "1scan.uz"
        return {
            "jupyter_url": f"https://jupyter-{self.device_id}.{base_domain}",
            "ssh_url": f"https://ssh-{self.device_id}.{base_domain}"
        }


# Usage example
def run_with_service_token(device_id):
    """
    Example of how simple it is with service token
    """
    tunnel = ServiceTokenTunnel(device_id)
    
    # No login needed!
    # No credential files needed!
    # Just run with the token
    process = tunnel.start_tunnel_with_token()
    
    if process:
        urls = tunnel.get_tunnel_info()
        print(f"Jupyter: {urls['jupyter_url']}")
        print(f"SSH: {urls['ssh_url']}")
        return process
    
    return None
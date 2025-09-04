"""
Cloudflare API-based Tunnel Configuration
Uses API to dynamically manage DNS and routes
"""

import os
import requests
import subprocess
import time
import logging
from pathlib import Path
from .binary_manager import CloudflaredBinaryManager

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv not installed, use system env vars only

logger = logging.getLogger(__name__)


class CloudflareAPITunnel:
    def __init__(self, base_domain, device_id):
        """
        Initialize API-based tunnel manager
        """
        self.base_domain = "1scan.uz"
        self.device_id = device_id
        
        # Clean device ID for subdomain
        self.clean_device_id = device_id.replace('-', '').replace('_', '').lower()[:20]
        
        # Cloudflare IDs (hardcoded for now, can move to env vars)
        self.zone_id = "78182c3883adad79d8f1026851a68176"
        self.account_id = "c91192ae20a5d43f65e087550d8dc89b"
        self.tunnel_id = "0777fc10-49c4-472d-8661-f60d80d6184d"  # unitlab-agent tunnel
        
        # API token from environment
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        if not self.api_token:
            logger.warning("CLOUDFLARE_API_TOKEN not set. API features will be disabled.")
        
        # API setup
        self.api_base = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        } if self.api_token else {}
        
        # URLs for services
        self.jupyter_subdomain = f"j{self.clean_device_id}"
        self.ssh_subdomain = f"s{self.clean_device_id}"
        self.jupyter_url = f"https://{self.jupyter_subdomain}.{self.base_domain}"
        self.ssh_hostname = f"{self.ssh_subdomain}.{self.base_domain}"
        self.ssh_url = self.ssh_hostname  # For backward compatibility
        
        self.tunnel_process = None
        self.created_dns_records = []
        self.binary_manager = CloudflaredBinaryManager()

    def create_dns_records(self):
        """
        Create DNS CNAME records for this device
        """
        if not self.api_token:
            print("⚠️  No API token configured. Skipping DNS creation.")
            print("   Assuming DNS records already exist or will be created manually.")
            return True
        
        print(f"📡 Creating DNS records for device {self.device_id}...")
        
        records = [
            {"name": self.jupyter_subdomain, "comment": f"Jupyter for {self.device_id}"},
            {"name": self.ssh_subdomain, "comment": f"SSH for {self.device_id}"}
        ]
        
        for record in records:
            try:
                # Check if record exists
                check_url = f"{self.api_base}/zones/{self.zone_id}/dns_records"
                params = {"name": f"{record['name']}.{self.base_domain}", "type": "CNAME"}
                
                response = requests.get(check_url, headers=self.headers, params=params)
                existing = response.json()
                
                if existing.get("result") and len(existing["result"]) > 0:
                    # Record exists
                    print(f"   ✓ DNS record {record['name']}.{self.base_domain} already exists")
                    continue
                
                # Create new record
                data = {
                    "type": "CNAME",
                    "name": record["name"],
                    "content": f"{self.tunnel_id}.cfargotunnel.com",
                    "ttl": 1,  # Auto
                    "proxied": True,
                    "comment": record["comment"]
                }
                
                response = requests.post(check_url, headers=self.headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print(f"   ✅ Created DNS: {record['name']}.{self.base_domain}")
                        self.created_dns_records.append(result["result"]["id"])
                    else:
                        print(f"   ⚠️  Failed to create {record['name']}: {result.get('errors')}")
                else:
                    print(f"   ❌ HTTP error {response.status_code} for {record['name']}")
                    
            except Exception as e:
                print(f"   ❌ Error creating DNS record: {e}")
                continue
        
        return True

    def update_tunnel_config(self, jupyter_port=8888, ssh_port=22):
        """
        Update tunnel configuration via API
        """
        if not self.api_token:
            print("⚠️  No API token. Tunnel will use existing configuration.")
            return True
        
        print(f"🔧 Configuring tunnel routes...")
        
        # Get current tunnel config first
        get_url = f"{self.api_base}/accounts/{self.account_id}/cfd_tunnel/{self.tunnel_id}/configurations"
        
        try:
            # Get existing config
            response = requests.get(get_url, headers=self.headers)
            current_config = response.json()
            
            # Build new ingress rules
            new_ingress = [
                {
                    "hostname": f"{self.jupyter_subdomain}.{self.base_domain}",
                    "service": f"http://localhost:{jupyter_port}",
                    "originRequest": {
                        "noTLSVerify": True
                    }
                },
                {
                    "hostname": f"{self.ssh_subdomain}.{self.base_domain}",
                    "service": f"ssh://localhost:{ssh_port}"
                }
            ]
            
            # Merge with existing ingress if any
            if current_config.get("success") and current_config.get("result"):
                existing_ingress = current_config["result"].get("config", {}).get("ingress", [])
                
                # Filter out our hostnames from existing
                filtered_ingress = [
                    rule for rule in existing_ingress
                    if rule.get("hostname") not in [
                        f"{self.jupyter_subdomain}.{self.base_domain}",
                        f"{self.ssh_subdomain}.{self.base_domain}"
                    ] and rule.get("service") != "http_status:404"
                ]
                
                # Combine
                new_ingress = new_ingress + filtered_ingress
            
            # Add catch-all at the end
            new_ingress.append({"service": "http_status:404"})
            
            # Update configuration
            config_data = {
                "config": {
                    "ingress": new_ingress
                }
            }
            
            put_url = f"{self.api_base}/accounts/{self.account_id}/cfd_tunnel/{self.tunnel_id}/configurations"
            response = requests.put(put_url, headers=self.headers, json=config_data)
            
            if response.status_code == 200:
                print(f"   ✅ Tunnel routes configured")
                return True
            else:
                print(f"   ⚠️  Route configuration status: {response.status_code}")
                # Continue anyway - routes might be configured manually
                return True
                
        except Exception as e:
            print(f"   ⚠️  Could not update routes via API: {e}")
            print("   Assuming routes are configured in dashboard.")
            return True

    def start_tunnel_with_token(self):
        """
        Start tunnel using the existing service token
        """
        try:
            print("🚀 Starting Cloudflare tunnel...")
            
            # First, try to set up DNS and routes via API
            if self.api_token:
                self.create_dns_records()
                self.update_tunnel_config()
            
            # Get cloudflared binary
            cloudflared_path = self.binary_manager.get_binary_path()
            
            # Use the existing service token from environment
            service_token = os.getenv(
                "CLOUDFLARE_TUNNEL_TOKEN",
                "eyJhIjoiYzkxMTkyYWUyMGE1ZDQzZjY1ZTA4NzU1MGQ4ZGM4OWIiLCJ0IjoiMDc3N2ZjMTAtNDljNC00NzJkLTg2NjEtZjYwZDgwZDYxODRkIiwicyI6Ik9XRTNaak5tTVdVdE1tWTRaUzAwTmpoakxUazBaalF0WXpjek1tSm1ZVGt4WlRRMCJ9"
            )
            
            # Start tunnel with service token
            cmd = [
                cloudflared_path,
                "tunnel",
                "--no-autoupdate",
                "run",
                "--token",
                service_token
            ]
            
            self.tunnel_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            print("⏳ Waiting for tunnel to connect...")
            time.sleep(5)
            
            if self.tunnel_process.poll() is None:
                print("✅ Tunnel is running!")
                print(f"📌 Device ID: {self.clean_device_id}")
                print(f"📌 Jupyter URL: {self.jupyter_url}")
                print(f"📌 SSH hostname: {self.ssh_hostname}")
                print(f"📌 SSH command: ssh -o ProxyCommand='cloudflared access ssh --hostname {self.ssh_hostname}' user@localhost")
                return self.tunnel_process
            else:
                output = self.tunnel_process.stdout.read() if self.tunnel_process.stdout else ""
                print(f"❌ Tunnel failed to start: {output}")
                return None
                
        except Exception as e:
            print(f"❌ Error starting tunnel: {e}")
            return None

    def setup(self, jupyter_port=8888):
        """
        Setup and start tunnel (maintains compatibility)
        """
        return self.start_tunnel_with_token()

    def stop(self):
        """
        Stop the tunnel if running
        """
        if self.tunnel_process and self.tunnel_process.poll() is None:
            print("Stopping tunnel...")
            self.tunnel_process.terminate()
            self.tunnel_process.wait(timeout=5)
            print("Tunnel stopped")

    def cleanup_dns(self):
        """
        Remove created DNS records (optional cleanup)
        """
        if not self.api_token or not self.created_dns_records:
            return
        
        print("🧹 Cleaning up DNS records...")
        for record_id in self.created_dns_records:
            try:
                url = f"{self.api_base}/zones/{self.zone_id}/dns_records/{record_id}"
                requests.delete(url, headers=self.headers)
                print(f"   Deleted record {record_id}")
            except:
                pass
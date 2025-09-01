"""
XCP-ng XAPI Client for VM lifecycle management
Handles authentication and REST API communication with XCP-ng hosts
"""

import requests
import json
import time
import urllib3
from urllib.parse import urljoin
from typing import Dict, List, Optional, Any

from .exceptions import VMManagerError, XCPngConnectionError

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XAPIClient:
    """Client for XCP-ng XAPI REST communication"""
    
    def __init__(self, host: str, username: str, password: str, verify_ssl: bool = False):
        """Initialize XAPI client
        
        Args:
            host: XCP-ng host IP or hostname
            username: XCP-ng username
            password: XCP-ng password  
            verify_ssl: Whether to verify SSL certificates
        """
        self.host = host
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session_id = None
        self.base_url = f"https://{host}"
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.verify = verify_ssl
        
        # Common headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def authenticate(self) -> bool:
        """Authenticate with XCP-ng and obtain session ID
        
        Returns:
            bool: True if authentication successful
            
        Raises:
            XCPngConnectionError: If authentication fails
        """
        try:
            auth_url = urljoin(self.base_url, "/api/session")
            auth_data = {
                "username": self.username,
                "password": self.password
            }
            
            response = self.session.post(auth_url, json=auth_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                self.session_id = result.get('session_id')
                
                # Add session ID to headers for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.session_id}'
                })
                
                return True
            else:
                raise XCPngConnectionError(
                    f"Authentication failed: {response.status_code} - {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            raise XCPngConnectionError(f"Failed to connect to XCP-ng host: {e}")
        except Exception as e:
            raise XCPngConnectionError(f"Authentication error: {e}")
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List available VM templates
        
        Returns:
            List of template dictionaries
            
        Raises:
            XCPngConnectionError: If API call fails
        """
        self._ensure_authenticated()
        
        try:
            url = urljoin(self.base_url, "/api/templates")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('templates', [])
            else:
                raise XCPngConnectionError(
                    f"Failed to list templates: {response.status_code} - {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            raise XCPngConnectionError(f"Failed to list templates: {e}")
    
    def find_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Find template by name
        
        Args:
            template_name: Name of template to find
            
        Returns:
            Template dictionary or None if not found
        """
        templates = self.list_templates()
        
        for template in templates:
            if template.get('name') == template_name:
                return template
                
        return None
    
    def create_vm_from_template(self, vm_name: str, template_name: str, 
                               config: Optional[Dict[str, Any]] = None) -> str:
        """Create VM from template
        
        Args:
            vm_name: Name for new VM
            template_name: Name of template to use
            config: Additional VM configuration
            
        Returns:
            VM UUID
            
        Raises:
            VMManagerError: If VM creation fails
        """
        self._ensure_authenticated()
        
        # Find template
        template = self.find_template(template_name)
        if not template:
            raise VMManagerError(f"Template not found: {template_name}")
        
        try:
            url = urljoin(self.base_url, "/api/vms")
            vm_data = {
                "name": vm_name,
                "template_uuid": template['uuid'],
                "config": config or {}
            }
            
            response = self.session.post(url, json=vm_data, timeout=60)
            
            if response.status_code == 201:
                result = response.json()
                return result.get('vm_uuid')
            else:
                raise VMManagerError(
                    f"Failed to create VM: {response.status_code} - {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            raise VMManagerError(f"Failed to create VM: {e}")
    
    def start_vm(self, vm_uuid: str) -> bool:
        """Start VM
        
        Args:
            vm_uuid: UUID of VM to start
            
        Returns:
            bool: True if started successfully
            
        Raises:
            VMManagerError: If VM start fails
        """
        self._ensure_authenticated()
        
        try:
            url = urljoin(self.base_url, f"/api/vms/{vm_uuid}/start")
            response = self.session.post(url, timeout=60)
            
            if response.status_code == 200:
                # Wait for VM to be running
                return self._wait_for_vm_state(vm_uuid, "running", timeout=120)
            else:
                raise VMManagerError(
                    f"Failed to start VM: {response.status_code} - {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            raise VMManagerError(f"Failed to start VM: {e}")
    
    def stop_vm(self, vm_uuid: str) -> bool:
        """Stop VM
        
        Args:
            vm_uuid: UUID of VM to stop
            
        Returns:
            bool: True if stopped successfully
        """
        self._ensure_authenticated()
        
        try:
            url = urljoin(self.base_url, f"/api/vms/{vm_uuid}/stop")
            response = self.session.post(url, timeout=60)
            
            if response.status_code == 200:
                return self._wait_for_vm_state(vm_uuid, "halted", timeout=60)
            else:
                raise VMManagerError(
                    f"Failed to stop VM: {response.status_code} - {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            raise VMManagerError(f"Failed to stop VM: {e}")
    
    def get_vm_info(self, vm_uuid: str) -> Dict[str, Any]:
        """Get VM information
        
        Args:
            vm_uuid: UUID of VM
            
        Returns:
            VM information dictionary
        """
        self._ensure_authenticated()
        
        try:
            url = urljoin(self.base_url, f"/api/vms/{vm_uuid}")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise VMManagerError(
                    f"Failed to get VM info: {response.status_code} - {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            raise VMManagerError(f"Failed to get VM info: {e}")
    
    def get_vm_network_info(self, vm_uuid: str) -> Dict[str, str]:
        """Get VM network information including IP address
        
        Args:
            vm_uuid: UUID of VM
            
        Returns:
            Dictionary with network info including 'ip_address'
        """
        vm_info = self.get_vm_info(vm_uuid)
        
        # Extract network information
        network_info = {}
        vifs = vm_info.get('VIFs', [])
        
        for vif in vifs:
            if vif.get('currently_attached'):
                # Get IP from guest metrics if available
                guest_metrics = vm_info.get('guest_metrics', {})
                networks = guest_metrics.get('networks', {})
                
                for device, ip in networks.items():
                    if ip and not ip.startswith('127.'):
                        network_info['ip_address'] = ip
                        network_info['device'] = device
                        break
        
        return network_info
    
    def delete_vm(self, vm_uuid: str) -> bool:
        """Delete VM
        
        Args:
            vm_uuid: UUID of VM to delete
            
        Returns:
            bool: True if deleted successfully
        """
        self._ensure_authenticated()
        
        try:
            # Stop VM first if running
            vm_info = self.get_vm_info(vm_uuid)
            if vm_info.get('power_state') == 'Running':
                self.stop_vm(vm_uuid)
            
            # Delete VM
            url = urljoin(self.base_url, f"/api/vms/{vm_uuid}")
            response = self.session.delete(url, timeout=30)
            
            return response.status_code == 204
                
        except requests.exceptions.RequestException as e:
            raise VMManagerError(f"Failed to delete VM: {e}")
    
    def _ensure_authenticated(self):
        """Ensure we have a valid session"""
        if not self.session_id:
            self.authenticate()
    
    def _wait_for_vm_state(self, vm_uuid: str, target_state: str, timeout: int = 60) -> bool:
        """Wait for VM to reach target state
        
        Args:
            vm_uuid: UUID of VM
            target_state: Target power state
            timeout: Timeout in seconds
            
        Returns:
            bool: True if state reached, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                vm_info = self.get_vm_info(vm_uuid)
                current_state = vm_info.get('power_state', '').lower()
                
                if current_state == target_state.lower():
                    return True
                    
                time.sleep(2)
                
            except Exception:
                time.sleep(2)
                continue
        
        return False
    
    def disconnect(self):
        """Clean up session"""
        if self.session_id:
            try:
                logout_url = urljoin(self.base_url, "/api/session/logout")
                self.session.post(logout_url, timeout=10)
            except:
                pass  # Ignore logout errors
            finally:
                self.session_id = None
                self.session.close()

"""
Networking functionality for Lua VM socket communication.

This module provides templates and utilities for creating networked Lua VMs
that can communicate via sockets using LuaSocket, enhanced with intelligent
package curation for AGI bootstrapping.
"""

from typing import Optional, Dict, Any, List
from pylua_bioxen_vm_lib.lua_process import LuaProcess
from pylua_bioxen_vm_lib.exceptions import NetworkingError, VMConnectionError, LuaSocketNotFoundError
from pylua_bioxen_vm_lib.logger import VMLogger


class NetworkedLuaVM(LuaProcess):
    """
    Lua VM with built-in networking capabilities using LuaSocket.
    
    Extends LuaProcess with methods for server, client, and P2P communication modes,
    enhanced with curator-based package management for intelligent network setups.
    """
    
    def __init__(self, name: str = "NetworkedLuaVM", lua_executable: str = "lua", debug_mode: bool = False):
        super().__init__(name=name, lua_executable=lua_executable, debug_mode=debug_mode)
        self.logger = VMLogger(debug_mode=debug_mode, component="NetworkedLuaVM")
        self._networking_packages_verified = False
        # Note: LuaSocket verification is deferred until first network operation
    
    # --- Enhanced Curator Integration for Networking ---
    
    def setup_networking_packages(self, include_advanced: bool = False) -> Dict[str, Any]:
        """
        Setup networking-specific packages using curator with optional advanced packages.
        
        Args:
            include_advanced: Include advanced networking packages like HTTP client libraries
            
        Returns:
            Dict with setup results and networking package information
        """
        self.logger.debug(f"Setting up networking packages (include_advanced={include_advanced})")
        
        try:
            # Initialize curator if not already done
            if self._curator is None:
                from pylua_bioxen_vm_lib.utils.curator import Curator
                self._curator = Curator()
                self.logger.debug("Curator initialized for networking setup")
            
            # Define networking packages to install
            networking_packages = ['luasocket']  # Core networking
            
            if include_advanced:
                networking_packages.extend(['http', 'json', 'lpeg'])  # Advanced networking tools
            
            # Install each networking package
            installed_packages = []
            failed_packages = []
            
            for package_name in networking_packages:
                self.logger.debug(f"Installing networking package: {package_name}")
                result = self._curator.install_package(package_name)
                
                if result.get('success', False):
                    installed_packages.append({
                        'package': package_name,
                        'version': result.get('installed_version', 'unknown'),
                        'dependencies': result.get('dependencies', [])
                    })
                else:
                    failed_packages.append({
                        'package': package_name,
                        'error': result.get('error', 'Unknown error')
                    })
            
            # Update networking packages verification status
            self._networking_packages_verified = len(installed_packages) > 0
            
            setup_info = {
                'success': len(failed_packages) == 0,
                'packages_requested': networking_packages,
                'packages_installed': installed_packages,
                'failed_packages': failed_packages,
                'networking_ready': self._networking_packages_verified,
                'advanced_features': include_advanced
            }
            
            if setup_info['success']:
                self.logger.debug(f"Networking setup completed successfully: {len(installed_packages)} packages installed")
            else:
                self.logger.debug(f"Networking setup had issues: {len(failed_packages)} packages failed")
                
            return setup_info
            
        except Exception as e:
            self.logger.debug(f"Networking package setup failed with exception: {e}")
            return {
                'success': False,
                'error': str(e),
                'networking_ready': False,
                'packages_installed': [],
                'failed_packages': []
            }
    
    def get_networking_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get curator recommendations specifically for networking packages.
        
        Returns:
            List of networking-focused recommendations
        """
        self.logger.debug("Getting networking-specific package recommendations")
        
        try:
            # Get general recommendations first
            all_recommendations = self.get_package_recommendations()
            
            # Filter for networking-related packages
            networking_keywords = ['socket', 'http', 'network', 'tcp', 'udp', 'json', 'xml', 'curl', 'ssl', 'tls']
            networking_recommendations = []
            
            for rec in all_recommendations:
                package_name = rec.get('package', '').lower()
                description = rec.get('description', '').lower()
                
                # Check if package is networking-related
                if any(keyword in package_name or keyword in description for keyword in networking_keywords):
                    # Enhance with networking-specific rationale
                    enhanced_rec = rec.copy()
                    enhanced_rec['networking_category'] = self._categorize_networking_package(package_name)
                    networking_recommendations.append(enhanced_rec)
            
            # Add default networking recommendations if none found
            if not networking_recommendations and not self._networking_packages_verified:
                networking_recommendations.append({
                    'package': 'luasocket',
                    'priority': 'high',
                    'networking_category': 'core',
                    'rationale': 'Essential TCP/UDP socket communication for networked VMs',
                    'estimated_benefit': 'Critical for any network functionality'
                })
                
                networking_recommendations.append({
                    'package': 'http',
                    'priority': 'medium',
                    'networking_category': 'web',
                    'rationale': 'HTTP client capabilities for web service integration',
                    'estimated_benefit': 'Enables REST API communication and web scraping'
                })
            
            self.logger.debug(f"Found {len(networking_recommendations)} networking-specific recommendations")
            return networking_recommendations
            
        except Exception as e:
            self.logger.debug(f"Failed to get networking recommendations: {e}")
            return []
    
    def _categorize_networking_package(self, package_name: str) -> str:
        """Categorize a networking package for better organization."""
        package_name = package_name.lower()
        
        if 'socket' in package_name:
            return 'core'
        elif 'http' in package_name or 'curl' in package_name:
            return 'web'
        elif 'json' in package_name or 'xml' in package_name:
            return 'data'
        elif 'ssl' in package_name or 'tls' in package_name:
            return 'security'
        else:
            return 'utility'
    
    def check_networking_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive networking health check including package verification.
        
        Returns:
            Dict with networking health status and diagnostics
        """
        self.logger.debug("Performing comprehensive networking health check")
        
        try:
            # Get base health check from parent
            base_health = self.check_environment_health()
            
            # Add networking-specific checks
            networking_health = {
                'luasocket_available': False,
                'http_available': False,
                'json_available': False,
                'networking_packages_verified': self._networking_packages_verified,
                'network_connectivity_tests': {},
                'recommended_networking_packages': []
            }
            
            # Test LuaSocket availability
            try:
                luasocket_result = self.execute_string('require("socket"); print("LuaSocket OK")', timeout=3)
                networking_health['luasocket_available'] = (
                    luasocket_result['success'] and 'LuaSocket OK' in luasocket_result['stdout']
                )
            except Exception as e:
                self.logger.debug(f"LuaSocket test failed: {e}")
                networking_health['luasocket_available'] = False
            
            # Test HTTP library availability
            try:
                http_result = self.execute_string('require("http"); print("HTTP OK")', timeout=3)
                networking_health['http_available'] = (
                    http_result['success'] and 'HTTP OK' in http_result['stdout']
                )
            except Exception as e:
                self.logger.debug(f"HTTP library test failed: {e}")
                networking_health['http_available'] = False
            
            # Test JSON library availability
            try:
                json_result = self.execute_string('local json = require("json"); print("JSON OK")', timeout=3)
                networking_health['json_available'] = (
                    json_result['success'] and 'JSON OK' in json_result['stdout']
                )
            except Exception as e:
                self.logger.debug(f"JSON library test failed: {e}")
                networking_health['json_available'] = False
            
            # Get networking recommendations if packages are missing
            if not all([networking_health['luasocket_available'], networking_health['http_available']]):
                networking_health['recommended_networking_packages'] = self.get_networking_recommendations()
            
            # Calculate overall networking readiness
            essential_packages = [networking_health['luasocket_available']]
            networking_readiness = sum(essential_packages) / len(essential_packages) * 100
            
            networking_health['networking_readiness_percentage'] = networking_readiness
            networking_health['is_network_ready'] = networking_readiness >= 100
            
            # Combine with base health
            combined_health = base_health.copy()
            combined_health['networking'] = networking_health
            combined_health['overall_networking_health'] = 'excellent' if networking_readiness >= 100 else 'needs_packages'
            
            self.logger.debug(f"Networking health check completed: readiness={networking_readiness}%")
            
            return combined_health
            
        except Exception as e:
            self.logger.debug(f"Networking health check failed with exception: {e}")
            base_health = self.check_environment_health()
            base_health['networking'] = {
                'error': str(e),
                'networking_readiness_percentage': 0,
                'is_network_ready': False
            }
            base_health['overall_networking_health'] = 'error'
            return base_health

    # --- Core Networking Methods with Enhanced Error Handling ---
    
    def _verify_luasocket(self) -> None:
        """Check if LuaSocket is available, with helpful curator suggestions."""
        self.logger.debug("Verifying LuaSocket availability")
        test_code = 'require("socket"); print("LuaSocket available")'
        result = self.execute_string(test_code, timeout=5)
        
        if not result['success'] or "LuaSocket available" not in result['stdout']:
            # Try to get curator recommendations
            recommendations_msg = ""
            try:
                if self._curator:
                    networking_recs = self.get_networking_recommendations()
                    if networking_recs:
                        recommendations_msg = f"\n\nCurator recommendations:\n"
                        for rec in networking_recs[:3]:  # Show top 3
                            recommendations_msg += f"- {rec['package']}: {rec.get('rationale', 'Networking package')}\n"
                        recommendations_msg += "\nUse vm.setup_networking_packages() for automatic installation."
            except Exception:
                pass  # Ignore curator errors during error handling
            
            raise LuaSocketNotFoundError(
                f"LuaSocket not found. Install with: luarocks install luasocket{recommendations_msg}"
            )
        
        self._networking_packages_verified = True
    
    def start_server(self, port: int, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Start a Lua socket server that accepts one client connection.
        
        Args:
            port: Port number to bind to (1024-65535)
            timeout: Maximum execution time in seconds
            
        Returns:
            Execution result dict
        """
        if not (1024 <= port <= 65535):
            raise ValueError("Port must be between 1024 and 65535")
        
        # Verify networking packages before starting server
        self._verify_luasocket()
        
        self.logger.debug(f"Starting server on port {port} with timeout {timeout}")
        
        server_code = f"""
        local socket = require("socket")
        local server = socket.bind("*", {port})
        if not server then
            io.stderr:write("Lua Server: Failed to bind to port {port}\\n")
            os.exit(1)
        end
        print("Lua Server: Listening on port {port}...")
        local client = server:accept()
        print("Lua Server: Client connected from " .. client:getpeername())
        client:send("Hello from Lua Server! What's your message?\\n")
        local data, err = client:receive()
        if data then
            print("Lua Server: Received from client: " .. data)
        else
            io.stderr:write("Lua Server: Error receiving data or client disconnected: " .. tostring(err) .. "\\n")
        end
        client:close()
        server:close()
        print("Lua Server: Connection closed.")
        """
        
        return self.execute_temp_script(server_code, timeout=timeout)
    
    def start_client(self, host: str, port: int, message: str = "Hello from Lua Client!", 
                    timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Start a Lua socket client that connects to a server.
        
        Args:
            host: Server hostname or IP address
            port: Server port number
            message: Message to send to server
            timeout: Maximum execution time in seconds
            
        Returns:
            Execution result dict
        """
        if not (1024 <= port <= 65535):
            raise ValueError("Port must be between 1024 and 65535")
        
        if not host.strip():
            raise ValueError("Host cannot be empty")
        
        # Verify networking packages before starting client
        self._verify_luasocket()
        
        self.logger.debug(f"Starting client connection to {host}:{port} with timeout {timeout}")
        
        # Escape the message for Lua string
        escaped_message = message.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        
        client_code = f"""
        local socket = require("socket")
        local client, err = socket.connect("{host}", {port})
        if not client then
            io.stderr:write("Lua Client: Failed to connect to {host}:{port}: " .. tostring(err) .. "\\n")
            os.exit(1)
        end
        print("Lua Client: Connected to server at {host}:{port}")
        local response, err_recv = client:receive()
        if response then
            print("Lua Client: Received from server: " .. response)
        else
            io.stderr:write("Lua Client: Error receiving initial message from server: " .. tostring(err_recv) .. "\\n")
        end
        client:send("{escaped_message}\\n")
        print("Lua Client: Sent message: '{escaped_message}'")
        client:close()
        print("Lua Client: Connection closed.")
        """
        
        return self.execute_temp_script(client_code, timeout=timeout)
    
    def start_p2p(self, local_port: int, peer_host: Optional[str] = None, 
                  peer_port: Optional[int] = None, run_duration: int = 30,
                  send_interval: int = 5, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Start a P2P Lua VM that both listens for connections and can connect to peers.
        
        Args:
            local_port: Port to listen on for incoming connections
            peer_host: Optional peer hostname/IP to connect to
            peer_port: Optional peer port to connect to
            run_duration: How long to run the P2P VM (seconds)
            send_interval: How often to send heartbeat messages (seconds)
            timeout: Maximum execution time in seconds
            
        Returns:
            Execution result dict
        """
        if not (1024 <= local_port <= 65535):
            raise ValueError("Local port must be between 1024 and 65535")
        
        if peer_port is not None and not (1024 <= peer_port <= 65535):
            raise ValueError("Peer port must be between 1024 and 65535")
        
        # Verify networking packages before starting P2P
        self._verify_luasocket()
        
        self.logger.debug(f"Starting P2P VM on port {local_port} (peer: {peer_host}:{peer_port})")
        
        # Generate peer connection code if peer specified
        peer_connect_code = ""
        if peer_host and peer_port:
            peer_connect_code = f"""
            local peer_client, peer_err = socket.connect("{peer_host}", {peer_port})
            if peer_client then
                peer_client:settimeout(0.1) -- Non-blocking for peer client
                print("P2P VM: Connected to peer at {peer_host}:{peer_port}")
                table.insert(sockets_to_monitor, peer_client)
                peer_client:send("Hello from P2P VM on port {local_port}!\\n")
            else
                io.stderr:write("P2P VM: Failed to connect to peer {peer_host}:{peer_port}: " .. tostring(peer_err) .. "\\n")
            end
            """
        
        p2p_code = f"""
        local socket = require("socket")

        local local_port = {local_port}
        local server_socket = socket.bind("*", local_port)
        if not server_socket then
            io.stderr:write("P2P VM: Failed to bind to local port " .. local_port .. "\\n")
            os.exit(1)
        end
        server_socket:settimeout(0.1) -- Non-blocking for server socket
        print("P2P VM: Listening on local port " .. local_port .. "...")

        local sockets_to_monitor = {{server_socket}}
        local connected_peers = {{}} -- To store active client connections

        {peer_connect_code}

        local last_send_time = os.clock()
        local send_interval = {send_interval}

        local run_duration = {run_duration}
        local start_time = os.clock()

        while os.clock() - start_time < run_duration do
            local readable_sockets, writable_sockets, err = socket.select(sockets_to_monitor, nil, 0.1)

            if err then
                io.stderr:write("P2P VM: socket.select error: " .. tostring(err) .. "\\n")
                break
            end

            for i, sock in ipairs(readable_sockets) do
                if sock == server_socket then
                    -- New incoming connection (server role)
                    local new_client = server_socket:accept()
                    if new_client then
                        new_client:settimeout(0.1) -- Non-blocking for new client
                        local peer_ip, peer_port = new_client:getpeername()
                        print("P2P VM: Accepted connection from " .. peer_ip .. ":" .. peer_port)
                        table.insert(sockets_to_monitor, new_client)
                        connected_peers[new_client] = true
                        new_client:send("Welcome to P2P VM on port " .. local_port .. "!\\n")
                    else
                        io.stderr:write("P2P VM: Error accepting new client: " .. tostring(new_client) .. "\\n")
                    end
                else
                    -- Data from an existing connection
                    local data, recv_err, partial = sock:receive()
                    if data then
                        print("P2P VM: Received from " .. sock:getpeername() .. ": " .. data)
                    elseif recv_err == "timeout" then
                        -- No data, just a timeout, continue
                    else
                        -- Connection closed or error
                        print("P2P VM: Connection from " .. sock:getpeername() .. " closed or error: " .. tostring(recv_err))
                        sock:close()
                        -- Remove socket from monitoring list
                        for k, v in ipairs(sockets_to_monitor) do
                            if v == sock then
                                table.remove(sockets_to_monitor, k)
                                break
                            end
                        end
                        connected_peers[sock] = nil
                    end
                end
            end

            -- Send periodic messages to connected peers
            if os.clock() - last_send_time > send_interval then
                for sock in pairs(connected_peers) do
                    local success, send_err = sock:send("P2P VM " .. local_port .. ": Heartbeat at " .. os.clock() .. "\\n")
                    if not success then
                        io.stderr:write("P2P VM: Error sending to " .. sock:getpeername() .. ": " .. tostring(send_err) .. "\\n")
                    end
                end
                last_send_time = os.clock()
            end
        end

        print("P2P VM: Shutting down after " .. run_duration .. " seconds.")
        for sock in pairs(connected_peers) do
            sock:close()
        end
        server_socket:close()
        """
        
        return self.execute_temp_script(p2p_code, timeout=timeout)


def validate_port(port: int) -> None:
    """Validate that a port number is in the valid range."""
    if not (1024 <= port <= 65535):
        raise ValueError("Port must be between 1024 and 65535")


def validate_host(host: str) -> None:
    """Basic validation for host string."""
    if not host or not host.strip():
        raise ValueError("Host cannot be empty")


class LuaScriptTemplate:
    """
    Utility class for generating common Lua networking script patterns.
    Enhanced with curator-aware package usage.
    """
    
    @staticmethod
    def simple_echo_server(port: int) -> str:
        """Generate a simple echo server script."""
        return f"""
        local socket = require("socket")
        local server = socket.bind("*", {port})
        server:listen(5)
        print("Echo server listening on port {port}")
        
        while true do
            local client = server:accept()
            local line, err = client:receive()
            if line then
                client:send("Echo: " .. line .. "\\n")
            end
            client:close()
        end
        """
    
    @staticmethod  
    def heartbeat_client(host: str, port: int, interval: int = 1, count: int = 10) -> str:
        """Generate a heartbeat client script."""
        return f"""
        local socket = require("socket")
        local client = socket.connect("{host}", {port})
        
        for i = 1, {count} do
            client:send("Heartbeat " .. i .. "\\n")
            local response = client:receive()
            print("Received: " .. (response or "nil"))
            socket.sleep({interval})
        end
        
        client:close()
        """
    
    @staticmethod
    def http_client_template(url: str, method: str = "GET") -> str:
        """Generate an HTTP client script template (requires http library)."""
        return f"""
        local http = require("http")
        local json = require("json") or require("cjson") or nil
        
        print("Making {method} request to {url}")
        
        local response, status = http.request("{url}")
        
        if response then
            print("HTTP Status: " .. (status or "unknown"))
            print("Response:")
            print(response)
            
            -- Try to parse as JSON if possible
            if json and status == 200 then
                local success, parsed = pcall(json.decode, response)
                if success then
                    print("Parsed JSON:")
                    for k, v in pairs(parsed) do
                        print("  " .. k .. ": " .. tostring(v))
                    end
                end
            end
        else
            print("HTTP request failed: " .. (status or "unknown error"))
        end
        """
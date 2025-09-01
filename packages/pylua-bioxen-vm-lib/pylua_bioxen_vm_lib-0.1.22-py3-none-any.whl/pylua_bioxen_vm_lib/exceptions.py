"""
Custom exceptions for pylua_bioxen_vm_lib library.
"""

class LuaVMError(Exception):
    """Base exception for all Lua VM related errors."""
    pass

class LuaProcessError(LuaVMError):
    """Raised when there's an error with Lua subprocess execution."""
    def __init__(self, message, return_code=None, stderr=None):
        super().__init__(message)
        self.return_code = return_code
        self.stderr = stderr

class NetworkingError(LuaVMError):
    """Raised for networking-related errors in Lua VMs."""
    pass

class LuaNotFoundError(LuaVMError):
    """Raised when the Lua interpreter is not found."""
    pass


class PTYError(LuaVMError):
    """Raised when there's an error with PTY (pseudo-terminal) operations."""
    pass

class LuaSocketNotFoundError(LuaVMError):
    """Raised when LuaSocket is not available."""
    pass

class VMConnectionError(LuaVMError):
    """Raised when a VM connection fails."""
    pass

class VMTimeoutError(LuaVMError):
    """Raised when a VM operation times out."""
    pass

class ScriptGenerationError(LuaVMError):
    """Raised when there's an error generating dynamic Lua scripts."""
    pass

class InteractiveSessionError(LuaVMError):
    """Raised for errors in interactive session management."""
    pass

class AttachError(InteractiveSessionError):
    """Raised when attaching to a session fails."""
    pass

class XCPngConnectionError(LuaVMError):
    """Raised when XCP-ng connection or authentication fails."""
    pass

class SessionNotFoundError(InteractiveSessionError):
    """Raised when a requested session is not found."""
    pass
    pass

class DetachError(InteractiveSessionError):
    """Raised when detaching from a session fails."""
    pass

class SessionNotFoundError(InteractiveSessionError):
    """Raised when trying to access a session that doesn't exist."""
    pass



class IOThreadError(InteractiveSessionError):
    """Raised when there's an error with I/O threading operations."""
    pass

class SessionStateError(InteractiveSessionError):
    """Raised when there's an error with session state management."""
    pass

class SessionAlreadyExistsError(InteractiveSessionError):
    """Raised when trying to create a session with an ID that already exists."""
    pass

class VMManagerError(LuaVMError):
    """Raised when there's an error with VM manager operations."""
    pass

class ProcessRegistryError(VMManagerError):
    """Raised when there's an error with the persistent VM registry."""
    pass

# Test 5: Interactive Session Lifecycle
print("\n5. Testing Interactive Session Lifecycle")
try:
    manager = VMManager()
    vm_id = "interactive_test_vm"
    
    # Create interactive session
    session = manager.create_interactive_vm(vm_id)
    print("✅ Interactive VM created")
    
    # Send commands and read output
    manager.send_input(vm_id, "x = 42\n")
    manager.send_input(vm_id, "print('The answer is:', x)\n")
    time.sleep(0.1)  # Brief pause for execution
    output = manager.read_output(vm_id)
    
    if "The answer is: 42" in output:
        print("✅ Interactive I/O:", "Commands executed successfully")
    else:
        print("⚠️ Interactive I/O: Unexpected output:", output)
    
    # Test session persistence
    manager.send_input(vm_id, "y = x * 2\n")
    manager.send_input(vm_id, "print('Double is:', y)\n")
    time.sleep(0.1)
    output2 = manager.read_output(vm_id)
    
    if "Double is: 84" in output2:
        print("✅ Session Persistence: Variables maintained between commands")
    else:
        print("⚠️ Session Persistence: Variables not maintained")
    
    # Detach and terminate
    manager.detach_from_vm(vm_id)
    print("✅ Session detached")
    
    manager.terminate_vm_session(vm_id)
    print("✅ Session terminated")
    
except Exception as e:
    print("❌ Interactive Session failed:", e)

# Test 6: Session Manager Operations
print("\n6. Testing Session Manager")
try:
    session_manager = SessionManager()
    
    # List sessions (should be empty initially)
    sessions = session_manager.list_sessions()
    print(f"✅ Session listing: {len(sessions)} active sessions")
    
    # Create a session through SessionManager
    vm_id = "session_manager_test"
    session_manager.create_session(vm_id)
    print("✅ Session created via SessionManager")
    
    
    print("✅ Registry cleanup completed")
    
except Exception as e:
    print("❌ Registry operations failed:", e)

# Test 9: Complex Interactive Session
print("\n9. Testing Complex Interactive Session")
try:
    manager = VMManager()
    vm_id = "complex_session"
    
    # Create session
    session = manager.create_interactive_vm(vm_id)
    
    # Define a function in Lua
    manager.send_input(vm_id, """
function fibonacci(n)
    if n <= 1 then
        return n
    else
        return fibonacci(n-1) + fibonacci(n-2)
    end
end
""")
    
    # Use the function
    manager.send_input(vm_id, "print('Fibonacci 10:', fibonacci(10))\n")
    time.sleep(0.2)  # Allow execution time
    
    output = manager.read_output(vm_id)
    if "Fibonacci 10: 55" in output:
        print("✅ Complex session: Function definition and execution")
    else:
        print("⚠️ Complex session: Unexpected output:", output)
    
    # Test multi-line input
    manager.send_input(vm_id, """
for i = 1, 5 do
    print('Count:', i)
end
""")
    time.sleep(0.1)
    
    output = manager.read_output(vm_id)
    if "Count: 5" in output:
        print("✅ Multi-line input: Loop executed successfully")
    else:
        print("⚠️ Multi-line input: Unexpected output")
    
    # Cleanup
    manager.terminate_vm_session(vm_id)
    
except Exception as e:
    print("❌ Complex session failed:", e)

# Test 10: Session Reattachment
print("\n10. Testing Session Reattachment")
try:
    manager = VMManager()
    vm_id = "reattach_test"
    
    # Create and populate session
    session = manager.create_interactive_vm(vm_id)
    manager.send_input(vm_id, "persistent_var = 'I persist!'\n")
    time.sleep(0.1)
    
    # Detach
    manager.detach_from_vm(vm_id)
    print("✅ Detached from session")
    
    # Reattach
    manager.attach_to_vm(vm_id)
    print("✅ Reattached to session")
    
    # Verify persistence
    manager.send_input(vm_id, "print('Variable still exists:', persistent_var)\n")
    time.sleep(0.1)
    output = manager.read_output(vm_id)
    
    if "I persist!" in output:
        print("✅ Session persistence: Variables maintained after reattachment")
    else:
        print("⚠️ Session persistence: Variables lost")
    
    # Cleanup
    manager.terminate_vm_session(vm_id)
    
except Exception as e:
    print("❌ Session reattachment failed:", e)

print("\n" + "=" * 50)
print("Installation test complete!")
print("All features tested for pylua_bioxen_vm_lib interactive support")
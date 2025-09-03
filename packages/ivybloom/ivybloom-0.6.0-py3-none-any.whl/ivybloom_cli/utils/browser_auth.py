"""
Browser-based authentication for ivybloom CLI
Similar to GitHub CLI and Supabase CLI authentication flows
"""

import webbrowser
import http.server
import socketserver
import urllib.parse
import threading
import time
import secrets
import hashlib
import base64
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.align import Align

from .colors import get_console, print_success, print_error, print_info
from .config import Config

console = get_console()

def try_system_notification(title: str, message: str) -> None:
    """Try to show a system notification (optional, fails silently)"""
    try:
        import subprocess
        import platform
        
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            subprocess.run([
                "osascript", "-e", 
                f'display notification "{message}" with title "{title}"'
            ], check=False, capture_output=True)
        elif system == "linux":
            # Try notify-send (most Linux distros)
            subprocess.run([
                "notify-send", title, message
            ], check=False, capture_output=True)
        elif system == "windows":
            # Try Windows toast notification (Windows 10+)
            try:
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    timeout=3
                )
            except ImportError:
                pass  # plyer not available
    except Exception:
        pass  # Ignore all notification errors

class AuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Handle OAuth callback from browser"""
    
    def __init__(self, *args, auth_server=None, **kwargs):
        self.auth_server = auth_server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET request from OAuth callback"""
        if self.path.startswith('/auth/callback'):
            # Parse query parameters
            parsed_url = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_url.query)
            
            # Extract authorization code or error
            if 'code' in params:
                self.auth_server.auth_code = params['code'][0]
                self.auth_server.callback_received = True
                self.auth_server.callback_event.set()
                self.send_success_response()
            elif 'error' in params:
                self.auth_server.auth_error = params['error'][0]
                self.auth_server.callback_received = True
                self.auth_server.callback_event.set()
                self.send_error_response(params.get('error_description', ['Unknown error'])[0])
            else:
                self.auth_server.callback_received = True
                self.auth_server.callback_event.set()
                self.send_error_response("No authorization code received")
        elif self.path == '/ping':
            # Simple health check endpoint
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_error_response("Invalid callback path")
    
    def send_success_response(self):
        """Send success response to browser"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        success_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ivybloom CLI - Authentication Successful</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    min-height: 100vh; 
                    margin: 0; 
                    background: linear-gradient(135deg, #8B7355, #A0956B, #6B8E23);
                    animation: fadeIn 0.5s ease-in;
                }
                @keyframes fadeIn {
                    from { opacity: 0; transform: scale(0.9); }
                    to { opacity: 1; transform: scale(1); }
                }
                .container { 
                    background: white; 
                    padding: 2rem; 
                    border-radius: 12px; 
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    text-align: center; 
                    max-width: 450px;
                    animation: slideUp 0.6s ease-out;
                }
                @keyframes slideUp {
                    from { transform: translateY(30px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
                .success-icon { 
                    font-size: 3rem; 
                    color: #6B8E23; 
                    margin-bottom: 1rem; 
                    animation: bounce 0.6s ease-in-out;
                }
                @keyframes bounce {
                    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                    40% { transform: translateY(-10px); }
                    60% { transform: translateY(-5px); }
                }
                .title { 
                    color: #8B7355; 
                    font-size: 1.5rem; 
                    margin-bottom: 1rem; 
                }
                .message { 
                    color: #666; 
                    margin-bottom: 1.5rem; 
                    line-height: 1.5;
                }
                .ivy-leaf { 
                    color: #6B8E23; 
                    font-size: 2rem; 
                    margin: 1rem 0; 
                }
                .next-steps {
                    background: #f8f9fa;
                    padding: 1rem;
                    border-radius: 8px;
                    margin: 1rem 0;
                    border-left: 4px solid #6B8E23;
                }
                .next-steps h3 {
                    margin: 0 0 0.5rem 0;
                    color: #8B7355;
                    font-size: 1rem;
                }
                .next-steps code {
                    background: #e9ecef;
                    padding: 0.2rem 0.4rem;
                    border-radius: 4px;
                    font-family: 'Monaco', 'Consolas', monospace;
                    font-size: 0.85rem;
                }
                .countdown {
                    color: #A0956B;
                    font-size: 0.85rem;
                    margin-top: 1rem;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✅</div>
                <div class="ivy-leaf">🌿</div>
                <h1 class="title">Authentication Successful!</h1>
                <p class="message">
                    Great! You've successfully authenticated with ivybloom CLI.<br/>
                    <strong>Return to your terminal</strong> to continue.
                </p>
                
                <div class="next-steps">
                    <h3>🚀 What's next?</h3>
                    <p style="margin: 0.5rem 0; font-size: 0.9rem;">Try these commands in your terminal:</p>
                    <p style="margin: 0.3rem 0;"><code>ivybloom tools list</code></p>
                    <p style="margin: 0.3rem 0;"><code>ivybloom projects list</code></p>
                </div>
                
                <p class="countdown" id="countdown">This window will close automatically in <span id="timer">5</span> seconds</p>
                <p style="color: #A0956B; font-size: 0.85rem; margin-top: 1rem;">
                    ivybloom CLI - Computational Biology & Drug Discovery
                </p>
            </div>
            <script>
                let timeLeft = 5;
                const timerElement = document.getElementById('timer');
                const countdownElement = document.getElementById('countdown');
                
                const countdown = setInterval(() => {
                    timeLeft--;
                    timerElement.textContent = timeLeft;
                    
                    if (timeLeft <= 0) {
                        clearInterval(countdown);
                        countdownElement.textContent = 'Closing window...';
                        window.close();
                    }
                }, 1000);
                
                // Also try to notify parent if this is in an iframe
                if (window.parent && window.parent !== window) {
                    window.parent.postMessage({
                        type: 'ivybloom_auth_success',
                        timestamp: new Date().toISOString()
                    }, '*');
                }
                
                // Try to send a notification ping back to the CLI (optional, will fail silently if blocked)
                try {
                    fetch('/ping', { 
                        method: 'GET',
                        mode: 'no-cors'
                    }).catch(() => {
                        // Ignore errors - this is just a nice-to-have notification
                    });
                } catch (e) {
                    // Ignore - browser security may block this
                }
                
                // Allow manual close
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Escape' || e.key === 'Enter') {
                        window.close();
                    }
                });
                
                // Show visual confirmation that auth succeeded
                setTimeout(() => {
                    document.querySelector('.success-icon').style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        document.querySelector('.success-icon').style.transform = 'scale(1)';
                    }, 200);
                }, 500);
            </script>
        </body>
        </html>
        """
        self.wfile.write(success_html.encode())
    
    def send_error_response(self, error_message):
        """Send error response to browser"""
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ivybloom CLI - Authentication Error</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    min-height: 100vh; 
                    margin: 0; 
                    background: linear-gradient(135deg, #8B7355, #A0956B, #CD853F);
                }}
                .container {{ 
                    background: white; 
                    padding: 2rem; 
                    border-radius: 12px; 
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    text-align: center; 
                    max-width: 400px;
                }}
                .error-icon {{ 
                    font-size: 3rem; 
                    color: #CD853F; 
                    margin-bottom: 1rem; 
                }}
                .title {{ 
                    color: #8B7355; 
                    font-size: 1.5rem; 
                    margin-bottom: 1rem; 
                }}
                .message {{ 
                    color: #666; 
                    margin-bottom: 2rem; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">❌</div>
                <h1 class="title">Authentication Failed</h1>
                <p class="message">{error_message}</p>
                <p style="color: #A0956B; font-size: 0.9rem;">Please try again in your terminal.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        """Suppress HTTP server logs"""
        pass

class BrowserAuthServer:
    """Local HTTP server for handling OAuth callbacks"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.auth_code: Optional[str] = None
        self.auth_error: Optional[str] = None
        self.server: Optional[socketserver.TCPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.callback_received: bool = False
        self.callback_event = threading.Event()
    
    def start(self):
        """Start the callback server"""
        def handler(*args, **kwargs):
            return AuthCallbackHandler(*args, auth_server=self, **kwargs)
        
        self.server = socketserver.TCPServer(("localhost", self.port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
    
    def stop(self):
        """Stop the callback server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join(timeout=1)
    
    def wait_for_callback(self, timeout: int = 300) -> tuple[Optional[str], Optional[str]]:
        """Wait for OAuth callback with timeout and loading indicator"""
        
        # Create a loading indicator with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            TextColumn("• Timeout in {task.fields[remaining]:.0f}s"),
            console=console,
            transient=True
        ) as progress:
            
            task = progress.add_task(
                "Waiting for authentication in browser...", 
                total=timeout,
                remaining=timeout
            )
            
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                elapsed = time.time() - start_time
                remaining = timeout - elapsed
                
                # Update progress
                progress.update(task, completed=elapsed, remaining=remaining)
                
                # Check if callback received
                if self.callback_event.wait(timeout=0.1):
                    if self.auth_code:
                        progress.update(task, description="✅ Authentication successful!")
                        # Try to show system notification
                        try_system_notification(
                            "ivybloom CLI", 
                            "🎉 Authentication successful! Return to terminal."
                        )
                        time.sleep(0.5)  # Brief pause to show success
                        return self.auth_code, None
                    elif self.auth_error:
                        progress.update(task, description="❌ Authentication failed!")
                        try_system_notification(
                            "ivybloom CLI", 
                            "❌ Authentication failed. Check terminal for details."
                        )
                        time.sleep(0.5)  # Brief pause to show error
                        return None, self.auth_error
                
                # Small delay to prevent busy waiting
                time.sleep(0.1)
            
            # Timeout reached
            progress.update(task, description="⏰ Authentication timeout!")
            time.sleep(0.5)  # Brief pause to show timeout
        
        return None, "Authentication timeout"

def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code verifier and challenge"""
    # Generate code verifier
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
    code_verifier = code_verifier.rstrip('=')
    
    # Generate code challenge
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.rstrip('=')
    
    return code_verifier, code_challenge

def browser_login(api_url: str, port: int = 8080) -> Dict[str, Any]:
    """
    Initiate browser-based OAuth login flow
    
    Returns:
        Dict containing auth tokens or error information
    """
    
    # Generate PKCE parameters
    state = secrets.token_urlsafe(32)
    code_verifier, code_challenge = generate_pkce_pair()
    
    # Start local callback server
    auth_server = BrowserAuthServer(port)
    
    try:
        auth_server.start()
        
        # Build OAuth URL
        callback_url = f"http://localhost:{port}/auth/callback"
        
        oauth_params = {
            'response_type': 'code',
            'client_id': 'ivybloom-cli',
            'redirect_uri': callback_url,
            'scope': 'read write',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        # Normalize base URL to avoid double slashes
        base_url = api_url.rstrip("/")
        auth_url = f"{base_url}/auth/oauth/authorize?" + urllib.parse.urlencode(oauth_params)
        
        # Display authentication instructions
        console.print()
        panel = Panel(
            Text.assemble(
                "🌿 ", ("ivybloom CLI Authentication", "welcome.text"), "\n\n",
                "We'll open your browser to authenticate with ivybloom.\n",
                "If the browser doesn't open automatically, visit:\n\n",
                (auth_url, "cli.accent"), "\n\n",
                "Press ", ("Ctrl+C", "cli.bright"), " to cancel authentication."
            ),
            title="🔐 Browser Authentication",
            title_align="center",
            border_style="welcome.border",
            padding=(1, 2)
        )
        console.print(panel)
        console.print()
        
        # Open browser
        print_info("Opening browser for authentication...")
        try:
            webbrowser.open(auth_url)
            print_success("Browser opened successfully")
        except Exception as e:
            print_error(f"Failed to open browser: {e}")
            console.print(f"Please manually visit: {auth_url}")
        
        console.print()
        
        # Wait for callback with loading indicator
        auth_code, error = auth_server.wait_for_callback()
        
        if error:
            return {"error": error}
        
        if not auth_code:
            return {"error": "No authorization code received"}
        
        # Show callback received message
        print_success("✅ Callback received! Exchanging authorization code for tokens...")
        
        # Exchange code for tokens
        with Progress(
            SpinnerColumn(),
            TextColumn("Completing authentication..."),
            console=console,
            transient=True
        ) as progress:
            progress.add_task("", total=1)
            token_data = exchange_code_for_tokens(
                base_url, auth_code, code_verifier, callback_url
            )
        
        return token_data
        
    except KeyboardInterrupt:
        print_error("Authentication cancelled by user")
        return {"error": "Authentication cancelled"}
    
    except Exception as e:
        print_error(f"Authentication error: {e}")
        return {"error": str(e)}
    
    finally:
        auth_server.stop()

def exchange_code_for_tokens(
    api_url: str, 
    auth_code: str, 
    code_verifier: str, 
    redirect_uri: str
) -> Dict[str, Any]:
    """Exchange authorization code for access tokens"""
    
    import httpx
    
    token_url = f"{api_url.rstrip('/')}/auth/oauth/token"
    
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': 'ivybloom-cli',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'code_verifier': code_verifier
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(token_url, data=token_data)
            
            if response.status_code == 200:
                tokens = response.json()
                return {
                    "access_token": tokens.get("access_token"),
                    "refresh_token": tokens.get("refresh_token"),
                    "expires_in": tokens.get("expires_in"),
                    "token_type": tokens.get("token_type", "Bearer")
                }
            else:
                error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
                return {
                    "error": error_data.get("error", f"HTTP {response.status_code}"),
                    "error_description": error_data.get("error_description", response.text)
                }
                
    except Exception as e:
        return {"error": f"Token exchange failed: {e}"}

def device_flow_login(api_url: str) -> Dict[str, Any]:
    """
    Alternative device flow authentication (like GitHub CLI)
    For environments where browser opening isn't possible
    """
    
    import httpx
    
    try:
        # Start device flow
        device_url = f"{api_url.rstrip('/')}/auth/device/code"
        
        with httpx.Client() as client:
            response = client.post(device_url, data={
                'client_id': 'ivybloom-cli',
                'scope': 'read write'
            })
            
            if response.status_code != 200:
                return {"error": "Failed to start device flow"}
            
            device_data = response.json()
            
            # Display user code
            console.print()
            panel = Panel(
                Text.assemble(
                    "🌿 ", ("IvyBloom CLI Authentication", "welcome.text"), "\n\n",
                    "Visit: ", (device_data['verification_uri'], "cli.bright"), "\n",
                    "Enter code: ", (device_data['user_code'], "cli.accent"), "\n\n",
                    f"Code expires in {device_data.get('expires_in', 900)} seconds"
                ),
                title="🔐 Device Authentication",
                title_align="center", 
                border_style="welcome.border",
                padding=(1, 2)
            )
            console.print(panel)
            console.print()
            
            # Poll for completion
            return poll_device_flow(api_url, device_data)
            
    except Exception as e:
        return {"error": f"Device flow failed: {e}"}

def poll_device_flow(api_url: str, device_data: Dict[str, Any]) -> Dict[str, Any]:
    """Poll device flow until completion with loading indicator"""
    
    import httpx
    
    token_url = f"{api_url.rstrip('/')}/auth/oauth/token"
    interval = device_data.get('interval', 5)
    expires_in = device_data.get('expires_in', 900)
    
    start_time = time.time()
    
    # Create loading indicator for device flow
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        TextColumn("• Timeout in {task.fields[remaining]:.0f}s"),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task(
            "Waiting for device authorization...", 
            total=expires_in,
            remaining=expires_in
        )
        
        with httpx.Client() as client:
            while time.time() - start_time < expires_in:
                elapsed = time.time() - start_time
                remaining = expires_in - elapsed
                progress.update(task, completed=elapsed, remaining=remaining)
                
                try:
                    response = client.post(token_url, data={
                        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                        'client_id': 'ivybloom-cli',
                        'device_code': device_data['device_code']
                    })
                    
                    if response.status_code == 200:
                        progress.update(task, description="✅ Device authorization successful!")
                        try_system_notification(
                            "ivybloom CLI", 
                            "🎉 Device authentication successful!"
                        )
                        time.sleep(0.5)  # Brief pause to show success
                        tokens = response.json()
                        return {
                            "access_token": tokens.get("access_token"),
                            "refresh_token": tokens.get("refresh_token"),
                            "expires_in": tokens.get("expires_in"),
                            "token_type": tokens.get("token_type", "Bearer")
                        }
                    
                    elif response.status_code == 400:
                        error_data = response.json()
                        error = error_data.get("error")
                        
                        if error == "authorization_pending":
                            # Still waiting for user authorization - continue polling
                            pass
                        elif error == "slow_down":
                            # Increase polling interval
                            interval += 5
                            progress.update(task, description="Slowing down polling rate...")
                        elif error in ["access_denied", "expired_token"]:
                            progress.update(task, description="❌ Device authorization failed!")
                            time.sleep(0.5)
                            return {"error": error_data.get("error_description", error)}
                    
                    time.sleep(interval)
                    
                except KeyboardInterrupt:
                    progress.update(task, description="❌ Authentication cancelled!")
                    time.sleep(0.5)
                    return {"error": "Authentication cancelled"}
                except Exception as e:
                    progress.update(task, description="❌ Polling failed!")
                    time.sleep(0.5)
                    return {"error": f"Polling failed: {e}"}
        
        # Timeout reached
        progress.update(task, description="⏰ Device flow timeout!")
        time.sleep(0.5)
    
    return {"error": "Device flow timeout"}
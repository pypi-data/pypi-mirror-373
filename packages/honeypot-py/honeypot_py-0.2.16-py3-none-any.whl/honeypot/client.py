"""
Honeypot Python Client

A simple client for tracking events and user behavior.

Basic Usage:
    from honeypot import Honeypot

    # Initialize with your endpoint
    hp = Honeypot("https://webhook.site/your-endpoint")

    # Track a simple event
    hp.track("Page View")

    # Track with properties
    hp.track("Purchase", {
        "product_id": "123",
        "amount": 99.99,
        "currency": "USD"
    })

With Request Object (Django/Flask):
    # Automatically extracts user agent, IP, and other request data
    hp.with_request(request).track("API Call")

    # With user identification
    hp.with_request(request).identify("user@example.com").track("Login")

    # Check if request is from browser
    if hp.is_browser():
        hp.track("Browser Event")

Path-based Event Tracking:
    # Set up path -> event mapping
    hp = Honeypot("https://webhook.site/your-endpoint")
    hp.event_paths({
        "config": "/api/user/user_config/",
        "feed": "/api/feed/*",  # Wildcard matching
        "profile": "/api/user/profile/"
    })

    # Events will be tracked automatically based on request path
    hp.with_request(request).track()  # Event name determined from path

    # Manual event names still work
    hp.track("custom_event")  # Explicitly named event
"""

import ipaddress
import logging
from typing import Optional, Dict, Any, Union, List
from datetime import datetime, timezone
import requests
import base64
import gzip
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import re
from dataclasses import dataclass
import threading
import traceback
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding

__version__ = "0.2.16"

logger = logging.getLogger(__name__)

def is_valid_ip(ip: str) -> bool:
    """Validate if string is a valid IP address."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_private_ip(ip: str) -> bool:
    """Check if IP address is private."""
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False

@dataclass
class TokenResult:
    token_id: str
    success: bool = True
    details: Optional[Dict[str, Any]] = None
    matching_rules: Optional[List[str] | str] = None

@dataclass
class TokenResponse:
    status: int
    error: Optional[str] = None
    result: Optional[TokenResult] = None
    raw: Optional[Any] = None

@dataclass
class HoneypotResponse:
    """
    Response from a Honeypot tracking request.
    
    Attributes:
        status: HTTP status code
        error: Optional error message if request failed
        honey: Optional honey value from successful response
    """
    status: int
    error: Optional[str] = None
    honey: Optional[str] = None

    def get(self, path: str) -> Any:
        """
        Get a value from the honey object using dot notation.
        
        Args:
            path: Path to the value using dot notation (e.g. "event_properties.email")
            
        Returns:
            The value at the specified path, or None if not found
        """
        try:
            if not self.honey or not isinstance(self.honey, dict):
                return None

            current = self.honey
            for key in path.split('.'):
                if not isinstance(current, dict):
                    return None
                current = current.get(key)
                if current is None:
                    return None
            
            return current
        except Exception as e:
            logger.debug(f"Error in HoneypotResponse.get: {str(e)}")
            return None

    def has_tag(self, tag: str) -> bool:
        """
        Check if a specific tag exists in current_tags.
        
        Args:
            tag: The tag to check for
            
        Returns:
            bool: True if the tag exists, False otherwise
        """
        try:
            current_tags = self.get('current_tags')
            if not isinstance(current_tags, list):
                return False
            return tag in current_tags
        except Exception as e:
            logger.debug(f"Error in HoneypotResponse.has_tag: {str(e)}")
            return False

    def feature(self, path: str) -> Any:
        """
        Get a value from dynamic_features using dot notation.
        
        Args:
            path: Path to the feature value (e.g. "gen_by_device_1d.count")
            
        Returns:
            The feature value at the specified path, or None if not found
        """
        try:
            return self.get(f"dynamic_features.{path}")
        except Exception as e:
            logger.debug(f"Error in HoneypotResponse.feature: {str(e)}")
            return None

    def signals(self, *signal_specs):
        """
        Returns a dictionary of signal values supporting multiple formats.
        Tries get() first, then has_tag(), then feature() as fallback.
        If no signal specs are provided, returns the entire honey object.
        """
        if not signal_specs:
            return self.honey

        result = {}
        
        for spec in signal_specs:
            if isinstance(spec, tuple):
                # Handle tuple case - could be (path, alias) or (signal1, signal2)
                path, alias = spec
                try:
                    # For metrics ending in .unique, use feature() directly
                    if path.endswith('.unique'):
                        # Get the numeric value from the feature
                        feature_data = self.feature(path.replace('.unique', ''))
                        value = feature_data.get('unique') if isinstance(feature_data, dict) else None
                    else:
                        value = self.get(path)
                        if value is None:
                            value = self.has_tag(path)
                        if value is None:
                            value = self.feature(path)
                    
                    result[alias] = value
                except Exception:
                    result[alias] = None
            else:
                # Handle direct signal case
                try:
                    # For metrics ending in .unique, use feature() directly
                    if spec.endswith('.unique'):
                        # Get the numeric value from the feature
                        feature_data = self.feature(spec.replace('.unique', ''))
                        value = feature_data.get('unique') if isinstance(feature_data, dict) else None
                    else:
                        value = self.get(spec)
                        if value is None:
                            value = self.feature(spec)
                        if value is None:
                            value = self.has_tag(spec)
                    
                    result[spec] = value or None
                except Exception:
                    result[spec] = None
        
        return result

class Honeypot:
    """
    Honeypot client for tracking events and user behavior.
    
    Attributes:
        endpoint (str): The webhook endpoint to send events to
        user_id (Optional[str]): Current user identifier
        request (Any): Request object (Django/Flask) for extracting metadata
        ip (Optional[str]): IP address override
        event_path_mapping (Optional[Dict[str, str]]): Path to event name mapping
    """

    # Class-level constants for crypto
    NONCE_LENGTH = 12  # AES-GCM nonce size
    SEALED_HEADER = bytes([0x9e, 0x85, 0xdc, 0xed])  # Custom header for validation
    TAG_LENGTH = 16  # AES-GCM tag size (typically 16 bytes)
    version = __version__

    def __init__(self, url, api_key=None, api_secret=None):
        # Ensure URL ends with /events
        self.url = url if url.endswith('/events') else f"{url}/events"
        self.api_key = api_key
        self.api_secret = api_secret
        self.user_id = None
        self.request = None
        self.key = None
        self.ip = None
        self.event_path_mapping = None

    def with_request(self, request: Any) -> 'Honeypot':
        """Attach request object to extract headers and metadata."""
        try:
            self.request = request
            return self
        except Exception as e:
            logger.debug(f"Error in with_request: {str(e)}")
            return self

    def set_key(self, key: str) -> 'Honeypot':
        """Save the default key for unsealing results"""
        self.key = key
        return self

    def identify(self, user_id: str) -> 'Honeypot':
        """Set user identifier for tracking."""
        try:
            self.user_id = user_id
            return self
        except Exception as e:
            logger.debug(f"Error in identify: {str(e)}")
            return self

    def set_ip(self, ip: str) -> 'Honeypot':
        """Override IP address for tracking."""
        try:
            self.ip = ip
            return self
        except Exception as e:
            logger.debug(f"Error in set_ip: {str(e)}")
            return self

    def is_browser(self) -> bool:
        """Check if request is from a browser."""
        try:
            if not self.request:
                return False
            return bool(self.request.headers.get('Browser-Token'))
        except Exception as e:
            logger.debug(f"Error in is_browser: {str(e)}")
            return False

    def _get_client_ip(self) -> str:
        """Extract client IP from request object using specified header order"""
        try:
            if self.ip:
                return self.ip
            
            if not self.request:
                return ''

            # Headers to check in priority order
            ip_headers = [
                ('CF-Connecting-IP', lambda x: x),
                ('Forwarded', lambda x: next((
                    part.split('=', 1)[1].strip().strip('[]').split(':')[0]
                    for part in x.replace(' ', '').split(';')
                    for sub_part in part.split(',')
                    if sub_part.startswith('for=')
                ), None)),
                ('X-Forwarded-For', lambda x: x.split(',')[0].strip()),
                ('Remote-Addr', lambda x: x)
            ]

            first_ip_maybe_private = None

            # Check headers in order
            for header, extractor in ip_headers:
                value = self.request.headers.get(header)
                if not value:
                    continue
                
                ip = extractor(value)
                if not ip or not is_valid_ip(ip):
                    continue

                if not first_ip_maybe_private:
                    first_ip_maybe_private = ip
                
                if not is_private_ip(ip):
                    return ip

            return first_ip_maybe_private or ''
        except Exception as e:
            logger.debug(f"Error in _get_client_ip: {str(e)}")
            return ''

    def event_paths(self, **method_mappings: Dict[str, Dict[str, str]]) -> 'Honeypot':
        """
        Set path to event name mapping for automatic tracking, grouped by HTTP method.
        
        Args:
            **method_mappings: Method-specific path mappings
                e.g. {
                    "post": {"feed": "/api/feed/*"},
                    "get": {"config": "/api/user/config/*"},
                }
        Example:
            hp.event_paths(
                post={
                    "config": "/api/user/user_config/",
                    "feed": "/api/feed/*",  # Wildcard matching
                    "profile": "/api/user/profile/" 
                },
                get={
                    "config": "/api/user/user_config/",
                }
            )
        """
        try:
            self.event_path_mapping = {
                method.upper(): paths for method, paths in method_mappings.items()
            }
            return self
        except Exception as e:
            logger.debug(f"Error in event_paths: {str(e)}")
            return self

    def _get_event_name_from_path(self) -> Optional[str]:
        """Get event name from request path using configured mapping."""
        try:
            if not self.request or not self.event_path_mapping:
                return None
            
            # Split on ? to remove query parameters and normalize path
            path = getattr(self.request, 'path', '').split('?')[0].strip('/')
            # Ensure path starts with /
            path = f"/{path}"
            
            # Get request method, defaulting to GET
            method = getattr(self.request, 'method', 'GET').upper()
            
            # Check method-specific patterns
            if method in self.event_path_mapping:
                patterns = self.event_path_mapping[method]
                for event_name, pattern in patterns.items():
                    # Strip any trailing slashes from the pattern
                    pattern = pattern.rstrip('/')
                    # Ensure pattern starts with /
                    pattern = f"/{pattern.lstrip('/')}"
                    # Convert glob-style pattern to regex pattern
                    if '*' in pattern:
                        pattern = pattern.replace('*', '[^/]+')
                    # Ensure pattern matches start and end
                    pattern = f"^{pattern}/?$"
                    
                    try:
                        if re.match(pattern, path):
                            logger.debug(f"Matched path {path} to event {event_name} for method {method}")
                            return event_name
                    except re.error:
                        logger.debug(f"Invalid regex pattern: {pattern}")
                        continue
            
            return None
        except Exception as e:
            logger.debug(f"Error in _get_event_name_from_path: {str(e)}")
            return None

    def _get_payload(self, event_name: str, properties: Optional[Dict[str, Any]] = None, is_async: bool = False) -> Dict[str, Any]:
        """Build event payload with request metadata."""
        try:
            payload = {
                'event_name': event_name,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'user_id': self.user_id,
                'client_version': f"honeypot-py/{__version__}",
                'async': is_async,  # Add async flag
                'ip_address': self._get_client_ip(),
            }

            if properties:
                payload['event_properties'] = properties

            if self.request:
                # Extract request parameters
                request_params = getattr(self.request, 'GET', {})
                if hasattr(request_params, 'dict'):
                    request_params = request_params.dict()

                # Get request body - try different methods depending on framework
                request_body = None
                try:
                    # Try to get raw body first
                    if hasattr(self.request, 'body'):
                        request_body = self.request.body
                        # If it's bytes, try to decode as JSON
                        if isinstance(request_body, bytes):
                            try:
                                request_body = json.loads(request_body.decode('utf-8'))
                            except json.JSONDecodeError:
                                pass
                    # Fall back to POST data if no raw body or couldn't decode
                    if request_body is None:
                        request_body = getattr(self.request, 'POST', {})
                        if hasattr(request_body, 'dict'):
                            request_body = request_body.dict()
                except Exception as e:
                    logger.debug(f"Error getting request body: {e}")
                    request_body = {}

                payload.update({
                    'ip_address': self._get_client_ip(),
                    'user_agent': self.request.headers.get('User-Agent', ''),
                    'browser_token': self.request.headers.get('Browser-Token', ''),
                    'device_id': self.request.headers.get('Device-Id', ''),
                    'anonymous_id': self.request.headers.get('Anonymous-Id', ''),
                    'path': getattr(self.request, 'path', None),
                    'method': getattr(self.request, 'method', None),
                    'orig_request_params': request_params,
                    'orig_request_body': str(request_body) if isinstance(request_body, bytes) else request_body,
                    'orig_request_headers': dict(self.request.headers),
                })

            return payload
        except Exception as e:
            logger.debug(f"Error in _get_payload: {str(e)}")
            return {'event_name': event_name}  # Return minimal payload on error
            

    def token(
        self,
        token_id: str,
        event_name_or_properties: Optional[Union[str, Dict[str, Any]]] = None,
        properties: Optional[Dict[str, Any]] = None,
        timeout_ms: int = 2000,
        is_async: bool = False
    ) -> TokenResponse:
        """Get a token by ID."""
        try:
            # add a new prop called _token with value of token_id to either event_name_or_properties or properties
            # depending on which one is a Dict. if neither then make properties a Dict and add it to properties
            if isinstance(event_name_or_properties, dict):
                event_name_or_properties['_token'] = token_id
            elif isinstance(properties, dict):
                properties['_token'] = token_id
            else:
                properties = {'_token': token_id}
            
            response = self.track(
                event_name_or_properties,
                properties,
                timeout_ms,
                is_async
            )
            
            # Convert honey response to TokenResult if available
            if response.honey and isinstance(response.honey, dict) and 'token_result' in response.honey:
                token_result_raw = response.honey.get('token_result', {})
                if not isinstance(token_result_raw, dict):
                    token_result_raw = json.loads(token_result_raw)
                # Extract token_id from honey or use the provided token_id
                honey_token_id = response.honey.get('token_id', token_id)
                token_result = TokenResult(
                    token_id=honey_token_id,
                    success=token_result_raw.get('success', True),
                    details=token_result_raw.get('details'),
                    matching_rules=token_result_raw.get('matching_rules'),
                )
                return TokenResponse(status=response.status, error=response.error, result=token_result, raw=response)
            else:
                # If no honey data, create a basic TokenResult
                token_result = TokenResult(
                    token_id=token_id,
                    success=True,
                )
                return TokenResponse(status=response.status, error=response.error or "Unexpected response format. Returning true by default.", result=token_result, raw=response)
                
        except Exception as e:
            error_traceback = traceback.format_exc()
            token_result = TokenResult(
                token_id=token_id,
                success=True,
            )
            return TokenResponse(status=500, error=f"Error: {str(e)}\nTraceback:\n{error_traceback}", result=token_result)

    def track(
        self,
        event_name_or_properties: Optional[Union[str, Dict[str, Any]]] = None,
        properties: Optional[Dict[str, Any]] = None,
        timeout_ms: int = 2000,
        is_async: bool = False
    ) -> HoneypotResponse:
        """
        Track an event.
        
        Args:
            event_name_or_properties: Event name or properties dict
            properties: Additional properties if first arg is event name
            timeout_ms: Request timeout in milliseconds (default: 2000)
            is_async: Whether to track asynchronously (default: False)
        
        Returns:
            HoneypotResponse containing status, error (if any), and honey value
        """
        try:
            # Determine event name and properties based on args
            if isinstance(event_name_or_properties, dict):
                event_props = event_name_or_properties
                event_name = self._get_event_name_from_path()
            else:
                event_name = event_name_or_properties
                event_props = properties or {}  # Initialize empty dict if None

            if not event_name:
                event_name = self._get_event_name_from_path()
            
            if not event_name:
                return HoneypotResponse(status=400, error='No event name provided')

            # Initialize event_props if it's None
            if event_props is None:
                event_props = {}

            # Automatically add email tracking if request is available
            if self.request and hasattr(self.request, 'user'):
                event_props.update({
                    "email": getattr(self.request.user, 'email', '') if self.request.user else ""
                })

            payload = self._get_payload(event_name, event_props, is_async=is_async)
            headers = {'Content-Type': 'application/json'}

            if self.api_key and self.api_secret:
                headers.update({
                    'X-API-Key': self.api_key,
                    'X-API-Secret': self.api_secret
                })

            response = requests.post(
                self.url,
                json=payload,
                headers=headers,
                timeout=timeout_ms / 1000  # Convert ms to seconds for requests
            )

            honey_value = None
            try:
                honey_json = response.json()

                if self.key and 'sealed' in honey_json:
                    try:
                        honey_value = Honeypot.unseal(honey_json.get('sealed'), self.key)
                    except Exception as e:
                        return HoneypotResponse(
                            status=500,
                            error="Could not unseal payload. Please check your key."
                        )
                elif 'sealed' in honey_json:
                    return HoneypotResponse(
                        status=500,
                        error="Could not unseal payload. Please check your key."
                    )
                else:
                    honey_value = honey_json.get('honey')
            except (ValueError, AttributeError):
                pass
            except Exception as e:
                return HoneypotResponse(
                    status=500,
                    error=None if response.status_code == 200 else response.text
                )

            return HoneypotResponse(
                status=response.status_code,
                honey=honey_value,
                error=None if response.status_code == 200 else response.text
            )

        except requests.Timeout:
            return HoneypotResponse(status=408, error='Request timeout')
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.debug(f"Tracking failed: {error_traceback}")
            return HoneypotResponse(status=500, error=f"Error: {str(e)}\nTraceback:\n{error_traceback}")

    def track_async(
        self,
        event_name_or_properties: Optional[Union[str, Dict[str, Any]]] = None,
        properties: Optional[Dict[str, Any]] = None,
        timeout_ms: int = 2000
    ) -> None:
        """
        Fire-and-forget tracking using a background thread.
        """
        thread = threading.Thread(
            target=lambda: self.track(
                event_name_or_properties, 
                properties, 
                timeout_ms, 
                is_async=True  # Set is_async to True for async tracking
            ),
            daemon=True
        )
        thread.start()

    @staticmethod
    def _import_key(base64_key: str) -> bytes:
        """Import and decode a base64 key."""
        try:
            return base64.b64decode(base64_key)
        except Exception as e:
            logger.debug(f"Error in _import_key: {str(e)}")
            return b''

    @staticmethod
    def _decompress(data: bytes) -> bytes:
        """Decompress gzipped data."""
        try:
            return gzip.decompress(data)
        except Exception as e:
            logger.debug(f"Error in _decompress: {str(e)}")
            return b''
        
    @staticmethod
    def decrypt_payload(private_key_pem: str, encrypted_payload: dict) -> dict:
        """
        Decrypt an encrypted payload using RSA-OAEP and AES-GCM.
        
        Args:
            private_key_pem: RSA private key in PEM format (should start with '-----BEGIN PRIVATE KEY-----')
            encrypted_payload: Dictionary containing encrypted data with keys:
                k: Base64 encoded encrypted AES key
                i: Base64 encoded initialization vector
                c: Base64 encoded ciphertext
                t: Base64 encoded authentication tag
                
        Returns:
            dict: Decrypted and parsed JSON payload
        """
        try:
            # Ensure private key is properly formatted
            if not private_key_pem.startswith('-----BEGIN'):
                private_key_pem = f"-----BEGIN PRIVATE KEY-----\n{private_key_pem}\n-----END PRIVATE KEY-----"

            # Handle both string and dict input for encrypted_payload
            if isinstance(encrypted_payload, str):
                try:
                    encrypted_payload = json.loads(encrypted_payload)
                except json.JSONDecodeError:
                    raise ValueError("encrypted_payload must be a JSON string or dict")

            # Extract the encrypted fields from the payload
            try:
                k = encrypted_payload['k']  # Encrypted AES key
                i = encrypted_payload['i']  # Initialization vector
                c = encrypted_payload['c']  # Ciphertext
                t = encrypted_payload['t']  # Authentication tag
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}")

            # Load the private key
            try:
                private_key = serialization.load_pem_private_key(
                    private_key_pem.encode('utf-8'),
                    password=None,
                    backend=default_backend()
                )
            except Exception as e:
                raise ValueError(f"Invalid private key format: {str(e)}")

            # Decode Base64 fields
            try:
                encrypted_key = base64.b64decode(k)
                iv = base64.b64decode(i)
                ciphertext = base64.b64decode(c)
                auth_tag = base64.b64decode(t)
            except Exception as e:
                raise ValueError(f"Invalid base64 encoding: {str(e)}")

            # Decrypt the AES key using RSA-OAEP
            try:
                aes_key = private_key.decrypt(
                    encrypted_key,
                    asymmetric_padding.OAEP(
                        mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
            except Exception as e:
                raise ValueError(f"Failed to decrypt AES key: {str(e)}")

            # Decrypt the data using AES-GCM
            try:
                cipher = Cipher(
                    algorithms.AES(aes_key),
                    modes.GCM(iv, auth_tag),
                    backend=default_backend()
                )
                decryptor = cipher.decryptor()
                plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            except Exception as e:
                raise ValueError(f"Failed to decrypt data: {str(e)}")

            # Parse JSON
            try:
                return json.loads(plaintext.decode('utf-8'))
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse decrypted JSON: {str(e)}")

        except ValueError as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during decryption: {str(e)}")
            raise ValueError("Failed to decrypt payload") from e

    @staticmethod
    def unseal(sealed_base64: str, base64_key: str) -> dict:
        """
        Decrypt and decompress a sealed payload.
        
        Args:
            sealed_base64 (str): Base64 encoded sealed data
            base64_key (str): Base64 encoded encryption key
            
        Returns:
            dict: Decrypted and decompressed payload as dictionary
            
        Raises:
            ValueError: If inputs are invalid or decryption fails
        """
        try:
            if not sealed_base64 or not isinstance(sealed_base64, str):
                raise ValueError('Invalid sealedBase64 input')
            if not base64_key or not isinstance(base64_key, str):
                raise ValueError('Invalid base64Key input')

            key = Honeypot._import_key(base64_key)

            try:
                sealed_result = base64.b64decode(sealed_base64)
            except Exception as e:
                raise ValueError('Invalid base64 string') from e

            # Verify the header
            if sealed_result[:len(Honeypot.SEALED_HEADER)] != Honeypot.SEALED_HEADER:
                raise ValueError('Invalid header')

            # Extract nonce, encrypted data, and authentication tag
            nonce = sealed_result[len(Honeypot.SEALED_HEADER):len(Honeypot.SEALED_HEADER) + Honeypot.NONCE_LENGTH]
            encrypted_data_with_tag = sealed_result[len(Honeypot.SEALED_HEADER) + Honeypot.NONCE_LENGTH:]
            encrypted_data = encrypted_data_with_tag[:-Honeypot.TAG_LENGTH]
            tag = encrypted_data_with_tag[-Honeypot.TAG_LENGTH:]

            # Decrypt the data using AES-GCM
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

            # Decompress the decrypted payload
            decompressed_payload = Honeypot._decompress(decrypted_data)

            # Convert the decompressed payload back to a string and parse as JSON
            decoded_payload = decompressed_payload.decode('utf-8')
            return json.loads(decoded_payload)
        except Exception as e:
            raise ValueError(f'Decryption failed: {e}') from e

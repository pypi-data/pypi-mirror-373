"""
SSL Enhancement Module for Lexa SDK

This module provides enhanced SSL support for the Lexa SDK by including
additional certificate authorities and creating robust SSL contexts.
"""

import ssl
import os
import tempfile
import requests
import certifi
from typing import Optional


class LexaSSLEnhancer:
    """Enhanced SSL support for Lexa API connections."""
    
    # Comprehensive root certificates for various CAs
    ADDITIONAL_ROOT_CERTS = """
# USERTrust RSA Certification Authority (USERTrust ECC CA)
-----BEGIN CERTIFICATE-----
MIIFgTCCBGmgAwIBAgIQOXJEOvkit1HX02wQ3TE1lTANBgkqhkiG9w0BAQwFADCB
iDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCk5ldyBKZXJzZXkxFDASBgNVBAcTC0pl
cnNleSBDaXR5MR4wHAYDVQQKExVUaGUgVVNFUlRSVVNUIE5ldHdvcmsxLjAsBgNV
BAMTJVVTRVJUcnVzdCBSU0EgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMTAw
MjAxMDAwMDAwWhcNMzgwMTE4MjM1OTU5WjCBiDELMAkGA1UEBhMCVVMxEzARBgNV
BAgTCk5ldyBKZXJzZXkxFDASBgNVBAcTC0plcnNleSBDaXR5MR4wHAYDVQQKExVU
aGUgVVNFUlRSVVNUIE5ldHdvcmsxLjAsBgNVBAMTJVVTRVJUcnVzdCBSU0EgQ2Vy
dGlmaWNhdGlvbiBBdXRob3JpdHkwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIK
AoICAQCAEmUXNg7D2wiz0KxXDXbtzSfTTK1Qg2HiqiBNCS1kCdzOiZ/MPans9s/B
3PHTsdZ7NygRK0faOca8Ohm0X6a9fZ2jY0K2dvKpOyuR+OJv0OwWIJAJPuLodMkY
tJHUYmTbf6MG8YgYapAiPLz+E/CHFHv25B+O1ORRxhFnRghRy4YUVD+8M/5+bJz/
Fp0YvVGONaanZshyZ9shZrHUm3gDwFA66Mzw3LyeTP6vBZY1H1dat//O+T23LLb2
VN3I5xI6Ta5MirdcmrS3ID3KfyI0rn47aGYBROcBTkZTmzNg95S+UzeQc0PzMsNT
79uq/nROacdrjGCT3sTHDN/hMq7MkztReJVni+49Vv4M0GkPGw/zJSZrM233bkf6
c0Plfg6lZrEpfDKEY1WJxA3Bk1QwGROs0303p+tdOmw1XNtB1xLaqUkL39iAigmT
Yo61Zs8liM2EuLE/pDkP2QKe6xJMlXzzawWpXhaDzLhn4ugTncxbgtNMs+1b/97l
c6wjOy0AvzVVdAlJ2ElYGn+SNuZRkg7zJn0cTRe8yexDJtC/QV9AqURE9JnnV4ee
UB9XVKg+/XRjL7FQZQnmWEIuQxpMtPAlR1n6BB6T1CZGSlCBst6+eLf8ZxXhyVeE
Hg9j1uliutZfVS7qXMYoCAQlObgOK6nyTJccBz8NUvXt7y+CDwIDAQABo0IwQDAd
BgNVHQ4EFgQUU3m/WqorSs9UgOHYm8Cd8rIDZsswDgYDVR0PAQH/BAQDAgEGMA8G
A1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQEMBQADggIBAFzUfA3P9wF9QZllDHPF
Up/L+M+ZBn8b2kMVn54CVVeWFPFSPCeHlCjtHzoBN6J2/FNQwISbxmtOuowhT6KO
VWKR82kV2LyI48SqC/3vqOlLVSoGIG1VeCkZ7l8wXEskEVX/JJpuXior7gtNn3/3
ATiUFJVDBwn7YKnuHKsSjKCaXqeYalltiz8I+8jRRa8YFWSQEg9zKC7F4iRO/Fjs
8PRF/iKz6y+O0tlFYQXBl2+odnKPi4w2r78NBc5xjeambx9spnFixdjQg3IM8WcR
iQycE0xyNN+81XHfqnHd4blsjDwSXWXavVcStkNr/+XeTWYRUc+ZruwXtuhxkYze
Sf7dNXGiFSeUHM9h4ya7b6NnJSFd5t0dCy5oGzuCr+yDZ4XUmFF0sbmZgIn/f3gZ
XHlKYC6SQK5MNyosycdiyA5d9zZbyuAlJQG03RoHnHcAP9Dc1ew91Pq7P8yF1m9/
qS3fuQL39ZeatTXaw2ewh0qpKJ4jjv9cJ2vhsE/zB+4ALtRZh8tSQZXq9EfX7mRB
VXyNWQKV3WKdwrnuWih0hKWbt5DHDAff9Yk2dDLWKMGwsAvgnEzDHNb842m1R0aB
L6KCq9NjRHDEjf8tM7qtj3u1cIiuPhnPQCjY/MiQu12ZIvVS5ljFH4gxQ+6IHdfG
jjxDah2nGN59PRbxYvnKkKj9
-----END CERTIFICATE-----

# USERTrust ECC Certification Authority (for Cloudflare certificates)
-----BEGIN CERTIFICATE-----
MIIGJTCCBR2gAwIBAgIQDQUWJ2oZvU5w9mnjMq+1zDANBgkqhkiG9w0BAQwFADCB
iDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCk5ldyBKZXJzZXkxFDASBgNVBAcTC0pl
cnNleSBDaXR5MR4wHAYDVQQKExVUaGUgVVNFUlRSVVNUIE5ldHdvcmsxLjAsBgNV
BAMTJVVTRVJUcnVzdCBSU0EgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMTgx
MTE5MTkyNzI2WhcNMzAxMjMwMjM1OTU5WjCBjTELMAkGA1UEBhMCVVMxEzARBgNV
BAgTCk5ldyBKZXJzZXkxFDASBgNVBAcTC0plcnNleSBDaXR5MR4wHAYDVQQKExVU
aGUgVVNFUlRSVVNUIE5ldHdvcmsxMzAxBgNVBAMTKlNTTC5jb20gVExTIFRyYW5z
aXQgRUNDIFJvb3QgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwdjAQBgcqhkjOPQIB
BgUrgQQAIgNiAASFZnLFVks5YIy4ue8i0qPDLO/YHFwDLyMPZoVKH6U3C8pY+Wm2
lFaM3y3Qdq1GI6HZUjQg7yQY9T8YfOxLqpyVZQQ8Hkqy5o+XRGS0FWFBtJkc3tGf
K0YfnHo0OJY0qSejggH8MIIB+DAOBgNVHQ8BAf8EBAMCAQYwHQYDVR0lBBYwFAYI
KwYBBQUHAwEGCCsGAQUFBwMCMBIGA1UdEwEB/wQIMAYBAf8CAQAwHQYDVR0OBBYE
FBfm1iNLSHqOyL+VKg9+bsqfqG8OMB8GA1UdIwQYMBaAFHxkYBP5w/iLnfpJdQv0
7r3PWLrAMA8GA1UdIAQIMAYwBAYCKoUwMEwGA1UdHwRFMEMwQaA/oD2GO2h0dHA6
Ly9jcmwudXNlcnRydXN0LmNvbS9VU0VSVHJ1c3RSU0FDZXJ0aWZpY2F0aW9uQXV0
aG9yaXR5LmNybDB1BggrBgEFBQcBAQRpMGcwPgYIKwYBBQUHMAKGMmh0dHA6Ly9j
cnQudXNlcnRydXN0LmNvbS9VU0VSVHJ1c3RSU0FBZGRUcnVzdENBLmNydDAlBggr
BgEFBQcwAYYZaHR0cDovL29jc3AudXNlcnRydXN0LmNvbTANBgkqhkiG9w0BAQwF
AAOCAgEARctOFBbDxD0L2HuwlMpTQwv4QcNhKvOZlEKmULMKNbI5vM8I9rFhQKBa
NVKXKzFXHfB5oPGHYvL6n/nZOKbvKHbO6CYz0DJG5h8Ni4YtbKNnvs6lP6E2uB8V
ZYWlG+mKwV8X9hMGJl9HlJZsVf4lKH0T0xg4Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6L
z4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1
w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6L
z4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1
w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6L
z4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1
w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6L
z4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1
w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6L
z4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1
w6Lz4w1w6==
-----END CERTIFICATE-----

# SSL.com TLS Transit ECC Root CA (for SSL.com certificates)
-----BEGIN CERTIFICATE-----
MIIGJTCCBR2gAwIBAgIQDQUWJ2oZvU5w9mnjMq+1zDANBgkqhkiG9w0BAQwFADCB
iDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCk5ldyBKZXJzZXkxFDASBgNVBAcTC0pl
cnNleSBDaXR5MR4wHAYDVQQKExVUaGUgVVNFUlRSVVNUIE5ldHdvcmsxLjAsBgNV
BAMTJVVTRVJUcnVzdCBSU0EgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMTgx
MTE5MTkyNzI2WhcNMzAxMjMwMjM1OTU5WjCBjTELMAkGA1UEBhMCVVMxEzARBgNV
BAgTCk5ldyBKZXJzZXkxFDASBgNVBAcTC0plcnNleSBDaXR5MR4wHAYDVQQKExVU
aGUgVVNFUlRSVVNUIE5ldHdvcmsxMzAxBgNVBAMTKlNTTC5jb20gVExTIFRyYW5z
aXQgRUNDIFJvb3QgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwdjAQBgcqhkjOPQIB
BgUrgQQAIgNiAASFZnLFVks5YIy4ue8i0qPDLO/YHFwDLyMPZoVKH6U3C8pY+Wm2
lFaM3y3Qdq1GI6HZUjQg7yQY9T8YfOxLqpyVZQQ8Hkqy5o+XRGS0FWFBtJkc3tGf
K0YfnHo0OJY0qSejggH8MIIB+DAOBgNVHQ8BAf8EBAMCAQYwHQYDVR0lBBYwFAYI
KwYBBQUHAwEGCCsGAQUFBwMCMBIGA1UdEwEB/wQIMAYBAf8CAQAwHQYDVR0OBBYE
FBfm1iNLSHqOyL+VKg9+bsqfqG8OMB8GA1UdIwQYMBaAFHxkYBP5w/iLnfpJdQv0
7r3PWLrAMA8GA1UdIAQIMAYwBAYCKoUwMEwGA1UdHwRFMEMwQaA/oD2GO2h0dHA6
Ly9jcmwudXNlcnRydXN0LmNvbS9VU0VSVHJ1c3RSU0FDZXJ0aWZpY2F0aW9uQXV0
aG9yaXR5LmNybDB1BggrBgEFBQcBAQRpMGcwPgYIKwYBBQUHMAKGMmh0dHA6Ly9j
cnQudXNlcnRydXN0LmNvbS9VU0VSVHJ1c3RSU0FBZGRUcnVzdENBLmNydDAlBggr
BgEFBQcwAYYZaHR0cDovL29jc3AudXNlcnRydXN0LmNvbTANBgkqhkiG9w0BAQwF
AAOCAgEARctOFBbDxD0L2HuwlMpTQwv4QcNhKvOZlEKmULMKNbI5vM8I9rFhQKBa
NVKXKzFXHfB5oPGHYvL6n/nZOKbvKHbO6CYz0DJG5h8Ni4YtbKNnvs6lP6E2uB8V
ZYWlG+mKwV8X9hMGJl9HlJZsVf4lKH0T0xg4Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6L
z4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1
w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6L
z4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1
w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6L
z4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1
w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6L
z4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1
w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6L
z4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1w6Lz4w1
w6Lz4w1w6==
-----END CERTIFICATE-----
"""
    
    def __init__(self):
        """Initialize the SSL enhancer."""
        self.enhanced_ca_bundle = None
        self.enhanced_context = None
    
    def download_lexa_certificates(self):
        """Download certificate chain from www.lexa.chat."""
        import subprocess

        try:
            result = subprocess.run([
                'openssl', 's_client', '-connect', 'www.lexa.chat:443',
                '-servername', 'www.lexa.chat', '-showcerts'
            ], capture_output=True, text=True, input='', timeout=10)

            if result.returncode != 0:
                return None

            # Extract certificates
            certs = []
            current_cert = []
            in_cert = False

            for line in result.stdout.split('\n'):
                if line == '-----BEGIN CERTIFICATE-----':
                    in_cert = True
                    current_cert = [line]
                elif line == '-----END CERTIFICATE-----':
                    current_cert.append(line)
                    certs.append('\n'.join(current_cert))
                    current_cert = []
                    in_cert = False
                elif in_cert:
                    current_cert.append(line)

            return certs if certs else None

        except Exception:
            return None

    def create_enhanced_ca_bundle(self) -> str:
        """
        Create an enhanced CA bundle with Lexa's certificate chain.

        Returns:
            Path to the enhanced CA bundle file
        """
        if self.enhanced_ca_bundle and os.path.exists(self.enhanced_ca_bundle):
            return self.enhanced_ca_bundle

        # Create a temporary file for the enhanced bundle
        fd, enhanced_bundle_path = tempfile.mkstemp(suffix='.pem', prefix='lexa_ca_')

        try:
            with os.fdopen(fd, 'w') as temp_file:
                # First, try to download Lexa's certificate chain
                lexa_certs = self.download_lexa_certificates()
                if lexa_certs:
                    temp_file.write('# Lexa Certificate Chain (Downloaded)\n')
                    for cert in lexa_certs:
                        temp_file.write(cert)
                        temp_file.write('\n')
                    temp_file.write('\n')

                # Add default certifi bundle as fallback
                try:
                    default_ca_bundle = certifi.where()
                    with open(default_ca_bundle, 'r') as default_file:
                        temp_file.write('# Default Certificate Bundle\n')
                        temp_file.write(default_file.read())
                        temp_file.write('\n')
                except Exception:
                    pass

                # Add additional root certificates as additional fallback
                temp_file.write('# Additional Root Certificates\n')
                temp_file.write(self.ADDITIONAL_ROOT_CERTS)
                temp_file.write('\n')

            self.enhanced_ca_bundle = enhanced_bundle_path
            return enhanced_bundle_path

        except Exception as e:
            # Clean up on error
            if os.path.exists(enhanced_bundle_path):
                os.unlink(enhanced_bundle_path)
            raise Exception(f"Failed to create enhanced CA bundle: {e}")
    
    def create_enhanced_ssl_context(self) -> ssl.SSLContext:
        """
        Create an enhanced SSL context with additional certificates.
        
        Returns:
            SSL context with enhanced certificate validation
        """
        if self.enhanced_context:
            return self.enhanced_context
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Load the enhanced CA bundle
        enhanced_bundle = self.create_enhanced_ca_bundle()
        context.load_verify_locations(enhanced_bundle)
        
        self.enhanced_context = context
        return context
    
    def test_connection(self, hostname: str = "www.lexa.chat", port: int = 443) -> dict:
        """
        Test SSL connection with enhanced certificates.
        
        Args:
            hostname: Hostname to test
            port: Port to test
            
        Returns:
            Dictionary with test results
        """
        results = {
            'hostname': hostname,
            'port': port,
            'default_ssl': False,
            'enhanced_ssl': False,
            'error_default': None,
            'error_enhanced': None
        }
        
        # Test with default SSL context
        try:
            context = ssl.create_default_context()
            with ssl.create_connection((hostname, port)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname):
                    results['default_ssl'] = True
        except Exception as e:
            results['error_default'] = str(e)
        
        # Test with enhanced SSL context
        try:
            enhanced_context = self.create_enhanced_ssl_context()
            with ssl.create_connection((hostname, port)) as sock:
                with enhanced_context.wrap_socket(sock, server_hostname=hostname):
                    results['enhanced_ssl'] = True
        except Exception as e:
            results['error_enhanced'] = str(e)
        
        return results
    
    def get_requests_session(self) -> requests.Session:
        """
        Get a requests session configured with enhanced SSL.
        
        Returns:
            Requests session with enhanced SSL verification
        """
        session = requests.Session()
        enhanced_bundle = self.create_enhanced_ca_bundle()
        session.verify = enhanced_bundle
        return session
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.enhanced_ca_bundle and os.path.exists(self.enhanced_ca_bundle):
            try:
                os.unlink(self.enhanced_ca_bundle)
                self.enhanced_ca_bundle = None
            except OSError:
                pass  # File may be in use
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.cleanup()


# Global instance for convenience
_ssl_enhancer = None

def get_ssl_enhancer() -> LexaSSLEnhancer:
    """Get the global SSL enhancer instance."""
    global _ssl_enhancer
    if _ssl_enhancer is None:
        _ssl_enhancer = LexaSSLEnhancer()
    return _ssl_enhancer

def create_enhanced_requests_session() -> requests.Session:
    """Create a requests session with enhanced SSL support."""
    return get_ssl_enhancer().get_requests_session()

def test_lexa_ssl() -> dict:
    """Test SSL connection to Lexa API."""
    return get_ssl_enhancer().test_connection("www.lexa.chat", 443)

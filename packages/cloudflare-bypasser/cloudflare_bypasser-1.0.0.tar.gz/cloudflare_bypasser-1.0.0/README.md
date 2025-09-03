# CloudflareBypasser

A professional Python library for bypassing Cloudflare protection mechanisms without relying on external paid services, with optional support for captcha solving APIs.

## Features

- **Free operation** - Uses proprietary techniques without external services
- **Optional API support** - Integration with 2captcha, anticaptcha, capmonster, and others
- **Human behavior simulation** - Advanced behavioral patterns
- **Fingerprint spoofing** - Browser fingerprint randomization
- **Multiple strategies** - Various bypass techniques with automatic fallbacks
- **Robust architecture** - Built-in retry mechanisms and error handling
- **Simple API** - Clean and intuitive interface

## Installation

```bash
# Basic installation
pip install cloudflare-bypasser

# With advanced dependencies
pip install cloudflare-bypasser[advanced]

# With machine learning support
pip install cloudflare-bypasser[ml]

# Complete installation
pip install cloudflare-bypasser[advanced,ml]
```

## Quick Start

### Basic Usage (Free)

```python
from cloudflare_bypass import CloudflareBypasser

# Simple usage
with CloudflareBypasser() as bypasser:
    success = bypasser.bypass_url("https://example.com")
    if success:
        print("Bypass successful")
        print(f"Title: {bypasser.get_title()}")
        print(f"URL: {bypasser.get_current_url()}")
```

### With API Key (More Reliable)

```python
from cloudflare_bypass import CloudflareBypasser

# With captcha service
bypasser = CloudflareBypasser(
    captcha_service="2captcha",  # or "anticaptcha", "capmonster"
    api_key="your_api_key_here"
)

with bypasser:
    success = bypasser.bypass_url("https://protected-site.com")
    if success:
        page_source = bypasser.get_page_source()
        # Continue with your logic
```

### Advanced Configuration

```python
from cloudflare_bypass import CloudflareBypasser, BypassConfig, BypassMode

# Custom configuration
config = BypassConfig(
    mode=BypassMode.STEALTH,
    headless=True,
    simulate_human=True,
    enable_fingerprint_spoofing=True,
    captcha_service="anticaptcha",
    api_key="your_api_key",
    timeout=90,
    max_retries=3
)

with CloudflareBypasser(config=config) as bypasser:
    success = bypasser.bypass_url("https://difficult-site.com")
```

### Predefined Configurations

```python
from cloudflare_bypass import CloudflareBypasser, STEALTH_CONFIG, FAST_CONFIG

# Stealth mode
with CloudflareBypasser(config=STEALTH_CONFIG) as bypasser:
    success = bypasser.bypass_url("https://example.com")

# Fast mode
with CloudflareBypasser(config=FAST_CONFIG) as bypasser:
    success = bypasser.bypass_url("https://example.com")
```

## Advanced Examples

### Processing Multiple URLs

```python
from cloudflare_bypass import CloudflareBypasser

urls = [
    "https://site1.com",
    "https://site2.com", 
    "https://site3.com"
]

with CloudflareBypasser(captcha_service="2captcha", api_key="key") as bypasser:
    for url in urls:
        print(f"Processing: {url}")
        if bypasser.bypass_url(url):
            print(f"Success: {bypasser.get_title()}")
        else:
            print(f"Failed: {url}")
```

### Using Proxy

```python
config = BypassConfig(
    proxy="http://proxy:port",
    proxy_auth={"username": "user", "password": "pass"},
    captcha_service="capmonster",
    api_key="your_key"
)

with CloudflareBypasser(config=config) as bypasser:
    success = bypasser.bypass_url("https://example.com")
```

### Error Handling

```python
from cloudflare_bypass import CloudflareBypasser, CloudflareBypassError, DriverError

try:
    with CloudflareBypasser() as bypasser:
        success = bypasser.bypass_url("https://example.com")
        
        if success:
            element = bypasser.find_element("css selector", ".some-class")
            
except DriverError as e:
    print(f"Driver error: {e}")
except CloudflareBypassError as e:
    print(f"Bypass error: {e}")
except Exception as e:
    print(f"General error: {e}")
```

## Configuration

### Supported Captcha Services

| Service | Approximate Cost | Speed | Accuracy |
|---------|------------------|-------|----------|
| 2captcha | $2.99/1k | Medium | High |
| anticaptcha | $2.00/1k | High | Very High |
| capmonster | $1.60/1k | Very High | High |
| deathbycaptcha | $1.39/1k | Medium | Medium |

### Bypass Modes

- **AUTO**: Automatically detects the best method
- **STEALTH**: Stealth mode with advanced techniques
- **AGGRESSIVE**: Aggressive mode for difficult cases  
- **MINIMAL**: Fast mode for simple cases

## Performance

| Challenge Type | Success Rate | Average Time |
|----------------|--------------|--------------|
| JS Challenge | 85-95% | 5-15s |
| Simple Turnstile | 70-85% | 10-30s |
| Complex Turnstile | 40-60% | 30-60s |
| With API Service | 95-99% | 15-45s |

## Command Line Interface

```bash
# Basic bypass
cloudflare-bypasser bypass "https://example.com"

# With configuration
cloudflare-bypasser bypass "https://example.com" --mode stealth --headless

# With API key
cloudflare-bypasser bypass "https://example.com" --captcha-service 2captcha --api-key "your_key"

# Save results
cloudflare-bypasser bypass "https://example.com" --output page.html --screenshot shot.png

# Show package info
cloudflare-bypasser info

# Run tests
cloudflare-bypasser test
```

## Development

### Development Installation

```bash
git clone https://github.com/yourusername/cloudflare-bypass.git
cd cloudflare-bypass
pip install -e .[dev,advanced,ml]
```

### Running Tests

```bash
pytest tests/
pytest --cov=cloudflare_bypass tests/
```

### Code Quality

```bash
black cloudflare_bypass/
flake8 cloudflare_bypass/
mypy cloudflare_bypass/
```

## Legal Considerations

- Research and testing purposes
- Automation of your own websites
- Educational purposes
- Respect terms of service
- No malicious activities
- No unauthorized scraping

**Use this library responsibly and respect website terms of service.**

## Contributing

Contributions are welcome. Please:

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

- Documentation: https://cloudflarebypass.readthedocs.io/
- Issues: https://github.com/yourusername/cloudflare-bypass/issues
- Discussions: https://github.com/yourusername/cloudflare-bypass/discussions

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a complete list of changes and version history.

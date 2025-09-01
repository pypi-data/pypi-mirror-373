# Python wrapper for Kiosker API

This Python library provides a comprehensive wrapper for the Kiosker API, enabling developers to programmatically control and manage Kiosker devices. Kiosker is a professional web kiosk application for iOS that transforms iPads into secure, full-screen web browsers perfect for public displays, interactive kiosks, and digital signage solutions.

The kiosker-python-api package allows you to:
- **Remote Control**: Navigate web pages, refresh content, and control browser functions
- **Device Management**: Monitor device status, battery levels, and system information
- **Content Control**: Manage blackout screens for maintenance or emergency messaging
- **Screen Management**: Control screensaver behavior
- **System Maintenance**: Clear cookies, cache, and perform system operations
- **Network Discovery**: Automatically discover Kiosker devices on your network using ZeroConf

Whether you're managing a single kiosk or deploying a fleet of devices across multiple locations, this library provides the tools needed to integrate Kiosker devices into your existing infrastructure and workflows.

---

### Installation

```shell
pip install kiosker-python-api
```

---

### Setup

```python
KioskerAPI(host, token, port = 8081, ssl = False, verify = False)
```

```python
from kiosker import KioskerAPI
from kiosker import Status, Result, Blackout, ScreensaverState
api = KioskerAPI('10.0.1.100', 'token')
```

#### Constructor Parameters

- **host** (str): IP address or hostname of the Kiosker device
- **token** (str): Authentication token for API access
- **port** (int, optional): Port number (default: 8081)
- **ssl** (bool, optional): Use HTTPS instead of HTTP (default: False)
- **verify** (bool | ssl.SSLContext, optional): SSL certificate verification. Set to False to disable SSL verification for self-signed certificates (default: False)

---

### Device Discovery with ZeroConf

Kiosker devices advertise themselves on the local network using ZeroConf (Bonjour/mDNS) autodiscovery. This allows you to automatically discover Kiosker devices without needing to know their IP addresses beforehand.

#### Service Information

Kiosker devices broadcast the following service:
- **Service Type**: `_kiosker._tcp`
- **TXT Records**:
  - `version`: App version (e.g., "25.1.0 (230)")
  - `app`: App name (e.g., "Kiosker Pro")
  - `uuid`: Unique device identifier (e.g., "2904C1F2-93FB-4954-BF85-FAAEFBA814F6")

---

### Functions

#### Get Status
```python
status = api.status()

print('Status:')
print(f'Device ID: {status.device_id}')
print(f'Model: {status.model}')
print(f'OS version: {status.os_version}')
print(f'Battery level: {status.battery_level}%')
print(f'Battery state: {status.battery_state}')
print(f'Last interaction: {status.last_interaction}')
print(f'Last motion: {status.last_motion}')
print(f'App name: {status.app_name}')
print(f'App version: {status.app_version}')
print(f'Last status update: {status.last_update}')
```
**Description**: Retrieves the current status of the kiosk.

#### Ping the API
```python
result = api.ping()
print(f"Ping successful: {result}")
```
**Description**: Checks if the API is reachable. Returns `True` if successful, otherwise raises an error.

#### Navigate to a URL
```python
result = api.navigate_url('https://example.com')
print(f"Navigation result: {result}")
```
**Description**: Navigates the kiosk to the specified URL.

#### Refresh the Page
```python
result = api.navigate_refresh()
print(f"Refresh result: {result}")
```
**Description**: Refreshes the current page on the kiosk.

#### Navigate Home
```python
result = api.navigate_home()
print(f"Home navigation result: {result}")
```
**Description**: Navigates the kiosk to the home page.

#### Navigate Forward
```python
result = api.navigate_forward()
print(f"Navigate forward result: {result}")
```
**Description**: Navigates forward in the browser's history.

#### Navigate Backward
```python
result = api.navigate_backward()
print(f"Navigate backward result: {result}")
```
**Description**: Navigates backward in the browser's history.

#### Print
```python
result = api.print()
print(f"Print result: {result}")
```
**Description**: Sends a print command to the kiosk.

#### Clear Cookies
```python
result = api.clear_cookies()
print(f"Cookies cleared: {result}")
```
**Description**: Clears all cookies stored on the kiosk.

#### Clear Cache
```python
result = api.clear_cache()
print(f"Cache cleared: {result}")
```
**Description**: Clears the cache on the kiosk.

#### Interact with Screensaver
```python
result = api.screensaver_interact()
print(f"Screensaver interaction result: {result}")
```
**Description**: Simulates user interaction with the screensaver to prevent it from activating.

#### Set Screensaver State
```python
result = api.screensaver_set_disabled_state(disabled=True)
print(f"Screensaver disabled: {result}")
```
**Description**: Enables or disables the screensaver.

#### Get Screensaver State
```python
state = api.screensaver_get_state()
print(f"Screensaver state: {state}")
```
**Description**: Retrieves the current state of the screensaver (enabled or disabled).

#### Set Blackout
```python
from kiosker import Blackout

blackout = Blackout(
    visible=True,                   # Required: show blackout screen
    text="Maintenance in progress", # Optional: text to display
    background="#000000",           # Optional: background color (hex)
    foreground="#FFFFFF",           # Optional: foreground/text color (hex)
    icon="warning",                 # Optional: icon name (SF Symbol)
    expire=60,                      # Optional: time in seconds before blackout expires
    dismissible=True,               # Optional: allow user to dismiss blackout with a button
    buttonBackground="#FF0000",     # Optional: button background color (hex)
    buttonForeground="#FFFFFF",     # Optional: button text color (hex)
    buttonText="OK",                # Optional: button label
    sound="1003"                    # Optional: sound to play (SystemSoundID)
)
result = api.blackout_set(blackout)
print(f"Blackout set: {result}")
```
**Description**: Sets a blackout screen with customizable text, colors, expiration time, and optional button/sound options.

#### Get Blackout State
```python
blackout_state = api.blackout_get()
print(f"Blackout state: {blackout_state}")
```
**Description**: Retrieves the current state of the blackout screen.

#### Clear Blackout
```python
result = api.blackout_clear()
print(f"Blackout cleared: {result}")
```
**Description**: Clears the blackout screen.

---

### Objects

#### `Status`
Represents the current status of the kiosk.

**Attributes**:
- `battery_level` (int): Battery percentage.
- `battery_state` (str): Current battery state (e.g., charging, discharging).
- `model` (str): Device model.
- `os_version` (str): Operating system version.
- `app_name` (str): Name of the currently running app.
- `app_version` (str): Version of the currently running app.
- `last_interaction` (datetime): Timestamp of the last user interaction.
- `last_motion` (Optional[datetime]): Timestamp of the last detected motion.
- `last_update` (datetime): Timestamp of the last status update.
- `device_id` (str): Unique identifier for the device.

#### `Result`
Represents the result of an API operation.

**Attributes**:
- `error` (bool): Indicates if an error occurred.
- `reason` (Optional[str]): Reason for the error, if any.
- `function` (Optional[str]): Name of the function that caused the error.

#### `Blackout`
Represents a blackout screen configuration.

**Attributes**:
- `visible` (bool): Whether the blackout screen is visible.
- `background` (Optional[str]): Background color in hex format.
- `foreground` (Optional[str]): Foreground/text color in hex format.
- `expire` (Optional[int]): Time in seconds before the blackout screen expires.
- `text` (Optional[str]): Text to display on the blackout screen.
- `icon` (Optional[str]): Icon to display on the blackout screen.
- `dismissible` (Optional[bool]): Allow user to dismiss blackout with a button.
- `buttonBackground` (Optional[str]): Button background color (hex).
- `buttonForeground` (Optional[str]): Button text color (hex).
- `buttonText` (Optional[str]): Button label.
- `sound` (Optional[str]): Sound to play (SystemSoundID).

#### `ScreensaverState`
Represents the state of the screensaver.

**Attributes**:
- `visible` (bool): Whether the screensaver is currently visible.
- `disabled` (bool): Whether the screensaver is disabled (cannot activate).

---

### Development
1. Clone the project

2. Create a virtual environment
```shell
python3 -m venv venv
```

3. Activate the virtual environment
```shell
source venv/bin/activate
```

4. Install dependencies
```shell
pip install wheel setuptools twine pytest httpx
```

5. Run tests
```shell
HOST="0.0.0.0" TOKEN="" pytest -s
```

6. Build the library
```shell
python -m build
```

7. Upload to test
```shell
twine upload --repository testpypi dist/*
```

8. Upload to prod
```shell
twine upload dist/*
```

---

### API Documentation
- [Docs](https://docs.kiosker.io/#/api)
- [Definition](https://swagger.kiosker.io)

---

### Get Kiosker for iOS on the App Store
- [Kiosker](https://apps.apple.com/us/app/kiosker-fullscreen-web-kiosk/id1481691530?uo=4&at=11l6hc&ct=fnd)
- [Kiosker Pro](https://apps.apple.com/us/app/kiosker-pro-web-kiosk/id1446738885?uo=4&at=11l6hc&ct=fnd)
# ThingsBoardLink

**A high-level IoT platform interaction toolkit designed for Python developers**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

ThingsBoardLink is a powerful Python package designed to simplify integration with the ThingsBoard IoT platform. It encapsulates ThingsBoard's REST API, providing object-oriented interfaces that allow developers to easily manage devices, process telemetry data, control alarms, and other core functions.

## Key Features

- 🔐 **Authentication Management**: Automatic JWT token and session management
- 📱 **Device Management**: Complete device CRUD operations and credential management
- 📊 **Telemetry Data**: Data upload, querying, and historical data retrieval
- ⚙️ **Attribute Management**: Client, server, and shared attribute operations
- 🚨 **Alarm Management**: Alarm creation, querying, acknowledgment, and clearing
- 🔄 **RPC Calls**: One-way and two-way remote procedure calls
- 🔗 **Relationship Management**: Creation and management of entity relationships
- 🛡️ **Error Handling**: Comprehensive exception handling and error messages
- 📚 **Type Safety**: Complete TypeScript-style type hints
- 🚀 **Easy to Use**: Clean API design and rich documentation

## Installation

### Install using pip

```bash
pip install thingsboardlink
```

### Install from source

```bash
git clone https://github.com/thingsboardlink/thingsboardlink.git
cd thingsboardlink
pip install -e .
```

### Development installation

```bash
git clone https://github.com/thingsboardlink/thingsboardlink.git
cd thingsboardlink
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from thingsboardlink import ThingsBoardClient
from thingsboardlink.models import AlarmSeverity

# Create client
client = ThingsBoardClient(
    base_url="http://localhost:8080",
    username="tenant@thingsboard.org",
    password="tenant"
)

# Login
client.login()

# Create or get device
try:
    # Try to create device
    device = client.device_service.create_device(
        name="MyDevice",
        device_type="sensor",
        label="Temperature Sensor"
    )
    print(f"Device created: {device.name} (ID: {device.id})")
except Exception as e:
    if "already exists" in str(e):
        # Device already exists, get by name
        print("Device already exists, getting existing device")
        devices = client.device_service.get_devices_by_name("MyDevice")
        if devices:
            device = devices[0]
            print(f"Got existing device: {device.name} (ID: {device.id})")
        else:
            print("Cannot find existing device")
            raise
    else:
        raise

# Upload telemetry data
success = client.telemetry_service.post_telemetry(
    device_id=device.id,
    telemetry_data={
        "temperature": 25.5,
        "humidity": 60.0,
        "status": "online"
    }
)

if success:
    print("Telemetry data uploaded successfully")

# Get latest telemetry data
latest_data = client.telemetry_service.get_latest_telemetry(device.id)
print(f"Latest data: {latest_data}")

# Set device attributes
client.attribute_service.set_server_attributes(
    device_id=device.id,
    attributes={
        "location": "Building A, Floor 2",
        "model": "DHT22",
        "firmware_version": "1.2.3"
    }
)

# Create alarm
alarm = client.alarm_service.create_alarm(
    alarm_type="High Temperature",
    originator_id=device.id,
    severity=AlarmSeverity.CRITICAL,
    details={"threshold": 30.0, "current_value": 35.2}
)

print(f"Alarm created: {alarm.type}")

# Safe logout
client.logout()
```

### Using Context Manager

```python
from thingsboardlink import ThingsBoardClient

# Use context manager for automatic login/logout
with ThingsBoardClient(
    base_url="http://localhost:8080",
    username="tenant@thingsboard.org",
    password="tenant"
) as client:
    # Automatic login
    
    # Get device list
    devices = client.device_service.get_tenant_devices(page_size=10)
    
    for device in devices.data:
        print(f"Device: {device.name} - {device.type}")
        
        # Get all device attributes
        attributes = client.attribute_service.get_all_attributes(device.id)
        print(f"Attributes: {attributes}")
    
    # Automatic logout
```

## Detailed Examples

### Device Management

```python
# Create device
device = client.device_service.create_device(
    name="TemperatureSensor01",
    device_type="sensor",
    label="Office Temperature Sensor",
    additional_info={
        "location": "Office Room 101",
        "installation_date": "2024-01-15"
    }
)

# Get device info
device_info = client.device_service.get_device_by_id(device.id)
print(f"Device info: {device_info.name}")

# Update device
device.label = "Updated Sensor Label"
updated_device = client.device_service.update_device(device)

# Get device credentials
credentials = client.device_service.get_device_credentials(device.id)
print(f"Device token: {credentials.credentials_value}")

# Delete device
# client.device_service.delete_device(device.id)
```

### Telemetry Data Processing

```python
import time
from datetime import datetime, timedelta

# Upload single data point
client.telemetry_service.post_telemetry(
    device_id=device.id,
    telemetry_data={"temperature": 23.5}
)

# Upload data with timestamp
custom_timestamp = int(time.time() * 1000) - 3600000  # 1 hour ago
client.telemetry_service.post_telemetry(
    device_id=device.id,
    telemetry_data={"temperature": 22.0, "humidity": 55.0},
    timestamp=custom_timestamp
)

# Get historical data
end_time = int(time.time() * 1000)
start_time = end_time - 24 * 3600 * 1000  # 24 hours ago

historical_data = client.telemetry_service.get_timeseries_telemetry(
    device_id=device.id,
    keys=["temperature", "humidity"],
    start_ts=start_time,
    end_ts=end_time,
    limit=100
)

for key, timeseries in historical_data.items():
    print(f"Data key: {key}")
    print(f"Latest value: {timeseries.get_latest_value()}")
    print(f"Data points: {len(timeseries.values)}")
```

### Attribute Management

```python
from thingsboardlink.models import AttributeScope

# Set server attributes
client.attribute_service.set_server_attributes(
    device_id=device.id,
    attributes={
        "model": "DHT22",
        "firmware_version": "1.2.3",
        "last_maintenance": "2024-01-15"
    }
)

# Set shared attributes (configuration)
client.attribute_service.set_shared_attributes(
    device_id=device.id,
    attributes={
        "sampling_rate": 60,  # Sampling rate: 60 seconds
        "alert_threshold": 30.0,  # Alert threshold
        "enabled": True
    }
)

# Get all attributes
all_attributes = client.attribute_service.get_all_attributes(device.id)
print(f"Server attributes: {all_attributes['server']}")
print(f"Shared attributes: {all_attributes['shared']}")
print(f"Client attributes: {all_attributes['client']}")

# Delete attributes
client.attribute_service.delete_attributes(
    device_id=device.id,
    scope=AttributeScope.SERVER_SCOPE,
    keys=["last_maintenance"]
)
```

### Alarm Management

```python
from thingsboardlink.models import AlarmSeverity, AlarmStatus

# Create alarm
alarm = client.alarm_service.create_alarm(
    alarm_type="High Temperature",
    originator_id=device.id,
    severity=AlarmSeverity.CRITICAL,
    details={
        "message": "Temperature exceeds threshold",
        "threshold": 30.0,
        "current_value": 35.2,
        "location": "Office Room 101"
    }
)

# Get all alarms for device
alarms = client.alarm_service.get_alarms(
    originator_id=device.id,
    page_size=10,
    status_list=[AlarmStatus.ACTIVE_UNACK, AlarmStatus.ACTIVE_ACK]
)

print(f"Active alarms count: {len(alarms.data)}")

# Acknowledge alarm
if alarms.data:
    first_alarm = alarms.data[0]
    client.alarm_service.ack_alarm(first_alarm.id)
    print(f"Alarm acknowledged: {first_alarm.type}")

# Clear alarm
# client.alarm_service.clear_alarm(first_alarm.id)
```

### RPC Calls

```python
# Send one-way RPC (device control)
success = client.rpc_service.send_one_way_rpc(
    device_id=device.id,
    method="setLedState",
    params={"enabled": True, "brightness": 80}
)

if success:
    print("Device control command sent")

# Send two-way RPC (get device status)
try:
    response = client.rpc_service.send_two_way_rpc(
        device_id=device.id,
        method="getDeviceStatus",
        params={},
        timeout_seconds=10.0
    )
    
    if response.is_success:
        print(f"Device status: {response.response}")
    else:
        print(f"RPC call failed: {response.error}")
        
except Exception as e:
    print(f"RPC call exception: {e}")

# Send persistent RPC (queued when device offline)
rpc_id = client.rpc_service.send_persistent_rpc(
    device_id=device.id,
    method="updateFirmware",
    params={"version": "1.3.0", "url": "https://example.com/firmware.bin"},
    timeout_seconds=300.0
)

print(f"Persistent RPC sent: {rpc_id}")

# Wait for persistent RPC response
try:
    response = client.rpc_service.wait_for_rpc_response(
        rpc_id=rpc_id,
        timeout_seconds=60.0,
        poll_interval=2.0
    )
    print(f"Firmware update response: {response.response}")
except Exception as e:
    print(f"Wait for RPC response timeout: {e}")
```

## API Reference

### Core Client

#### ThingsBoardClient

Main client class providing unified interface for ThingsBoard platform interaction.

**Initialization Parameters:**
- `base_url`: ThingsBoard server base URL
- `username`: Username (optional)
- `password`: Password (optional)
- `timeout`: Request timeout (default 30 seconds)
- `max_retries`: Maximum retry count (default 3)
- `verify_ssl`: Whether to verify SSL certificates (default True)

**Main Methods:**
- `login(username, password)`: User login
- `logout()`: User logout
- `is_authenticated`: Check authentication status

**Service Properties:**
- `device_service`: Device management service
- `telemetry_service`: Telemetry data service
- `attribute_service`: Attribute management service
- `alarm_service`: Alarm management service
- `rpc_service`: RPC call service
- `relation_service`: Relationship management service

### Service Classes

#### DeviceService - Device Management Service

- `create_device(name, device_type, label, additional_info)`: Create device
- `get_device_by_id(device_id)`: Get device information
- `update_device(device)`: Update device
- `delete_device(device_id)`: Delete device
- `get_tenant_devices(page_size, page, text_search)`: Get device list
- `get_device_credentials(device_id)`: Get device credentials
- `device_exists(device_id)`: Check if device exists

#### TelemetryService - Telemetry Data Service

- `post_telemetry(device_id, telemetry_data, timestamp)`: Upload telemetry data
- `get_latest_telemetry(device_id, keys)`: Get latest telemetry data
- `get_timeseries_telemetry(device_id, keys, start_ts, end_ts)`: Get historical data
- `delete_telemetry(device_id, keys, start_ts, end_ts)`: Delete telemetry data
- `get_telemetry_keys(device_id)`: Get telemetry data keys list

#### AttributeService - Attribute Management Service

- `get_client_attributes(device_id, keys)`: Get client attributes
- `get_server_attributes(device_id, keys)`: Get server attributes
- `get_shared_attributes(device_id, keys)`: Get shared attributes
- `set_client_attributes(device_id, attributes)`: Set client attributes
- `set_server_attributes(device_id, attributes)`: Set server attributes
- `set_shared_attributes(device_id, attributes)`: Set shared attributes
- `delete_attributes(device_id, scope, keys)`: Delete attributes
- `get_all_attributes(device_id)`: Get all attributes

#### AlarmService - Alarm Management Service

- `create_alarm(alarm_type, originator_id, severity, details)`: Create alarm
- `get_alarm(alarm_id)`: Get alarm information
- `get_alarms(originator_id, page_size, page, status_list)`: Get alarm list
- `ack_alarm(alarm_id)`: Acknowledge alarm
- `clear_alarm(alarm_id)`: Clear alarm
- `delete_alarm(alarm_id)`: Delete alarm
- `get_highest_alarm_severity(originator_id)`: Get highest alarm severity

#### RpcService - RPC Call Service

- `send_one_way_rpc(device_id, method, params)`: Send one-way RPC
- `send_two_way_rpc(device_id, method, params, timeout_seconds)`: Send two-way RPC
- `send_persistent_rpc(device_id, method, params, timeout_seconds)`: Send persistent RPC
- `get_persistent_rpc(rpc_id)`: Get persistent RPC response
- `wait_for_rpc_response(rpc_id, timeout_seconds)`: Wait for RPC response
- `send_rpc_with_retry(device_id, method, params, max_retries)`: RPC call with retry

#### RelationService - Relationship Management Service

- `create_relation(from_id, from_type, to_id, to_type, relation_type)`: Create relationship
- `delete_relation(from_id, from_type, to_id, to_type, relation_type)`: Delete relationship
- `get_relation(from_id, from_type, to_id, to_type, relation_type)`: Get relationship
- `find_by_from(from_id, from_type)`: Find relationships from specified entity
- `find_by_to(to_id, to_type)`: Find relationships to specified entity
- `relation_exists(from_id, from_type, to_id, to_type, relation_type)`: Check if relationship exists

## Error Handling

ThingsBoardLink provides comprehensive exception handling:

```python
from thingsboardlink import (
    ThingsBoardError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    APIError,
    ConnectionError,
    TimeoutError
)

try:
    client = ThingsBoardClient("http://localhost:8080")
    client.login("invalid_user", "invalid_password")
    
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    print(f"Error details: {e.details}")
    
except ConnectionError as e:
    print(f"Connection failed: {e}")
    
except ValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Field name: {e.details.get('field_name')}")
    
except APIError as e:
    print(f"API call failed: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response data: {e.response_data}")
    
except ThingsBoardError as e:
    print(f"ThingsBoard error: {e}")
    print(f"Error dict: {e.to_dict()}")
```

## Configuration

### Environment Variables

You can use environment variables to configure the client:

```bash
export THINGSBOARD_URL="http://localhost:8080"
export THINGSBOARD_USERNAME="tenant@thingsboard.org"
export THINGSBOARD_PASSWORD="tenant"
```

```python
import os
from thingsboardlink import ThingsBoardClient

client = ThingsBoardClient(
    base_url=os.getenv("THINGSBOARD_URL"),
    username=os.getenv("THINGSBOARD_USERNAME"),
    password=os.getenv("THINGSBOARD_PASSWORD")
)
```

### Advanced Configuration

```python
client = ThingsBoardClient(
    base_url="https://demo.thingsboard.io",
    username="tenant@thingsboard.org",
    password="tenant",
    timeout=60.0,  # Request timeout
    max_retries=5,  # Maximum retries
    retry_backoff_factor=0.5,  # Retry backoff factor
    verify_ssl=True  # SSL certificate verification
)
```

## Development

### Setting up Development Environment

```bash
# Clone repository
git clone https://github.com/thingsboardlink/thingsboardlink.git
cd thingsboardlink

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_device_service.py

# Run tests with coverage
pytest --cov=thingsboardlink --cov-report=html
```

### Code Quality Checks

```bash
# Code formatting
black src/thingsboardlink

# Import sorting
isort src/thingsboardlink

# Code linting
flake8 src/thingsboardlink

# Type checking
mypy src/thingsboardlink
```

## Contributing

We welcome all forms of contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

- 📖 **Documentation**: None
- 🐛 **Bug Reports**: None
- 💬 **Discussions**: None
- 📧 **Email**: None

## Acknowledgments

- Thanks to the [ThingsBoard](https://thingsboard.io/) team for providing an excellent IoT platform
- Thanks to all contributors and users for their support

---

**ThingsBoardLink** - Making IoT development easier
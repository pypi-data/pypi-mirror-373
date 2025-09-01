# Cobalt SDK

Python SDK containing utilities and useful extensions when working with the cobalt perception stack.

At the moment, this is more of an API intended for talking to a backend perception pipeline, but eventually it will be extended with more advanced features.

## Features

- WebSocket connections to Cobalt perception stack
- Object detection data structures with ctypes for efficient binary data handling
- Support for subscribing to object detection streams
- Async/await support for real-time data processing

## Installation

### From PyPI (when published)

```bash
pip install cobalt-sdk
```

### From source

```bash
git clone https://github.com/ceptontech/cobalt.git
cd cobalt/cobalt-py-sdk
pip install .
```

### Using requirements.txt

```bash
pip install -r requirements.txt
```

## Development Installation

For development work, install the package in editable mode with development dependencies:

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or using requirements files
pip install -r requirements-dev.txt
pip install -e .
```

### Development Dependencies

The development environment includes:
- `pytest>=7.0` - Testing framework
- `black>=22.0` - Code formatter
- `flake8>=4.0` - Linting
- `mypy>=0.950` - Type checking

## Usage

### API Reference

#### Connection Functions

- `proto_connect()` - Connect to protocol WebSocket (port 23787)
- `data_connect()` - Connect to data WebSocket (port 9030)
- `subscribe_objects(ws)` - Subscribe to object detection data on a WebSocket connection

#### Data Structures

**Object** - Represents a single detected object:
- `x`, `y`, `z` (float) - 3D position coordinates
- `length`, `width`, `height` (float) - Object dimensions
- `theta` (float) - Rotation angle
- `classification` (uint32) - Object classification ID
- `object_id` (uint32) - Unique object identifier

**Objects** - Frame containing multiple objects:
- `magic` - Frame identifier ("COBJ")
- `num_objects` (uint32) - Number of objects in frame
- `sequence_id` (uint32) - Frame sequence number
- `objects` - List of Object instances

**ForegroundCloud** - Frame of a foreground point cloud:
- `magic` - Frame identifier ("FGCL")
- `num_points` (uint32) - Number of points in frame
- `sequence_id` (uint32) - Frame sequence number
- `positions` - NumPy array of each points' coordinates [[x, y, z], ...] 

**BackgroundCloud** - Frame of a background point cloud:
- `magic` - Frame identifier ("BGCL")

    ...the rest is the same as ForegroundCloud

**GroundCloud** - Frame of a ground point cloud:
- `magic` - Frame identifier ("GRCL")

    ...the rest is the same as ForegroundCloud

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ samples/
```

### Linting

```bash
flake8 src/ samples/
```

### Type Checking

```bash
mypy src/
```

## Requirements

- Python >= 3.8
- websockets library for WebSocket connections
- NumPy library for point clouds manipulation

## Examples

See the `samples/` directory for complete examples:
- `connection_example.py` - Basic connection and object subscription example

## License

MIT License - see LICENSE file for details

## Contributing

1. Install development dependencies: `pip install -e ".[dev]"`
2. Make your changes
3. Run tests: `pytest`
4. Format code: `black .`
5. Check linting: `flake8`
6. Submit a pull request

## Support

For issues and questions, please visit: https://github.com/ceptontech/cobalt/issues

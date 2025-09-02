# ROS2Top

A real-time monitor for ROS2 nodes showing CPU, RAM, and GPU usage - like `htop` but for ROS2 nodes.

<!-- ![ROS2Top Demo]() -->

## Features

- 🔍 **Real-time monitoring** of all ROS2 nodes
- 💻 **CPU usage** tracking per node
- 🧠 **RAM usage** monitoring
- 🎮 **GPU usage** tracking (NVIDIA GPUs via NVML)
- 🖥️ **Terminal-based interface** using curses
- 🔄 **Auto-refresh** with configurable intervals
- 🏷️ **Process tree awareness** (includes child processes)
- 📝 **Node registration API** for reliable node-to-monitor communication

## Installation

### From PyPI (when published)

```bash
pip install ros2top
```

### From Source

```bash
git clone https://github.com/AhmedARadwan/ros2top.git
cd ros2top
pip install -e .
```

## Requirements

- Python 3.8+
- NVIDIA drivers (for GPU monitoring)

### Python Dependencies

- `psutil>=5.8.0`
- `pynvml>=11.0.0`

### CPP Dependencies

- [nlohmann json](https://github.com/nlohmann/json) installed from source.

## Usage

### Examples

- **[Python Example](examples/python/README.md)**: Complete ROS2 Python node with ros2top integration
- **[C++ Example](examples/cpp/README.md)**: Complete ROS2 C++ package with ros2top integration

### Basic Usage

```bash
# Run ros2top
ros2top
```

### Command Line Options

```bash
ros2top --help                # Show help
ros2top --refresh 2          # Refresh every 2 seconds (default: 5)
ros2top --version           # Show version
```

### Interactive Controls

The enhanced terminal UI provides responsive and interactive controls:

| Key        | Action                        |
| ---------- | ----------------------------- |
| `q` or `Q` | Quit application              |
| `h` or `H` | Show help dialog              |
| `r` or `R` | Force refresh node list       |
| `p` or `P` | Pause/resume monitoring       |
| `+` or `=` | Increase refresh rate         |
| `-`        | Decrease refresh rate         |
| `↑` / `↓`  | Navigate through nodes        |
| `Tab`      | Cycle focus between UI panels |
| `Space`    | Force immediate update        |
| `Home/End` | Jump to first/last node       |

## Terminal UI

### Visual Features

- **Color-coded usage bars**: Green (low), Yellow (medium), Red (high)
- **Real-time progress bars** for CPU, memory, and GPU
- **Interactive navigation** with keyboard shortcuts
- **Adaptive refresh rates** for optimal performance

### System Overview Panel

The top panel shows real-time system information:

- CPU usage (per-core or summary based on terminal size)
- Memory usage with progress bar
- GPU utilization and memory (if available)
- ROS2 status and active node count

## Display Columns

| Column      | Description                                     |
| ----------- | ----------------------------------------------- |
| **Node**    | ROS2 node name                                  |
| **PID**     | Process ID                                      |
| **%CPU**    | CPU usage percentage (normalized by core count) |
| **RAM(MB)** | RAM usage in megabytes                          |
| **GPU#**    | GPU device number (if using GPU)                |
| **GPU%**    | GPU utilization percentage                      |
| **GMEM**    | GPU memory usage in MB                          |

## Examples

### Monitor nodes with 2-second refresh

```bash
ros2top --refresh 2
```

## How It Works

1. **Node Registartion**: Every node registers its name and PID at startup with ros2top.
2. **Resource Monitoring**: Uses `psutil` for CPU/RAM and `pynvml` for GPU metrics.
3. **Display**: Curses-based terminal interface for real-time updates.

## Troubleshooting

### No GPU monitoring

- Install NVIDIA drivers
- Install pynvml: `pip install pynvml`

### Nodes not showing up

- Verify nodes are running: `ros2 node list`
- Check node info: `ros2 node info /your_node`
- Some nodes might not have detectable PIDs

## Development

### Setup Development Environment

```bash
git clone https://github.com/AhmedARadwan/ros2top.git
cd ros2top
pip install -e .
```

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

```bash
black ros2top/
flake8 ros2top/
mypy ros2top/
```

## Architecture

```text
ros2top/
├── ros2top/                 # Python package
│   ├── __init__.py         # Package initialization and public API
│   ├── main.py             # CLI entry point
│   ├── node_monitor.py     # Core monitoring logic
│   ├── node_registry.py    # Node registration system
│   ├── gpu_monitor.py      # GPU monitoring
│   ├── ros2_utils.py       # ROS2 utilities
│   └── ui/                 # User interface components
│       ├── __init__.py
│       ├── terminal_ui.py  # Main curses interface
│       ├── components.py   # UI components
│       └── layout.py       # UI layout management
├── include/                # C++ headers
│   └── ros2top/
│       └── ros2top.hpp     # C++ API for node registration
├── examples/               # Example integrations
│   ├── python/             # Python examples
│   │   ├── README.md
│   │   └── example_node.py
│   └── cpp/                # C++ examples
│       ├── README.md
│       └── example_monitored_node/  # Complete ROS2 package
├── tests/                  # Test suite
│   ├── __init__.py
│   └── test_ros2top.py
├── cmake/                  # CMake configuration
├── pyproject.toml          # Python build configuration
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT license
└── README.md              # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.3

- Remove dependency on ROS2 to start ros2top.

### v0.1.2

- Enhance README

### v0.1.1

- Add example usage
- Enhance README

### v0.1.0

- Initial release
- Basic node monitoring with CPU, RAM, GPU usage
- Terminal interface with curses
- Command line options
- Node registration and process mapping

## Similar Tools

- `htop` - System process monitor
- `nvtop` - GPU process monitor
- `ros2 node list` - Basic ROS2 node listing

## Acknowledgments

- Inspired by `htop` and `nvtop`
- Built for the ROS2 community
- Uses `psutil` for system monitoring and `pynvml` for GPU monitoring

## Node Registration API

For the most reliable monitoring, ROS2 nodes can register themselves with `ros2top`. This is especially useful for:

- Multiple nodes running in the same Python process
- Complex applications where automatic detection might miss some nodes
- Getting additional metadata about nodes

### Basic Registration

```python
import ros2top

# Register your node (call this once when your node starts)
ros2top.register_node('/my_node_name')

# Send periodic heartbeats (optional, but recommended)
ros2top.heartbeat('/my_node_name')

# Unregister when shutting down (optional, automatic cleanup on process exit)
ros2top.unregister_node('/my_node_name')
```

### Advanced Registration with Metadata

```python
import ros2top

# Register with additional information
ros2top.register_node('/camera_processor', {
    'description': 'Processes camera feed for object detection',
    'type': 'vision_processor',
    'input_topics': ['/camera/image_raw'],
    'output_topics': ['/detected_objects'],
    'framerate': 30
})

# In your main loop, send heartbeats every few seconds
ros2top.heartbeat('/camera_processor')
```

## Node Detection

`ros2top` uses a **node registration system** for reliable node detection:

### Primary Method: Node Registration API

The most reliable way is for ROS2 nodes to explicitly register themselves:

```python
import ros2top

# Register your node
ros2top.register_node('/my_node', {'description': 'My awesome node'})

# Send periodic heartbeats (recommended)
ros2top.heartbeat('/my_node')

# Unregister when shutting down (optional - automatic cleanup on exit)
ros2top.unregister_node('/my_node')
```

### Automatic Cleanup

- Nodes are automatically unregistered when the process exits
- Stale registrations are cleaned up periodically
- Registry is stored in `~/.ros2top/registry/`

### Benefits of Registration API

- **Reliable**: No dependency on tracing or process matching
- **Fast**: Instant node detection without scanning
- **Accurate**: Direct PID mapping from the registering process
- **Simple**: Works with any ROS2 node type (Python, C++, etc.)

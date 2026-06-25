# Covenant - ROS 2 Autonomous Drone System

A modular ROS 2 workspace for autonomous drone operations, integrating ArduPilot DDS communication, LIDAR odometry, and navigation. Designed for **ROS 2 Jazzy** on Raspberry Pi 5 with serial connection to an ArduPilot flight controller.

---

## 📁 Project Structure

The repository is organized into two main areas:

```
covenant/
├── covenant_main/          # Your custom ROS 2 package
│   ├── config/             # YAML configuration files (EKF, SLAM, Nav2, QoS)
│   ├── covenant_main/      # Python source code (UDP bridges, arming server, LIDAR test)
│   ├── launch/             # Launch files for SLAM and navigation
│   ├── package.xml         # ROS 2 package manifest
│   ├── setup.py            # Python package setup
│   └── test/               # Unit tests (flake8, pep257, copyright)
│
└── vendor/                 # Git submodules (third-party dependencies)
    ├── ardupilot/          # ArduPilot source (provides ardupilot_msgs)
    ├── micro_ros_agent/    # micro-ROS DDS bridge (serial ↔ ROS 2)
    ├── ldrobot-d500-ros2/  # LDROBOT D500 LIDAR driver
    └── rf2o_laser_odometry/# Range-Flow 2D laser odometry
```

### covenant_main (Your Package)

This package contains all your custom nodes:

- **`arm_command_udp_server.py`** – Receives arming commands via UDP and publishes to `/ap/cmd_vel`
- **`ros_topics_udp_bridge.py`** – Bridges ROS 2 topics to UDP for external control/telemetry
- **`test_udp_sender_lidar.py`** – Test utility for LIDAR data over UDP

### vendor (Git Submodules)

These are external dependencies managed as Git submodules. They are not stored directly in this repository—only their references are tracked.

| Submodule | Purpose |
| :--- | :--- |
| `ardupilot` | Provides `ardupilot_msgs` message definitions for DDS communication |
| `micro_ros_agent` | Serial-to-DDS bridge that translates FC data to ROS 2 topics |
| `ldrobot-d500-ros2` | LIDAR driver for LDROBOT D500 series |
| `rf2o_laser_odometry` | Laser odometry package for 2D range-flow estimation |

---

## 🚀 Quick Setup

### 1. Clone the Repository

```bash
git clone --recurse-submodules git@github.com:N-rwal/covenant.git
cd covenant
```

### 2. Initialize Submodules (Shallow Clones to Save Space)

```bash
# Initialize all submodules with shallow clones where possible
git submodule update --init --depth 1 vendor/ardupilot
git submodule update --init --depth 1 vendor/micro_ros_agent
git submodule update --init vendor/ldrobot-d500-ros2
git submodule update --init vendor/rf2o_laser_odometry
```

### 3. Build the Workspace

Place the `covenant` folder inside your ROS 2 workspace `src/` directory, then build:

```bash
cd ~/your_ros_ws
colcon build --packages-select micro_ros_agent ardupilot_msgs covenant_main
```

### 4. Source and Run

```bash
source ~/your_ros_ws/install/setup.bash
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
```

---

## 🔌 Flight Controller Setup

Configure these ArduPilot parameters (via Mission Planner or QGC):

| Parameter | Value | Notes |
| :--- | :--- | :--- |
| `DDS_ENABLE` | `1` | Enables DDS output |
| `SERIALx_PROTOCOL` | `45` | `x` = UART port connected to USB adapter |
| `SERIALx_BAUD` | `115` | Must match agent's `-b 115200` |

**⚠️ Important:** Ensure **GND** is connected between the FC and USB‑to‑serial adapter.

---

## 📡 Key Topics

| Topic | Description |
| :--- | :--- |
| `/ap/pose/filtered` | Position & orientation from EKF |
| `/ap/imu/experimental/data` | High‑frequency IMU data |
| `/ap/navsat` | GPS data (latitude, longitude, altitude) |
| `/ap/battery` | Voltage, current, remaining capacity |
| `/ap/cmd_vel` | Velocity commands (published to FC) |

---

## 🐛 Troubleshooting Quick Reference

| Issue | Solution |
| :--- | :--- |
| `Permission denied` on `/dev/ttyUSB0` | `sudo usermod -a -G dialout $USER` + reboot |
| `NotEnoughMemoryException` | Switch to Cyclone DDS: `export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` |
| No topics | Verify `DDS_ENABLE=1` and GND connection |
| Agent hangs | Ensure FC is powered and baud rate matches |

---

## 📝 License

[Add your license here]

---

**Happy flying! 🚁**

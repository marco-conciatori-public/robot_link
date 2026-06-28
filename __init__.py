"""
robot_link: code shared by the two onboard computers of the Yahboom RDK X3 robot.

The RDK X3 board ("the brain") and the Jetson Nano talk over a wired point-to-point
Ethernet link. This package is the single source of truth for everything that must match
on both sides: the wire protocol (framing of commands, audio and video), the YAML config
loader, the network endpoints, and a couple of small shared helpers.

It is included in both repositories as a git submodule, so a change here updates both
computers from one place and the two sides can never drift apart on the byte layout.

The package is deliberately dependency-light (standard library plus PyYAML) and has no
ROS2 dependency, so it imports cleanly on the Jetson (where ROS2 Foxy is not available).
"""

"""
Canonical network endpoints and audio formats for the intra-robot link.

The RDK X3 (static address on the point-to-point Ethernet link) is the TCP server on every
channel; the Jetson Nano always connects out to it. These values MUST be identical on both
computers, so defining them once here removes the risk of the two sides drifting (previously
each port was restated in several YAML files on each machine).

These are protocol invariants rather than per-run tunables, so they live in code. A per-repo
YAML config may still override any of them where a deployment genuinely needs to (the config
loaders treat these as the fallback default).
"""

# Wired link: the RDK X3 side.
ROBOT_HOST = '192.168.10.11'

# TCP ports, one concern per port.
COMMAND_PORT = 65432           # bidirectional JSON command channel
ARM_CAMERA_PORT = 65433        # arm camera JPEG pull stream (Jetson -> RDK X3)
MIC_STREAM_PORT = 65434        # microphone stream (RDK X3 -> Jetson)
SPEAKER_PLAYBACK_PORT = 65435  # TTS playback (Jetson -> RDK X3)

# Audio formats (mono int16 PCM). The detailed ALSA capture/playback parameters stay in
# audio_bridge_server.yaml on the RDK X3; these are the rates both sides agree on.
MIC_SAMPLE_RATE = 16000
SPEAKER_SAMPLE_RATE = 24000

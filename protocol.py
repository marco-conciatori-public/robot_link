"""
Wire protocol for the intra-robot TCP link (RDK X3 <-> Jetson Nano).

This is the ONE definition of the byte layout used on every channel, so the two computers
can never drift apart. These are plain blocking-socket helpers with no ROS2 dependency.

Framing primitives:
  - length-prefixed message:  [4-byte big-endian length][payload]
        used for JSON commands, TTS PCM playback, and JPEG camera frames.
  - VAD-tagged audio frame:   [1-byte flag][4-byte big-endian length][payload]
        used for the microphone stream (the flag is the ReSpeaker hardware VAD).

Higher-level helpers (send_command / recv_command) layer a JSON {"name", "args"} object
on top of a length-prefixed message.

Return-value convention for the recv_* helpers:
  - a value (bytes / tuple / dict, possibly an empty payload) means a frame was received;
  - None means the peer closed the connection (cleanly or mid-frame).
"""

import json
import struct

# 4-byte big-endian unsigned length prefix, shared by every framed message.
LENGTH_PREFIX_BYTES = 4
_LENGTH_STRUCT = struct.Struct('>I')


def recv_exactly(sock, num_bytes):
    """
    Receive exactly num_bytes from the socket.

    Returns the bytes, or None if the peer closed the connection before all bytes arrived.
    recv() may return fewer bytes than requested, so we loop until we have them all.
    """
    buffer = bytearray()
    while len(buffer) < num_bytes:
        chunk = sock.recv(num_bytes - len(buffer))
        if not chunk:
            return None
        buffer += chunk
    return bytes(buffer)


def send_message(sock, payload):
    """Send a length-prefixed binary message: [4-byte big-endian length][payload]."""
    sock.sendall(_LENGTH_STRUCT.pack(len(payload)) + payload)


def recv_message(sock):
    """
    Receive one length-prefixed message.

    Returns the payload bytes (b'' when the sender framed a zero-length message, e.g. the
    camera relay's "no frame available yet"), or None if the peer closed the connection.
    """
    length_prefix = recv_exactly(sock, LENGTH_PREFIX_BYTES)
    if length_prefix is None:
        return None
    length = _LENGTH_STRUCT.unpack(length_prefix)[0]
    if length == 0:
        return b''
    return recv_exactly(sock, length)


def send_command(sock, name, args=None):
    """
    Send a JSON command as a length-prefixed UTF-8 message.

    Layout of the JSON object: {"name": <str>, "args": <dict>}. This matches what the
    RDK X3 FunctionCaller and the Jetson command dispatcher expect.
    """
    payload = json.dumps({'name': name, 'args': {} if args is None else args}).encode('utf-8')
    send_message(sock, payload)


def recv_command(sock):
    """
    Receive one JSON command.

    Returns a dict {"name", "args"}, or None if the peer closed the connection (or framed an
    empty message).
    """
    payload = recv_message(sock)
    if not payload:
        return None
    data = json.loads(payload.decode('utf-8'))
    return {'name': data.get('name'), 'args': data.get('args')}


def send_audio_frame(sock, pcm_bytes, is_voice):
    """Send a microphone frame: [1-byte VAD flag][4-byte big-endian length][PCM bytes]."""
    flag = b'\x01' if is_voice else b'\x00'
    sock.sendall(flag + _LENGTH_STRUCT.pack(len(pcm_bytes)) + pcm_bytes)


def recv_audio_frame(sock):
    """
    Receive one microphone frame.

    Returns (is_voice: bool, pcm_bytes: bytes); pcm_bytes may be b'' for a silent/empty
    frame. Returns None if the peer closed the connection (during the header or the PCM).
    """
    header = recv_exactly(sock, 1 + LENGTH_PREFIX_BYTES)
    if header is None:
        return None
    is_voice = bool(header[0])
    length = _LENGTH_STRUCT.unpack(header[1:])[0]
    if length == 0:
        return is_voice, b''
    pcm_bytes = recv_exactly(sock, length)
    if pcm_bytes is None:
        return None
    return is_voice, pcm_bytes

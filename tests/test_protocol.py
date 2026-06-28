"""
Unit tests for robot_link.protocol, exercising the framing over a real socket pair.

Run from the directory that contains the robot_link package (its grandparent of this file),
e.g.  python -m pytest robot_link/tests/test_protocol.py
or simply  python robot_link/tests/test_protocol.py
"""

import sys
import socket
import threading
from pathlib import Path

# Make the robot_link package importable when this file is run directly (the package dir is
# two levels up: <grandparent>/robot_link/tests/test_protocol.py).
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from robot_link import protocol


def _pair():
    a, b = socket.socketpair()
    return a, b


def test_recv_exactly_reassembles_chunks():
    a, b = _pair()
    try:
        payload = bytes(range(256)) * 10  # 2560 bytes, likely split across several recv() calls

        def send():
            # send in small slices to force recv_exactly to loop
            for i in range(0, len(payload), 7):
                a.sendall(payload[i:i + 7])

        threading.Thread(target=send).start()
        got = protocol.recv_exactly(b, len(payload))
        assert got == payload
    finally:
        a.close()
        b.close()


def test_recv_exactly_returns_none_on_close():
    a, b = _pair()
    try:
        a.sendall(b'abc')
        a.close()  # only 3 bytes will ever arrive
        assert protocol.recv_exactly(b, 10) is None
    finally:
        b.close()


def test_message_roundtrip():
    a, b = _pair()
    try:
        payload = b'\x00\x01\x02hello world' * 1000
        protocol.send_message(a, payload)
        assert protocol.recv_message(b) == payload
    finally:
        a.close()
        b.close()


def test_zero_length_message():
    a, b = _pair()
    try:
        protocol.send_message(a, b'')
        # b'' (a framed empty message) is distinct from None (peer closed)
        assert protocol.recv_message(b) == b''
    finally:
        a.close()
        b.close()


def test_recv_message_none_on_close():
    a, b = _pair()
    try:
        a.close()
        assert protocol.recv_message(b) is None
    finally:
        b.close()


def test_command_roundtrip():
    a, b = _pair()
    try:
        protocol.send_command(a, 'turn_on_headlight', {'level': 2})
        command = protocol.recv_command(b)
        assert command == {'name': 'turn_on_headlight', 'args': {'level': 2}}
    finally:
        a.close()
        b.close()


def test_command_defaults_args_to_empty_dict():
    a, b = _pair()
    try:
        protocol.send_command(a, 'toggle_headlight')
        command = protocol.recv_command(b)
        assert command == {'name': 'toggle_headlight', 'args': {}}
    finally:
        a.close()
        b.close()


def test_audio_frame_roundtrip():
    a, b = _pair()
    try:
        pcm = (b'\x10\x20' * 4096)
        protocol.send_audio_frame(a, pcm, is_voice=True)
        is_voice, got = protocol.recv_audio_frame(b)
        assert is_voice is True
        assert got == pcm
    finally:
        a.close()
        b.close()


def test_audio_frame_silence():
    a, b = _pair()
    try:
        protocol.send_audio_frame(a, b'', is_voice=False)
        is_voice, got = protocol.recv_audio_frame(b)
        assert is_voice is False
        assert got == b''
    finally:
        a.close()
        b.close()


def test_audio_frame_none_on_close():
    a, b = _pair()
    try:
        a.close()
        assert protocol.recv_audio_frame(b) is None
    finally:
        b.close()


def _run_all():
    tests = [value for name, value in sorted(globals().items())
             if name.startswith('test_') and callable(value)]
    failures = 0
    for test in tests:
        try:
            test()
            print(f'PASS {test.__name__}')
        except Exception as error:  # noqa: BLE001 - test harness wants to keep going
            failures += 1
            print(f'FAIL {test.__name__}: {error!r}')
    print(f'\n{len(tests) - failures}/{len(tests)} passed')
    return failures


if __name__ == '__main__':
    sys.exit(1 if _run_all() else 0)

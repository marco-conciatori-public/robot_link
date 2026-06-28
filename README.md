# robot_link

Shared code for the two onboard computers of the Yahboom RDK X3 robot:

- the **RDK X3** board (`yahboom_rdk_x3_robot`), the "brain", and
- the **Jetson Nano** (`voice_robot_interaction`), voice + arm camera.

They talk over a wired point-to-point Ethernet link. This package is the single source of
truth for everything that must match on both sides, so the two can never drift apart.

## Modules

| Module        | Purpose |
|---------------|---------|
| `protocol.py` | Wire framing: `recv_exactly`, `send_message`/`recv_message` (length-prefixed), `send_command`/`recv_command` (JSON), `send_audio_frame`/`recv_audio_frame` (VAD-tagged mic frames). |
| `config.py`   | YAML config loader (`import_args`). Priority: kwargs > CLI > YAML > defaults. |
| `common.py`   | `pretty_print_dict`, `print_exception`. |
| `endpoints.py`| Canonical host, ports, and audio sample rates. |

No ROS2 dependency, so it imports cleanly on the Jetson (no Foxy). Dependencies: standard
library plus PyYAML.

## How it is consumed

Included in both repositories as a **git submodule**, mounted as `robot_link/` on each
computer's Python path so both `import robot_link.protocol`. Each repo keeps a thin local
`args.py` / `utils.py` shim that re-exports from here, so existing `import args` /
`import utils` call sites keep working while the implementation lives in one place.

## Tests

```bash
python robot_link/tests/test_protocol.py      # run from the package's parent directory
# or
python -m pytest robot_link/tests/
```

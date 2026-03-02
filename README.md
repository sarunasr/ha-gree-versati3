# Gree Versati 3 Local (Home Assistant)

Custom Home Assistant integration for local LAN control of a Gree Versati 3 heat pump over the device UDP JSON protocol.

This integration is inspired by protocol behavior observed in [`tomikaa87/gree-remote`](https://github.com/tomikaa87/gree-remote), but implemented from scratch in this repository without vendoring or subprocess calls.

## Features

- Local UDP communication (no cloud dependency)
- AES `pack` payload support for both ECB and GCM devices (auto-detected)
- Config Flow + Config Entry setup
- DataUpdateCoordinator polling (default 30s, configurable)
- Number entities:
  - `HeWatOutTemSet` (20..60, step 1)
  - `WatBoxTemSet` (20..60, step 1)
- Switch entity:
  - `Pow` (power on/off)
- Select entity:
  - `Mod` (mode selector)
- Sensor entities (unavailable when missing from device response):
  - `HeWatOutTemSet`
  - `WatBoxTemSet`
  - `TemUn`
  - `AllErr`
  - `Mod`
  - `Pow`
- Services:
  - `gree_versati.set_param`
  - `gree_versati.get_params`

## Install via HACS (Custom Repository)

1. Open HACS in Home Assistant.
2. Go to `Integrations`.
3. Open the menu (`⋮`) and choose `Custom repositories`.
4. Add this repository URL and category `Integration`.
5. Install `Gree Versati 3 Local` from HACS.
6. Restart Home Assistant.
7. Add integration: `Settings` -> `Devices & Services` -> `Add Integration` -> `Gree Versati 3 Local`.

## Configuration Fields

- `host`: Heat pump IP or hostname
- `port`: UDP port (default `7000`)
- `device_id`: Device identifier used by protocol envelope
- `key`: 16-byte AES key string
- `timeout`: UDP timeout in seconds (default `5`)

Options flow:
- `scan_interval`: Polling interval in seconds (default `30`)

## Notes

- The AES key must be exactly 16 bytes (UTF-8 byte length).
- The integration does not log the key.
- If a parameter is not returned by the device, corresponding entities are marked unavailable.

## Getting `device_id` and `key`

If you do not know the `device_id` and `key`, you can obtain them with `gree-remote`:

1. Clone the tool:

```bash
git clone https://github.com/tomikaa87/gree-remote
cd gree-remote
```

2. Search/bind to retrieve device credentials:

```bash
python3 PythonCLI/gree.py search -b <gree-ip>
```

The output should include the discovered device ID and bound key.

Note: in many networks, `-b` should be the subnet broadcast address (for example `192.168.1.255`), but some setups may work using the device IP directly.

3. Verify credentials by reading a known parameter:

```bash
python3 PythonCLI/gree.py -c <gree-ip> -i <id> -k <key> get HeWatOutTemSet
```

If this returns a value, use the same `host`, `device_id`, and `key` in this Home Assistant integration.

### Troubleshooting key retrieval

- Ensure your laptop/host and the heat pump are on the same subnet.
- Avoid guest Wi-Fi networks (client/AP isolation can block UDP device discovery).
- Try broadcast address for your subnet (for `/24`, usually `x.x.x.255`).
- If you have multiple interfaces (Ethernet + Wi-Fi), bind `gree.py` to the correct one:

```bash
python3 PythonCLI/gree.py --socket-interface <iface> search -b <broadcast_ip>
```

- If `search` fails but direct `get` works with known credentials, discovery traffic may be blocked while unicast traffic still works.

## Legal / Licensing Note

This repository is original MIT-licensed code.

Protocol behavior was implemented based on reverse engineering and public interoperability knowledge. No direct source copy from `gree-remote` is included.

You are responsible for complying with local laws, device warranties, and network/security policies when using reverse-engineered protocols.

## Development

Repository layout follows Home Assistant custom integration conventions with `custom_components/gree_versati`.

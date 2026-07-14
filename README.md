# CANopen Communication Project

A Python-based CANopen communication project developed for configuring and communicating with a CANopen encoder over a PEAK PCAN-USB interface.

The project implements low-level CANopen communication without relying on high-level CANopen libraries. Communication is performed directly through SDO (Service Data Object) and NMT (Network Management) messages.

---

## Hardware

- Baumer EAM360 CANopen Encoder
- PEAK PCAN-USB
- CAN Bus
- Windows
- Python 3

---

## Features

### CAN Communication

- PCAN-USB connection
- CAN message transmission
- CAN message reception
- Message filtering

### SDO Communication

- SDO Read
- SDO Write
- Read/Write response verification
- Abort message detection
- Timeout handling

### Encoder Configuration

The project can configure the encoder through CANopen Object Dictionary.

Currently supported parameters:

- Producer Heartbeat Time
- TPDO1 Transmission Type
- TPDO1 Event Timer
- Node ID
- Baud Rate

Each parameter is:

1. Written via SDO
2. Read back
3. Verified automatically

---

## EEPROM Support

After configuration, parameters are permanently stored inside the encoder using the CANopen Store Parameters object.

```
Index    : 0x1010
Subindex : 0x01
Command  : "save"
```

---

## NMT Support

Implemented Network Management commands:

- Start Node
- Stop Node
- Enter Pre-operational
- Reset Node
- Reset Communication

The current configuration process performs:

1. Save parameters
2. Reset Communication
3. Wait for heartbeat
4. Verify SDO communication after reboot

---

## Project Structure

```
CANOPEN_PROJECT
│
├── bus/
│   ├── can_bus.py
│   ├── can_message.py
│   ├── real_can.py
│   └── fake_can.py
│
├── canopen/
│   ├── client.py
│   ├── encoder_configurator.py
│   ├── object_dictionary.py
│   ├── sdo.py
│   └── nmt.py
│
├── config.py
├── main.py
└── README.md
```

---

## Current Workflow

The current implementation performs the following steps:

1. Connect to CAN bus
2. Configure encoder parameters
3. Verify written values
4. Save parameters to EEPROM
5. Send NMT Reset Communication
6. Wait for heartbeat
7. Verify SDO communication after reset

---

## Planned Features

The following features are planned for the next stage:

- Interactive user configuration
- Runtime Node ID selection
- Runtime baud rate selection
- Configuration validation
- Improved logging
- Additional CANopen Object Dictionary support

---

## Status

Current project status:

- CAN communication ✔
- SDO Read ✔
- SDO Write ✔
- EEPROM save ✔
- NMT Reset Communication ✔
- Heartbeat monitoring ✔
- Post-reset SDO verification ✔
- Node ID configuration ✔
- Baud Rate configuration ✔
- Modular project structure ✔

Project is under active development.

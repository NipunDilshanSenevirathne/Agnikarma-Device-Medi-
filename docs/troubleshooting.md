# Prototype troubleshooting

| Observation | Check |
|---|---|
| UNPROVISIONED | Correct role, disabled-default flag, nonempty calibration record and correctly typed/ranged numeric values. Do not bypass measurement work just to clear this state. |
| No OLED | Actual auto-reset STEMMA QT revision, I2C mode/address 60 or 61, 3.3 V interface, SDA/SCL mapping and valid power. |
| SENSOR or RTD exception | Pt1000 module/reference version, four-wire jumper setup, sensor terminal pairs, electrical continuity and actual sensor resistance. |
| SETPOINT_MISMATCH | Both boards must read the same single button; check branches, debounce and stuck/multiple keys. |
| STALE_LINK / HEARTBEAT | Cross TX/RX and pulse lines, ground, role identity, packet sequence and board resets. A one-board restart may need a simultaneous cold restart of both boards. |
| WAIT_PERMIT | Supervisor health, armed state, HEAT hold, interlocks and peer permit. Do not short the relay or bypass the supervisor. |
| PACK_VOLTAGE / PACK_TEMP | Bench supply/pack range, each divider, calibration, thermistor circuit and actual pack temperature. |
| Cannot reach a high target | Available battery power, restricted commissioning duty, heat losses and calibration. Do not raise safety limits to force a demonstration. |
| COOL pressed but tip remains hot | Normal stored energy remains after current stops. Verify actual input interruption and use the guarded cooling fixture. A timer cannot prove safe handling. |

Electrical work uses a disconnected heater until low-current verification is complete. No fault message or host test authorizes patient use.

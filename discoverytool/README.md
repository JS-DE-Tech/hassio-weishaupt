# Weishaupt Discovery Tools

This directory contains read-only discovery tools for the local Weishaupt CanApiJson interface.

## Safety

All included scripts operate in read-only mode.

Only the following command type is used:

* `CM=0x01` (GET)

The tools never send:

* `CM=0x03` (SET)
* `CM=0x13` (SETS)

No configuration values are modified.

---

## Requirements

Before running any tool:

1. Disable the cloud connection.
2. Enable the local JSON interface.
3. Extract the ZIP package.
4. Run the supplied CMD launcher.

---

## Tool 1 – Snapshot Package

**File:**

`weishaupt-wtc-readonly-package.zip`

Purpose:

* Collect confirmed WTC values
* Collect system and hydraulic parameters
* Collect known native WTC objects
* Match values against portal screenshots

Output:

`weishaupt-wtc-snapshot.zip`

Recommended as the first step.

Typical runtime:

* 1–5 minutes

---

## Tool 2 – Discovery Scanner

**File:**

`weishaupt_discovery_skript.zip`

Purpose:

* Search for undocumented registers
* Discover additional burner parameters
* Discover operating hours
* Discover pump information
* Discover fan information
* Discover ionization values
* Discover gas valve parameters
* Discover additional portal values

Features:

* Read-only operation
* Automatic checkpoints
* Resume after interruption
* Metadata collection
* CSV and JSON export

Output:

`weishaupt-discovery.zip`

Typical runtime:

* 25–45 minutes

---

## Recommended Workflow

1. Run the Snapshot Package.
2. Upload the generated snapshot ZIP file.
3. Run the Discovery Scanner.
4. Upload the generated discovery ZIP file.

This sequence provides the fastest path to identifying additional Weishaupt registers while minimizing load on the controller.

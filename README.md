# OPCUA Client over Asyncua

This is an hacs integration using asyncua to connect various industrial PLC to HA. My initial approach was to develop a gateway which connect the PLC over RESTful API. After a couple of integration for projects, I found that it would be beneficial to the community to have a custom integration in HA for OPC UA servers.

I found an older project which uses the python-opcua, which is deprecated and decided to start a new integration using opcua-asyncio.

[![Buy me a beer](https://img.shields.io/badge/Donate-Buy%20me%20a%20beer-yellow?logo=buy-me-a-coffee)](https://buymeacoffee.com/kvsoong)

<br>

## Table of contents

**[`Installation`](#installation)** **[`Asyncua-Coordinator`](#asyncua-coordinator)** **[`Sensor`](#sensors-entities)** **[`Binary-Sensor`](#binary-sensors-entities)** **[`Switch`](#switch-entities)** **[`Directory`](#-directory-structure)** **[`Donate`](#donate)**

<br>

## Installation

<details>


<summary>With HACS</summary>

1. If HACS is not installed yet, download it following the instructions on [https://hacs.xyz/docs/setup/download/](https://hacs.xyz/docs/use/download/download/)
2. Proceed to the HACS initial configuration following the instructions on [https://hacs.xyz/docs/configuration/basic](https://hacs.xyz/docs/configuration/basic)
3. Copy this project directory, https://github.com/KVSoong/asyncua.
4. Navigate to HACS in HA and select _Integration_.
5. At the top right corner, select the vertical 3 dots and click **Custom repositories**.
6. Paste the link in the `Repository` input field and select **Integration** for the Categeroy dropdown select.
7. Click Add to add this repository to your HA.
8. Once added, you should see this custom repository installed. It should prompt you to restart.
9. Once restarted, you should be able to connect to a OPCUA server.

</details>

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kvsoong&repository=asyncua&category=integration)

<br>

## Asyncua Coordinator

This integration is developed with the option to connect to multiple OPCUA servers, as it is commonly used in an industrial environment.

Paste the following lines to your `configuration.yaml` file. Remove or add more OPCUA servers as required. Specify a unique name for each server, under the key `name`.

  ```yaml
  asyncua:
    - name: "plc-01" # Unique name to identify the server. Will be used by the sensors to indicate which server to get the node value.
      url: "opc.tcp://localhost:4840/" # URL of the server.
      scan_interval: 10 # Optional. Interval for coordinator to read from OPCUA. Default is set at 30s.
      username: admin # Optional username
      password: admin # Optional password
    - name: "plc-02"
      url: "opc.tcp://localhost2:4840/"
      scan_interval: 10
      username: admin
      password: admin
  ```

<details>

<summary>Options (YAML + descriptions)</summary>

| Name | Type | Requirement | Description |
| - | - | - | - |
| `name` | string | **Required** | **Unique** identifier for each OPCUA Server |
| `url` | string | **Required** | OPCUA server URL within the same network |
| `scan_interval` | int | Optional | Polling interval to refresh data |
| `username` | string | **Optional** | Username to connect to the server |
| `password` | string | **Optional** | Password to connect to the server |

</details>

---

## Sensors Entities

This entity allows you to create any type of device class sensor specified in [homeassistant](https://www.home-assistant.io/integrations/sensor). To add a custom sensor entity, paste the following example into your `configuration.yaml` file and update the values.

  ```yaml
  sensor:
    - platform: asyncua
      nodes:
        - name: sensor-01 # Name of the sensor
          unique_id: sensor-01 # Unique ID of the sensor
          device_class: temperature # Device class according to Homeassistant sensors
          hub: plc-01 # OPCUA unique name defined in the coordinator that serve the data.
          nodeid: "ns=1;s=3000" # Node id from OPCUA server
          unit_of_measurement: °C # Optional unit of measurement.
        - name: sensor-02
          unique_id: sensor-02
          device_class: temperature
          hub: plc-02
          nodeid: "ns=1;s=3000"
          unit_of_measurement: °C
  ```

<details>

<summary>Options (YAML + descriptions)</summary>

| Name | Type | Requirement | Description |
| - | - | - | - |
| `name` | string | **Required** | **Unique** identifier for each sensor |
| `unique_id` | string | Optional | Entity ID stored in homeassistant |
| `device_class` | string | Optional | [sensors](https://www.home-assistant.io/integrations/sensor) available in homeassistant |
| `hub` | string | **Required** | Corresponded OPCUA hub defined in **[`asyncua-coordinator`](#asyncua-coordinator)** **name** key |
| `nodeid` | string | **Required** | node id address of a single node |
| `unit_of_measurement` | string | Optional | to allow historical statistic graph if `device_class` is not defined |

</details>

---

## Binary Sensors Entities

This entity allows you to create any type of device class binary sensor specified in [homeassistant](https://www.home-assistant.io/integrations/binary_sensor/#device-class). To add a custom binary sensor entity, paste the following example into your `configuration.yaml` file and update the values.

  ```yaml
  binary_sensor:
    - platform: asyncua
      nodes:
        - name: "binary-sensor-01" # Unique id for the binary sensor
          unique_id: "binary-sensor-01" # Homeassistnat unique_id
          device_class: "power" # Device class according to Homeassistant binary sensors
          hub: "plc-01" # Defined Asyncua coordinator
          nodeid: "ns=1;s=1000" # Node id from OPCUA server
        - name: "binary-sensor-01" 
          unique_id: "binary-sensor-01" 
          device_class: "power"
          hub: "plc-01"
          nodeid: "ns=1;s=1000"
  ```

<details>

<summary>Options (YAML + descriptions)</summary>

| Name | Type | Requirement | Description |
| - | - | - | - |
| `name` | string | **Required** | **Unique** identifier for each binary sensor |
| `unique_id` | string | Optional | Entity ID stored in homeassistant |
| `device_class` | string | Optional | [binary sensors](https://www.home-assistant.io/integrations/binary_sensor/#device-class) available in homeassistant |
| `hub` | string | **Required** | Corresponded OPCUA hub defined in **[`asyncua-coordinator`](#asyncua-coordinator)** **name** key |
| `nodeid` | string | **Required** | node id address of a single node |

</details>

<br>

## Switch Entities

This entity allow you to create a switch entity which can be a representative of a contactor or relay in a automation environment. Node id address for DO(digital output) to set the new value and also an optional DI(digital input) can be used to read the real state of the node. If DI is not specified, DO node address is used instead to check the state of the node. To add a custom binary sensor entity, paste the following example into your `configuration.yaml` file and update the values.

  ```yaml
  switch:
    - platform: asyncua
      nodes:
        - name: "switch-01" # Unique id for the binary sensor
          unique_id: "switch-01"  # Homeassistnat unique_id
          hub: "plc-01 "   # Defined Asyncua coordinator
          nodeid: "ns=1;s=1000"  # DO node id from OPCUA server
          nodeid_switch_di: "ns=1;s=2000" # DI node id from OPCUA server
        - name: "switch-02"
          unique_id: "switch-02"
          hub: "plc-01 "
          nodeid: "ns=1;s=1001"
          nodeid_switch_di: "ns=1;s=2001"
  ```

<details>

<summary>Options (YAML + descriptions)</summary>

| Name | Type | Requirement | Description |
| - | - | - | - |
| `name` | string | **Required** | **Unique** identifier for each switch |
| `unique_id` | string | Optional | Entity ID stored in homeassistant |
| `hub` | string | **Required** | Corresponded OPCUA hub defined in **[`asyncua-coordinator`](#asyncua-coordinator)** **name** key |
| `nodeid` | string | **Required** | node id address for the digital output |
| `nodeid_switch_di` | string | Optional | node id address for the digital input. If not specified, `nodeid_switch_do` node is used for the latest state |

</details>

## Organizing subdirectories for custom sensors and binary_sensor

Will be included in the future.

## Set values to node

To set a new value to a node, a service can be called from **Developer Tools** -> **Services** -> **asyncua: set value**.

1. Ensure that a valid [asyncua-coordnator](#asyncua-coordinator) is created.
1. Paste the following code sample in `UI Mode` and make the necessary changes

    ```yaml
    hub: plc-01
    nodeid: ns=1;s=1000
    value: false
    ```

1. In `YAML Mode`, paste the following code sample and make the necessary changes

    ```yaml
    service: asyncua.set_value
    target: {}
    data:
      hub: plc-01
      nodeid: ns=1;s=1000
      value: false
    ```

## 📂 Directory Structure

To better organize entities and avoid clumping them in a single `configuration.yaml` file, you can include the following lines in the `configuration.yaml` file, and create the directory stucture as shown in the tree below.

```tree
home-assistant/
├── asyncua-binary-sensor/
|   ├── sensor-01.yaml
|   ├── ...
|   └── sensor-n.yaml
├── asyncua-sensor/
|   ├── sensor-01.yaml
|   ├── ...
|   └── sensor-n.yaml
├── asyncua-switch/
|   ├── switch-01.yaml
|   ├── ...
|   └── switch-n.yaml
└── configuration.yaml
```

<details>

<summary>Configuration YAML</summary>

Include the following lines in the `configuration.yaml` file to import the entites in each directory.

```yaml
binary_sensor asyncua: !include_dir_merge_list asyncua-binary-sensor/
sensor asyncua: !include_dir_merge_list asyncua-sensor/
switch asyncua: !include_dir_merge_list asyncua-switch/
```

</details>

<details>

<summary>Binary Sensor YAML</summary>

```yaml
- platform: asyncua
  nodes:
    - name: "binary-sensor-01" # Unique id for the binary sensor
      unique_id: "binary-sensor-01" # Homeassistnat unique_id
      device_class: "power" # Device class according to Homeassistant binary sensors
      hub: "plc-01" # Defined Asyncua coordinator
      nodeid: "ns=1;s=1000" # Node id from OPCUA server
    - name: "binary-sensor-01" 
      unique_id: "binary-sensor-01" 
      device_class: "power"
      hub: "plc-01"
      nodeid: "ns=1;s=1000"
```

</details>

<details>

<summary>Sensor YAML</summary>

```yaml
- platform: asyncua
  nodes:
    - name: sensor-01 # Name of the sensor
      unique_id: sensor-01 # Unique ID of the sensor
      device_class: temperature # Device class according to Homeassistant sensors
      hub: plc-01 # OPCUA unique name defined in the coordinator that serve the data.
      nodeid: "ns=1;s=3000" # Node id from OPCUA server
      unit_of_measurement: °C # Optional unit of measurement.
    - name: sensor-02
      unique_id: sensor-02
      device_class: temperature
      hub: plc-02
      nodeid: "ns=1;s=3000"
      unit_of_measurement: °C
```

</details>

<details>

<summary>Switch YAML</summary>

```yaml
- platform: asyncua
  nodes:
    - name: "switch-01" # Unique id for the binary sensor
      unique_id: "switch-01"  # Homeassistnat unique_id
      hub: "plc-01 "   # Defined Asyncua coordinator
      nodeid: "ns=1;s=1000"  # DO node id from OPCUA server
      nodeid_switch_di: "ns=1;s=2000" # DI node id from OPCUA server
    - name: "switch-02"
      unique_id: "switch-02"
      hub: "plc-01 "
      nodeid: "ns=1;s=1001"
      nodeid_switch_di: "ns=1;s=2001"
```

</details>
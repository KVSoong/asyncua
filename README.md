# OPCUA Client over Asyncua

---

## Introduction

This is an hacs integration using asyncua to connect various industrial PLC to HA. My initial approach was to develop a gateway which connect the PLC over RESTful API. After a couple of integration for projects, I found that it would be beneficial to the community to have a custom integration in HA for OPC UA servers.

I found an older project which uses the python-opcua, which is deprecated and decided to start a new integration using opcua-asyncio.

## Installation with HACS

1. Install hacs to your homeassistant if not already installed following the instruction here, https://hacs.xyz/docs/setup/download/
2. Copy this project directory, https://github.com/KVSoong/asyncua.
3. Navigate to HACS in HA and select *Integration*.
4. At the top right corner, select the vertical 3 dots and click **Custom repositories**.
5. Paste the link in the `Repository` input field and select **Integration** for the Categeroy dropdown select.
6. Click Add to add this repository to your HA.
7. Once added, you should see this custom repository installed. It should prompt you to restart.
8. Once restarted, you should be able to connect to a OPCUA server.

## Configure Asyncua Coordinator(**Required**)

This integration is developed with the option to connect multiple OPCUA servers, as it is commonly used in an industrial environment.

1. Paste the following lines to your `configuration.yaml` file. Remove or add more OPCUA servers as required. Specify a unique name for each server, under the key `name`.

   ```yaml
   asyncua:
     - name: "plc-01"   # Unique name to identify the server. Will be used by the sensors to indicate which server to get the node value.
       url: "opc.tcp://localhost:4840/" # URL of the server.
       scan_interval: 10    # Optional. Interval for coordinator to read from OPCUA. Default is set at 30s.
       username: admin  # Optional username
       password: admin  # Optional password
     - name: "plc-02"
       url: "opc.tcp://localhost2:4840/"
       scan_interval: 10
       username: admin
       password: admin
   ```

## Configure Sensor entities(Optional)

1. To add a custom sensor entity, paste the following example into your `configuration.yaml` file and make the necessary changes
   
   ```yaml
   sensor:
      - platform: asyncua
        nodes:
          - name: sensor-01 # Name of the sensor
            unique_id: sensor-01    # Unique ID of the sensor
            device_class: temperature   # Device class according to Homeassistant sensors
            hub: plc-01 # OPCUA unique name defined in the coordinator that serve the data.
            nodeid: "ns=1;s=3000"   # Node id from OPCUA server
            unit_of_measurement: °C # Optional unit of measurement.
          - name: sensor-02
            unique_id: sensor-02
            device_class: temperature
            hub: plc-02
            nodeid: "ns=1;s=3000"
            unit_of_measurement: °C
   ```

## Configure Binary Sensor entities(Optional)

1. To add a custom sensor entity, paste the following example into your `configuration.yaml` file and make the necessary changes

   ```yaml
   binary_sensor:
     - platform: asyncua
       nodes:
         - name: "binary-sensor-01" # Desired unique name
           unique_id: "binary-sensor-01"    # Desired unique_id
           hub: "plc-01"    # Device class according to Homeassistant binary_sensor
           nodeid: "ns=1;s=1000"    # Node id from OPCUA server
         - name: "binary-sensor-02" # Desired unique name
           unique_id: "binary-sensor-02"    # Desired unique_id
           hub: "plc-02"    # Device class according to Homeassistant binary_sensor
           nodeid: "ns=1;s=1000"    # Node id from OPCUA server
   ```

## Organizing subdirectories for custom sensors and binary_sensor

Will be included in the future.
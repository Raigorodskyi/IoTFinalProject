import bluetooth

def count_bluetooth_devices():
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, lookup_class=True, device_id=-1, device_name="",
                                                device_address=None, device_class=None, device_type=None, lookup_oui=True, lookup_oui_data=True)

    return len(nearby_devices)

if name == "main":
    num_devices = count_bluetooth_devices()
    print("Number of Bluetooth devices: " + num_devices)

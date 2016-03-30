#!/usr/bin/env python3

import time
import os


def get_connections():
    raw_data = os.popen("nmcli --terse --fields NAME,DEVICE,TYPE connection show")
    data = []
    line = raw_data.readline()
    while line != "":
        line_data = line.strip("\n").split(":")
        if len(line_data) == 3:
            data.append(line_data)
        line = raw_data.readline()
    return data


class Py3status:
    order = "VEW"
    vpn_text = "V"
    eth_text = "E"
    wifi_text = "W"
    timeout = 5

    def __init__(self):
        self.first_run = True

    def kill(*args, **kwargs):
        pass

    def on_click(*args, **kwargs):
        pass

    def get_status(self, i3s_output_list, i3s_config):
        if self.first_run:
            self.color_good = i3s_config["color_good"]
            self.color_bad = i3s_config["color_bad"]
            self.good = True
            self.first_run = False

        self.good = not self.good
        color = self.color_good if self.good else self.color_bad

        connections = get_connections()

        text = []

        status = {"V": 0, "E": 0, "W": 0}
        for name, device, dtype in connections:
            if device == "--":
                continue
            if dtype == "802-11-wireless":
                status["W"] = 1
            elif dtype == "802-3-ethernet":
                status["E"] = 1
            elif dtype == "vpn":
                status["V"] = 1

        full_text = ""
        for device in self.order:
            if device == "V": name = self.vpn_text
            elif device == "E": name = self.eth_text
            elif device == "W": name = self.wifi_text
            else: raise ValueError(device + " is not a valid device.")

            full_text += "<span foreground='%s'>%s</span>" % \
            (self.color_good if status[device] else self.color_bad, name)
        # full_text = self.vpn_text

        response = {
            "markup": "pango",
            "full_text": full_text,
            "cached_until": time.time() + 10
        }
        return response

if __name__ == "__main__":
    """
    Test this module by calling it directly.
    This SHOULD work before contributing your module please.
    """
    from time import sleep
    x = Py3status()
    config = {
        'color_bad': '#FF0000',
        'color_degraded': '#FFFF00',
        'color_good': '#00FF00'
    }
    while True:
        print(x.get_status([], config))
        sleep(1)

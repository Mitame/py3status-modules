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
    format = "{vpn}{eth}{wifi}"
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

        status = {"vpn": 0, "eth": 0, "wifi": 0}
        for name, device, dtype in connections:
            if device == "--":
                continue
            if dtype == "802-11-wireless":
                status["wifi"] = 1
            elif dtype == "802-3-ethernet":
                status["eth"] = 1
            elif dtype == "vpn":
                status["vpn"] = 1

        fields = {
            "vpn": "<span foreground='%s'>%s</span>" % ((self.color_good if status["vpn"] else self.color_bad, self.vpn_text)),
            "eth": "<span foreground='%s'>%s</span>" % ((self.color_good if status["eth"] else self.color_bad, self.eth_text)),
            "wifi": "<span foreground='%s'>%s</span>" % ((self.color_good if status["wifi"] else self.color_bad, self.wifi_text)),
        }
        response = {
            "markup": "pango",
            "full_text": "<span foreground='%s'>%s</span>" % (self.color_bad, self.format.format(**fields)),
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

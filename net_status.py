#!/usr/bin/env python3

import time
import os
import re


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
    color = None
    format = "{vpn:V:V}{eth:E:E}{wifi:W:W}"
    timeout = 5



    def __init__(self):
        self.first_run = True

    def _on_first_run(self):
        _formatting_regex = "{(vpn|eth|wifi)\:([^\:}]*)\:([^\:}]*)}"

        self._format = ""
        self._formatting_strings =  {}

        for group in re.findall(_formatting_regex, self.format):
            # print(group)
            self._formatting_strings[group[0]] = {}
            if len(group) > 2:
                self._formatting_strings[group[0]]["on"] = group[1]
                self._formatting_strings[group[0]]["off"] = group[2]
            elif len(group) == 2:
                self._formatting_strings[group[0]]["on"] = group[1]
                self._formatting_strings[group[0]]["off"] = group[1]
            else:
                self._formatting_strings[group[0]]["on"] = group[0][0].upper()
                self._formatting_strings[group[0]]["off"] = group[0][0].upper()

        self._format = re.sub(_formatting_regex, "{\\1}", self.format)
        self.first_run = False

    def kill(self, *args, **kwargs):
        pass

    def on_click(self, *args, **kwargs):
        pass

    def get_status(self, i3s_output_list, i3s_config):
        if self.first_run:
            self._on_first_run()

        connections = get_connections()

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
        fields = {}
        for dev in self._formatting_strings.keys():
            if status[dev]:
                fields[dev] = "<span foreground='%s'>%s</span>" % \
                (i3s_config["color_good"], self._formatting_strings[dev]["on"])
            else:
                fields[dev] = "<span foreground='%s'>%s</span>" % \
                (i3s_config["color_bad"], self._formatting_strings[dev]["off"])

        if self.color:
            full_text = "<span foreground='%s'>%s</span>" % \
            (self.color, self._format.format(**fields))
        else:
            full_text = self._format.format(**fields)
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

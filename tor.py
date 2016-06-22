#!/usr/bin/env python3

import time
import os
import re
from stem.control import Controller
from stem import CircStatus
from stem.response.events import CircuitEvent


class Py3status:
    format = "{exit}/{exit_region}"
    timeout = 5
    control_address = "127.0.0.1"
    control_port = 9051
    control_password = None

    def __init__(self):
        self.controller = None
        self.circuits = {}
        self.cur_view = 0

    def kill(self, *args, **kwargs):
        pass

    def on_click(self, *args, **kwargs):
        self.cur_view += 1

    def _on_circuit_change(self, event):
        if event.status == CircStatus.BUILT:
            exit_node = self.controller.get_network_status(event.path[-1][0], None)
            addr = exit_node.address
            country = self.controller.get_info("ip-to-country/%s" % addr)

            self.circuits[event.id] = {
                "status": event.status,
                "exit_addr": addr,
                "exit_region": country,
                "exit_nick": event.path[-1][1],
                "length": len(event.path)
            }
        elif event.status == CircStatus.CLOSED:
            try:
                del(self.circuits[event.id])
            except:
                pass
        else:
            self.circuits[event.id] = {
                "status": event.status,
                "exit_addr": None,
                "exit_region": None,
                "exit_nick": None,
                "length": len(event.path)
            }

        self.py3.update()

    def show_status(self, i3_output_list, i3s_config):
        self.config = i3s_config
        if self.controller is None:
            self.controller = Controller.from_port(self.control_address, self.control_port)
            if self.control_password:
                self.controller.authenticate(self.control_password)
            else:
                self.controller.authenticate()

            self.controller.add_event_listener(self._on_circuit_change, "CIRC")
            for circuit in self.controller.get_circuits():
                if circuit.status != CircStatus.BUILT:
                    continue

                exit_fp, exit_nick = circuit.path[-1]

                exit_node = self.controller.get_network_status(exit_fp, None)
                if exit_node:
                    exit_addr = exit_node.address

                    country = self.controller.get_info("ip-to-country/%s" % exit_addr)
                    self.circuits[circuit.id] = {
                        "status": circuit.status,
                        "exit_addr": exit_addr,
                        "exit_region": country,
                        "exit_nick": exit_nick,
                        "length": len(circuit.path)
                    }


        self.cur_view %= len(self.circuits)
        key = sorted(self.circuits.keys())[self.cur_view]
        circuit = self.circuits[key]
        if circuit["status"] == CircStatus.BUILT:
            color = self.config["color_good"]
        elif circuit["status"] == CircStatus.CLOSED:
            color = self.config["color_bad"]
        else:
            color = self.config["color_degraded"]

        data = {"color": color, "n": self.cur_view}
        data.update(circuit)
        frmt_string = "<span color=\"{color}\">" + self.format + "</span>"


        return {
            "markup": "pango",
            "full_text": frmt_string.format(**data),
            "cached_until": time.time() + 600
        }

if __name__ == "__main__":
    """
    Test this module by calling it directly.
    This SHOULD work before contributing your module please.
    """
    from time import sleep, time as clock
    x = Py3status()
    config = {
        'color_bad': '#FF0000',
        'color_degraded': '#FFFF00',
        'color_good': '#00FF00'
    }
    x.control_address = "127.0.0.1"
    x.control_port = 9051
    x.control_password = ""
    while True:
        res = x.show_status([], config)
        print(res)
        delay = res["cached_until"] - clock()
        if delay > 0:
            sleep(delay)

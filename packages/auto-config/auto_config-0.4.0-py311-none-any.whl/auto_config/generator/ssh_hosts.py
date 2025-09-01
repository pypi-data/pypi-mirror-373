from __future__ import annotations

from collections.abc import Sequence

from loguru import logger

from ..device import Device
from ..field import DefaultExtraField, SSHHostField
from .base import GeneratorBase


class SSHHostsGenerator(GeneratorBase):
    def __init__(self, devices: Sequence[Device[DefaultExtraField]], domain: str):
        super().__init__()
        self.domain = domain
        self.devices = devices

    def add_host(self, host_name: str, host_domain: str, desc: str, ssh_field: SSHHostField):
        self.add_block("Host {:}".format(host_name), indentation=2)
        self.add_line("HostName {:}".format(host_domain))
        self.add_line("Port {:}".format(ssh_field.port))
        self.add_line("User {:}".format(ssh_field.user))
        self.add_line("ForwardAgent {:}".format('yes' if ssh_field.forward_agent else 'no'))
        self.add_line("#_Desc {:}".format(desc))

    def generate(self):
        for device in self.devices:
            if device.extra.ssh is None:
                logger.warning("device {:} has no ssh config".format(device))
                continue
            domain = "{:}.{:}".format(device.get_domain(), self.domain)
            self.add_host(device.get_name(), domain, device.desc, device.extra.ssh)
            logger.debug("added host {:} to ssh config".format(device.get_name()))
            for container in device.extra.ssh.containers:
                container_name = container.name or str(container.port)
                name = "{:}-{:}".format(device.get_name(), container_name)
                self.add_host(name, domain, "{:}: {:} 容器".format(device.desc, name), container)
                logger.debug("added container host {:} to ssh config".format(name))

        super().generate()

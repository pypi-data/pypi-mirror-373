from __future__ import annotations

import os
from pathlib import Path
from sys import stdout

import toml
from loguru import logger
from pydantic import ValidationError

from .device import Device
from .field import BaseExtraField, DefaultExtraField
from .generator import (
    AnsibleHostsGenerator,
    DNSHostsGenerator,
    DNSManagerGenerator,
    SSHHostsGenerator,
)
from .service import Service
from typing import TypeVar

def __wrapper_func_get_devices():
    __get_devices_T = TypeVar("__get_devices_T", bound = BaseExtraField)
    
    
    def get_devices(
        devices_config: list[dict], extra_field_cls: type[__get_devices_T] = BaseExtraField
    ) -> list[Device[__get_devices_T]]:
        devices = []
        for device in devices_config:
            try:
                extra_field_cls.model_validate(device.get("extra", {}))
                devices.append(Device[extra_field_cls].model_validate(device))
            except ValidationError as e:
                logger.warning("device has invalid extra field: {:}".format(e))
                continue
        return devices
    return get_devices
get_devices = __wrapper_func_get_devices()


def get_services(services_config: list[dict]) -> list[Service]:
    services = []
    for service in services_config:
        services.append(Service.model_validate(service))
    return services


def generate_config(
    path: Path,
    *,
    groups: list[str] | None = None,
    gateway_group: str | None = None,
    log_level="INFO",
):
    logger.remove()
    logger.add(stdout, level=log_level)
    path = path.expanduser()
    with open(path) as f:
        config = toml.load(f)
    devices = get_devices(config["devices"], DefaultExtraField)
    domain = config.get("domain", "sixbones.dev")
    generator = AnsibleHostsGenerator(devices)
    generator.write("~/.config/ansible/hosts")
    generator = SSHHostsGenerator(devices, domain=domain)
    generator.write("~/.ssh/config")
    generator = DNSManagerGenerator(devices, domain=domain, extra_groups=groups)
    # TODO: `ddns.json` is not only ddns, so we need a better name.
    generator.write("~/.config/dns-manager/ddns.json")
    if gateway_group is not None:
        generator = DNSHostsGenerator(devices, domain=domain, group=gateway_group)
        generator.write("/var/mosdns/hosts")

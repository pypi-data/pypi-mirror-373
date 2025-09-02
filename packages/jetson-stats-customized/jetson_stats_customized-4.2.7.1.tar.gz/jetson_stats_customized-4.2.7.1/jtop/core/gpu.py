# -*- coding: UTF-8 -*-
# This file is part of the jetson_stats package (https://github.com/rbonghi/jetson_stats or http://rnext.it).
# Copyright (c) 2019-2023 Raffaello Bonghi.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
# Logging
import logging
from .common import cat, GenericInterface
from .exceptions import JtopException
from .command import Command
import subprocess
# Create logger
logger = logging.getLogger(__name__)
# default ipgu path for Jetson devices
DEFAULT_IGPU_PATH = "/sys/class/devfreq/"


def check_nvidia_smi():
    cmd = Command(['nvidia-smi'])
    try:
        cmd()
        return True
    except (OSError, Command.CommandException):
        pass
    return False


def parse_nvidia_smi_dmon_sm():
    """
    Thor GPU için sadece 'sm' sütununu (GPU utilization %) okur.
    """
    try:
        cmd = ["nvidia-smi", "dmon", "-s", "puc", "-c", "1"]
        output = subprocess.check_output(cmd, universal_newlines=True)
        lines = output.strip().splitlines()

        # Son satırı bul (header olmayan)
        data_line = None
        for line in lines:
            if not line.startswith("#") and line.strip():
                data_line = line
        if data_line is None:
            return None

        parts = data_line.split()
        return int(parts[4]) if parts[4].isdigit() else 0

    except Exception as e:
        logger.warning(f"Failed to parse nvidia-smi dmon (sm): {e}")
        return None

def igpu_read_freq(path, is_thor=False):
    gpu = {}

    # --- Thor için ---
    if is_thor:
        sm_val = parse_nvidia_smi_dmon_sm()
        if sm_val is not None:
            gpu['load'] = sm_val
        return gpu

    # --- Jetson için ---
    if os.access(path + "/governor", os.R_OK):
        with open(path + "/governor", 'r') as f:
            gpu['governor'] = f.read().strip()
    if os.access(path + "/cur_freq", os.R_OK):
        with open(path + "/cur_freq", 'r') as f:
            gpu['cur'] = int(f.read()) // 1000
    if os.access(path + "/max_freq", os.R_OK):
        with open(path + "/max_freq", 'r') as f:
            gpu['max'] = int(f.read()) // 1000
    if os.access(path + "/min_freq", os.R_OK):
        with open(path + "/min_freq", 'r') as f:
            gpu['min'] = int(f.read()) // 1000
    for idx in range(2):
        path_gpc = f"/sys/kernel/debug/bpmp/debug/clk/nafll_gpc{idx}/pto_counter"
        if os.access(path_gpc, os.R_OK):
            with open(path_gpc, 'r') as f:
                if 'GPC' not in gpu:
                    gpu['GPC'] = []
                gpu['GPC'] += [int(f.read()) // 1000]

    return gpu


def igpu_read_status(path, is_thor=False):
    gpu = {}

    # --- Thor için ---
    if is_thor:
        sm_val = parse_nvidia_smi_dmon_sm()
        if sm_val is not None:
            gpu['load'] = sm_val
        return gpu

    # --- Jetson için ---
    if os.access(path + "/railgate_enable", os.R_OK):
        with open(path + "/railgate_enable", 'r') as f:
            gpu['railgate'] = int(f.read()) == 1
    if os.access(path + "/tpc_pg_mask", os.R_OK):
        with open(path + "/tpc_pg_mask", 'r') as f:
            gpu['tpc_pg_mask'] = int(f.read()) == 1
    if os.access(path + "/enable_3d_scaling", os.R_OK):
        with open(path + "/enable_3d_scaling", 'r') as f:
            gpu['3d_scaling'] = int(f.read()) == 1
    if os.access(path + "/load", os.R_OK):
        with open(path + "/load", 'r') as f:
            gpu['load'] = float(f.read()) / 10.0

    return gpu


def get_raw_igpu_devices():
    igpu_path = DEFAULT_IGPU_PATH
    raw_output = {}
    for item in os.listdir(igpu_path):
        item_path = os.path.join(igpu_path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            # Check name device
            name_path = "{item}/device/of_node/name".format(item=item_path)
            if os.path.isfile(name_path):
                # Decode name
                name = cat(name_path)
                # path and file
                raw_output[name_path] = "{}".format(name)
    return raw_output


def find_igpu(igpu_path):
    igpu = {}
    if not os.path.isdir(igpu_path):
        logger.error(f"Folder {igpu_path} doesn't exist")
        return igpu

    gpc_added = False  # Thor’da önce gpu-gpc-0 varsa onu alacağız

    for item in os.listdir(igpu_path):
        item_path = os.path.join(igpu_path, item)
        logger.debug(f"Checking {item_path}")

        if os.path.isfile(item_path) or os.path.islink(item_path):
            name_path = f"{item_path}/device/of_node/name"
            if os.path.isfile(name_path):
                try:
                    name = cat(name_path)
                    logger.debug(f"Found name={name} in {name_path}")
                    if name in ['gv11b', 'gp10b', 'ga10b', 'gpu']:
                        path = os.path.realpath(os.path.join(item_path, "device"))
                        frq_path = os.path.realpath(item_path)
                        igpu[name] = {'type': 'integrated', 'path': path, 'frq_path': frq_path}
                        logger.info(f"GPU \"{name}\" status in {path}")
                        logger.info(f"GPU \"{name}\" frq in {frq_path}")
                        # opsiyonel railgate ve 3d_scaling dosyaları
                        path_railgate = os.path.join(path, "railgate_enable")
                        if os.path.isfile(path_railgate):
                            igpu[name]['railgate'] = path_railgate
                        path_3d_scaling = os.path.join(path, "enable_3d_scaling")
                        if os.path.isfile(path_3d_scaling):
                            igpu[name]['3d_scaling'] = path_3d_scaling
                except Exception as e:
                    logger.warning(f"Failed to read {name_path}: {e}")

        # --- Thor için özel ekleme ---
        if item.startswith("gpu-gpc-") and not gpc_added:
            key_name = "gpu"
            path = os.path.join(item_path, "device")
            if os.path.isdir(path):
                frq_path = os.path.realpath(item_path)
                igpu[key_name] = {'type': 'integrated', 'path': path, 'frq_path': frq_path, 'is_thor':True}
                gpc_added = True
                logger.info(f"Thor GPU (GPC) detected at {path}")
            else:
                logger.warning(f"gpu-gpc-0 found but device folder not present under {item_path}")

        elif item.startswith("gpu-nvd-") and not gpc_added:
            key_name = "gpu"
            path = os.path.join(item_path, "device")
            if os.path.isdir(path):
                frq_path = os.path.realpath(item_path)
                igpu[key_name] = {'type': 'integrated', 'path': path, 'frq_path': frq_path, 'is_thor':True}
                gpc_added = True
                logger.info(f"Thor GPU (NVD) detected at {path}")
            else:
                logger.warning(f"gpu-nvd-0 found but device folder not present under {item_path}")

    if not igpu:
        logger.error("No GPU detected in find_igpu()")

    return igpu


def find_dgpu():
    # Check if there are discrete gpu
    # if not os.path.exists("/dev/nvidiactl") and not os.path.isdir("/dev/nvgpu-pci"):
    #     return []
    # https://enterprise-support.nvidia.com/s/article/Useful-nvidia-smi-Queries-2
    dgpu = {}
    if check_nvidia_smi():
        logger.info("NVIDIA SMI exist!")
    if dgpu:
        logger.info("Discrete GPU found")
    return dgpu


class GPU(GenericInterface):
    """
    This class get the output from your GPU, this class is readable like a dictionary,
    please read the documentation on :py:attr:`~jtop.jtop.gpu` but is also usable to enable, disable 3d scaling on your device.

    .. code-block:: python

        with jtop() as jetson:
            if jetson.ok():
                jetson.gpu.set_scaling_3D("gpu", True)

    Below all methods available using the :py:attr:`~jtop.jtop.gpu` attribute
    """

    def __init__(self):
        super(GPU, self).__init__()

    def set_scaling_3D(self, name, value):
        """
        Enable disable GPU 3D scaling. this method send a command like below on your Jetson.

        Set 3D scaling on your board, like the command below. To know the GPU name use :py:attr:`~jtop.jtop.gpu`

        .. code-block:: python

            with jtop() as jetson:
                if jetson.ok():
                    jetson.gpu.set_scaling_3D("ga10b", True)

        is equivalent to:

        .. code-block:: bash
            :class: no-copybutton

            echo 1 > /sys/devices/17000000.ga10b/enable_3d_scaling

        :param name: GPU name
        :type name: str
        :param value: Enable/Disable 3D scaling
        :type value: bool
        :raises JtopException: if GPU doesn't exist
        """
        if name not in self._data:
            raise JtopException("GPU \"{name}\" does not exist".format(name=name))
        # Set new 3D scaling
        self._controller.put({'gpu': {'command': '3d_scaling', 'name': name, 'value': value}})

    def get_scaling_3D(self, name):
        """
        Return status of 3D scaling, this output is also readable from :py:attr:`~jtop.jtop.gpu` attribute

        :param name: GPU name
        :type name: str
        :raises JtopException: if GPU doesn't exist
        :return: status 3D scaling
        :rtype: bool
        """
        if name not in self._data:
            raise JtopException("GPU \"{name}\" does not exist".format(name=name))
        return self._data[name]['status']['3d_scaling']

    @property
    def scaling_3D(self):
        """
        Return status of 3D scaling, this output is also readable from :py:attr:`~jtop.jtop.gpu` attribute

        .. code-block:: python

            with jtop() as jetson:
                if jetson.ok():
                    # Set new 3D scaling
                    jetson.gpu.set_scaling_3D = True
                    # same of
                    jetson.gpu.set_scaling_3D("ga10b", True)

        :raises JtopException: if there are no integrated GPU
        :return: status 3D scaling
        :rtype: bool
        """
        # Get first integrated gpu
        name = self._get_first_integrated_gpu()
        if not name:
            raise JtopException("no Integrated GPU available")
        return self.get_scaling_3D(name)

    @scaling_3D.setter
    def scaling_3D(self, value):
        # Get first integrated gpu
        name = self._get_first_integrated_gpu()
        if not name:
            raise JtopException("no Integrated GPU available")
        self.set_scaling_3D(name, value)

    def set_railgate(self, name, value):
        if name not in self._data:
            raise JtopException("GPU \"{name}\" does not exist".format(name=name))
        # Set new 3D scaling
        self._controller.put({'gpu': {'command': 'railgate', 'name': name, 'value': value}})

    def get_railgate(self, name):
        if name not in self._data:
            raise JtopException("GPU \"{name}\" does not exist".format(name=name))
        return self._data[name]['status']['railgate']

    def _get_first_integrated_gpu(self):
        for name in self._data:
            if self._data[name]['type'] == 'integrated':
                return name
        return ''


class GPUService(object):

    def __init__(self):
        # Detect integrated GPU
        igpu_path = DEFAULT_IGPU_PATH
        if os.getenv('JTOP_TESTING', False):
            igpu_path = "/fake_sys/class/devfreq/"
            logger.warning("Running in JTOP_TESTING folder={root_dir}".format(root_dir=igpu_path))
        self._gpu_list = find_igpu(igpu_path)
        # Find discrete GPU
        self._gpu_list.update(find_dgpu())
        # Check status
        if not self._gpu_list:
            logger.warning("No NVIDIA GPU available")

    def set_scaling_3D(self, name, value):
        if name not in self._gpu_list:
            logger.error("GPU \"{name}\" does not exist".format(name=name))
            return False
        if '3d_scaling' not in self._gpu_list[name]:
            logger.error("GPU \"{name}\" does not have 3D scaling".format(name=name))
            return False
        path_3d_scaling = self._gpu_list[name]['3d_scaling']
        string_value = "1" if value else "0"
        # Write new status 3D scaling
        try:
            if os.access(path_3d_scaling, os.W_OK):
                with open(path_3d_scaling, 'w') as f:
                    f.write(string_value)
            logger.info("GPU \"{name}\" set 3D scaling to {value}".format(name=name, value=value))
        except OSError as e:
            logger.error("I cannot set 3D scaling {}".format(e))

    def set_railgate(self, name, value):
        if name not in self._gpu_list:
            logger.error("GPU \"{name}\" does not exist".format(name=name))
            return False
        if 'railgate' not in self._gpu_list[name]:
            logger.error("GPU \"{name}\" does not have railgate".format(name=name))
            return False
        path_railgate = self._gpu_list[name]['railgate']
        string_value = "1" if value else "0"
        # Write new status railgate
        try:
            if os.access(path_railgate, os.W_OK):
                with open(path_railgate, 'w') as f:
                    f.write(string_value)
            logger.info("GPU \"{name}\" set railgate to {value}".format(name=name, value=value))
        except OSError as e:
            logger.error("I cannot set Railgate {}".format(e))

    def get_status(self):
        gpu_list = {}
        # Read iGPU frequency
        for name, data in self._gpu_list.items():
            # Initialize GPU status
            gpu = {'type': data['type']}

            # Detect frequency and load
            if gpu['type'] == 'integrated':
                is_thor = data.get('is_thor', False)

                # Read status GPU
                gpu['status'] = igpu_read_status(data['path'], is_thor)

                # Read frequency
                gpu['freq'] = igpu_read_freq(data['frq_path'], is_thor)

                # Thor cihazlarda sysfs "power/control" olmayacak
                if not is_thor and os.access(data['path'] + "/power/control", os.R_OK):
                    with open(data['path'] + "/power/control", 'r') as f:
                        gpu['power_control'] = f.read().strip()

            elif gpu['type'] == 'discrete':
                logger.info("TODO discrete GPU")

            # Load all status in GPU
            gpu_list[name] = gpu

        return gpu_list

# EOF
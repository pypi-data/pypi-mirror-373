## gpu_list

This is a simple little utility to list GPUs and their VRAM amounts in Windows and Linux. The main reason I create this is because WMI doesn't list accurate VRAM information, and it's slow, and I hate WMI a lot. The Windows code uses no external libraries or tools. Linux code will use `nvidia-smi` if necessary.

## How it works

In Windows, it enumerates the registry keys at `SYSTEM\ControlSet001\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}` and gets the info from there.
It relies on the existence of `HardwareInformation.qwMemorySize` keys, which were added sometime in Windows 10 I think. Maybe. So this probably won't work for older Windows. I purposely didn't add support for the 32 bit registry key because it's bunk.

Vendor and Device name are looked up in the included pci.ids file from https://pci-ids.ucw.cz/

In Linux, it's a bit tougher. First it checks sysfs files `mem_info_vram_total` and `vram_total`, and uses those if found.
If any NVidia devices are found it will use `nvidia-smi` to get an accurate VRAM total. For everything else it will check the pcie BAR memory mapping and try to estimate the VRAM. It was very close for my Intel GPU, so I kept it in. Please report any inaccurate readings.

## Installation

`pip install gpu_list`

## Usage

If you just want some quick info printed out, run `gpu_list` from the console, you will get output that looks like this:
```
┌────────────────────────────────────────┬───────────┬─────────────────────────────┬───────────┬─────────┐
│                 vendor                 │ vendor_id │            device           │ device_id │ vram_gb │
├────────────────────────────────────────┼───────────┼─────────────────────────────┼───────────┼─────────┤
│           Intel Corporation            │    8086   │        DG2 [Arc A770]       │    56a0   │  17.05  │
│           NVIDIA Corporation           │    10de   │ GA102 [GeForce RTX 3090 Ti] │    2203   │  24.15  │
│ Advanced Micro Devices, Inc. [AMD/ATI] │    1002   │           Raphael           │    164e   │   0.07  │
└────────────────────────────────────────┴───────────┴─────────────────────────────┴───────────┴─────────┘
```

(vram_gb = bytes / 1e9)

However, this is mostly meant to be used from code.  gpu_list exports one function: `get_info`. It returns a list of dicts, one dict per GPU found.
Each dict has the following keys: `vendor`, `vendor_id`, `device`, `device_id`, and `vram_gb`

Here's some example code:

```python
from gpu_list import get_info

infos = get_info()

if infos:
    for index, info in enumerate(infos):
        print(f"Info for GPU #{index+1}")
        print("-" * 50)
        print(f"vendor = {info["vendor"]}")
        print(f"vendor_id = {info["vendor_id"]}")
        print(f"device = {info["device"]}")
        print(f"device_id = {info["device_id"]}")
        print(f"vram_gb = {info["vram_gb"]}")
        print("-" * 50)
else:
    print("Error getting GPU list!")
```

Running that code produces something like this:
```
Info for GPU #1
--------------------------------------------------
vendor = Intel Corporation
vendor_id = 8086
device = DG2 [Arc A770]
device_id = 56a0
vram_gb = 17.05
--------------------------------------------------
Info for GPU #2
--------------------------------------------------
vendor = NVIDIA Corporation
vendor_id = 10de
device = GA102 [GeForce RTX 3090 Ti]
device_id = 2203
vram_gb = 24.15
--------------------------------------------------
Info for GPU #3
--------------------------------------------------
vendor = Advanced Micro Devices, Inc. [AMD/ATI]
vendor_id = 1002
device = Raphael
device_id = 164e
vram_gb = 0.07
--------------------------------------------------
```
import re
import os
import platform
from prettytable import PrettyTable, TableStyle
import subprocess

VENDORS = {}
current_vendor_id = None
pci_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pci.ids")
try:
    with open(pci_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            if line.startswith("\t\t"):
                continue
            elif line.startswith("\t"):
                if current_vendor_id and current_vendor_id in VENDORS:
                    parts = line.strip().split("  ", 1)
                    if len(parts) == 2:
                        device_id, device_name = parts
                        VENDORS[current_vendor_id]["devices"][device_id] = device_name
            else:
                parts = line.split("  ", 1)
                if len(parts) == 2:
                    vendor_id, vendor_name = parts
                    if len(vendor_id) == 4 and all(
                        c in "0123456789abcdef" for c in vendor_id.lower()
                    ):
                        current_vendor_id = vendor_id
                        VENDORS[current_vendor_id] = {
                            "name": vendor_name,
                            "devices": {},
                        }
                    else:
                        current_vendor_id = None

except FileNotFoundError:
    print(f"Error: File not found at {pci_path}")


def get_vendor_name(vendor_id: str) -> str:
    try:
        return VENDORS[vendor_id]["name"].strip()
    except:
        return "Unknown"


def get_device_name(vendor_id: str, device_id: str) -> str:
    try:
        return VENDORS[vendor_id]["devices"][device_id].strip()
    except:
        return "Unknown"


def get_vendor(device_id: str) -> str | None:
    m = re.search(r"VEN_([0-9a-fA-F]{4})", device_id, re.IGNORECASE)
    return m.group(1).lower() if m else None


def get_device(device_id: str) -> str | None:
    m = re.search(r"DEV_([0-9a-fA-F]{4})", device_id, re.IGNORECASE)
    return m.group(1).lower() if m else None


def get_gpu_info_windows():
    import winreg
    devices = {}
    path = r"SYSTEM\ControlSet001\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as base_key:
            index = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(base_key, index)
                    subkey_path = f"{path}\\{subkey_name}"
                    with winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE, subkey_path
                    ) as subkey:
                        try:
                            device_id = str(
                                winreg.QueryValueEx(subkey, "MatchingDeviceId")[0]
                            ).upper()
                            mem, _ = winreg.QueryValueEx(
                                subkey, "HardwareInformation.qwMemorySize"
                            )
                            # desc, _ = winreg.QueryValueEx(subkey, "DriverDesc")
                            vendor = get_vendor(device_id)
                            vendor_name = get_vendor_name(vendor)
                            device = get_device(device_id)
                            device_name = get_device_name(vendor, device)
                            # key by device_id to get rid of possible dupes
                            devices[device_id] = {
                                "vendor": vendor_name,
                                "vendor_id": vendor,
                                "device": device_name,
                                "device_id": device,
                                "vram_gb": round(mem / 1e9, 2),
                            }
                        except FileNotFoundError:
                            pass
                    index += 1
                except OSError:
                    break
    except FileNotFoundError:
        print(f"Error: Registry key not found: HKLM\\{path}")
        print("This could be a permissions issue or an unusual Windows configuration.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return [v for _,v in devices.items()] if devices else []

    
def get_gpu_info_linux():
    def get_nvidia_vram_map():
        nvidia_vram = {}
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=pci.bus_id,memory.total', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, check=True
            )
            for line in result.stdout.strip().split('\n'):
                parts = line.split(', ')
                # fix pci format
                if len(parts) == 2:
                    pci_id_raw, memory_mib = parts
                    pci_parts = pci_id_raw.split(':')
                    if len(pci_parts) == 3:
                        pci_id = f"0000:{pci_parts[1]}:{pci_parts[2]}"
                    else:
                        pci_id = pci_id_raw
                    vram_bytes = int(memory_mib) * 1024 * 1024
                    nvidia_vram[pci_id] = vram_bytes
        except:
            pass
        return nvidia_vram

    base_path = "/sys/class/drm/"
    devices = {}
    nvidia_vram_map = get_nvidia_vram_map()

    try:
        cards = sorted(
            [d for d in os.listdir(base_path) if d.startswith("card") and not "-" in d]
        )

        for card in cards:
            device_symlink_path = os.path.join(base_path, card, "device")
            if not os.path.islink(device_symlink_path):
                continue

            pci_device_real_path = os.path.realpath(device_symlink_path)
            pci_slot_id = os.path.basename(pci_device_real_path)

            vendor_id, device_id = None, None
            try:
                with open(os.path.join(pci_device_real_path, "vendor"), "r") as f:
                    vendor_id = f.read().strip()[2:].lower()
                with open(os.path.join(pci_device_real_path, "device"), "r") as f:
                    device_id = f.read().strip()[2:].lower()
            except (IOError, IndexError):
                continue

            vendor_name = get_vendor_name(vendor_id)
            device_name = get_device_name(vendor_id, device_id)

            vram_bytes = 0
            
            # vendor is nvidia, use nvidia-smi output from earlier
            if vendor_id == "10de":
                vram_bytes = nvidia_vram_map.get(pci_slot_id, 0)
            else:
                # method 1, most accurate but not always available
                vram_files_to_check = ["mem_info_vram_total", "vram_total"]
                for filename in vram_files_to_check:
                    vram_path = os.path.join(pci_device_real_path, filename)
                    if os.path.exists(vram_path):
                        try:
                            with open(vram_path, "r") as f:
                                vram_bytes = int(f.read().strip())
                            if vram_bytes > 0:
                                break
                        except (IOError, ValueError):
                            continue
                
                # method 2, check PCI BAR, might be inaccurate. for nvidia i got +10gb
                if vram_bytes == 0:
                    try:
                        IORESOURCE_MEM = 0x00000200
                        mem_bar_sizes = []
                        resource_path = os.path.join(pci_device_real_path, "resource")
                        if os.path.exists(resource_path):
                            with open(resource_path, "r") as f:
                                for line in f:
                                    try:
                                        parts = line.split()
                                        flags = int(parts[2], 16)
                                        if flags & IORESOURCE_MEM:
                                            start = int(parts[0], 16)
                                            end = int(parts[1], 16)
                                            size = end - start + 1
                                            mem_bar_sizes.append(size)
                                    except (ValueError, IndexError):
                                        continue
                        
                        MIN_VRAM_THRESHOLD_BYTES = 256 * 1024 * 1024
                        large_bars = [s for s in mem_bar_sizes if s > MIN_VRAM_THRESHOLD_BYTES]
                        if large_bars:
                            large_bars.sort(reverse=True)
                            if len(large_bars) > 1:
                                vram_bytes = large_bars[1]
                            else:
                                vram_bytes = large_bars[0]
                    except (IOError, ValueError):
                        pass

            devices[pci_slot_id] = {
                "vendor": vendor_name,
                "vendor_id": vendor_id,
                "device": device_name,
                "device_id": device_id,
                "vram_gb": round(vram_bytes / 1e9, 2),
            }

        return [v for _,v in devices.items()]

    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"An unexpected error occurred in get_gpu_info_linux: {e}")
        return []


def get_info() -> list[dict]:
    if platform.system() == "Windows":
        return get_gpu_info_windows()
    else:
        return get_gpu_info_linux()
    

def main():
    def print_info(infos: list):
        if infos:
            pt = PrettyTable()
            pt.set_style(TableStyle.SINGLE_BORDER)
            pt.field_names = ["vendor", "vendor_id", "device", "device_id", "vram_gb"]
            for x in infos:
                pt.add_row(
                    [
                        x["vendor"],
                        x["vendor_id"],
                        x["device"],
                        x["device_id"],
                        x["vram_gb"],
                    ]
                )
            print(pt)
        else:
            print("Either no GPU found or error getting GPU info!")
    i = []
    if platform.system() == "Windows":
        i = get_gpu_info_windows()
    else:
        i = get_gpu_info_linux()
    print_info(i)

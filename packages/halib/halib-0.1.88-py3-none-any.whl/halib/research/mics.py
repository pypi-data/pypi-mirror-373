import platform

PC_NAME_TO_ABBR = {
    "DESKTOP-JQD9K01": "MainPC",
    "DESKTOP-5IRHU87": "MSI_Laptop",
    "DESKTOP-96HQCNO": "4090_SV",
    "DESKTOP-Q2IKLC0": "4GPU_SV",
    "DESKTOP-QNS3DNF": "1GPU_SV"
}

def get_PC_name():
    return platform.node()

def get_PC_abbr_name():
    pc_name = get_PC_name()
    return PC_NAME_TO_ABBR.get(pc_name, "Unknown")

def get_toolchain_info(version):
    """Retrieve information from the toolchains"""

    url = "https://gitlab.cern.ch/lhcb-core/lcg-toolchains/-/raw/master/LCG_{version}/lcginfo.json"
    import json

    import requests

    resp = requests.get(url.format(version=version))
    info = json.loads(resp.text)
    return info


def get_toolchain_packages(
    version, platform, used_packages, toolchain_variant="LHCB_Core"
):
    """Look for packages in the list in the toolchain information
    The toolchain variant is LHCB_Core, LHCB_7 etc...
    used_packaged is a map name:version"""

    all_toolchain_info = get_toolchain_info(version)
    info = all_toolchain_info.get(toolchain_variant)
    if info is None:
        raise Exception(f"{toolchain_variant} not found for LCG {version}")

    # Looking for the packages for the platform
    if platform not in info:
        raise Exception(
            "Platform {plat} not found in toolchain information from {lcg}",
            plat=platform,
            lcg=version,
        )
    toolchain_platform_info = info[platform]
    toolchain_packages = toolchain_platform_info["packages"]

    # Looking for the package hashes from the toolchain list
    deps = {}
    not_found = []
    version_mismatch = []
    for p, v in used_packages.items():
        tp = toolchain_packages.get(p)
        if tp is None:
            not_found.append(p)
        else:
            # Checking that the version in the toolchain matches what we found
            if v != tp["version"]:
                version_mismatch.append(p)
            deps[p] = tp
    return deps, not_found, version_mismatch

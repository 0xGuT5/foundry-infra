#!/usr/bin/env python3
"""Validate the inventory before Terraform ever sees it."""

import ipaddress
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent / "inventory"

REQUIRED = {
    "name", "owner", "purpose", "vlan", "node",
    "vm_id", "cores", "memory_mb", "disk_gb", "ipv4", "expires",
}

MIN_VM_ID = 9200
MAX_VM_ID = 9999

errors = []
hints = []


def load(name):
    return yaml.safe_load((ROOT / name).read_text())


def main():
    vlans = load("vlans.yaml")["vlans"]
    nodes = {n["name"]: n for n in load("nodes.yaml")["nodes"]}
    vms = load("vms.yaml").get("vms") or []

    # How many VMs each node already carries. Used for placement hints.
    load_by_node = Counter(vm.get("node") for vm in vms if vm.get("node"))

    seen_names, seen_ids, seen_ips = {}, {}, {}

    for i, vm in enumerate(vms):
        label = vm.get("name", f"entry #{i}")

        missing = REQUIRED - vm.keys()
        if missing:
            errors.append(f"{label}: missing fields: {', '.join(sorted(missing))}")
            # A missing vlan means we can't hint at placement either.
            if "vlan" in vm and "node" in missing:
                suggest_node(vm["vlan"], nodes, load_by_node, label)
            continue

        # --- names ---
        if vm["name"] in seen_names:
            errors.append(f"{label}: duplicate name")
        seen_names[vm["name"]] = i

        # --- vm_id ---
        if vm["vm_id"] in seen_ids:
            other = vms[seen_ids[vm["vm_id"]]]["name"]
            errors.append(f"{label}: vm_id {vm['vm_id']} already used by {other}")
        seen_ids[vm["vm_id"]] = i

        if not MIN_VM_ID <= vm["vm_id"] <= MAX_VM_ID:
            errors.append(
                f"{label}: vm_id {vm['vm_id']} outside Terraform range "
                f"{MIN_VM_ID}-{MAX_VM_ID}"
            )

        # --- vlan exists ---
        if vm["vlan"] not in vlans:
            errors.append(
                f"{label}: unknown vlan '{vm['vlan']}' "
                f"(known: {', '.join(sorted(vlans))})"
            )
            continue


        # --- node exists, reaches that vlan, and has a template ---
        if vm["node"] not in nodes:
            errors.append(f"{label}: unknown node '{vm['node']}'")
        else:
            node = nodes[vm["node"]]

            if vm["vlan"] not in node["vlans"]:
                errors.append(
                    f"{label}: node '{vm['node']}' has no port on vlan "
                    f"'{vm['vlan']}'"
                )
                suggest_node(vm["vlan"], nodes, load_by_node, label)

            if not node.get("template_vm_id"):
                errors.append(
                    f"{label}: node '{vm['node']}' has no cloud-init template. "
                    f"Build one there and record its VMID in nodes.yaml."
                )
        # --- ip valid, unique, inside the vlan subnet ---
        try:
            iface = ipaddress.ip_interface(vm["ipv4"])
            addr = str(iface.ip)

            if addr in seen_ips:
                other = vms[seen_ips[addr]]["name"]
                errors.append(f"{label}: IP {addr} already used by {other}")
            seen_ips[addr] = i

            subnet = ipaddress.ip_network(vlans[vm["vlan"]]["subnet"])
            if iface.ip not in subnet:
                errors.append(
                    f"{label}: {addr} is not inside {vm['vlan']} ({subnet})"
                )
            if iface.network.prefixlen != subnet.prefixlen:
                errors.append(
                    f"{label}: prefix /{iface.network.prefixlen} does not match "
                    f"{vm['vlan']} (/{subnet.prefixlen})"
                )
        except ValueError:
            errors.append(f"{label}: '{vm['ipv4']}' is not a valid address/prefix")

        # --- expiry ---
        try:
            expires = datetime.strptime(str(vm["expires"]), "%Y-%m-%d").date()
            if expires <= date.today():
                errors.append(f"{label}: expires {vm['expires']} is in the past")
        except ValueError:
            errors.append(f"{label}: expires '{vm['expires']}' is not YYYY-MM-DD")

        # --- sizes ---
        if not 1 <= vm["cores"] <= 32:
            errors.append(f"{label}: cores {vm['cores']} outside 1-32")
        if not 512 <= vm["memory_mb"] <= 131072:
            errors.append(f"{label}: memory_mb {vm['memory_mb']} outside 512-131072")
        if not 10 <= vm["disk_gb"] <= 1000:
            errors.append(f"{label}: disk_gb {vm['disk_gb']} outside 10-1000")

    return report(len(vms))


def suggest_node(vlan, nodes, load_by_node, label):
    """Tell the operator which nodes can actually serve this VLAN."""

    eligible = [
        n for n, cfg in nodes.items()
        if vlan in cfg["vlans"] and cfg.get("template_vm_id")
    		]
    if not eligible:
        hints.append(
            f"{label}: no node both reaches '{vlan}' and has a template"
        )
        return
    ranked = sorted(eligible, key=lambda n: (load_by_node[n], n))
    listing = ", ".join(f"{n} ({load_by_node[n]} VMs)" for n in ranked)
    hints.append(f"{label}: eligible for '{vlan}' — {listing}. Least loaded: {ranked[0]}")


def report(count):
    for h in hints:
        print(f"  → {h}")
    if errors:
        print(f"\n✗ {len(errors)} problem(s):\n")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"✓ {count} VM(s) validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())

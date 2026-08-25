# foundry-infra

Self-service infrastructure and services for a bare-metal research testbed.

Basically removing the bottleneck... which was me. Let it be a PR validation instead.

## Placement

A requester chooses a VLAN. nodes.yaml records which nodes are cabled to which VLAN and over which bridge.
The validator lists eligible nodes ranked by current load. The chosen node is written into vms.yaml and becomes a recorded fact.
Placement is decided once, at creation. Terraform never recomputes it (changing node_name forces a rebuild).

To add a node to a VLAN change to nodes.yaml. It Takes effect for the next VM placement. 

## VM Image 
Image customisation must happen on the management VM, not on a hypervisor. Installing libguestfs-tools pulls fuse3, which conflicts with fuse, which pve-cluster depends on.
The template image is built on the management VM with `virt-customize`, then copied to the proxmox node before `qm create`. Packages are pre-downloaded and installed offline via `--copy-in`, since the libguestfs appliance has no working network inside a nested VM.

## Architecture

_TBD

# foundry-infra

Self-service infrastructure and services for a bare-metal research testbed.

Basically removing the bottleneck... which was me. Let it be a PR validation instead.

## Placement

A requester chooses a VLAN. nodes.yaml records which nodes are cabled to which VLAN and over which bridge.
The validator lists eligible nodes ranked by current load. The chosen node is written into vms.yaml and becomes a recorded fact.
Placement is decided once, at creation. Terraform never recomputes it (changing node_name forces a rebuild).

To add a node to a VLAN change to nodes.yaml. It Takes effect for the next VM placement. 


## Architecture

_TBD

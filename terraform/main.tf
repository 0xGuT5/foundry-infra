provider "proxmox" {}

locals {
  vlans = yamldecode(file("${path.module}/../inventory/vlans.yaml")).vlans
  nodes = {
    for n in yamldecode(file("${path.module}/../inventory/nodes.yaml")).nodes :
    n.name => n
  }

  # Resolve each VM's bridge and gateway from its node and VLAN.
  vms = {
    for vm in yamldecode(file("${path.module}/../inventory/vms.yaml")).vms :
    vm.name => merge(vm, {
      bridge      = local.nodes[vm.node].vlans[vm.vlan]
      gateway     = local.vlans[vm.vlan].gateway
      template_id = local.nodes[vm.node].template_vm_id
    })
  }
  imported = {
    for vm in yamldecode(file("${path.module}/../inventory/imported.yaml")).imported :
    vm.name => vm
  }
}

resource "proxmox_virtual_environment_vm" "vm" {
  for_each = local.vms

  name      = each.value.name
  node_name = each.value.node
  vm_id     = each.value.vm_id

  description = "Owner: ${each.value.owner}. ${each.value.purpose}"
  tags        = ["terraform", "foundry-infra", each.value.vlan]

  clone {
    vm_id = each.value.template_id
    full  = true
  }

  cpu {
    cores = each.value.cores
    type  = "host"
  }

  memory {
    dedicated = each.value.memory_mb
  }

  disk {
    datastore_id = var.datastore_id
    interface    = "scsi0"
    size         = each.value.disk_gb
  }

  network_device {
    bridge   = each.value.bridge
    firewall = true
  }

  initialization {
    datastore_id = var.datastore_id

    ip_config {
      ipv4 {
        address = each.value.ipv4
        gateway = each.value.gateway
      }
    }

    user_account {
      username = "ubuntu"
      keys     = var.ssh_public_keys
    }
  }

  agent {
    enabled = true
  }
}

resource "proxmox_virtual_environment_vm" "imported" {
  for_each = local.imported

  name      = each.value.hostname
  node_name = each.value.node
  vm_id     = each.value.vm_id

  on_boot       = false
  scsi_hardware = "virtio-scsi-single"

  cpu {
    cores   = each.value.cores
    sockets = each.value.sockets
    type    = "host"
  }

  memory {
    dedicated = each.value.memory_mb
  }

  disk {
    datastore_id = var.datastore_id
    interface    = "scsi0"
    size         = each.value.disk_gb
    iothread     = true
  }

  network_device {
    bridge   = local.nodes[each.value.node].vlans[each.value.vlan]
    firewall = true
  }

  lifecycle {
    prevent_destroy = true
  }
}

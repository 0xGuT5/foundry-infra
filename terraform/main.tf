provider "proxmox" {}

resource "proxmox_virtual_environment_vm" "demo" {
  name      = "demo-01"
  node_name = var.target_node
  vm_id     = 200

  description = "First VM provisioned by Terraform. Managed in foundry-infra."
  tags        = ["terraform", "foundry-infra"]

  clone {
    vm_id = 9000
    full  = true
  }

  cpu {
    cores = 2
    type  = "host"
  }

  memory {
    dedicated = 4096
  }

  disk {
    datastore_id = var.datastore_id
    interface    = "scsi0"
    size         = 40
  }

  network_device {
    bridge   = "vmbr0"
    firewall = true
  }

  initialization {
    datastore_id = var.datastore_id

    ip_config {
      ipv4 {
        address = "172.21.18.95/24"
        gateway = "172.21.19.254"
      }
    }

    user_account {
      username = "ubuntu"
      keys     = [trimspace(file("~/.ssh/id_ed25519.pub"))]
    }
  }

  agent {
    enabled = true
  }
}

variable "target_node" {
  description = "Node to place VMs on"
  type        = string
}

variable "datastore_id" {
  description = "Storage for VM disks"
  type        = string
  default     = "local-lvm"
}

variable "ssh_public_keys" {
  description = "SSH public keys to inject into provisioned VMs"
  type        = list(string)
}

variable "datastore_id" {
  description = "Storage for VM disks"
  type        = string
  default     = "local-lvm"
}

variable "ssh_public_keys" {
  description = "SSH public keys to inject into provisioned VMs"
  type        = list(string)
}

variable "template_vm_id" {
  description = "VMID of the cloud-init template to clone from"
  type        = number
  default     = 9000
}

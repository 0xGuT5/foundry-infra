output "vm_id" {
  value = proxmox_virtual_environment_vm.demo.vm_id
}

output "vm_name" {
  value = proxmox_virtual_environment_vm.demo.name
}

output "vm_ipv4" {
  value = proxmox_virtual_environment_vm.demo.ipv4_addresses
}

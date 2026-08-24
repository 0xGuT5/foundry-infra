output "vms" {
  description = "Provisioned VMs and their addresses"
  value = {
    for name, vm in proxmox_virtual_environment_vm.vm :
    name => {
      vm_id = vm.vm_id
      node  = vm.node_name
      ipv4  = vm.ipv4_addresses
    }
  }
}

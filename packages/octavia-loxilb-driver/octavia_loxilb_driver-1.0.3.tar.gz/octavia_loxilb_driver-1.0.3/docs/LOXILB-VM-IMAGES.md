# LoxiLB VM Images - Distribution Guide

This document explains how LoxiLB VM images are distributed and how users can obtain them for OpenStack integration.

## 📦 Image Distribution

### Official Release Location

LoxiLB VM images are distributed through **GitHub Releases** at:
**https://github.com/loxilb-io/loxilb/releases**

### Download Process

The automated setup script handles image download, but users can also download manually:

```bash
# Download latest LoxiLB VM image
wget https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/releases/download/vm-v1.0.0/loxilb-vm-standard-v1.0.0.qcow2.gz

```

## 🖥️ VM Image Specifications

### Default Configuration

- **Format**: QCOW2
- **OS**: Ubuntu 22.04 LTS (minimal)
- **Architecture**: x86_64
- **Default Size**: 8GB (compressed), expands to 40GB
- **Boot**: UEFI and Legacy BIOS compatible

### Pre-installed Components

- **LoxiLB Service**: Latest stable version
- **Dependencies**: All required libraries and tools
- **Network Tools**: Standard networking utilities
- **SSH Server**: Enabled with key-based authentication
- **Cloud-init**: Configured for OpenStack metadata

### Default Credentials

- **Username**: `ubuntu`
- **Authentication**: SSH key-based (no password)
- **sudo**: Passwordless sudo enabled
- **LoxiLB API**: admin/admin (default credentials)

## 🚀 Automated Registration

### Using Setup Script

The setup script automatically handles image registration:

```bash
# Automatic download and registration
octavia-loxilb-setup --deployment-type kolla

```

### Configuration Override

For custom image locations:

```json
{
  "image": {
    "name": "custom-loxilb-vm-image",
    "url": "https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/releases/download/vm-v1.0.0/loxilb-vm-standard-v1.0.0.qcow2.gz
    ",
    "min_disk": 40,
    "min_ram": 4096
  }
}
```

Use with: `octavia-loxilb-setup --custom-config config.json`

## 🔧 Manual Registration

### Step-by-Step Process

**1. Download Image:**
```bash
# Create directory for images
mkdir -p ~/loxilb-images
cd ~/loxilb-images

# Download latest release
wget https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/releases/download/vm-v1.0.0/loxilb-vm-standard-v1.0.0.qcow2.gz

unzip loxilb-vm-standard-v1.0.0.qcow2.gz

```

**2. Register in OpenStack:**
```bash
# Create Glance image
openstack image create \
  --disk-format qcow2 \
  --container-format bare \
  --min-disk 40 \
  --min-ram 4096 \
  --public \
  --file loxilb-vm.qcow2 \
  loxilb-vm-image

# Verify registration
openstack image show loxilb-vm-image
openstack image list | grep loxilb
```

**3. Set Image Properties:**
```bash
# Add metadata for better identification
openstack image set \
  --property os_type=linux \
  --property os_distro=ubuntu \
  --property os_version=22.04 \
  --property hw_scsi_model=virtio-scsi \
  --property hw_disk_bus=scsi \
  loxilb-vm-image
```

### Advanced Registration Options

**For Production Environments:**
```bash
# Set specific properties for performance
openstack image set \
  --property hw_vif_model=virtio \
  --property hw_vif_multiqueue_enabled=true \
  --property hw_cpu_policy=dedicated \
  --property hw_mem_page_size=large \
  loxilb-vm-image
```

**For Development/Testing:**
```bash
# Minimal requirements for testing
openstack image create \
  --disk-format qcow2 \
  --container-format bare \
  --min-disk 20 \
  --min-ram 2048 \
  --file loxilb-vm.qcow2 \
  loxilb-vm-dev-image
```

## 🔍 Image Verification

### Test Boot

```bash
# Create test instance to verify image works
openstack server create \
  --flavor m1.small \
  --image loxilb-vm-image \
  --network private \
  --key-name my-key \
  loxilb-test

# Check if it boots successfully
openstack server show loxilb-test
openstack console log show loxilb-test
```

### Service Verification

```bash
# SSH to test instance
ssh -i ~/.ssh/my-key.pem ubuntu@<VM_IP>

# Check LoxiLB service
sudo systemctl status loxilb

# Test API endpoint
curl -k https://localhost:8091/netlox/v1/config/status
```

## 📋 Supported Versions

### Version Compatibility

| OpenStack Version | LoxiLB Image Version | Compatibility |
|-------------------|---------------------|---------------|
| Zed               | v0.9.0+             | ✅ Full        |
| 2023.1 (Antelope)| v0.9.2+             | ✅ Full        |
| 2023.2 (Bobcat)  | v0.9.3+             | ✅ Full        |
| 2024.1 (Caracal) | v0.9.3+             | ✅ Full        |
| Master            | latest              | 🧪 Testing     |

### Version Selection

```bash
# Use specific version
octavia-loxilb-setup --image-version v0.9.3

# Use latest stable (default)
octavia-loxilb-setup

# Use development version (not recommended for production)
octavia-loxilb-setup --image-version latest
```

## 🏗️ Custom Image Building

### When to Build Custom Images

- Custom LoxiLB configuration requirements
- Integration with existing configuration management
- Specific OS requirements or hardening
- Custom networking or security configurations

### Building Process

```bash
# Clone LoxiLB repository
git clone https://github.com/loxilb-io/loxilb.git
cd loxilb

# Use provided Packer/cloud-init templates
cd openstack-images/

# Customize configuration
vim cloud-init-config.yml
vim loxilb-custom.conf

# Build image (requires Packer)
packer build loxilb-openstack.pkr.hcl

# Upload custom image
openstack image create \
  --disk-format qcow2 \
  --container-format bare \
  --file custom-loxilb.qcow2 \
  custom-loxilb-vm-image
```

### Custom Configuration Template

Example cloud-init configuration for custom requirements:

```yaml
# cloud-init-config.yml
#cloud-config
package_update: true
package_upgrade: false

packages:
  - curl
  - wget
  - jq
  - htop

write_files:
  - path: /etc/loxilb/custom.conf
    content: |
      # Custom LoxiLB configuration
      log_level: debug
      api_port: 8091
      bgp_port: 9443
    owner: root:root
    permissions: '0644'

runcmd:
  - systemctl enable loxilb
  - systemctl start loxilb
  - systemctl status loxilb
```

## 🔒 Security Considerations

### Image Security

- **Source Verification**: Always download from official GitHub releases
- **Checksum Verification**: Verify image checksums before use
- **Network Security**: Images contain minimal attack surface
- **Access Control**: Use proper SSH key management

### Deployment Security

```bash
# Create dedicated project for LoxiLB resources
openstack project create loxilb-infra

# Use service accounts
openstack user create --project loxilb-infra loxilb-service
openstack role add --user loxilb-service --project loxilb-infra member

# Restrict image visibility
openstack image set --private --project loxilb-infra loxilb-vm-image
```

### Network Security

```bash
# Create isolated management network
openstack network create --project loxilb-infra loxilb-mgmt-private

# Restrict security group rules
openstack security group rule create loxilb-mgmt-sec-grp \
  --protocol tcp --dst-port 8091 --remote-ip 192.168.1.0/24
```

## 📊 Monitoring & Updates

### Update Strategy

```bash
# Check for new releases
curl -s https://api.github.com/repos/loxilb-io/loxilb/releases/latest | jq -r .tag_name

# Download and register new version
wget https://github.com/loxilb-io/loxilb/releases/download/v0.9.4/loxilb-vm.qcow2
openstack image create --file loxilb-vm.qcow2 loxilb-vm-image-v0.9.4

# Update configuration to use new image
octavia-loxilb-setup --image-name loxilb-vm-image-v0.9.4
```

### Monitoring

```bash
# Check image usage
openstack server list --image loxilb-vm-image

# Monitor image health
openstack image show loxilb-vm-image | grep status

# Automated health checking
octavia-loxilb-health-check --image-verification
```

## 🆘 Troubleshooting Image Issues

### Common Problems

**Image Download Fails:**
```bash
# Check GitHub API rate limits
curl -I https://api.github.com/repos/loxilb-io/loxilb/releases/latest

# Use alternative download methods
curl -L -o loxilb-vm.qcow2 https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/releases/download/vm-v1.0.0/loxilb-vm-standard-v1.0.0.qcow2.gz
```

**Image Registration Issues:**
```bash
# Check Glance service
openstack service list | grep glance
openstack endpoint list --service glance

# Verify disk space
openstack quota show --class
df -h /var/lib/glance/images/
```

**VM Boot Issues:**
```bash
# Check console logs
openstack console log show <VM_ID>

# Verify flavor requirements
openstack flavor show <FLAVOR_ID>
openstack image show loxilb-vm-image | grep -E "min_disk|min_ram"
```

## 📚 Additional Resources

- **LoxiLB Documentation**: https://github.com/loxilb-io/loxilb/wiki
- **OpenStack Glance**: https://docs.openstack.org/glance/latest/
- **Cloud-init**: https://cloudinit.readthedocs.io/
- **QEMU/KVM**: https://www.qemu.org/documentation/

---

**For support with custom image requirements or distribution issues, please contact the LoxiLB team through GitHub issues.**
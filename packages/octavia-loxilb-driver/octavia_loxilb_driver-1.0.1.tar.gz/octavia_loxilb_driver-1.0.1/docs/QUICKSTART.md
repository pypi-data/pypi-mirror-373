# LoxiLB Octavia Driver - Quick Start Guide

Get the LoxiLB Octavia Driver running in under 10 minutes!

## 🚀 One-Command Setup

```bash
# Install and setup everything automatically
pip install octavia-loxilb-driver && octavia-loxilb-setup
```

That's it! The automated setup will:
- ✅ Create required OpenStack resources (networks, flavors, security groups)
- ✅ Download and register LoxiLB VM image
- ✅ Generate Octavia configuration
- ✅ Provide next steps for service restart

## 📋 Prerequisites Check

Before starting, ensure you have:

```bash
# OpenStack credentials configured
openstack token issue

# Admin privileges
openstack project list --my-projects

# Python 3.8+ with pip
python3 --version && pip --version
```

## 🔧 Step-by-Step (5 minutes)

### Step 1: Install the Driver (30 seconds)

```bash
pip install octavia-loxilb-driver
```

### Step 2: Choose Your Environment (30 seconds)

**For Development/Testing:**
```bash
octavia-loxilb-setup --deployment-type devstack
```

**For Production:**
```bash
octavia-loxilb-setup --deployment-type production
```

**For Standard Kolla Deployment (Default):**
```bash
octavia-loxilb-setup
```

### Step 3: Apply Configuration (2 minutes)

The setup script will output something like:

```bash
✅ Setup completed successfully!

📝 Configuration generated at: /tmp/octavia-loxilb.conf

🔧 Next steps:
1. Add the following to /etc/octavia/octavia.conf:

[api_settings]
enabled_provider_drivers = amphora:amphora,loxilb:loxilb

[loxilb]
# LoxiLB API Configuration
api_timeout = 30
api_retries = 3
debug_api_calls = true

# OpenStack Authentication (for VM provisioning)
auth_url = YOUR_KEYSTONE_AUTH_URL
auth_type = password
username = octavia
password = YOUR_OCTAVIA_PASSWORD

# OpenStack resource IDs (populated by setup script)
image_id = abc123-def456-789
flavor_id = def456-ghi789-012
mgmt_network_id = ghi789-012345-678
security_group_ids = 012345-678901-234

2. Restart Octavia services:
   sudo systemctl restart octavia-api octavia-worker
```

Copy the generated configuration to your Octavia config file.

### Step 4: Restart Services (1 minute)

**For systemd:**
```bash
sudo systemctl restart octavia-api octavia-worker
```

**For Kolla-Ansible:**
```bash
docker restart octavia_api octavia_worker
```

### Step 5: Verify Installation (1 minute)

```bash
# Check provider is available
openstack loadbalancer provider list

# Should show:
# +--------+---------+
# | name   | default |
# +--------+---------+
# | amphora| True    |
# | loxilb | False   |
# +--------+---------+

# Run health check
octavia-loxilb-health-check
```

## 🎯 Create Your First LoxiLB Load Balancer

```bash
# Create a load balancer using LoxiLB provider
openstack loadbalancer create \
  --provider loxilb \
  --subnet-id <YOUR_SUBNET_ID> \
  my-first-loxilb-lb

# Check status
openstack loadbalancer show my-first-loxilb-lb
```

## ⚡ Deployment Profiles

### DevStack (Minimal Resources)
```bash
octavia-loxilb-setup --deployment-type devstack
```
- 1 vCPU, 4GB RAM, 20GB disk
- Perfect for development and testing

### Standard (Standard Production)
```bash
octavia-loxilb-setup --deployment-type standard
```
- 2 vCPUs, 8GB RAM, 40GB disk  
- Recommended for most production deployments

### Production (High Performance)
```bash
octavia-loxilb-setup --deployment-type production
```
- 4 vCPUs, 16GB RAM, 80GB disk
- For high-throughput environments

## 🛠️ Custom Configuration (Advanced)

Create a custom config file:

```json
{
  "flavor": {
    "name": "my-loxilb-flavor",
    "vcpus": 3,
    "ram": 6144,
    "disk": 50
  },
  "network": {
    "name": "my-octavia-network",
    "cidr": "10.0.100.0/24"
  }
}
```

Use it:
```bash
octavia-loxilb-setup --custom-config /path/to/config.json
```

## 🩺 Troubleshooting Quick Fixes

### Provider Not Showing Up
```bash
# Check configuration
sudo grep -A 5 "enabled_provider_drivers" /etc/octavia/octavia.conf

# Verify driver installation
pip show octavia-loxilb-driver
```

### LoxiLB VM Issues
```bash
# Check LoxiLB VM status
openstack server list --name loxilb-vm

# Check VM console logs
openstack console log show <LOXILB_VM_ID>

# Check security group
openstack security group rule list loxilb-mgmt-sec-grp
```

### Resource Creation Fails
```bash
# Check quotas
openstack quota show

# Verify credentials
openstack token issue
```

## 🔍 What's Created For You

The automated setup creates:

**OpenStack Resources:**
- 🌐 **Management Network**: `octavia-mgmt-net` (192.168.1.0/24)
- 🖥️ **Flavor**: `loxilb-flavor` (specs based on deployment type)
- 🔒 **Security Group**: `loxilb-mgmt-sec-grp` (ports 22, 8091, 9443, 11111, 22222)
- 💾 **VM Image**: `loxilb-vm-image` (downloaded from GitHub releases)
- 🔑 **SSH Keypair**: `loxilb-key` (for debugging access)

**Configuration Files:**
- 📄 **Octavia Config**: Ready-to-use configuration sections
- 🔧 **Resource IDs**: All actual OpenStack resource IDs populated

## 📚 What's Next?

After your quick start:

1. **Read the [Full Installation Guide](INSTALLATION.md)** for advanced options
2. **Check [Architecture Documentation](architecture/)** to understand the integration
3. **Review [Troubleshooting Guide](TROUBLESHOOTING.md)** for common issues
4. **Join the Community** - GitHub Issues for support

## 💡 Pro Tips

**Speed Up Setup:**
```bash
# Skip interactive prompts with environment variables
export OS_LOXILB_MGMT_NETWORK_CIDR="10.0.200.0/24"
octavia-loxilb-setup --deployment-type production
```

**Validate Before Production:**
```bash
# Run comprehensive health check
octavia-loxilb-health-check --detailed

# Test load balancer creation
octavia-loxilb-setup --test-deployment
```

**Multiple Environments:**
```bash
# Development environment
octavia-loxilb-setup --deployment-type devstack --custom-config dev-config.json

# Production environment  
octavia-loxilb-setup --deployment-type production --custom-config prod-config.json
```

---

🎉 **Congratulations!** You now have LoxiLB integrated with OpenStack Octavia. 

Your load balancers can now leverage eBPF/XDP-based high-performance load balancing!

---

**Need Help?** 
- 📖 [Full Documentation](INSTALLATION.md)
- 🐛 [Report Issues](https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/issues)
- 💬 [Community Support](https://github.com/loxilb-io/loxilb)
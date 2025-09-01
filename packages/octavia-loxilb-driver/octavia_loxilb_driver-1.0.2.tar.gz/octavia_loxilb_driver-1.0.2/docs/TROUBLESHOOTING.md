# LoxiLB Octavia Driver - Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the LoxiLB Octavia Driver.

## 🩺 Health Check First

Always start with the built-in health check:

```bash
# Basic health check
octavia-loxilb-health-check

# Detailed health check with verbose output
octavia-loxilb-health-check --detailed --verbose
```

## 📊 Common Issues & Solutions

### 1. Provider Not Available

**Symptom:**
```bash
$ openstack loadbalancer provider list
# LoxiLB provider is missing
```

**Diagnosis:**
```bash
# Check Octavia configuration
sudo grep -A 10 "enabled_provider_drivers" /etc/octavia/octavia.conf

# Verify driver installation
pip show octavia-loxilb-driver

# Check Python path
python -c "import octavia_loxilb_driver; print(octavia_loxilb_driver.__file__)"
```

**Solutions:**

**A. Driver Not Installed:**
```bash
pip install octavia-loxilb-driver
```

**B. Configuration Missing:**
Add to `/etc/octavia/octavia.conf`:
```ini
[api_settings]
enabled_provider_drivers = amphora:amphora,loxilb:loxilb
```

**C. Service Not Restarted:**
```bash
# Systemd
sudo systemctl restart octavia-api octavia-worker octavia-controller

# Kolla
docker restart octavia_api octavia_worker octavia_controller_worker
```

### 2. LoxiLB Connection Issues

**Symptoms:**
- Load balancer creation fails
- "Connection refused" errors in logs
- LoxiLB API timeouts

**Diagnosis:**
```bash
# Test LoxiLB API connectivity
curl -k https://<LOXILB_IP>:8091/netlox/v1/config/status

# Check network connectivity
ping <LOXILB_IP>

# Verify security group rules
openstack security group rule list loxilb-mgmt-sec-grp

# Check if LoxiLB service is running
ssh -i loxilb-key.pem ubuntu@<LOXILB_IP> "sudo systemctl status loxilb"
```

**Solutions:**

**A. Security Group Issues:**
```bash
# Add missing rules to security group
openstack security group rule create loxilb-mgmt-sec-grp \
  --protocol tcp --dst-port 8091 --remote-ip 0.0.0.0/0

openstack security group rule create loxilb-mgmt-sec-grp \
  --protocol tcp --dst-port 9443 --remote-ip 0.0.0.0/0
```

**B. LoxiLB Service Not Running:**
```bash
# SSH to LoxiLB VM and restart service
ssh -i loxilb-key.pem ubuntu@<LOXILB_IP>
sudo systemctl restart loxilb
sudo systemctl status loxilb
```

**C. Network Configuration:**
```bash
# Verify management network routing
openstack subnet show <MGMT_SUBNET_ID>

# Check if Octavia controller can reach management network
traceroute <LOXILB_IP>
```

### 3. Resource Creation Failures

**Symptoms:**
- `octavia-loxilb-setup` fails partway through
- "Quota exceeded" errors
- "Insufficient resources" messages

**Diagnosis:**
```bash
# Check quotas
openstack quota show

# Check available resources
openstack hypervisor list
openstack network agent list

# Verify credentials
openstack token issue
openstack project list --my-projects
```

**Solutions:**

**A. Quota Issues:**
```bash
# Increase quotas (as admin)
openstack quota set --instances 20 --cores 40 --ram 81920 <PROJECT_ID>

# Or use smaller deployment profile
octavia-loxilb-setup --deployment-type devstack
```

**B. Resource Already Exists:**
```bash
# Setup handles existing resources, but check for conflicts
openstack network show octavia-mgmt-net
openstack flavor show loxilb-flavor
openstack security group show loxilb-mgmt-sec-grp

# Clean up if needed
openstack network delete octavia-mgmt-net
octavia-loxilb-setup  # Re-run setup
```

### 4. Load Balancer Creation Fails

**Symptoms:**
- Load balancer stuck in "PENDING_CREATE"
- Creation fails with error status
- No LoxiLB VM is created

**Diagnosis:**
```bash
# Check load balancer status and details
openstack loadbalancer show <LB_ID>
openstack loadbalancer show <LB_ID> -f yaml

# Check Octavia logs
sudo tail -f /var/log/octavia/octavia-worker.log
sudo tail -f /var/log/octavia/octavia-controller.log

# Verify LoxiLB VM creation
openstack server list --name loxilb
```

**Solutions:**

**A. Image Issues:**
```bash
# Verify LoxiLB image exists and is active
openstack image list | grep loxilb

# Re-download if needed
wget https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/releases/download/vm-v1.0.0/loxilb-vm-standard-v1.0.0.qcow2.gz
openstack image create --disk-format qcow2 --container-format bare \
  --public --file loxilb-vm.qcow2 loxilb-vm-image
```

**B. Flavor Issues:**
```bash
# Check if flavor exists and has sufficient resources
openstack flavor show loxilb-flavor
openstack hypervisor stats show
```

**C. Network Issues:**
```bash
# Verify networks and subnets
openstack network show octavia-mgmt-net
openstack subnet list --network octavia-mgmt-net

# Check if ports can be created
openstack port create --network octavia-mgmt-net test-port
openstack port delete test-port
```

### 5. Authentication & Authorization Issues

**Symptoms:**
- "Unauthorized" errors
- "Forbidden" responses
- Setup script fails on resource creation

**Diagnosis:**
```bash
# Check current authentication
openstack token issue

# Verify role assignments
openstack role assignment list --user <USER_ID> --project <PROJECT_ID>

# Test basic operations
openstack network list
openstack flavor list
```

**Solutions:**

**A. Re-authenticate:**
```bash
# Source OpenStack credentials
source openrc.sh  # or your credentials file

# Or set environment variables
export OS_AUTH_URL=https://keystone.example.com:5000/v3
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=password
# ... additional variables
```

**B. Insufficient Privileges:**
```bash
# Ensure user has admin role (needed for Octavia)
openstack role add --user <USER> --project <PROJECT> admin

# Or create service user
openstack user create --project service --password <PASS> octavia-loxilb
openstack role add --user octavia-loxilb --project service admin
```

### 6. Configuration Issues

**Symptoms:**
- Driver loads but doesn't work correctly
- Incorrect resource IDs in configuration
- Services fail to start after configuration changes

**Diagnosis:**
```bash
# Validate configuration syntax
sudo octavia-api --config-file /etc/octavia/octavia.conf --help > /dev/null

# Check driver-specific configuration
sudo grep -A 20 "\[driver_loxilb\]" /etc/octavia/octavia.conf

# Verify resource IDs exist
openstack network show <NETWORK_ID>
openstack flavor show <FLAVOR_ID>
```

**Solutions:**

**A. Regenerate Configuration:**
```bash
# Generate fresh configuration with current resource IDs
octavia-loxilb-setup --output-config /tmp/fresh-config.conf

# Compare with current configuration
diff /etc/octavia/octavia.conf /tmp/fresh-config.conf
```

**B. Fix Resource IDs:**
```bash
# Get current resource IDs
MGMT_NET_ID=$(openstack network show octavia-mgmt-net -f value -c id)
FLAVOR_ID=$(openstack flavor show loxilb-flavor -f value -c id)
IMAGE_ID=$(openstack image show loxilb-vm-image -f value -c id)

# Update configuration with correct IDs
sudo sed -i "s/lb_mgmt_net_id = .*/lb_mgmt_net_id = $MGMT_NET_ID/" /etc/octavia/octavia.conf
```

## 🔍 Log Analysis

### Key Log Locations

**Systemd Deployments:**
- `/var/log/octavia/octavia-api.log`
- `/var/log/octavia/octavia-worker.log`
- `/var/log/octavia/octavia-controller.log`

**Kolla Deployments:**
```bash
# View container logs
docker logs octavia_api
docker logs octavia_worker  
docker logs octavia_controller_worker

# Follow logs in real-time
docker logs -f octavia_worker
```

### Common Log Patterns

**Connection Issues:**
```
ERROR octavia.api.drivers.loxilb_driver: Failed to connect to LoxiLB server
ConnectionError: HTTPSConnectionPool(host='192.168.1.10', port=8091)
```

**Authentication Issues:**
```
ERROR octavia.api.drivers.loxilb_driver: LoxiLB authentication failed
HTTP 401: Unauthorized
```

**Resource Issues:**
```
ERROR nova.compute: Insufficient resources for instance creation
NoValidHost: No valid host was found
```

## 🚨 Emergency Recovery

### Reset All Resources

If you need to completely reset the LoxiLB setup:

```bash
# Remove all LoxiLB resources
openstack loadbalancer list --provider loxilb  # Note IDs to delete
openstack server list --name loxilb  # Note LoxiLB VMs to delete

# Clean up resources
openstack security group delete loxilb-mgmt-sec-grp
openstack network delete octavia-mgmt-net
openstack flavor delete loxilb-flavor
openstack image delete loxilb-vm-image
openstack keypair delete loxilb-key

# Re-run setup
octavia-loxilb-setup
```

### Restore Configuration

```bash
# Backup current configuration
sudo cp /etc/octavia/octavia.conf /etc/octavia/octavia.conf.backup

# Remove LoxiLB configuration sections
sudo sed -i '/\[driver_loxilb\]/,/^\[/d' /etc/octavia/octavia.conf
sudo sed -i 's/,loxilb:loxilb//g' /etc/octavia/octavia.conf

# Regenerate clean configuration
octavia-loxilb-setup --output-config /tmp/clean-config.conf
```

## 🔧 Advanced Debugging

### Enable Debug Logging

Add to `/etc/octavia/octavia.conf`:

```ini
[DEFAULT]
debug = True
verbose = True

# LoxiLB-specific debug logging
[driver_loxilb]
debug = True
```

Restart services and check logs for detailed debug information.

### API Testing

Test LoxiLB API directly:

```bash
# Test authentication
curl -k -X POST https://<LOXILB_IP>:8091/netlox/v1/config/auth \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# Test status endpoint
curl -k https://<LOXILB_IP>:8091/netlox/v1/config/status

# Test load balancer operations
curl -k -X GET https://<LOXILB_IP>:8091/netlox/v1/config/loadbalancer
```

### Network Troubleshooting

```bash
# Test connectivity from Octavia controller
telnet <LOXILB_IP> 8091

# Check routing
traceroute <LOXILB_IP>

# Verify DNS resolution
nslookup <LOXILB_HOSTNAME>

# Test from LoxiLB VM
ssh -i loxilb-key.pem ubuntu@<LOXILB_IP>
curl -k https://localhost:8091/netlox/v1/config/status
```

## 📞 Getting Help

### Information to Collect

When reporting issues, include:

1. **Environment Information:**
   ```bash
   openstack --version
   pip show octavia-loxilb-driver
   python --version
   uname -a
   ```

2. **Configuration:**
   ```bash
   sudo grep -A 20 "\[driver_loxilb\]" /etc/octavia/octavia.conf
   ```

3. **Logs:**
   ```bash
   sudo tail -100 /var/log/octavia/octavia-worker.log
   ```

4. **Resource Status:**
   ```bash
   openstack loadbalancer provider list
   openstack network show octavia-mgmt-net
   octavia-loxilb-health-check --detailed
   ```

### Community Support

- **GitHub Issues**: https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/issues
- **LoxiLB Community**: https://github.com/loxilb-io/loxilb
- **OpenStack Octavia**: https://docs.openstack.org/octavia/latest/

### Professional Support

For production deployments requiring guaranteed response times, consider:

- Commercial OpenStack distributions with Octavia support
- Professional services from LoxiLB team
- Custom integration consulting

---

## 💡 Prevention Tips

1. **Regular Health Checks**: Set up monitoring with `octavia-loxilb-health-check`
2. **Configuration Backups**: Backup `/etc/octavia/octavia.conf` before changes
3. **Resource Monitoring**: Monitor quota usage and resource availability
4. **Update Strategy**: Test updates in development environment first
5. **Documentation**: Document any custom configurations or modifications

---

**Still having issues?** Create a GitHub issue with the information collected above, and the community will help you resolve it!
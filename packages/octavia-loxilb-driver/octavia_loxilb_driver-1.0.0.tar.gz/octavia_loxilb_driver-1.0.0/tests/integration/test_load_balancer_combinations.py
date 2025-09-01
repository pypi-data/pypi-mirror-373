#!/usr/bin/env python3
"""
Integration tests for LoxiLB Octavia Driver - Load Balancer Combinations

This test suite validates different protocol and algorithm combinations
for load balancers using the LoxiLB provider.
"""

import subprocess
import sys
import time
from typing import List, Dict, Any


class LoadBalancerIntegrationTest:
    """Integration test class for load balancer combinations."""
    
    def __init__(self):
        self.protocols = ["HTTP", "TCP", "UDP", "SCTP"]
        self.algorithms = ["ROUND_ROBIN", "LEAST_CONNECTIONS", "SOURCE_IP", "SOURCE_IP_PORT"]
        self.vip_subnet = "loxilb-test-subnet"
        self.subnet_id = "b6c30a42-ee19-4296-a7f5-3b86ef3bcec8"
        self.provider = "loxilb"
        self.member_ips = ["192.168.100.184"]
        self.member_port = 80
        self.created_resources = []

    def run_openstack_command(self, command: List[str]) -> Dict[str, Any]:
        """Execute OpenStack CLI command and return result."""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=True
            )
            return {"success": True, "output": result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr.strip()}

    def create_load_balancer(self, name: str) -> str:
        """Create a load balancer and return its ID."""
        cmd = [
            "openstack", "loadbalancer", "create",
            "--name", name,
            "--vip-subnet-id", self.vip_subnet,
            "--provider", self.provider,
            "--wait"
        ]
        
        result = self.run_openstack_command(cmd)
        if not result["success"]:
            raise Exception(f"Failed to create load balancer {name}: {result['error']}")
        
        # Get LB ID
        cmd = ["openstack", "loadbalancer", "show", name, "-f", "value", "-c", "id"]
        result = self.run_openstack_command(cmd)
        if not result["success"]:
            raise Exception(f"Failed to get load balancer ID: {result['error']}")
        
        lb_id = result["output"]
        self.created_resources.append(("loadbalancer", name, lb_id))
        return lb_id

    def create_listener(self, name: str, protocol: str, lb_id: str) -> str:
        """Create a listener and return its ID."""
        cmd = [
            "openstack", "loadbalancer", "listener", "create",
            "--name", name,
            "--protocol", protocol,
            "--protocol-port", str(self.member_port),
            "--wait", lb_id
        ]
        
        result = self.run_openstack_command(cmd)
        if not result["success"]:
            raise Exception(f"Failed to create listener {name}: {result['error']}")
        
        # Get listener ID
        cmd = ["openstack", "loadbalancer", "listener", "show", name, "-f", "value", "-c", "id"]
        result = self.run_openstack_command(cmd)
        if not result["success"]:
            raise Exception(f"Failed to get listener ID: {result['error']}")
        
        listener_id = result["output"]
        self.created_resources.append(("listener", name, listener_id))
        return listener_id

    def create_pool(self, name: str, protocol: str, algorithm: str, listener_id: str) -> str:
        """Create a pool and return its ID."""
        cmd = [
            "openstack", "loadbalancer", "pool", "create",
            "--name", name,
            "--protocol", protocol,
            "--lb-algorithm", algorithm,
            "--listener", listener_id,
            "--wait"
        ]
        
        result = self.run_openstack_command(cmd)
        if not result["success"]:
            raise Exception(f"Failed to create pool {name}: {result['error']}")
        
        # Get pool ID
        cmd = ["openstack", "loadbalancer", "pool", "show", name, "-f", "value", "-c", "id"]
        result = self.run_openstack_command(cmd)
        if not result["success"]:
            raise Exception(f"Failed to get pool ID: {result['error']}")
        
        pool_id = result["output"]
        self.created_resources.append(("pool", name, pool_id))
        return pool_id

    def add_member(self, pool_id: str, member_name: str, member_ip: str) -> str:
        """Add a member to the pool."""
        cmd = [
            "openstack", "loadbalancer", "member", "create",
            "--name", member_name,
            "--address", member_ip,
            "--protocol-port", str(self.member_port),
            "--subnet-id", self.subnet_id,
            pool_id,
            "--wait"
        ]
        
        result = self.run_openstack_command(cmd)
        if not result["success"]:
            raise Exception(f"Failed to add member {member_name}: {result['error']}")
        
        self.created_resources.append(("member", member_name, f"{pool_id}:{member_ip}"))
        return member_ip

    def test_protocol_algorithm_combination(self, protocol: str, algorithm: str) -> bool:
        """Test a specific protocol and algorithm combination."""
        lb_name = f"test-{protocol.lower()}-{algorithm.lower()}"
        listener_name = f"{protocol.lower()}-{algorithm.lower()}-listener"
        pool_name = f"{protocol.lower()}-{algorithm.lower()}-pool"
        
        try:
            print(f"Testing {protocol} with {algorithm}...")
            
            # Create load balancer
            lb_id = self.create_load_balancer(lb_name)
            print(f"  ✓ Created load balancer: {lb_name} ({lb_id})")
            
            # Create listener
            listener_id = self.create_listener(listener_name, protocol, lb_id)
            print(f"  ✓ Created listener: {listener_name} ({listener_id})")
            
            # Create pool
            pool_id = self.create_pool(pool_name, protocol, algorithm, listener_id)
            print(f"  ✓ Created pool: {pool_name} ({pool_id})")
            
            # Add members
            for i, member_ip in enumerate(self.member_ips):
                member_name = f"web-server-{i+1}"
                self.add_member(pool_id, member_name, member_ip)
                print(f"  ✓ Added member: {member_name} ({member_ip})")
            
            print(f"  ✅ Successfully tested {protocol} with {algorithm}")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to test {protocol} with {algorithm}: {str(e)}")
            return False

    def cleanup_resources(self):
        """Clean up all created resources."""
        print("\nCleaning up resources...")
        
        # Reverse order for proper cleanup
        for resource_type, name, resource_id in reversed(self.created_resources):
            try:
                if resource_type == "member":
                    pool_id, member_ip = resource_id.split(":")
                    cmd = ["openstack", "loadbalancer", "member", "delete", pool_id, member_ip]
                else:
                    cmd = ["openstack", "loadbalancer", resource_type, "delete", name]
                
                result = self.run_openstack_command(cmd)
                if result["success"]:
                    print(f"  ✓ Deleted {resource_type}: {name}")
                else:
                    print(f"  ⚠️  Failed to delete {resource_type} {name}: {result['error']}")
                    
            except Exception as e:
                print(f"  ⚠️  Error deleting {resource_type} {name}: {str(e)}")

    def run_all_tests(self):
        """Run all protocol and algorithm combination tests."""
        print("🧪 Starting LoxiLB Load Balancer Integration Tests")
        print("=" * 60)
        
        total_tests = len(self.protocols) * len(self.algorithms)
        passed_tests = 0
        failed_tests = 0
        
        try:
            for protocol in self.protocols:
                for algorithm in self.algorithms:
                    if self.test_protocol_algorithm_combination(protocol, algorithm):
                        passed_tests += 1
                    else:
                        failed_tests += 1
                    print("-" * 60)
                    
        finally:
            # Always cleanup
            self.cleanup_resources()
        
        print(f"\n📊 Test Results:")
        print(f"  Total tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        return failed_tests == 0


def main():
    """Main test execution function."""
    test_runner = LoadBalancerIntegrationTest()
    
    try:
        success = test_runner.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        test_runner.cleanup_resources()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        test_runner.cleanup_resources()
        sys.exit(1)


if __name__ == "__main__":
    main()

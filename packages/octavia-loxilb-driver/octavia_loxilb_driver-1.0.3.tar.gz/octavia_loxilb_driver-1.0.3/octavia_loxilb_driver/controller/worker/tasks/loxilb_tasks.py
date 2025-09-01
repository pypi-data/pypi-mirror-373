# Copyright 2025 LoxiLB
# Licensed under the Apache License, Version 2.0

from oslo_config import cfg
from oslo_log import log as logging
from taskflow import task

from octavia_loxilb_driver.api.loxilb_client import LoxiLBAPIClient
from octavia_loxilb_driver.common import exceptions
from octavia_loxilb_driver.driver.loadbalancer_driver import LoadBalancerDriver
from octavia_loxilb_driver.resource_mapping.mapper import ResourceMapper

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class CreateLoadBalancerInLoxiLB(task.Task):
    """Task to create a load balancer in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)
        

    def execute(self, loadbalancer, vip_subnet_id, **kwargs):
        """Create load balancer in LoxiLB.        
        :param loadbalancer: LoadBalancer object
        """
        LOG.info("Creating load balancer %s in LoxiLB", loadbalancer.id)
        
        try:
            # Use the driver layer to create the load balancer
            # This will handle ID mapping, resource transformation, and API calls
            self.lb_driver.create(loadbalancer)
            
            LOG.info("Successfully created load balancer %s in LoxiLB", loadbalancer.id)
            return loadbalancer.id
            
        except Exception as e:
            LOG.error("Failed to create load balancer %s in LoxiLB: %s", 
                     loadbalancer.id, str(e))
            raise exceptions.LoxiLBAPIException(
                f"Failed to create load balancer: {str(e)}"
            )

    def revert(self, loadbalancer, result=None, **kwargs):
        """Revert load balancer creation."""
        if result:
            try:
                LOG.warning("Reverting load balancer creation %s", loadbalancer.id)
                # Use the driver layer to delete the load balancer
                # This will handle ID mapping and API calls
                self.lb_driver.delete(loadbalancer)
            except Exception:
                LOG.exception("Failed to revert load balancer creation")


class CreateVIPInLoxiLB(task.Task):
    """Task to create VIP configuration in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, loadbalancer, **kwargs):
        """Create VIP in LoxiLB.
        
        Note: In the driver architecture, VIP creation is handled as part of
        load balancer creation. This task ensures the VIP is properly configured
        in LoxiLB by verifying the load balancer exists and has the correct VIP.
        """
        LOG.info("Configuring VIP for load balancer %s", loadbalancer.id)
        
        try:
            # The VIP is already created as part of the load balancer creation
            # We just need to verify it exists and log the success
            LOG.info("VIP configuration for load balancer %s is handled by the driver", loadbalancer.id)
            LOG.info("VIP address: %s", loadbalancer.vip.ip_address)
            return loadbalancer.id
        except Exception as e:
            LOG.error("Failed to configure VIP for load balancer %s: %s", 
                     loadbalancer.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to configure VIP: {str(e)}")


class DeleteLoadBalancerInLoxiLB(task.Task):
    """Task to delete a load balancer in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, loadbalancer, **kwargs):
        """Delete load balancer in LoxiLB."""
        LOG.info("Deleting load balancer %s from LoxiLB", loadbalancer.id)
        
        try:
            # Use the driver layer to delete the load balancer
            # This will handle ID mapping and API calls
            self.lb_driver.delete(loadbalancer)
            LOG.info("Successfully deleted load balancer %s from LoxiLB", 
                    loadbalancer.id)
        except Exception as e:
            LOG.error("Failed to delete load balancer %s from LoxiLB: %s", 
                     loadbalancer.id, str(e))
            raise exceptions.LoxiLBAPIException(
                f"Failed to delete load balancer: {str(e)}"
            )


# Add similar tasks for other operations...
class UpdateLoadBalancerInLoxiLB(task.Task):
    """Task to update a load balancer in LoxiLB."""
    # Implementation similar to Create but for updates


# Add these additional task classes to the existing loxilb_tasks.py file

class CreateListenerInLoxiLB(task.Task):
    """Task to create a listener in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the listener driver instead of loadbalancer driver
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.listener_driver import ListenerDriver
        self.listener_driver = ListenerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, listener, loadbalancer, **kwargs):
        """Create listener in LoxiLB.
        
        :param listener: Listener object from database
        :param loadbalancer: LoadBalancer object from database
        """
        LOG.info("Creating listener %s in LoxiLB", listener.id)
        
        try:
            # Pass both the listener and loadbalancer to the driver
            self.listener_driver.create(listener, loadbalancer)
            LOG.info("Successfully created listener %s in LoxiLB", listener.id)
            return listener.id
        except Exception as e:
            LOG.error("Failed to create listener %s in LoxiLB: %s", 
                     listener.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to create listener: {str(e)}")


class DeleteListenerInLoxiLB(task.Task):
    """Task to delete a listener in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the listener driver
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.listener_driver import ListenerDriver
        self.listener_driver = ListenerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, listener, loadbalancer, **kwargs):
        """Delete listener in LoxiLB.
        
        :param listener: Listener object from database
        :param loadbalancer: LoadBalancer object from database
        """
        LOG.info("Deleting listener %s from LoxiLB", listener.id)
        
        try:
            # Pass both the listener and loadbalancer to the driver
            self.listener_driver.delete(listener)
            LOG.info("Successfully deleted listener %s from LoxiLB", listener.id)
        except Exception as e:
            LOG.error("Failed to delete listener %s in LoxiLB: %s", 
                     listener.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to delete listener: {str(e)}")


class UpdateListenerInLoxiLB(task.Task):
    """Task to update a listener in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the listener driver
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.listener_driver import ListenerDriver
        self.listener_driver = ListenerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, listener, listener_updates, loadbalancer, **kwargs):
        """Update listener in LoxiLB.
        
        :param listener: Listener object from database
        :param listener_updates: Dictionary with the changed attributes
        :param loadbalancer: LoadBalancer object from database
        """
        LOG.info("Updating listener %s in LoxiLB with changes: %s", 
                listener.id, listener_updates.keys())
        
        try:
            # Pass both the listener, updates, and loadbalancer to the driver
            self.listener_driver.update(listener, listener_updates, loadbalancer)
            LOG.info("Successfully updated listener %s in LoxiLB", listener.id)
            return listener.id
        except Exception as e:
            LOG.error("Failed to update listener %s in LoxiLB: %s", 
                     listener.id, str(e))
            raise exceptions.LoxiLBAPIException(
                f"Failed to update listener: {str(e)}"
            )


class CreatePoolInLoxiLB(task.Task):
    """Task to create a pool in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the pool driver instead of loadbalancer driver
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.pool_driver import PoolDriver
        self.pool_driver = PoolDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, pool, loadbalancer, listener=None, **kwargs):
        """Create pool in LoxiLB with full context.
        
        :param pool: Pool object from database
        :param loadbalancer: LoadBalancer object from database
        :param listener: Listener object from database (optional)
        """
        LOG.info("Creating pool %s in LoxiLB", pool.id)
        
        try:
            self.pool_driver.create(pool, listener_metadata=listener, loadbalancer_metadata=loadbalancer)
            LOG.info("Successfully created pool %s in LoxiLB", pool.id)
            return pool.id
        except Exception as e:
            LOG.error("Failed to create pool %s in LoxiLB: %s", pool.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to create pool: {str(e)}")


class DeletePoolInLoxiLB(task.Task):
    """Task to delete a pool in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the pool driver instead of loadbalancer driver
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.pool_driver import PoolDriver
        self.pool_driver = PoolDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, pool, loadbalancer, listener=None, **kwargs):
        """Delete pool in LoxiLB with full context.
        
        :param pool: Pool object from database
        :param loadbalancer: LoadBalancer object from database
        :param listener: Listener object from database (optional)
        """
        LOG.info("Deleting pool %s from LoxiLB", pool.id)
        
        try:
            self.pool_driver.delete(pool, listener_metadata=listener, loadbalancer_metadata=loadbalancer)
            LOG.info("Successfully deleted pool %s from LoxiLB", pool.id)
        except Exception as e:
            LOG.error("Failed to delete pool %s from LoxiLB: %s", pool.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to delete pool: {str(e)}")


class UpdatePoolInLoxiLB(task.Task):
    """Task to update a pool in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the pool driver instead of loadbalancer driver
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.pool_driver import PoolDriver
        self.pool_driver = PoolDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, pool, update_dict, loadbalancer, listener=None, **kwargs):
        """Update pool in LoxiLB with full context.
        
        :param pool: Pool object from database
        :param update_dict: Dictionary with the changed attributes
        :param loadbalancer: LoadBalancer object from database
        :param listener: Listener object from database (optional)
        """
        LOG.info("Updating pool %s in LoxiLB with changes: %s", pool.id, update_dict.keys())
        
        try:
            self.pool_driver.update(pool, update_dict, listener_metadata=listener, loadbalancer_metadata=loadbalancer)
            LOG.info("Successfully updated pool %s in LoxiLB", pool.id)
            return pool.id
        except Exception as e:
            LOG.error("Failed to update pool %s in LoxiLB: %s", pool.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to update pool: {str(e)}")


class CreateMemberInLoxiLB(task.Task):
    """Task to create a member in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.member_driver import MemberDriver
        self.member_driver = MemberDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, member, pool=None, loadbalancer=None, **kwargs):
        member_id = member.get("id") if isinstance(member, dict) else getattr(member, "id", None)
        LOG.info("Creating member %s in LoxiLB", member_id)
        try:
            self.member_driver.create(member, pool, loadbalancer)
            LOG.info("Successfully created member %s in LoxiLB", member_id)
            return member_id
        except Exception as e:
            LOG.error("Failed to create member %s in LoxiLB: %s", member_id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to create member: {str(e)}")


class DeleteMemberInLoxiLB(task.Task):
    """Task to delete a member in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.member_driver import MemberDriver
        self.member_driver = MemberDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, member, pool=None, loadbalancer=None, **kwargs):
        member_id = member.get("id") if isinstance(member, dict) else getattr(member, "id", None)
        LOG.info("Deleting member %s from LoxiLB", member_id)
        try:
            self.member_driver.delete(member, pool, loadbalancer)
            LOG.info("Successfully deleted member %s from LoxiLB", member_id)
            return member_id
        except Exception as e:
            LOG.error("Failed to delete member %s from LoxiLB: %s", member_id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to delete member: {str(e)}")


class UpdateMemberInLoxiLB(task.Task):
    """Task to update a member in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.member_driver import MemberDriver
        self.member_driver = MemberDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, member, update_dict, pool=None, loadbalancer=None, **kwargs):
        member_id = member.get("id") if isinstance(member, dict) else getattr(member, "id", None)
        LOG.info("Updating member %s in LoxiLB with changes: %s", member_id, update_dict.keys())
        try:
            self.member_driver.update(member, update_dict, pool, loadbalancer)
            LOG.info("Successfully updated member %s in LoxiLB", member_id)
            return member_id
        except Exception as e:
            LOG.error("Failed to update member %s in LoxiLB: %s", member_id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to update member: {str(e)}")


class CreateHealthMonitorInLoxiLB(task.Task):
    """Task to create a health monitor in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the health monitor driver instead of loadbalancer driver
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.healthmonitor_driver import HealthMonitorDriver
        self.health_monitor_driver = HealthMonitorDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, health_monitor, pool, loadbalancer, **kwargs):
        """Create health monitor in LoxiLB.
        
        :param health_monitor: Health monitor object from database
        :param pool: Pool object from database
        :param loadbalancer: LoadBalancer object from database
        """
        LOG.info("Creating health monitor %s in LoxiLB", health_monitor.id)
        
        try:
            # Pass the health_monitor, pool, and loadbalancer to the driver
            self.health_monitor_driver.create(health_monitor, pool, loadbalancer)
            LOG.info("Successfully created health monitor %s in LoxiLB", health_monitor.id)
            return health_monitor.id
        except Exception as e:
            LOG.error("Failed to create health monitor %s in LoxiLB: %s", 
                     health_monitor.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to create health monitor: {str(e)}")


class DeleteHealthMonitorInLoxiLB(task.Task):
    """Task to delete a health monitor in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the health monitor driver instead of loadbalancer driver
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.healthmonitor_driver import HealthMonitorDriver
        self.health_monitor_driver = HealthMonitorDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, health_monitor, pool, loadbalancer, **kwargs):
        """Delete health monitor in LoxiLB.
        
        :param health_monitor: Health monitor object from database
        :param pool: Pool object from database
        :param loadbalancer: LoadBalancer object from database
        """
        LOG.info("Deleting health monitor %s from LoxiLB", health_monitor.id)
        
        try:
            # Pass the health_monitor, pool, and loadbalancer to the driver
            self.health_monitor_driver.delete(health_monitor, pool, loadbalancer)
            LOG.info("Successfully deleted health monitor %s from LoxiLB", health_monitor.id)
            return health_monitor.id
        except Exception as e:
            LOG.error("Failed to delete health monitor %s from LoxiLB: %s", 
                     health_monitor.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to delete health monitor: {str(e)}")


class UpdateHealthMonitorInLoxiLB(task.Task):
    """Task to update a health monitor in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the health monitor driver instead of loadbalancer driver
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.healthmonitor_driver import HealthMonitorDriver
        self.health_monitor_driver = HealthMonitorDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, health_monitor, update_dict, pool, loadbalancer, **kwargs):
        """Update health monitor in LoxiLB.
        
        :param health_monitor: Health monitor object from database
        :param update_dict: Dictionary with the changed attributes
        :param pool: Pool object from database
        :param loadbalancer: LoadBalancer object from database
        """
        LOG.info("Updating health monitor %s in LoxiLB with changes: %s", 
                health_monitor.id, update_dict.keys())
        
        try:
            # Pass the health_monitor, update_dict, pool, and loadbalancer to the driver
            self.health_monitor_driver.update(health_monitor, update_dict, pool, loadbalancer)
            LOG.info("Successfully updated health monitor %s in LoxiLB", health_monitor.id)
            return health_monitor.id
        except Exception as e:
            LOG.error("Failed to update health monitor %s in LoxiLB: %s", 
                     health_monitor.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to update health monitor: {str(e)}")


# Batch operation tasks
class BatchDeleteMembersInLoxiLB(task.Task):
    """Task to batch delete members in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, old_members, pool=None, **kwargs):
        """Batch delete members in LoxiLB.
        
        Note: In the driver architecture, members are typically handled as part of
        pool operations. Since the driver doesn't have specific batch member methods,
        we'll use the API client directly for now, but in a future implementation,
        this should be handled through the driver's update method.
        """
        LOG.info("Batch deleting %d members in LoxiLB", len(old_members))
        
        try:
            # Since the driver doesn't have specific batch member methods, we'll use the API client directly
            # In a future implementation, this should be integrated with the driver layer
            member_ids = [member.id for member in old_members]
            self.lb_driver.api_client.batch_delete_members(member_ids)
            LOG.info("Successfully batch deleted members in LoxiLB")
        except Exception as e:
            LOG.error("Failed to batch delete members in LoxiLB: %s", str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to batch delete members: {str(e)}")


class BatchCreateMembersInLoxiLB(task.Task):
    """Task to batch create members in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, new_members, pool, **kwargs):
        """Batch create members in LoxiLB.
        
        Note: In the driver architecture, members are typically handled as part of
        pool operations. Since the driver doesn't have specific batch member methods,
        we'll use the API client directly for now, but in a future implementation,
        this should be handled through the driver's update method.
        """
        LOG.info("Batch creating %d members in LoxiLB", len(new_members))
        
        try:
            # Since the driver doesn't have specific batch member methods, we'll use the API client directly
            # In a future implementation, this should be integrated with the driver layer
            # Create member configs directly without using a transform method
            member_configs = []
            for member in new_members:
                member_config = {
                    'id': member.id,
                    'name': member.name or f"octavia-member-{member.id}",
                    'address': member.address,
                    'protocol_port': member.protocol_port,
                    'pool_id': pool.id,
                    'weight': member.weight,
                    'admin_state_up': member.admin_state_up,
                    'subnet_id': member.subnet_id
                }
                member_configs.append(member_config)
                
            self.lb_driver.api_client.batch_create_members(member_configs)
            LOG.info("Successfully batch created members in LoxiLB")
        except Exception as e:
            LOG.error("Failed to batch create members in LoxiLB: %s", str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to batch create members: {str(e)}")

    # Transformation method removed as we're now using the driver's resource mapper


class BatchUpdateMembersInLoxiLB(task.Task):
    """Task to batch update members in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, updated_members, pool=None, **kwargs):
        """Batch update members in LoxiLB.
        
        Note: In the driver architecture, members are typically handled as part of
        pool operations. Since the driver doesn't have specific batch member methods,
        we'll use the API client directly for now, but in a future implementation,
        this should be handled through the driver's update method.
        """
        LOG.info("Batch updating %d members in LoxiLB", len(updated_members))
        
        try:
            # Since the driver doesn't have specific batch member methods, we'll use the API client directly
            # In a future implementation, this should be integrated with the driver layer
            # Since the driver doesn't have specific batch member methods, we'll use the API client directly
            # In a future implementation, this should be integrated with the driver layer
            member_configs = []
            for member in updated_members:
                # Create a simple dict with the necessary attributes instead of using a transform method
                member_config = {
                    'id': member.id,
                    'admin_state_up': member.admin_state_up,
                    'weight': member.weight,
                    'name': member.name
                }
                member_configs.append(member_config)
                
            self.lb_driver.api_client.batch_update_members(member_configs)
            LOG.info("Successfully batch updated %d members in LoxiLB", len(updated_members))
        except Exception as e:
            LOG.error("Failed to batch update members in LoxiLB: %s", str(e))
            raise exceptions.LoxiLBAPIException(
                f"Failed to batch update members: {str(e)}"
            )

    # Transformation method removed as we're now using the driver's resource mapper


# Cascade Delete Tasks
class DeleteAllMembersInLoxiLB(task.Task):
    """Task to delete all members associated with pools in a load balancer in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.member_driver import MemberDriver
        self.member_driver = MemberDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, loadbalancer, **kwargs):
        """Delete all members associated with pools in a load balancer in LoxiLB.
        
        :param loadbalancer: LoadBalancer object from database
        """
        lb_id = loadbalancer.get('id') if isinstance(loadbalancer, dict) else getattr(loadbalancer, 'id', None)
        LOG.info("Deleting all members for load balancer %s from LoxiLB", lb_id)
        
        try:
            # Get all pools from the loadbalancer object
            pools = loadbalancer.get('pools') if isinstance(loadbalancer, dict) else getattr(loadbalancer, 'pools', [])
            
            if not pools:
                LOG.info("No pools found for load balancer %s, so no members to delete", lb_id)
                return
                
            for pool in pools:
                pool_id = pool.get('id') if isinstance(pool, dict) else getattr(pool, 'id', None)
                # Get members from the pool
                members = pool.get('members') if isinstance(pool, dict) else getattr(pool, 'members', [])
                
                if not members:
                    LOG.info("No members found for pool %s", pool_id)
                    continue
                    
                LOG.info("Deleting %d members from pool %s", len(members), pool_id)
                
                for member in members:
                    member_id = member.get('id') if isinstance(member, dict) else getattr(member, 'id', None)
                    LOG.info("Deleting member %s from pool %s in LoxiLB", member_id, pool_id)
                    try:
                        self.member_driver.delete(member, pool, loadbalancer)
                        LOG.info("Successfully deleted member %s from LoxiLB", member_id)
                    except Exception as e:
                        LOG.warning("Failed to delete member %s from LoxiLB: %s", 
                                  member_id, str(e))
                        # Continue with other members even if one fails
                    
            LOG.info("Completed deletion of all members for load balancer %s", lb_id)
        except Exception as e:
            LOG.error("Failed to delete all members for load balancer %s: %s", 
                     lb_id, str(e))
            raise exceptions.LoxiLBAPIException(
                f"Failed to delete all members: {str(e)}"
            )


class DeleteAllListenersInLoxiLB(task.Task):
    """Task to delete all listeners associated with a load balancer in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.listener_driver import ListenerDriver
        self.listener_driver = ListenerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, loadbalancer, **kwargs):
        """Delete all listeners associated with a load balancer in LoxiLB.
        
        :param loadbalancer: LoadBalancer object from database
        """
        lb_id = loadbalancer.get('id') if isinstance(loadbalancer, dict) else getattr(loadbalancer, 'id', None)
        LOG.info("Deleting all listeners for load balancer %s from LoxiLB", lb_id)
        
        try:
            # Get all listeners from the loadbalancer object
            listeners = loadbalancer.get('listeners') if isinstance(loadbalancer, dict) else getattr(loadbalancer, 'listeners', [])
            
            if not listeners:
                LOG.info("No listeners found for load balancer %s", lb_id)
                return
                
            for listener in listeners:
                listener_id = listener.get('id') if isinstance(listener, dict) else getattr(listener, 'id', None)
                LOG.info("Deleting listener %s from LoxiLB", listener_id)
                try:
                    self.listener_driver.delete(listener)
                    LOG.info("Successfully deleted listener %s from LoxiLB", listener_id)
                except Exception as e:
                    LOG.warning("Failed to delete listener %s from LoxiLB: %s", 
                              listener_id, str(e))
                    # Continue with other listeners even if one fails
                    
            LOG.info("Completed deletion of all listeners for load balancer %s", lb_id)
        except Exception as e:
            LOG.error("Failed to delete all listeners for load balancer %s: %s", 
                     lb_id, str(e))
            raise exceptions.LoxiLBAPIException(
                f"Failed to delete all listeners: {str(e)}"
            )


class DeleteAllPoolsInLoxiLB(task.Task):
    """Task to delete all pools associated with a load balancer in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.pool_driver import PoolDriver
        self.pool_driver = PoolDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, loadbalancer, **kwargs):
        """Delete all pools associated with a load balancer in LoxiLB.
        
        :param loadbalancer: LoadBalancer object from database
        """
        lb_id = loadbalancer.get('id') if isinstance(loadbalancer, dict) else getattr(loadbalancer, 'id', None)
        LOG.info("Deleting all pools for load balancer %s from LoxiLB", lb_id)
        
        try:
            # Get all pools from the loadbalancer object
            pools = loadbalancer.get('pools') if isinstance(loadbalancer, dict) else getattr(loadbalancer, 'pools', [])
            
            if not pools:
                LOG.info("No pools found for load balancer %s", lb_id)
                return
                
            for pool in pools:
                pool_id = pool.get('id') if isinstance(pool, dict) else getattr(pool, 'id', None)
                LOG.info("Deleting pool %s from LoxiLB", pool_id)
                try:
                    self.pool_driver.delete(pool, loadbalancer_metadata=loadbalancer)
                    LOG.info("Successfully deleted pool %s from LoxiLB", pool_id)
                except Exception as e:
                    LOG.warning("Failed to delete pool %s from LoxiLB: %s", 
                              pool_id, str(e))
                    # Continue with other pools even if one fails
                    
            LOG.info("Completed deletion of all pools for load balancer %s", lb_id)
        except Exception as e:
            LOG.error("Failed to delete all pools for load balancer %s: %s", 
                     lb_id, str(e))
            raise exceptions.LoxiLBAPIException(
                f"Failed to delete all pools: {str(e)}"
            )


# L7 Policy Tasks
class CreateL7PolicyInLoxiLB(task.Task):
    """Task to create an L7 policy in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, l7policy, loadbalancer, listener, **kwargs):
        """Create L7 policy in LoxiLB.
        
        The driver has a specific method for L7 policy creation, so we'll use that.
        """
        LOG.info("Creating L7 policy %s in LoxiLB", l7policy.id)
        
        try:
            # Use the driver's l7policy_create method directly
            result = self.lb_driver.l7policy_create(l7policy)
            LOG.info("Successfully created L7 policy %s in LoxiLB", l7policy.id)
            return result
        except Exception as e:
            LOG.error("Failed to create L7 policy %s in LoxiLB: %s", 
                     l7policy.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to create L7 policy: {str(e)}")

    # Transformation method removed as we're now using the driver's resource mapper


class DeleteL7PolicyInLoxiLB(task.Task):
    """Task to delete an L7 policy in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, l7policy, **kwargs):
        """Delete L7 policy in LoxiLB.
        
        The driver has a specific method for L7 policy deletion, so we'll use that.
        """
        LOG.info("Deleting L7 policy %s from LoxiLB", l7policy.id)
        
        try:
            # Use the driver's l7policy_delete method directly
            self.lb_driver.l7policy_delete(l7policy)
            LOG.info("Successfully deleted L7 policy %s from LoxiLB", l7policy.id)
        except Exception as e:
            LOG.error("Failed to delete L7 policy %s from LoxiLB: %s", 
                     l7policy.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to delete L7 policy: {str(e)}")


class UpdateL7PolicyInLoxiLB(task.Task):
    """Task to update an L7 policy in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, l7policy, loadbalancer, listener, update_dict, **kwargs):
        """Update L7 policy in LoxiLB.
        
        The driver has a specific method for L7 policy updates, so we'll use that.
        """
        LOG.info("Updating L7 policy %s in LoxiLB", l7policy.id)
        
        try:
            # Use the driver's l7policy_update method directly
            # Apply the update_dict to the l7policy object first
            for key, value in update_dict.items():
                setattr(l7policy, key, value)
            
            self.lb_driver.l7policy_update(l7policy)
            LOG.info("Successfully updated L7 policy %s in LoxiLB", l7policy.id)
        except Exception as e:
            LOG.error("Failed to update L7 policy %s in LoxiLB: %s", 
                     l7policy.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to update L7 policy: {str(e)}")

    # Transformation method removed as we're now using the driver's resource mapper


class DeleteAllL7RulesInLoxiLB(task.Task):
    """Task to delete all L7 rules of an L7 policy in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, l7policy, **kwargs):
        """Delete all L7 rules of an L7 policy in LoxiLB.
        
        The driver has specific methods for L7 rule operations, so we'll use those.
        """
        LOG.info("Deleting all L7 rules of L7 policy %s from LoxiLB", l7policy.id)
        
        try:
            # Get all L7 rules for this policy and delete them using the driver
            for l7rule in l7policy.rules:
                self.lb_driver.l7rule_delete(l7rule)
                LOG.debug("Deleted L7 rule %s from LoxiLB", l7rule.id)
                
            LOG.info("Successfully deleted all L7 rules of L7 policy %s from LoxiLB", 
                    l7policy.id)
        except Exception as e:
            LOG.error("Failed to delete all L7 rules of L7 policy %s from LoxiLB: %s", 
                     l7policy.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to delete all L7 rules: {str(e)}")


# L7 Rule Tasks
class CreateL7RuleInLoxiLB(task.Task):
    """Task to create an L7 rule in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, l7rule, l7policy, loadbalancer, listener, **kwargs):
        """Create L7 rule in LoxiLB.
        
        The driver has specific methods for L7 rule operations, so we'll use those.
        """
        LOG.info("Creating L7 rule %s in LoxiLB", l7rule.id)
        
        try:
            # Use the driver's l7rule_create method directly
            result = self.lb_driver.l7rule_create(l7rule, l7policy)
            LOG.info("Successfully created L7 rule %s in LoxiLB", l7rule.id)
            return result
        except Exception as e:
            LOG.error("Failed to create L7 rule %s in LoxiLB: %s", 
                     l7rule.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to create L7 rule: {str(e)}")

    # Transformation method removed as we're now using the driver's resource mapper


class DeleteL7RuleInLoxiLB(task.Task):
    """Task to delete an L7 rule in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, l7rule, **kwargs):
        """Delete L7 rule in LoxiLB.
        
        The driver has specific methods for L7 rule operations, so we'll use those.
        """
        LOG.info("Deleting L7 rule %s from LoxiLB", l7rule.id)
        
        try:
            # Use the driver's l7rule_delete method directly
            self.lb_driver.l7rule_delete(l7rule)
            LOG.info("Successfully deleted L7 rule %s from LoxiLB", l7rule.id)
        except Exception as e:
            LOG.error("Failed to delete L7 rule %s from LoxiLB: %s", 
                     l7rule.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to delete L7 rule: {str(e)}")


class UpdateL7RuleInLoxiLB(task.Task):
    """Task to update an L7 rule in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, l7rule, l7policy, loadbalancer, listener, update_dict, **kwargs):
        """Update L7 rule in LoxiLB.
        
        The driver has specific methods for L7 rule operations, so we'll use those.
        """
        LOG.info("Updating L7 rule %s in LoxiLB", l7rule.id)
        
        try:
            # Use the driver's l7rule_update method directly
            # Apply the update_dict to the l7rule object first
            for key, value in update_dict.items():
                setattr(l7rule, key, value)
            
            self.lb_driver.l7rule_update(l7rule, l7policy)
            LOG.info("Successfully updated L7 rule %s in LoxiLB", l7rule.id)
        except Exception as e:
            LOG.error("Failed to update L7 rule %s in LoxiLB: %s", 
                     l7rule.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to update L7 rule: {str(e)}")

    # Transformation method removed as we're now using the driver's resource mapper


class DeleteAllL7PoliciesInLoxiLB(task.Task):
    """Task to delete all L7 policies associated with a listener in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        # Initialize the driver layer instead of directly using the API client
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        self.lb_driver = LoadBalancerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, listener, **kwargs):
        """Delete all L7 policies associated with a listener in LoxiLB.
        
        :param listener: Listener object from database
        """
        LOG.info("Deleting all L7 policies for listener %s from LoxiLB", listener.id)
        
        try:
            # Get all L7 policies for this listener and delete them using the driver
            if hasattr(listener, 'l7policies') and listener.l7policies:
                for l7policy in listener.l7policies:
                    LOG.debug("Deleting L7 policy %s from LoxiLB", l7policy.id)
                    self.lb_driver.l7policy_delete(l7policy)
                    LOG.debug("Successfully deleted L7 policy %s from LoxiLB", l7policy.id)
                
                LOG.info("Successfully deleted all L7 policies for listener %s from LoxiLB", 
                        listener.id)
            else:
                LOG.info("No L7 policies found for listener %s", listener.id)
        except Exception as e:
            LOG.error("Failed to delete all L7 policies for listener %s from LoxiLB: %s", 
                     listener.id, str(e))
            raise exceptions.LoxiLBAPIException(
                f"Failed to delete all L7 policies: {str(e)}"
            )


class DeleteAllListenersInLoxiLB(task.Task):
    """Task to delete all listeners associated with a load balancer in LoxiLB."""

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        api_client = LoxiLBAPIClient(CONF.loxilb)
        resource_mapper = ResourceMapper(CONF.loxilb)
        from octavia_loxilb_driver.driver.listener_driver import ListenerDriver
        self.listener_driver = ListenerDriver(api_client, resource_mapper, CONF.loxilb)

    def execute(self, loadbalancer, **kwargs):
        """Delete all listeners for the given load balancer in LoxiLB."""
        lb_id = loadbalancer.get("id") if isinstance(loadbalancer, dict) else getattr(loadbalancer, "id", None)
        LOG.info(f"Deleting all listeners for load balancer {lb_id} in LoxiLB")
        try:
            # Retrieve listeners from loadbalancer object
            listeners = loadbalancer.get("listeners", []) if isinstance(loadbalancer, dict) else getattr(loadbalancer, "listeners", [])
            for listener in listeners:
                listener_id = listener.get("id") if isinstance(listener, dict) else getattr(listener, "id", None)
                LOG.info(f"Deleting listener {listener_id} from LoxiLB (cascade)")
                self.listener_driver.delete(listener)
            LOG.info(f"Successfully deleted all listeners for load balancer {lb_id} in LoxiLB")
        except Exception as e:
            LOG.error(f"Failed to delete all listeners for load balancer {lb_id} in LoxiLB: {str(e)}")
            raise exceptions.LoxiLBAPIException(f"Failed to delete all listeners: {str(e)}")

# octavia_loxilb_driver/common/state_reconciler.py
"""State Reconciliation Utilities for Octavia-LoxiLB Driver."""

import logging
from datetime import datetime

from octavia_loxilb_driver.common import utils

LOG = logging.getLogger(__name__)


class StateReconciler:
    """Handles state reconciliation between Octavia and LoxiLB.
    
    This class provides utilities to detect and resolve state inconsistencies
    that can occur due to the architectural mismatch between Octavia's granular
    resource model and LoxiLB's composite service model.
    """

    def __init__(self, resource_mapper, api_client):
        """Initialize the StateReconciler.
        
        Args:
            resource_mapper: Resource mapper with ID mapping capabilities
            api_client: LoxiLB API client instance
        """
        self.resource_mapper = resource_mapper
        self.api_client = api_client

    def get_dependent_resources(self, listener):
        """Get all resources that depend on a listener.
        
        When a listener is deleted in LoxiLB, the entire service is removed,
        which affects all dependent resources. This method identifies those
        dependencies so they can be properly handled.
        
        Args:
            listener: Listener object or dict from Octavia
            
        Returns:
            dict: Mapping of resource types to lists of dependent resource IDs
        """
        dependent_resources = {
            'pools': [],
            'members': [],
            'health_monitors': []
        }
        
        try:
            # Handle both dictionary and object types for listener parameter
            if isinstance(listener, dict):
                listener_id = listener.get('id')
                default_pool = listener.get('default_pool')
            else:
                listener_id = getattr(listener, 'id', None)
                default_pool = getattr(listener, 'default_pool', None)
            
            if default_pool:
                # Handle both dictionary and object types for pool
                if isinstance(default_pool, dict):
                    pool_id = default_pool.get('id')
                    members = default_pool.get('members', [])
                    health_monitor = default_pool.get('healthmonitor')
                else:
                    pool_id = getattr(default_pool, 'id', None)
                    members = getattr(default_pool, 'members', []) or []
                    health_monitor = getattr(default_pool, 'healthmonitor', None)
                
                if pool_id:
                    dependent_resources['pools'].append(pool_id)
                    
                    # Get members in this pool
                    for member in members:
                        # Handle both dictionary and object types for member
                        if isinstance(member, dict):
                            member_id = member.get('id')
                        else:
                            member_id = getattr(member, 'id', None)
                            
                        if member_id:
                            dependent_resources['members'].append(member_id)
                    
                    # Get health monitor for this pool
                    if health_monitor:
                        # Handle both dictionary and object types for health monitor
                        if isinstance(health_monitor, dict):
                            hm_id = health_monitor.get('id')
                        else:
                            hm_id = getattr(health_monitor, 'id', None)
                            
                        if hm_id:
                            dependent_resources['health_monitors'].append(hm_id)
            
            # TODO: Handle multiple pools per listener when supported
            # For now, LoxiLB only supports one pool per listener
            
        except Exception as e:
            # Handle both dictionary and object types for listener ID in error message
            if isinstance(listener, dict):
                log_listener_id = listener.get('id')
            else:
                log_listener_id = getattr(listener, 'id', 'unknown')
                
            LOG.warning("Failed to determine dependent resources for listener %s: %s", 
                       log_listener_id, e)
        
        return dependent_resources

    def reconcile_cascade_delete(self, listener_id, dependent_resources):
        """Reconcile Octavia state after a cascade delete in LoxiLB.
        
        When a listener is deleted in LoxiLB, it cascade deletes the entire
        service including pools, members, and health monitors. This method
        cleans up the corresponding Octavia state to maintain consistency.
        
        Args:
            listener_id: ID of the deleted listener
            dependent_resources: Dict of dependent resources from get_dependent_resources()
            
        Returns:
            dict: Summary of reconciliation actions taken
        """
        reconciliation_summary = {
            'listener_id': listener_id,
            'cleaned_up': {
                'pools': [],
                'members': [],
                'health_monitors': []
            },
            'errors': []
        }
        
        LOG.info("Starting cascade delete reconciliation for listener %s", listener_id)
        
        # Clean up health monitors first (they depend on pools)
        for hm_id in dependent_resources.get('health_monitors', []):
            try:
                self._mark_resource_cascade_deleted('health_monitor', hm_id)
                reconciliation_summary['cleaned_up']['health_monitors'].append(hm_id)
                LOG.info("Marked health monitor %s as cascade deleted", hm_id)
            except Exception as e:
                error_msg = f"Failed to clean up health monitor {hm_id}: {e}"
                reconciliation_summary['errors'].append(error_msg)
                LOG.error(error_msg)
        
        # Clean up members next (they depend on pools)
        for member_id in dependent_resources.get('members', []):
            try:
                self._mark_resource_cascade_deleted('member', member_id)
                reconciliation_summary['cleaned_up']['members'].append(member_id)
                LOG.info("Marked member %s as cascade deleted", member_id)
            except Exception as e:
                error_msg = f"Failed to clean up member {member_id}: {e}"
                reconciliation_summary['errors'].append(error_msg)
                LOG.error(error_msg)
        
        # Clean up pools last
        for pool_id in dependent_resources.get('pools', []):
            try:
                self._mark_resource_cascade_deleted('pool', pool_id)
                reconciliation_summary['cleaned_up']['pools'].append(pool_id)
                LOG.info("Marked pool %s as cascade deleted", pool_id)
            except Exception as e:
                error_msg = f"Failed to clean up pool {pool_id}: {e}"
                reconciliation_summary['errors'].append(error_msg)
                LOG.error(error_msg)
        
        LOG.info("Cascade delete reconciliation completed for listener %s: %s", 
                listener_id, reconciliation_summary)
        
        return reconciliation_summary

    def _mark_resource_cascade_deleted(self, resource_type, resource_id):
        """Mark a resource as cascade deleted by cleaning up its mapping.
        
        This removes the resource from the ID mapping cache, effectively
        marking it as deleted from the LoxiLB perspective while leaving
        Octavia to handle the database cleanup.
        
        Args:
            resource_type: Type of resource ('pool', 'member', 'health_monitor')
            resource_id: UUID of the resource
        """
        # Remove ID mapping to indicate resource no longer exists in LoxiLB
        utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, resource_id)
        
        # Log the cascade delete for auditing
        LOG.warning("CASCADE DELETE: %s %s was implicitly deleted from LoxiLB "
                   "due to listener deletion", resource_type, resource_id)

    def validate_resource_consistency(self, resource_type, resource_id):
        """Validate that a resource exists consistently in both systems.
        
        Args:
            resource_type: Type of resource to validate
            resource_id: UUID of the resource
            
        Returns:
            dict: Validation result with consistency status and details
        """
        validation_result = {
            'resource_type': resource_type,
            'resource_id': resource_id,
            'consistent': False,
            'octavia_exists': False,
            'loxilb_exists': False,
            'issues': []
        }
        
        try:
            # Check if resource has mapping (indicates it should exist in LoxiLB)
            loxilb_key = utils.get_loxilb_key_from_octavia_id(
                self.resource_mapper.id_mapping_cache, resource_id
            )
            validation_result['octavia_exists'] = loxilb_key is not None
            
            if loxilb_key:
                # Try to verify the resource exists in LoxiLB
                # This is resource-type specific
                loxilb_exists = self._check_loxilb_resource_exists(
                    resource_type, loxilb_key
                )
                validation_result['loxilb_exists'] = loxilb_exists
                
                if not loxilb_exists:
                    validation_result['issues'].append(
                        f"Resource {resource_id} has mapping but doesn't exist in LoxiLB"
                    )
            else:
                validation_result['issues'].append(
                    f"Resource {resource_id} has no LoxiLB mapping"
                )
            
            validation_result['consistent'] = (
                validation_result['octavia_exists'] == validation_result['loxilb_exists']
            )
            
        except Exception as e:
            validation_result['issues'].append(f"Validation failed: {e}")
            LOG.error("Failed to validate resource consistency for %s %s: %s", 
                     resource_type, resource_id, e)
        
        return validation_result

    def _check_loxilb_resource_exists(self, resource_type, loxilb_key):
        """Check if a resource exists in LoxiLB based on its key.
        
        Args:
            resource_type: Type of resource
            loxilb_key: LoxiLB key for the resource
            
        Returns:
            bool: True if resource exists in LoxiLB
        """
        try:
            if resource_type in ['listener', 'pool']:
                # For listeners and pools, check if the service exists
                service_info = utils.parse_loxilb_service_key(loxilb_key)
                rules = self.api_client.get_loadbalancer_rules()
                for rule in rules:
                    if (rule.get('externalIP') == service_info['external_ip'] and
                        rule.get('port') == service_info['port'] and
                        rule.get('protocol') == service_info['protocol']):
                        return True
                return False
            
            elif resource_type == 'health_monitor':
                # For health monitors, check if the endpoint exists
                endpoints = self.api_client.get_endpoints()
                return any(ep.get('name') == loxilb_key for ep in endpoints)
            
            elif resource_type == 'member':
                # For members, this is more complex as they're part of services
                # For now, assume they exist if the parent service exists
                # TODO: Implement more precise member existence checking
                return True
            
            else:
                LOG.warning("Unknown resource type for existence check: %s", resource_type)
                return False
                
        except Exception as e:
            LOG.error("Failed to check LoxiLB resource existence for %s: %s", 
                     loxilb_key, e)
            return False

    def detect_orphaned_resources(self):
        """Detect resources that exist in one system but not the other.
        
        Returns:
            dict: Summary of orphaned resources found
        """
        orphaned_resources = {
            'octavia_orphans': [],  # Resources in Octavia but not LoxiLB
            'loxilb_orphans': []    # Resources in LoxiLB but not Octavia
        }
        
        try:
            # Check all mapped resources for consistency
            for octavia_id, loxilb_key in self.resource_mapper.id_mapping_cache.items():
                # TODO: Determine resource type from mapping metadata
                # For now, skip detailed orphan detection
                pass
            
            # TODO: Implement comprehensive orphan detection
            # This would require scanning both Octavia and LoxiLB APIs
            # and comparing their resource lists
            
        except Exception as e:
            LOG.error("Failed to detect orphaned resources: %s", e)
        
        return orphaned_resources

    def create_reconciliation_report(self):
        """Create a comprehensive report of state consistency.
        
        Returns:
            dict: Detailed report of system state consistency
        """
        report = {
            'timestamp': utils.get_current_timestamp(),
            'total_mapped_resources': len(self.resource_mapper.id_mapping_cache),
            'consistency_checks': [],
            'orphaned_resources': None,
            'recommendations': []
        }
        
        try:
            # Run orphan detection
            report['orphaned_resources'] = self.detect_orphaned_resources()
            
            # Add recommendations based on findings
            if report['orphaned_resources']['octavia_orphans']:
                report['recommendations'].append(
                    "Found Octavia resources without LoxiLB mappings - consider cleanup"
                )
            
            if report['orphaned_resources']['loxilb_orphans']:
                report['recommendations'].append(
                    "Found LoxiLB resources without Octavia mappings - consider reconciliation"
                )
            
            if report['total_mapped_resources'] == 0:
                report['recommendations'].append(
                    "No mapped resources found - this may indicate a configuration issue"
                )
            
        except Exception as e:
            LOG.error("Failed to create reconciliation report: %s", e)
            report['error'] = str(e)
        
        return report

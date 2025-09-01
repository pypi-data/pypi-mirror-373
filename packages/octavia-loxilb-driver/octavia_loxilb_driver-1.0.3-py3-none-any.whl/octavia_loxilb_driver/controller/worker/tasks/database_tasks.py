# Copyright 2025 LoxiLB
# Licensed under the Apache License, Version 2.0

from oslo_log import log as logging
from taskflow import task

from octavia.db import api as db_apis
from octavia.db import repositories as repo

LOG = logging.getLogger(__name__)


class UpdateLoadBalancerInDB(task.Task):
    """Task to update load balancer status in database."""

    def __init__(self, provisioning_status=None, operating_status=None, **kwargs):
        self.provisioning_status = provisioning_status
        self.operating_status = operating_status
        super().__init__(**kwargs)
        self.lb_repo = repo.LoadBalancerRepository()

    def execute(self, loadbalancer, **kwargs):
        """Update load balancer in database."""
        LOG.debug("Updating load balancer %s status in database", loadbalancer.id)
        
        update_dict = {}
        if self.provisioning_status:
            update_dict['provisioning_status'] = self.provisioning_status
        if self.operating_status:
            update_dict['operating_status'] = self.operating_status
            
        if update_dict:
            self.lb_repo.update(
                db_apis.get_session(),
                loadbalancer.id,
                **update_dict
            )
            LOG.debug("Updated load balancer %s with status: %s", 
                     loadbalancer.id, update_dict)


class MarkLoadBalancerDeletedInDB(task.Task):
    """Task to mark load balancer as deleted in database."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lb_repo = repo.LoadBalancerRepository()

    def execute(self, loadbalancer, **kwargs):
        """Mark load balancer as deleted."""
        LOG.debug("Marking load balancer %s as deleted", loadbalancer.id)
        
        # Octavia will handle the actual deletion from DB
        # We just mark it with deleted status
        self.lb_repo.update(
            db_apis.get_session(),
            loadbalancer.id,
            provisioning_status='DELETED'
        )
        
class UpdateListenerInDB(task.Task):
    """Task to update listener status in database."""

    def __init__(self, provisioning_status=None, operating_status=None, **kwargs):
        self.provisioning_status = provisioning_status
        self.operating_status = operating_status
        super().__init__(**kwargs)
        self.listener_repo = repo.ListenerRepository()

    def execute(self, listener, **kwargs):
        """Update listener in database."""
        LOG.debug("Updating listener %s status in database", listener.id)
        
        update_dict = {}
        if self.provisioning_status:
            update_dict['provisioning_status'] = self.provisioning_status
        if self.operating_status:
            update_dict['operating_status'] = self.operating_status
            
        if update_dict:
            self.listener_repo.update(
                db_apis.get_session(),
                listener.id,
                **update_dict
            )


class MarkListenerDeletedInDB(task.Task):
    """Task to mark listener as deleted in database."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.listener_repo = repo.ListenerRepository()

    def execute(self, listener, **kwargs):
        """Mark listener as deleted."""
        LOG.debug("Marking listener %s as deleted", listener.id)
        self.listener_repo.update(
            db_apis.get_session(),
            listener.id,
            provisioning_status='DELETED'
        )


class UpdatePoolInDB(task.Task):
    """Task to update pool status in database."""

    def __init__(self, provisioning_status=None, operating_status=None, **kwargs):
        self.provisioning_status = provisioning_status
        self.operating_status = operating_status
        super().__init__(**kwargs)
        self.pool_repo = repo.PoolRepository()

    def execute(self, pool, **kwargs):
        """Update pool in database."""
        LOG.debug("Updating pool %s status in database", pool.id)
        
        update_dict = {}
        if self.provisioning_status:
            update_dict['provisioning_status'] = self.provisioning_status
        if self.operating_status:
            update_dict['operating_status'] = self.operating_status
            
        if update_dict:
            self.pool_repo.update(
                db_apis.get_session(),
                pool.id,
                **update_dict
            )


class MarkPoolDeletedInDB(task.Task):
    """Task to mark pool as deleted in database."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pool_repo = repo.PoolRepository()

    def execute(self, pool, **kwargs):
        """Mark pool as deleted."""
        LOG.debug("Marking pool %s as deleted", pool.id)
        self.pool_repo.update(
            db_apis.get_session(),
            pool.id,
            provisioning_status='DELETED'
        )


class UpdateMemberInDB(task.Task):
    """Task to update member status in database."""

    def __init__(self, provisioning_status=None, operating_status=None, **kwargs):
        self.provisioning_status = provisioning_status
        self.operating_status = operating_status
        super().__init__(**kwargs)
        self.member_repo = repo.MemberRepository()

    def execute(self, member, **kwargs):
        """Update member in database."""
        LOG.debug("Updating member %s status in database", member.id)
        
        update_dict = {}
        if self.provisioning_status:
            update_dict['provisioning_status'] = self.provisioning_status
        if self.operating_status:
            update_dict['operating_status'] = self.operating_status
            
        if update_dict:
            self.member_repo.update(
                db_apis.get_session(),
                member.id,
                **update_dict
            )


class MarkMemberDeletedInDB(task.Task):
    """Task to mark member as deleted in database."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.member_repo = repo.MemberRepository()

    def execute(self, member, **kwargs):
        """Mark member as deleted."""
        LOG.debug("Marking member %s as deleted", member.id)
        self.member_repo.update(
            db_apis.get_session(),
            member.id,
            provisioning_status='DELETED'
        )


class UpdateHealthMonitorInDB(task.Task):
    """Task to update health monitor status in database."""

    def __init__(self, provisioning_status=None, operating_status=None, **kwargs):
        self.provisioning_status = provisioning_status
        self.operating_status = operating_status
        super().__init__(**kwargs)
        self.health_mon_repo = repo.HealthMonitorRepository()

    def execute(self, health_monitor, **kwargs):
        """Update health monitor in database."""
        LOG.debug("Updating health monitor %s status in database", health_monitor.id)
        
        update_dict = {}
        if self.provisioning_status:
            update_dict['provisioning_status'] = self.provisioning_status
        if self.operating_status:
            update_dict['operating_status'] = self.operating_status
            
        if update_dict:
            self.health_mon_repo.update(
                db_apis.get_session(),
                health_monitor.id,
                **update_dict
            )


class MarkHealthMonitorDeletedInDB(task.Task):
    """Task to mark health monitor as deleted in database."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.health_mon_repo = repo.HealthMonitorRepository()

    def execute(self, health_monitor, **kwargs):
        """Mark health monitor as deleted."""
        LOG.debug("Marking health monitor %s as deleted", health_monitor.id)
        self.health_mon_repo.update(
            db_apis.get_session(),
            health_monitor.id,
            provisioning_status='DELETED'
        )


class UpdateL7PolicyInDB(task.Task):
    """Task to update L7 policy status in database."""

    def __init__(self, provisioning_status=None, operating_status=None, **kwargs):
        self.provisioning_status = provisioning_status
        self.operating_status = operating_status
        super().__init__(**kwargs)
        self.l7policy_repo = repo.L7PolicyRepository()

    def execute(self, l7policy, **kwargs):
        """Update L7 policy in database."""
        LOG.debug("Updating L7 policy %s status in database", l7policy.id)
        
        update_dict = {}
        if self.provisioning_status:
            update_dict['provisioning_status'] = self.provisioning_status
        if self.operating_status:
            update_dict['operating_status'] = self.operating_status
            
        if update_dict:
            self.l7policy_repo.update(
                db_apis.get_session(),
                l7policy.id,
                **update_dict
            )


class MarkL7PolicyDeletedInDB(task.Task):
    """Task to mark L7 policy as deleted in database."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.l7policy_repo = repo.L7PolicyRepository()

    def execute(self, l7policy, **kwargs):
        """Mark L7 policy as deleted."""
        LOG.debug("Marking L7 policy %s as deleted", l7policy.id)
        self.l7policy_repo.update(
            db_apis.get_session(),
            l7policy.id,
            provisioning_status='DELETED'
        )


class UpdateL7RuleInDB(task.Task):
    """Task to update L7 rule status in database."""

    def __init__(self, provisioning_status=None, operating_status=None, **kwargs):
        self.provisioning_status = provisioning_status
        self.operating_status = operating_status
        super().__init__(**kwargs)
        self.l7rule_repo = repo.L7RuleRepository()

    def execute(self, l7rule, **kwargs):
        """Update L7 rule in database."""
        LOG.debug("Updating L7 rule %s status in database", l7rule.id)
        
        update_dict = {}
        if self.provisioning_status:
            update_dict['provisioning_status'] = self.provisioning_status
        if self.operating_status:
            update_dict['operating_status'] = self.operating_status
            
        if update_dict:
            self.l7rule_repo.update(
                db_apis.get_session(),
                l7rule.id,
                **update_dict
            )


class MarkL7RuleDeletedInDB(task.Task):
    """Task to mark L7 rule as deleted in database."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.l7rule_repo = repo.L7RuleRepository()

    def execute(self, l7rule, **kwargs):
        """Mark L7 rule as deleted."""
        LOG.debug("Marking L7 rule %s as deleted", l7rule.id)
        self.l7rule_repo.update(
            db_apis.get_session(),
            l7rule.id,
            provisioning_status='DELETED'
        )


class MarkChildObjectsDeletedInDB(task.Task):
    """Task to mark all child objects of a load balancer as deleted in database."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.listener_repo = repo.ListenerRepository()
        self.pool_repo = repo.PoolRepository()
        self.l7policy_repo = repo.L7PolicyRepository()

    def execute(self, loadbalancer, **kwargs):
        """Mark all child objects as deleted."""
        LOG.debug("Marking all child objects of load balancer %s as deleted", loadbalancer.id)
        
        # Mark all listeners as deleted
        for listener in loadbalancer.listeners:
            self.listener_repo.update(
                db_apis.get_session(),
                listener.id,
                provisioning_status='DELETED'
            )
            
            # Mark all L7 policies of this listener as deleted
            for l7policy in listener.l7policies:
                self.l7policy_repo.update(
                    db_apis.get_session(),
                    l7policy.id,
                    provisioning_status='DELETED'
                )
        
        # Mark all pools as deleted
        for pool in loadbalancer.pools:
            self.pool_repo.update(
                db_apis.get_session(),
                pool.id,
                provisioning_status='DELETED'
            )


class MarkL7PoliciesDeletedInDB(task.Task):
    """Task to mark all L7 policies of a listener as deleted in database."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.l7policy_repo = repo.L7PolicyRepository()
        self.l7rule_repo = repo.L7RuleRepository()

    def execute(self, listener, **kwargs):
        """Mark all L7 policies and their rules as deleted."""
        LOG.debug("Marking all L7 policies of listener %s as deleted", listener.id)
        
        # Mark all L7 policies as deleted
        for l7policy in listener.l7policies:
            self.l7policy_repo.update(
                db_apis.get_session(),
                l7policy.id,
                provisioning_status='DELETED'
            )
            
            # Mark all L7 rules of this policy as deleted
            for l7rule in l7policy.rules:
                self.l7rule_repo.update(
                    db_apis.get_session(),
                    l7rule.id,
                    provisioning_status='DELETED'
                )


class MarkL7RulesDeletedInDB(task.Task):
    """Task to mark all L7 rules of an L7 policy as deleted in database."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.l7rule_repo = repo.L7RuleRepository()

    def execute(self, l7policy, **kwargs):
        """Mark all L7 rules as deleted."""
        LOG.debug("Marking all L7 rules of L7 policy %s as deleted", l7policy.id)
        
        # Mark all L7 rules as deleted
        for l7rule in l7policy.rules:
            self.l7rule_repo.update(
                db_apis.get_session(),
                l7rule.id,
                provisioning_status='DELETED'
            )


class MarkPoolChildrenDeletedInDB(task.Task):
    """Task to mark all child objects of a pool as deleted in database."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.member_repo = repo.MemberRepository()
        self.health_mon_repo = repo.HealthMonitorRepository()

    def execute(self, pool, **kwargs):
        """Mark all child objects as deleted."""
        LOG.debug("Marking all child objects of pool %s as deleted", pool.id)
        
        # Mark all members as deleted
        for member in pool.members:
            self.member_repo.update(
                db_apis.get_session(),
                member.id,
                provisioning_status='DELETED'
            )
        
        # Mark health monitor as deleted if it exists
        if pool.health_monitor:
            self.health_mon_repo.update(
                db_apis.get_session(),
                pool.health_monitor.id,
                provisioning_status='DELETED'
            )
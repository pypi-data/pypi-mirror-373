"""Base test class for unit tests."""

import unittest
from unittest import mock

from oslo_config import cfg
from oslo_log import log as logging

from octavia_loxilb_driver.common import config

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class TestCase(unittest.TestCase):
    """Base test case class for all unit tests."""

    def setUp(self):
        super(TestCase, self).setUp()
        self.addCleanup(mock.patch.stopall)
        
        # Register configuration once - check if already registered to avoid duplicates
        if not self._config_already_registered():
            self._register_config()
        
        # Clear and set test configuration values
        self._setup_test_config()

        # Mock logging
        self.LOG = mock.MagicMock()
    
    def _config_already_registered(self):
        """Check if loxilb config options are already registered."""
        try:
            # Try to access a config option - if it exists, config is registered
            CONF.loxilb.api_endpoints
            return True
        except (cfg.NoSuchOptError, cfg.NoSuchGroupError):
            return False
    
    def _register_config(self):
        """Register configuration options if not already registered."""
        try:
            CONF.register_group(config.loxilb_group)
            CONF.register_opts(config.loxilb_opts, group="loxilb")
        except cfg.DuplicateOptError:
            # Options already registered, ignore
            pass
    
    def _setup_test_config(self):
        """Set up test configuration values."""
        # Override with test-specific values
        CONF.set_override("api_endpoints", ["http://localhost:11111"], group="loxilb")
        CONF.set_override("api_timeout", 30, group="loxilb")
        CONF.set_override("api_retries", 3, group="loxilb")
        CONF.set_override("api_retry_interval", 1, group="loxilb")
        
    def tearDown(self):
        """Clean up after test."""
        super(TestCase, self).tearDown()
        # Clear any configuration overrides
        CONF.clear_override("api_endpoints", group="loxilb")
        CONF.clear_override("api_timeout", group="loxilb")
        CONF.clear_override("api_retries", group="loxilb")
        CONF.clear_override("api_retry_interval", group="loxilb")

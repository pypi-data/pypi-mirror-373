#!/usr/bin/env python

# Copyright 2025 LoxiLB
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from setuptools import setup, find_packages

setup(
    name="octavia_loxilb_driver",
    version="0.1.0",
    packages=find_packages(),
    description="Octavia LoxiLB Provider Driver",
    author="LoxiLB Team",
    author_email="info@loxilb.io",
    url="https://github.com/loxilb-io/octavia-loxilb-driver",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: OpenStack",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        'octavia.api.drivers': [
            'loxilb = octavia_loxilb_driver.driver.provider_driver:LoxiLBProviderDriver',
        ],
        'octavia.driver_agent.provider_agents': [
            'loxilb = octavia_loxilb_driver.controller.worker:LoxiLBControllerWorker',
        ],
        'console_scripts': [
            'octavia-loxilb-worker = octavia_loxilb_driver.cmd.loxilb_worker:main',
            'octavia-loxilb-controller-worker = octavia_loxilb_driver.cmd.loxilb_controller_worker:main',
        ],
        'oslo.config.opts': [
            'octavia_loxilb_driver = octavia_loxilb_driver.common.config:list_opts',
        ],
    },
    python_requires='>=3.8',
    install_requires=[
        'octavia-lib>=2.5.0',
        'oslo.config>=8.0.0',
        'oslo.log>=4.4.0',
        'oslo.messaging>=12.4.0',
        'oslo.db>=8.4.0',
        'taskflow>=4.0.0',
        'tenacity>=6.0.0',
        'requests>=2.25.0',
        'SQLAlchemy>=1.4.0',
        'alembic>=1.4.0',
    ],
    extras_require={
        'test': [
            'pytest>=6.0.0',
            'pytest-cov>=2.10.0',
            'mock>=4.0.0',
            'testtools>=2.4.0',
        ],
    },
    data_files=[
        ('share/octavia-loxilb-driver', [
            'LICENSE',
            'README.md',
            'CHANGELOG.md',
        ]),
        ('etc/octavia', [
            'etc/loxilb.conf.sample',
        ]),
    ],
    include_package_data=True,
    zip_safe=False,
)
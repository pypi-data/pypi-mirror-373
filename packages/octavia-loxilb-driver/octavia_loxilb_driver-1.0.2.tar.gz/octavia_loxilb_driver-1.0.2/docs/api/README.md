# API Reference

Technical API documentation for the LoxiLB Octavia Driver.

## Overview

The LoxiLB Octavia Driver provides two main API interfaces:

1. **Octavia Provider Driver API**: Standard Octavia driver interface
2. **LoxiLB API Client**: Internal client for LoxiLB communication

## API Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OpenStack     │    │  LoxiLB Octavia │    │     LoxiLB      │
│   Octavia       │◄───┤     Driver      ├───►│   REST API      │
│   API           │    │                 │    │   (Port 8080)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Octavia Provider Driver API

Implements the standard Octavia provider driver interface:

### Core Operations
- **LoadBalancer**: Create, update, delete, get operations
- **Listener**: Protocol and port management
- **Pool**: Backend server pool management
- **Member**: Individual backend server operations
- **HealthMonitor**: Health check configuration

### RPC Communication
Uses OpenStack RPC for asynchronous operation handling:
- Provider driver sends requests via RPC
- Controller worker processes operations using TaskFlow
- Status updates sent back to Octavia

## LoxiLB API Client

HTTP client for LoxiLB REST API communication:

### Key Features
- Connection pooling and retry logic
- Load balancer CRUD operations
- Network interface configuration
- Health check management

### API Endpoints
- `/config/loadbalancer` - Load balancer operations
- `/config/port/all` - Network port discovery
- `/config/ipv4address` - IP address configuration
- `/config/healthcheck` - Health monitoring

---

*For implementation details, see the source code in `octavia_loxilb_driver/` directory.*

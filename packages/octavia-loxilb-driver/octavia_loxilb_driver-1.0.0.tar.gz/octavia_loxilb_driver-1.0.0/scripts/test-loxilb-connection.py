#!/usr/bin/env python3
"""Test LoxiLB connection."""

import json
import platform
import sys

import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def test_connection():
    """Test connection to LoxiLB endpoints."""
    print(f"🔍 Testing LoxiLB connection from {platform.machine()} architecture")

    endpoints = ["http://localhost:8080/netlox/v1", "http://localhost:8081/netlox/v1"]

    success_count = 0

    for endpoint in endpoints:
        print(f"\n📡 Testing {endpoint}...")
        try:
            response = requests.get(f"{endpoint}/version", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
                try:
                    data = response.json()
                    print(f"   📊 Status: {json.dumps(data, indent=2)}")
                except:
                    print(f"   📄 Response: {response.text}")
                success_count += 1
            else:
                print(f"❌ {endpoint} - HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Connection refused")
            print("   💡 Hint: Run 'make start-loxilb' to start LoxiLB")
        except requests.exceptions.Timeout:
            print(f"❌ {endpoint} - Timeout")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

    print(f"\n📈 Summary: {success_count}/{len(endpoints)} endpoints responding")

    if success_count == 0:
        print("💡 To start LoxiLB: make start-loxilb")
        sys.exit(1)
    elif success_count < len(endpoints):
        print("⚠️  Some endpoints not responding")
        sys.exit(1)
    else:
        print("✅ All LoxiLB endpoints are healthy!")


if __name__ == "__main__":
    test_connection()

#!/usr/bin/env python3
"""Illustrative Foundry delegated-subnet sizing calculator."""

import argparse
import ipaddress
import math


def usable(prefix: int) -> int:
    return (2 ** (32 - prefix)) - 5


def choose_prefix(required: int) -> tuple[int, int]:
    for prefix in range(27, 15, -1):
        capacity = usable(prefix)
        if capacity >= required:
            return prefix, capacity
    raise ValueError("Required capacity exceeds this calculator's supported range")


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate a Foundry delegated-subnet baseline")
    parser.add_argument("--sessions", type=int, required=True, help="Peak concurrent hosted-agent sessions")
    parser.add_argument("--platform-ips", type=int, default=20, help="Project and platform address allowance")
    parser.add_argument("--target-utilization", type=float, default=0.80, help="Maximum planned utilization from 0 to 1")
    parser.add_argument("--regional-quota", type=int, help="Approved regional hosted-session quota")
    args = parser.parse_args()

    if args.sessions < 0 or args.platform_ips < 0:
        parser.error("sessions and platform-ips must be non-negative")
    if not 0 < args.target_utilization < 1:
        parser.error("target-utilization must be between 0 and 1")

    required = math.ceil((args.sessions + args.platform_ips) / args.target_utilization)
    prefix, capacity = choose_prefix(required)
    print(f"Required usable addresses: {required}")
    print(f"Suggested subnet baseline: /{prefix}")
    print(f"Approximate usable addresses: {capacity}")
    print(f"Example network: {ipaddress.ip_network(f'10.0.0.0/{prefix}')}")
    if args.regional_quota is not None:
        print(f"Effective session ceiling before other overhead: {min(capacity, args.regional_quota)}")
        if args.regional_quota < args.sessions:
            print("Warning: the supplied regional quota is below the planned hosted-session demand")
    print("Validate the result against current Microsoft guidance, project count, quotas and load testing.")


if __name__ == "__main__":
    main()

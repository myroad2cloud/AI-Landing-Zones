# Pre-Sales Solution Playbook

## 1. Executive recommendation

Contoso Retail Bank should use a Standard Microsoft Foundry setup with customer-managed networking for its employee service-desk agent. Production uses a dedicated `/24` subnet delegated to `Microsoft.App/environments`, a separate private-endpoint subnet and controlled outbound traffic through the connectivity hub.

The working design supports 150 expected concurrent hosted-agent sessions across three projects. Final approval depends on customer telemetry, non-overlapping address allocation, regional quota confirmation, private DNS testing and performance acceptance.

## 2. Discovery method

Collect evidence from the business, application, network, security, data and operations teams. The architect should establish:

- Eligible users and busiest-hour active users
- Session starts per minute and P95 session duration
- Prompt-agent versus hosted-agent use cases
- Projects, environments, regions and regulatory boundaries
- VNet ranges, peering, DNS forwarding and firewall policy
- Data services and internal APIs used by each agent
- Tool traffic that uses the VNet, Microsoft backbone or public endpoints
- Availability targets, monitoring ownership and recovery objectives

Use measured peak values where possible. Daily averages hide capacity requirements.

## 3. Evidence classification

| Classification | Meaning | Pre-sales treatment |
|---|---|---|
| Confirmed | Approved customer fact or requirement | May support a commitment |
| Measured | Telemetry, logs or inventory | Record source and observation period |
| Estimated | Calculation based on available evidence | Record method and sensitivity |
| Assumed | Working value with insufficient evidence | Assign owner and validation date |
| Design decision | Architecture choice | Record alternatives and rationale |

## 4. Demand model

An early hosted-session estimate can use:

```text
Peak hosted sessions =
peak active users × simultaneous-use rate × hosted-agent share × sessions per hosted user
```

The expected case assumes:

```text
2,400 × 20% × 30% × 1 = 144
```

The model rounds this to 150 for planning.

Subnet requirement:

```text
Required usable IPs =
(peak hosted sessions + project/platform allowance) / target utilization

(150 + 20) / 0.80 = 213
```

The `/24` baseline provides approximately 251 usable addresses. The high scenario requires a larger subnet and quota review.

## 5. Architecture model

### Microsoft-managed platform

- Foundry endpoint
- Tools Service
- Prompt-agent compute
- Platform control components

### Customer VNet

- Dedicated Foundry delegated subnet
- Hosted-agent Micro VMs
- Project-level single-tenant Data Proxies
- Separate private-endpoint subnet
- Private endpoints for Storage, Cosmos DB, Azure AI Search, Key Vault and Container Registry
- Azure Firewall or an approved NVA for inspected outbound traffic
- Azure DNS Private Resolver or approved enterprise DNS pattern

Hosted-agent sessions consume subnet capacity through Micro VM network interfaces. Prompt agents use Microsoft-managed compute, but their projects still require Data Proxy capacity. Tool calls from both agent types pass through the project Data Proxy.

## 6. Account boundaries

All projects under one Foundry account share the delegated subnet. Separate production and non-production accounts when production capacity, change control or regulatory isolation matters.

Consider separate accounts for:

- Production and non-production
- Different regulatory boundaries
- Regions with separate recovery designs
- Business units that need capacity isolation

## 7. Private connectivity and DNS

Create private endpoints for each required data service and disable public network access where the approved architecture requires it. Private endpoints do not automatically solve DNS.

Validate from the actual client and agent network paths:

```bash
nslookup <service-fqdn>
```

The service FQDN should resolve to the intended private address. Also test TCP 443, managed identity, RBAC and the required data-plane operation.

## 8. Security controls

- Use managed identities instead of stored application credentials.
- Separate deployment, runtime and human administration identities.
- Grant each agent only the actions required by its tools.
- Review the real traffic path for every tool.
- Use Azure Policy and diagnostic settings for preventive and detective controls.
- Treat prompt injection and over-privileged tools as application-security risks.

## 9. Capacity and quota

Subnet capacity and Foundry regional quota are different limits. Effective capacity is the lower value.

```text
Effective capacity = min(subnet capacity, approved regional quota)
```

Do not promise a quota increase before Microsoft confirms it. Record it as a proposal dependency and allow lead time.

## 10. Load-test gates

Test baseline, expected, burst and deployment-overlap scenarios. Measure:

- Session creation and startup latency
- Tool-call P50 and P95 latency
- HTTP 429 and 5xx errors
- `subnet_exhausted` signals
- DNS and private-endpoint failures
- Data Proxy behavior
- Recovery after a burst
- Behavior during a new agent revision rollout

Production approval requires accepted results at the expected peak with operational headroom.

## 11. SOW protection

Suggested wording:

> The proposed network sizing assumes a peak of 150 concurrent hosted-agent sessions across three production projects, with 30 percent growth over 24 months. The solution uses a `/24` delegated subnet and a separate private-endpoint subnet. Final sizing remains subject to customer telemetry, IP-address approval, Foundry regional quota confirmation and performance testing. A material increase in projects, hosted-agent concurrency, regions or public-endpoint restrictions may require redesign and commercial change control.

## 12. Approval gates

1. The sponsor approves use cases, adoption and success measures.
2. Network and security teams approve CIDRs, DNS, private endpoints and egress paths.
3. Microsoft confirms regional quota and capacity.
4. The pilot validates identity, tool paths and monitoring.
5. Load and recovery testing prove production readiness.

## 13. Key lesson

A defensible proposal links every recommendation to evidence, an explicit assumption or a documented constraint. Subnet size alone is not the solution. The architecture must align agent type, concurrency, account boundaries, private connectivity, DNS, identity, quotas, operations and recovery.

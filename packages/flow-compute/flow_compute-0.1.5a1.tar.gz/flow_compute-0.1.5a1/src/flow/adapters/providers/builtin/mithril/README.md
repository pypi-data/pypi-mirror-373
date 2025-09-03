# Mithril (Mithril) Provider

This directory contains the Mithril (Foundry Compute Platform) provider implementation for Flow SDK.

## Environment Specifications

Mithril instances run on:
- **OS**: Ubuntu 22.04
- **Shell**: bash (required)
- **Pre-installed**: NVIDIA driver 535, CUDA 12.2
- **Startup Script Limit**: 10,000 characters
- **Execution**: First boot only (not on restart/preemption)

## Official Documentation

For the most up-to-date information, refer to the official Mithril documentation:

- [API Reference](https://docs.mithril.ai/compute-api/compute-api-reference)
- [API Overview](https://docs.mithril.ai/compute-api/api-overview-and-quickstart)
- [Startup Scripts](https://docs.mithril.ai/compute-and-storage/startup-scripts)
- [Instance Types](https://docs.mithril.ai/compute-and-storage/instance-types-and-specifications)
- [OpenAPI Spec](https://firebasestorage.googleapis.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FOTq5EAhUq1bhaygVHT8s%2Fimports%2F0gQyVfnbr1SwJA8ot4uG%2Fopenapi8.json?alt=media&token=a18e9b66-119f-4276-a372-5be3e52150c3)

## Key Implementation Details

### Startup Scripts
- Scripts are stored at `/var/lib/foundry/startup_script.sh`
- Logs are written to `/var/log/foundry/startup_script.log`
- Must begin with `#!/bin/bash`
- Only runs on initial instance creation

### Instance Types
Mithril uses specific instance type naming:
- Format: `{gpu}-{memory}gb.{interconnect}.{count}x`
- Examples: `a100-80gb.sxm.1x`, `h100-80gb.sxm.8x`

The SDK translates user-friendly names:
- `"a100"` → `"a100-80gb.sxm.1x"`
- `"4xa100"` → `"a100-80gb.sxm.4x"`

### API Endpoints
Base URL: `https://api.mithril.ai/v2/`

Key endpoints:
- `/v2/spot/bids` - Create and manage spot instances
- `/v2/volumes` - Storage management
- `/v2/instance-types` - Available instance types
- `/v2/spot/availability` - Check spot capacity

### Storage
- Block volumes: Need formatting on first use
- File shares: Pre-formatted (not yet exposed in SDK)
- Ephemeral storage: Automatically mounted at `/mnt/local`

## Provider-Specific Features

### Docker Caching
Mount a volume at `/var/lib/docker` to persist Docker images:
```python
volumes=[VolumeSpec(size_gb=50, mount_path="/var/lib/docker")]
```

### Multi-Node Support
Environment variables available:
- `Mithril_BID_ID` - Unique bid identifier
- `FLOW_NODE_RANK` - Node index in multi-node setup
- `FLOW_MAIN_IP` - Main node IP address

### SSH Access
Mithril provides SSH access through bastion hosts. The SDK handles connection details automatically.

## Known Limitations

1. **Startup Script Size**: 10,000 characters (not 16KB as cloud-init)
2. **Script Execution**: Only on first boot, not on restart
3. **Spot Instances**: May be preempted based on capacity
4. **Regions**: Limited availability in some regions

## Development Notes

### Testing
Use the Mithril test environment with appropriate API keys:
```bash
export MITHRIL_API_KEY="your-test-key"
export MITHRIL_PROJECT="test-project"
```

### Error Handling
Mithril-specific errors are mapped in `error_handler.py`:
- 422: Validation errors (e.g., invalid instance type)
- 404: Resource not found
- 403: Insufficient permissions or quota

### Future Enhancements
- [ ] File share support
- [ ] Reserved instance support
- [ ] Advanced networking features
- [ ] Custom image support
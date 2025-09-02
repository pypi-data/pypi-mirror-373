# Build-time configuration for baseshift CLI
# This file is generated/modified during the build process

# Tailscale integration enabled/disabled at build time
# For baseshift, Tailscale is enabled by default
TAILSCALE_ENABLED = True

# Custom host prompting enabled/disabled at build time
CUSTOM_HOST_ENABLED = False

def is_tailscale_enabled():
    """Check if Tailscale integration is enabled in this build."""
    return TAILSCALE_ENABLED

def is_custom_host_enabled():
    """Check if custom host prompting is enabled in this build."""
    return CUSTOM_HOST_ENABLED

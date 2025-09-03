def _can_use_ddtrace() -> bool:
    try:
        from ddtrace import __version__ as version

        # Parse version string into components (e.g. "2.6.0" -> [2, 6, 0])
        version_parts = version.split(".")

        # Check if it's version 2.6.0 or higher
        if len(version_parts) >= 2:
            major = int(version_parts[0])
            minor = int(version_parts[1])

            # Allow ddtrace 2.6+ to be used
            return major == 2 and minor >= 6
        return False
    except Exception:
        return False


def _can_use_datadog_statsd() -> bool:
    try:
        from datadog.dogstatsd.base import statsd

        _ = statsd
        return True
    except ImportError:
        return False


can_use_ddtrace = _can_use_ddtrace()
can_use_datadog_statsd = _can_use_datadog_statsd()

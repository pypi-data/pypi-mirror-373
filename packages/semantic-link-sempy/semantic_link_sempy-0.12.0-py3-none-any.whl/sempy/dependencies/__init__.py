from .._utils._telemetry import log_telemetry

from sempy.dependencies._plot import plot_dependency_metadata

__all__ = [
    "plot_dependency_metadata",
]

# log telemetry
log_telemetry(activity_name="sempy.dependencies")

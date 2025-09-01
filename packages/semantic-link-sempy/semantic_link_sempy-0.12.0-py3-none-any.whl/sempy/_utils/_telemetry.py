import os
import sys
from typing import Optional, Tuple
from .. import _version

ENVIRONMENT_NAME_TELEMETRY: Optional[str] = None
ENVIRONMENT_VERSION_TELEMETRY: Optional[str] = None

try:
    from synapse.ml.fabric.telemetry_utils import report_usage_telemetry
    REPORT_USAGE_TELEMETRY_ENV = "REPORT_USAGE_TELEMETRY"  # Environment variable to control telemetry reporting
except ImportError:
    report_usage_telemetry = None


def log_telemetry(activity_name: str = ""):

    def get_environment() -> Tuple[str, str]:
        from sempy.fabric._environment import _on_fabric, _on_aiskill, _on_jupyter
        environment_name = ""
        environment_version = ""
        if _on_fabric():
            if _on_jupyter():
                environment_name = "jupyter"
                environment_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            elif _on_aiskill():
                environment_name = "aiskill"
            else:
                environment_name = "spark"
                try:
                    import pyspark
                    environment_version = '.'.join(pyspark.__version__.split(".")[:2])
                except ImportError:
                    pass
        return environment_name, environment_version

    if report_usage_telemetry and \
            os.environ.get(REPORT_USAGE_TELEMETRY_ENV, "true").lower() == "true":
        global ENVIRONMENT_NAME_TELEMETRY
        global ENVIRONMENT_VERSION_TELEMETRY
        if ENVIRONMENT_NAME_TELEMETRY is None or ENVIRONMENT_VERSION_TELEMETRY is None:
            environment_info = get_environment()
            ENVIRONMENT_NAME_TELEMETRY = environment_info[0]
            ENVIRONMENT_VERSION_TELEMETRY = environment_info[1]
        report_usage_telemetry(
            "PyLibraryImport",
            activity_name,
            attributes={"version": _version.get_versions()['version'], "ImportType": "EXPLICIT_IMPORTED_BY_USER",
                        "EnvironmentName": ENVIRONMENT_NAME_TELEMETRY, "EnvironmentVersion":  ENVIRONMENT_VERSION_TELEMETRY},
        )
    else:
        # For unit test and robustness
        print(f"log_telemetry: {activity_name}")

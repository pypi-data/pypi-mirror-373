from sempy._utils._log import _get_user_logger

bullet = "\u2022"
green_dot = "\U0001F7E2"
yellow_dot = "\U0001F7E1"
red_dot = "\U0001F534"
warning = "\u26a0\ufe0f"
error = "\u274C"
info = "\u2139\ufe0f"
in_progress = "\u231b"
checked = "\u2611"
unchecked = "\u2610"
severity_mapping = {warning: "Warning", error: "Error", info: "Info"}

data_type_string = "string"
data_type_long = "long"
data_type_timestamp = "timestamp"
data_type_double = "double"
data_type_bool = "bool"

int_format = "int"
pct_format = "pct"
size_format = "size"
no_format = ""


class Logger:

    @staticmethod
    def warn(msg, *args, **kwargs):
        msg = f"{warning} {msg}"
        _get_user_logger().warning(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        msg = f"{error} {msg}"
        _get_user_logger().error(*args, **kwargs)

    @staticmethod
    def info(msg, *args, **kwargs):
        msg = f"{info} {msg}"
        _get_user_logger().info(*args, **kwargs)


sll_ann_name = "PBI_ProTooling"
sll_prefix = "SLL_"

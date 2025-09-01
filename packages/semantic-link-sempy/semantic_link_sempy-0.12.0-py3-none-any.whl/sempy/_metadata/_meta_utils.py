# -------------------------------------------------------------------------------------------------------------------------
# Debugging code
# -------------------------------------------------------------------------------------------------------------------------


def dump_meta(self, other, method):   # pragma: no cover
    self_meta = self.column_metadata if hasattr(self, "column_metadata") else None
    other_meta = other.column_metadata if hasattr(other, "column_metadata") else None
    print(f"method: {method}, {type(self).__name__}({dump_cols(self)})={self_meta}, {type(self).__name__}({dump_cols(other)}))={other_meta}")


def dump_cols(obj):   # pragma: no cover
    if hasattr(obj, "columns"):
        return list(obj.columns)
    elif hasattr(obj, "name"):
        return obj.name
    else:
        return None

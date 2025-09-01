class Multiplicity:
    """
    PowerBI relationship cardinality descriptor stored in :class:`~sempy.fabric.FabricDataFrame`.
    """

    MANY_TO_MANY = "m:m"

    MANY_TO_ONE = "m:1"

    ONE_TO_ONE = "1:1"

    _valid_multiplicities = [MANY_TO_MANY, MANY_TO_ONE, ONE_TO_ONE]

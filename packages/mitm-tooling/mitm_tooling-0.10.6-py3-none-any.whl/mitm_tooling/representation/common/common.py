ColumnName = str


class MITMRepresentationError(Exception):
    pass


class MITMSyntacticError(MITMRepresentationError):
    pass


class MITMTypeError(MITMRepresentationError):
    pass


class MITMDataError(MITMRepresentationError):
    pass

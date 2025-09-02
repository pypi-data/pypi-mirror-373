from ..data_models import DBMetaInfo
from ..data_models.base import ForeignKeyConstraintBase


def add_foreign_key_constraint(db_meta: DBMetaInfo, fkc: ForeignKeyConstraintBase):
    sa_fkc = fkc.to_sa_constraint(db_meta)
    if sa_fkc is not None:
        sa_fkc.table.append_constraint(sa_fkc)
        return True
    else:
        return False

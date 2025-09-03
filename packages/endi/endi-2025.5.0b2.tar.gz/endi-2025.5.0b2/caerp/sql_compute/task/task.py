from sqlalchemy import func

from caerp.models.task import TaskLine

"""
SQLAlchemy counterparts of compute classes

Implementation is partial atm (not all fields)

Computation logic is the same as compute classes

As it is used for stats only, precision is not that important
So division mode is used for ht reversal.

Anyway, things as epsilon cannot be easily handled in pure SQL
"""


class TaskLineSqlCompute:
    cost = func.ifnull(TaskLine.cost, 0)
    quantity = func.ifnull(TaskLine.quantity, 1)

    unit_ht = func.IF(
        TaskLine.mode == "ht",
        cost,
        cost * 10000 / (TaskLine.tva + 100 * 100.0),
    )
    total_ht = unit_ht * quantity

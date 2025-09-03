from alembic import op
import sqlalchemy as sa


def force_rename_table(old, new):
    """
    Rename a table, dropping any pre-existing table with new name

    Required because a table with new table name will be auto-created (empty)
    before migrations are ran. Making op.rename_table crash.
    """
    from alembic.context import get_bind

    if table_exists(old):
        if table_exists(new):
            op.drop_table(new)
        op.rename_table(old, new)


def table_exists(tbl):
    from alembic.context import get_bind

    conn = get_bind()
    ret = False
    try:
        conn.execute("select * from `%s`" % tbl)
        ret = True
    except:
        pass
    return ret


def rename_column(
    tbl, column_name, name, type_=sa.Integer, nullable=False, autoincrement=False, **kw
):
    if column_exists(tbl, column_name):
        if autoincrement:
            op.execute(
                "Alter table `%s` change `%s` `%s` int(11) NOT NULL "
                "AUTO_INCREMENT;" % (tbl, column_name, name)
            )
        else:
            op.alter_column(
                tbl,
                column_name,
                new_column_name=name,
                type_=type_,
                nullable=nullable,
                **kw,
            )


def column_exists(tbl, column_name):
    from alembic.context import get_bind

    conn = get_bind()
    ret = False
    try:
        conn.execute("select %s from %s" % (column_name, tbl))
        ret = True
    except:
        pass
    return ret


def add_column(tbl, column):
    if not column_exists(tbl, column.name):
        op.add_column(tbl, column)


def disable_constraints():
    op.execute("SET FOREIGN_KEY_CHECKS=0;")


def enable_constraints():
    op.execute("SET FOREIGN_KEY_CHECKS=1;")


def foreign_key_exists(table, fkey_name):
    """
    Check if a foreignkey exists

    :param str table:
    :param str fkey_name:
    :rtype: bool
    """
    from alembic.context import get_bind

    conn = get_bind()

    schema = conn.engine.url.database

    query = conn.execute(
        "select * from information_schema.TABLE_CONSTRAINTS where "
        "CONSTRAINT_SCHEMA='%s' and TABLE_NAME = '%s' "
        "and CONSTRAINT_NAME = '%s' AND CONSTRAINT_TYPE='FOREIGN KEY';"
        % (schema, table, fkey_name)
    )
    result = False
    if query.fetchone():
        result = True
    return result


def drop_foreign_key_if_exists(table, fkey_name):
    """
    Drop a foreignkey if it exists
    :param str table:
    :param str fkeyname:
    :returns: True if a key has been dropped
    :rtype: bool
    """
    result = foreign_key_exists(table, fkey_name)
    if result:
        op.drop_constraint(fkey_name, table, type_="foreignkey")
    return result


def index_exists(table, index_name):
    """
    Test if the index exists

    :param str table:
    :param str index_name:
    :rtype: bool
    """
    from alembic.context import get_bind

    conn = get_bind()

    schema = conn.engine.url.database

    query = conn.execute(
        "select * from information_schema.statistics where "
        "TABLE_SCHEMA='%s' and TABLE_NAME = '%s' "
        "and INDEX_NAME = '%s';" % (schema, table, index_name)
    )
    if query.fetchone():
        result = True
    else:
        result = False
    return result


def drop_index_if_exists(table, index_name):
    """
    Drop the index if it exists in the table

    :param str table:
    :param str index_name:
    :returns: True if an index has been dropped
    :rtype: bool
    """
    result = index_exists(table, index_name)
    if result:
        op.drop_index(index_name, table_name=table)
    return result


def raw_sql(sql_statement):
    """
    Run raw sql and persist it to the database
    """
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    op.execute(sql_statement)
    mark_changed(session)

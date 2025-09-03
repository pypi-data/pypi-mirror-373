import colander
from caerp.models.tva import (
    Tva,
    Product,
)


def _get_context_task(context):
    """
    Renvoie la Task associée au contexte
    """
    result = None
    if hasattr(context, "get_task"):
        result = context.get_task()
    return result


@colander.deferred
def deferred_default_tva_id(node, kw):
    """
    Collect the default tva id
    """
    context = kw["request"].context
    task = _get_context_task(context)

    if task is not None and task.internal:
        result = Tva.get_internal().id
    else:
        result = (
            kw["request"]
            .dbsession.query(Tva.id)
            .filter_by(default=True)
            .filter_by(active=True)
            .scalar()
        )
        if result is None:
            result = Tva.get_default().id

    return result


@colander.deferred
def deferred_default_product_id(node, kw):
    """
    Collect the default product id
    """
    context = kw["request"].context
    task = _get_context_task(context)
    internal = False
    if task is not None and task.internal:
        internal = True

    tva_id = deferred_default_tva_id(node, kw)

    result = (
        kw["request"]
        .dbsession.query(Product.id)
        .filter_by()
        .filter_by(active=True)
        .filter_by(tva_id=tva_id)
        .filter_by(internal=internal)
        .first()
    )

    if result:
        result = result[0]

    return result

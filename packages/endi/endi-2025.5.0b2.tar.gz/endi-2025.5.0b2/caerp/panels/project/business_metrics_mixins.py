from caerp.models.project.mixins import BusinessMetricsMixin


def business_metrics_totals(
    context,
    request,
    instance: BusinessMetricsMixin,
    tva_on_margin: bool,
):
    expense_warnings = []
    if tva_on_margin:
        """
        Nota 2025.4.0 : Modification pour retourner directement les totaux TTC car on a
        le cas d'affaires en TVA sur marge avec des achats hors UE (donc sans TVA sur
        marge) qui du coup n'afffichent plus. Jusque là on excluait exprès les dépenses
        hors TVA sur marge mais la CAE Voyage n'a pas été capable de dire pourquoi, le
        code précédent a été conservé pour revenir facilement en arrière en cas de besoin.
        """
        total_estimated = instance.get_total_estimated("ttc")
        total_income = instance.get_total_income("ttc")
        # total_expenses = instance.get_total_expenses(tva_on_margin=True)
        # total_margin = instance.get_total_margin(tva_on_margin=True)
        total_expenses = instance.get_total_expenses(mode="ttc")
        total_margin = total_income - (total_expenses * 1000)

        # if instance.get_total_expenses(tva_on_margin=False) > 0:
        #     expense_warnings.append("les dépenses hors TVA sur marge ont été ignorées")
        expense_info = "Total des dépenses TTC"

    else:
        total_estimated = instance.get_total_estimated()
        total_income = instance.get_total_income()
        total_expenses = instance.get_total_expenses()
        total_margin = instance.get_total_margin()
        expense_info = "Total des dépenses HT + TVA non déductible"

    if instance.has_nonvalid_expenses():
        expense_warnings.append("incluant des dépenses non validées")

    return {
        "mode_label": "TTC" if tva_on_margin else "HT",
        "total_estimated": total_estimated,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "total_margin": total_margin,
        "total_topay": instance.get_topay(),
        "tooltip_msg": " ; ".join([expense_info] + expense_warnings),
        "tooltip_icon": "warning" if expense_warnings else "question-circle",
    }


def includeme(config):
    config.add_panel(
        business_metrics_totals,
        "business_metrics_totals",
        renderer="caerp:templates/panels/project/business_metrics_totals.mako",
    )

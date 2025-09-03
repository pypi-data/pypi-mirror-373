"""
Main classes for statistics computation
Allows to generate and combine queries

1- Build SQLAlchemy query objects
2- Combine the result of multiple query objects to merge them python-side (this
way we avoid conflict in group/having/join clauses)

Stats are composed of
Sheets which contains Entries which are composed with Criteria

For each entry, we build a main EntryQueryFactory, which contains a
query_object that is the root of our query tree

To be able to build queries

On doit pouvoir générer des query :
    1-
    db().query(
        distinct(models.user.UserDatas.id)
    ).filter(
        models.user.UserDatas.coordonnees_lastname.startswith('tje')
    ).count()

    2- Des relations M2o
    Les objets remotes existent déjà, c'est forcément par l'id qu'on match

    db().query(
        distinct(models.user.UserDatas.id)
    ).filter(
        models.user.UserDatas.parcours_status_id.in_((1,2,3))
    ).count()

    3- Des relations o2M
    On doit passer par les attributs des objets remotes pour filtrer
    filtre sur un attribut cible :

    db().query(
        distinct(models.user.UserDatas.id)
    ).outerjoin(
        models.user.UserDatas.parcours_date_diagnostic
    ).filter(
        models.user.DateDiagnosticDatas.date<datetime.datetime.now()
    ).count()


    filtre sur deux attributs cibles :

    db().query(
        distinct(models.user.UserDatas.id), models.user.UserDatas
        ).outerjoin(
        models.user.UserDatas.statut_external_activity
        ).filter(
        models.user.ExternalActivityDatas.brut_salary>100
        ).filter(models.user.ExternalActivityDatas.hours<8).count()

TODO :
    In [3]: query = db().query(UserDatas.id).outerjoin(
        UserDatas.parcours_convention_cape)

    In [4]: query = query.group_by(UserDatas.id)

    In [5]: query = query.having(
        func.max(DateConventionCAPEDatas.date) > datetime.date.today())

    In [6]: query.count()



Cas 1 :

    Attribut de la classe UserDatas :

        String / Booléen / Date / Option Statique / ForeignKey


Cas 2 :

    Attribut d'une relation O2M :

        String / Booléen / Date / Option Statique / ForeignKey de la classe
"""


from .inspect import get_inspector
from .query_helper import (
    EntryQueryFactory,
    SheetQueryFactory,
)
from .filter_options import STATISTIC_FILTER_OPTIONS

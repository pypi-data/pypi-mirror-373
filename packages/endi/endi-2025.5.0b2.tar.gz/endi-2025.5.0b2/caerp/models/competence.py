"""
Models related to competence evaluation
"""
import datetime
import deform

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    Float,
    Date,
)
from sqlalchemy.orm import relationship
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)
from caerp.forms import (
    EXCLUDED,
    get_deferred_model_select,
    get_hidden_field_conf,
)

from caerp.models.options import (
    ConfigurableOption,
    get_id_foreignkey_col,
)


EPSILON = 0.01


class CompetenceDeadline(ConfigurableOption):
    __colanderalchemy_config__ = {
        "title": "Échéances d'évaluation",
        "validation_msg": "Les échéances ont bien été configurées",
        "help_msg": "Configurer les échéances à laquelle les compétences des \
entrepreneurs seront évaluées",
        "seq_widget_options": {
            "add_subitem_text_template": "Ajouter une échéance",
        },
    }
    id = get_id_foreignkey_col("configurable_option.id")
    requirements = relationship(
        "CompetenceRequirement",
        back_populates="deadline",
        info={
            "colanderalchemy": {"exclude": True},
        },
    )

    def __json__(self, request):
        return dict(
            id=self.id,
            label=self.label,
        )

    @classmethod
    def query(cls, *args):
        query = super(CompetenceDeadline, cls).query(*args)
        return query


class CompetenceScale(ConfigurableOption):
    __colanderalchemy_config__ = {
        "title": "Barêmes",
        "validation_msg": "Les barêmes ont bien été configurés",
        "help_msg": "Configurer les échelles d'évaluation des compétences. \
<br />Dans la grille de compétence, chaque valeur correspondra à une colonne.",
        "seq_widget_options": {
            "add_subitem_text_template": "Ajouter un niveau à l'échelle "
            "d'évaluation",
        },
    }
    id = get_id_foreignkey_col("configurable_option.id")
    value = Column(
        Float(),
        info={
            "colanderalchemy": {
                "title": "Valeur numérique",
                "description": "Valeurs utilisées comme unité dans \
les graphiques",
            }
        },
    )

    def __json__(self, request):
        return dict(
            id=self.id,
            value=self.value,
            label=self.label,
        )

    @classmethod
    def query(cls, *args):
        query = super(CompetenceScale, cls).query(*args)
        query = query.order_by(None).order_by(CompetenceScale.value)
        return query


class CompetenceOption(ConfigurableOption):
    """
    A competence model (both for the main one and the sub-competences)

    :param int required_id: The id of the bareme element needed
    """

    __table_args__ = default_table_args
    __colanderalchemy_config__ = {
        "title": "Liste des compétences",
        "seq_widget_options": {
            "add_subitem_text_template": "Ajouter une compétence",
        },
        "validation_msg": "La liste des compétences a bien été configurée",
        "help_msg": "Définissez des compétences, celles-ci sont \
composées: <ul><li>D'un libellé</li>\
<li>D'un ensemble de sous-compétences</li></ul>",
    }
    id = get_id_foreignkey_col("configurable_option.id")
    # To be removed in 3.2
    requirement = Column(
        Float(), default=0, info={"colanderalchemy": {"exclude": True}}
    )
    requirements = relationship(
        "CompetenceRequirement",
        back_populates="competence",
        info={
            "colanderalchemy": {
                "title": "Niveaux de référence pour cette compétence",
            },
        },
    )
    children = relationship(
        "CompetenceSubOption",
        primaryjoin="CompetenceOption.id==CompetenceSubOption.parent_id",
        info={
            "colanderalchemy": {
                "title": "Sous-compétences associées",
                "widget": deform.widget.SequenceWidget(
                    add_subitem_text_template="Ajouter une \
sous-compétence",
                    min_len=1,
                ),
            },
        },
        back_populates="parent",
    )

    @classmethod
    def query(cls, active=True, *args):
        query = super(CompetenceOption, cls).query(*args)
        query = query.filter_by(active=active)
        return query

    def __json__(self, request):
        return dict(
            id=self.id,
            label=self.label,
            requirements=[req.__json__(request) for req in self.requirement],
            children=[child.__json__(request) for child in self.children],
        )

    @classmethod
    def __radar_datas__(cls, deadline_id):
        result = []
        for option in cls.query():
            result.append(
                {"axis": option.label, "value": option.get_requirement(deadline_id)}
            )
        return result

    def get_requirement(self, deadline_id):
        for req in self.requirements:
            if req.deadline_id == deadline_id:
                return req.requirement
        return 0


class CompetenceSubOption(ConfigurableOption):
    __table_args__ = default_table_args
    __colanderalchemy_config__ = {"title": "Sous-compétence"}
    id = get_id_foreignkey_col("configurable_option.id")
    parent_id = Column(
        ForeignKey("competence_option.id"), info={"colanderalchemy": EXCLUDED}
    )
    parent = relationship(
        "CompetenceOption",
        primaryjoin="CompetenceOption.id==CompetenceSubOption.parent_id",
        cascade="all",
        info={"colanderalchemy": EXCLUDED},
        back_populates="children",
    )

    def __json__(self, request):
        return dict(
            id=self.id,
            label=self.label,
            parent_id=self.parent_id,
        )


class CompetenceRequirement(DBBASE):
    __colanderalchemy_config__ = {
        "title": "Niveau de référence de la grille de compétence",
        "validation_msg": "Les niveaux de référence de la grille de \
compétences ont bien été configurés",
        "help_msg": "Pour chaque compétence, définissez les niveaux de \
référence à chaque échéance.",
        "seq_widget_options": {
            "add_subitem_text_template": "Ajouter un niveau de référence",
        },
    }
    competence_id = Column(
        ForeignKey("competence_option.id"),
        primary_key=True,
        info={"colanderalchemy": get_hidden_field_conf()},
    )
    deadline_id = Column(
        ForeignKey("competence_deadline.id"),
        primary_key=True,
        info={"colanderalchemy": get_hidden_field_conf()},
    )
    requirement = Column(
        Float(),
        default=0,
        info={
            "colanderalchemy": {
                "title": "Niveau de référence",
                "widget": get_deferred_model_select(
                    CompetenceScale,
                    mandatory=True,
                    keys=("value", "label"),
                ),
            }
        },
    )

    competence = relationship(
        "CompetenceOption",
        info={
            "colanderalchemy": {"exclude": True},
        },
    )
    deadline = relationship(
        "CompetenceDeadline",
        info={
            "colanderalchemy": {"exclude": True},
        },
    )

    def __json__(self, request):
        return dict(
            deadline_id=self.deadline_id,
            competence_id=self.competence_id,
            requirement=self.requirement,
            deadline_label=self.deadline.label,
        )


class CompetenceGrid(DBBASE):
    """
    The competences grid
    """

    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)

    deadline_id = Column(ForeignKey("competence_deadline.id"))
    deadline = relationship("CompetenceDeadline")
    created_at = Column(
        Date(),
        info={
            "colanderalchemy": {
                "exclude": True,
                "title": "Créé(e) le",
            }
        },
        default=datetime.date.today,
    )

    updated_at = Column(
        Date(),
        info={
            "colanderalchemy": {
                "exclude": True,
                "title": "Mis(e) à jour le",
            }
        },
        default=datetime.date.today,
        onupdate=datetime.date.today,
    )

    contractor_id = Column(ForeignKey("accounts.id"))
    contractor = relationship("User")
    items = relationship(
        "CompetenceGridItem",
        back_populates="grid",
    )

    def ensure_item(self, competence_option):
        """
        Return the item that is used to register evaluation for the given
        competence_option

        :param obj competence_option: The competence_option object
        """
        query = CompetenceGridItem.query()
        query = query.filter_by(
            option_id=competence_option.id,
            grid_id=self.id,
        )
        item = query.first()
        if item is None:
            item = CompetenceGridItem(option_id=competence_option.id)
            self.items.append(item)
        for suboption in competence_option.children:
            item.ensure_subitem(suboption)

        return item

    def __json__(self, request):
        return dict(
            id=self.id,
            deadline_id=self.deadline_id,
            contractor_id=self.contractor_id,
            deadline_label=self.deadline.label,
            items=[item.__json__(request) for item in self.items if item.option.active],
        )

    def __radar_datas__(self):
        return [item.__radar_datas__() for item in self.items if item.option.active]


class CompetenceGridItem(DBBASE):
    """
    An item of the grid compound of two text boxes

    represented by a table
    """

    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)

    progress = Column(Text(), default="")

    option_id = Column(ForeignKey("competence_option.id"))
    option = relationship(
        "CompetenceOption",
        primaryjoin="CompetenceOption.id==CompetenceGridItem.option_id",
    )

    grid_id = Column(ForeignKey("competence_grid.id"))
    grid = relationship("CompetenceGrid")
    subitems = relationship("CompetenceGridSubItem", back_populates="item")

    def __json__(self, request):
        return dict(
            id=self.id,
            progress=self.progress,
            option_id=self.option_id,
            label=self.option.label,
            requirement=self.option.get_requirement(self.grid.deadline_id),
            grid_id=self.grid_id,
            subitems=[subitem.__json__(request) for subitem in self.subitems],
            average=self.average,
        )

    @property
    def average(self):
        """
        Return the average evaluation for this item
        """
        values = [
            subitem.evaluation
            for subitem in self.subitems
            if subitem.evaluation is not None
        ]
        if not values:
            values = [0.0]
        sum_of_values = sum(values)
        return sum_of_values / float(len(self.subitems))

    def ensure_subitem(self, competence_option):
        """
        Return a sub competence item used for the evaluation of the give
        competence option

        :param obj competence_option: The competence_option object
        """
        query = CompetenceGridSubItem.query()
        query = query.filter_by(
            option_id=competence_option.id,
            item_id=self.id,
        )
        item = query.first()
        if item is None:
            self.subitems.append(
                CompetenceGridSubItem(
                    option_id=competence_option.id,
                    item_id=self.id,
                )
            )
        return item

    def __radar_datas__(self):
        return {"axis": self.option.label, "value": self.average}

    @property
    def contractor(self):
        return self.grid.contractor


class CompetenceGridSubItem(DBBASE):
    """
    A subcompetence represented by a table line
    """

    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)

    evaluation = Column(Float(), default=None)

    option_id = Column(ForeignKey("competence_sub_option.id"))
    option = relationship("CompetenceSubOption")

    comments = Column(Text(), default="")

    item_id = Column(ForeignKey("competence_grid_item.id"))
    item = relationship("CompetenceGridItem")

    def __json__(self, request):
        return dict(
            id=self.id,
            evaluation=self.evaluation,
            option_id=self.option_id,
            label=self.option.label,
            item_id=self.item_id,
            comments=self.comments,
        )

    @property
    def scale(self):
        """
        Returns the scale matching the current evaluation value
        Since scales can be changed, we get the first scale that is <= evaluation
        """
        scales = CompetenceScale.query()
        if self.evaluation is None:
            result = scales.first()
        else:
            result = (
                scales.filter(CompetenceScale.value <= self.evaluation + EPSILON)
                .order_by(CompetenceScale.value)
                .all()[-1]
            )
        if result is None:  # No scale is lower than evaluation
            result = scales.first()
        return result

    @property
    def contractor(self):
        return self.item.grid.contractor

import logging

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
)
from sqlalchemy.sql.expression import func

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
    DBSESSION,
)
from .services import ExpenseTypeService

from caerp.forms import (
    get_hidden_field_conf,
)

logger = logging.getLogger(__name__)


class ExpenseType(DBBASE):
    """
    Base Type for expenses
    :param label: Label of the expense type that will be used in the UI
    :param code: Analytic code related to this expense
    :param type: Column for polymorphic discrimination
    """

    __colanderalchemy_config__ = {
        "title": "Configuration des types de dépenses",
        "validation_msg": "Les types de dépenses ont bien été configurés",
        "help_msg": "Configurer les types de dépenses utilisables dans \
les formulaires de saisie",
    }
    __tablename__ = "expense_type"
    __table_args__ = default_table_args
    __mapper_args__ = dict(
        polymorphic_on="type", polymorphic_identity="expense", with_polymorphic="*"
    )
    _caerp_service = ExpenseTypeService

    # frais
    EXPENSE_CATEGORY = "1"
    # achat
    PURCHASE_CATEGORY = "2"

    id = Column(
        Integer,
        primary_key=True,
    )
    type = Column(
        String(30),
        nullable=False,
    )
    active = Column(
        Boolean(),
        default=True,
    )
    label = Column(
        String(50),
        info={
            "colanderalchemy": {
                "title": "Libellé",
            }
        },
        nullable=False,
    )
    code = Column(
        String(15),
        info={
            "colanderalchemy": {
                "title": "Compte de charge de la dépense",
            }
        },
        nullable=False,
    )

    code_tva = Column(
        String(15),
        default="",
        info={
            "colanderalchemy": {
                "title": "Code TVA (si nécessaire)",
            }
        },
    )
    compte_tva = Column(
        String(15),
        default="",
        info={
            "colanderalchemy": {
                "title": "Compte de TVA déductible (si nécessaire)",
            }
        },
    )
    tva_on_margin = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {
                "title": "Fonctionne en TVA sur marge",
                "description": (
                    "Ce type de dépense relève-t-il du calcul en "
                    + "TVA sur marge ? (ex: achat de voyages, vente d'occasion)"
                ),
            }
        },
    )
    compte_produit_tva_on_margin = Column(
        String(15),
        default="",
        info={
            "colanderalchemy": {
                "title": "Compte produit pour la TVA sur marge",
                "description": "Doit être défini impérativement si on est en "
                + "mode TVA sur marge (en toute logique, un compte 7XX…). "
                + "Inutile sinon.",
            }
        },
    )
    contribution = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {
                "title": "Incluse dans la contribution",
                "description": "Ce type de dépense est-il intégré dans la \
contribution à la CAE ?",
            }
        },
    )
    internal = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {
                "title": "Spécifique à la sous-traitance interne",
                "description": "Ce type désigne des dépenses liées à des \
transactions internes à la CAE ?",
            }
        },
    )
    order = Column(
        Integer,
        nullable=False,
        default=0,
        info={"colanderalchemy": get_hidden_field_conf()},
    )
    category = Column(
        String(1),
        nullable=True,
        default=None,
        info={"colanderalchemy": {"title": "Catégorie de dépense"}},
    )

    @classmethod
    def _query_active_items(cls):
        """
        Build a query to collect active items of the current class

        :rtype: :class:`sqlalchemy.Query`
        """
        return (
            DBSESSION()
            .query(cls)
            .filter_by(type=cls.__mapper_args__["polymorphic_identity"])
            .filter_by(active=True)
        )

    @classmethod
    def insert(cls, item, new_order):
        """
        Place the item at the given index

        :param obj item: The item to move
        :param int new_order: The new index of the item
        """
        query = cls._query_active_items()
        query = query.filter_by(type=cls.__mapper_args__["polymorphic_identity"])
        items = query.filter(cls.id != item.id).order_by(cls.order).all()

        items.insert(new_order, item)

        for index, item in enumerate(items):
            item.order = index
            DBSESSION().merge(item)

    @classmethod
    def get_next_order(cls):
        """
        :returns: The next available order
        :rtype: int
        """
        query = DBSESSION().query(func.max(cls.order)).filter_by(active=True)
        query = query.filter_by(type=cls.__mapper_args__["polymorphic_identity"])
        query = query.first()
        if query is not None and query[0] is not None:
            result = query[0] + 1
        else:
            result = 0
        return result

    def move_up(self):
        """
        Move the current instance up in the category's order
        """
        order = self.order
        if order > 0:
            new_order = order - 1
            self.__class__.insert(self, new_order)

    def move_down(self):
        """
        Move the current instance down in the category's order
        """
        order = self.order
        new_order = order + 1
        self.__class__.insert(self, new_order)

    @property
    def family(self):
        if self.type == "expensetel":
            return "tel"
        elif self.type == "expensekm":
            return "km"
        else:
            return "regular"

    @property
    def is_tva_deductible(self):
        return self.compte_tva != ""

    def __json__(self, request=None):
        return {
            "id": self.id,
            "value": self.id,
            "active": self.active,
            "code": self.code,
            "label": self.display_label,
            "family": self.family,
            "is_tva_deductible": self.is_tva_deductible,
            "tva_on_margin": bool(self.tva_on_margin),
            "order": self.order,
            "category": self.category or "all",
        }

    @property
    def display_label(self):
        return "{0} ({1})".format(self.label, self.code)

    @classmethod
    def find_internal(cls):
        return cls._caerp_service.find_internal(cls)

    @classmethod
    def query(cls, *args, **kwargs):
        query = super().query(*args, **kwargs)
        return query

    @classmethod
    def get_by_label(cls, label: str, case_sensitive: bool = False):
        return cls._caerp_service.get_by_label(cls, label, case_sensitive)


class ExpenseKmType(ExpenseType):
    """
    Type of expenses related to kilometric fees
    """

    __colanderalchemy_config__ = {
        "title": "type de dépenses kilométriques",
        "validation_msg": "Les types de dépenses kilométriques ont bien été \
configurés",
        "help_msg": "Configurer les types de dépenses kilométriques \
utilisables dans les notes de dépenses",
    }
    __tablename__ = "expensekm_type"
    __table_args__ = default_table_args
    __mapper_args__ = dict(polymorphic_identity="expensekm")
    id = Column(
        Integer,
        ForeignKey("expense_type.id"),
        primary_key=True,
    )
    amount = Column(
        Float(precision=4),
        info={
            "colanderalchemy": {
                "title": "Tarif au km",
            }
        },
        nullable=False,
    )
    year = Column(
        Integer,
        nullable=True,
        info={
            "colanderalchemy": {
                "title": "Année de référence",
                "description": "Année à laquelle ce barême est associé",
            }
        },
    )

    def __json__(self, request=None):
        res = ExpenseType.__json__(self)
        res["amount"] = self.amount
        return res

    def duplicate(self, year):
        new_model = ExpenseKmType()
        new_model.amount = self.amount
        new_model.year = year
        new_model.label = self.label
        new_model.code = self.code
        new_model.code_tva = self.code_tva
        new_model.compte_tva = self.compte_tva
        new_model.contribution = self.contribution
        return new_model

    def get_by_year(self, year):
        """
        Retrieving the ExpenseKmType matching the current one but for the given
        year

        :param int year: The year the type should be attached to
        :returns: A ExpenseKmType instance
        """
        if year == self.year:
            return self
        else:
            query = ExpenseKmType.query().filter_by(year=year)
            query = query.filter_by(label=self.label)
            query = query.filter_by(code=self.code)
            return query.first()


class ExpenseTelType(ExpenseType):
    """
    Type of expenses related to telefonic fees
    """

    __colanderalchemy_config__ = {
        "title": "type de dépenses téléphoniques",
        "validation_msg": "Les types de dépenses téléphoniques ont bien été \
configurés",
        "help_msg": "Configurer les types de dépenses téléphoniques \
utilisables dans les notes de dépenses",
    }
    __tablename__ = "expensetel_type"
    __table_args__ = default_table_args
    __mapper_args__ = dict(polymorphic_identity="expensetel")
    id = Column(
        Integer,
        ForeignKey("expense_type.id"),
        primary_key=True,
    )
    percentage = Column(
        Integer,
        info={
            "colanderalchemy": {
                "title": "Pourcentage de la dépense remboursé " "à l'entrepreneur",
            }
        },
        nullable=False,
    )
    initialize = Column(
        Boolean,
        default=True,
        info={
            "colanderalchemy": {
                "title": "Créer une entrée par défaut",
                "description": "Dans le formulaire de saisie des notes de \
dépense, une ligne sera automatiquement ajouté au Frais de l'entrepreneur.",
            }
        },
    )

    def __json__(self, request=None):
        res = ExpenseType.__json__(self)
        res["percentage"] = self.percentage
        return res

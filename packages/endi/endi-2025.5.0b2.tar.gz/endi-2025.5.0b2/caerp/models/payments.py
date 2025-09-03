import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Boolean,
    String,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import (
    relationship,
)
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)
from caerp.models.options import (
    ConfigurableOption,
    get_id_foreignkey_col,
)
from caerp import forms


class PaymentModelMixin:
    """
    Common fields for payment various payment models
    """

    @declared_attr
    def mode(cls):
        return Column(String(50))

    @declared_attr
    def amount(cls):
        return Column(
            Integer,
            info={"colanderalchemy": {"title": "Montant"}},
        )

    precision = 2

    @declared_attr
    def date(cls):
        return Column(
            DateTime(),
            default=datetime.datetime.now,
            info={"colanderalchemy": {"title": "Date de remise"}},
        )

    @declared_attr
    def bank_remittance_id(cls):
        return Column(
            String(255),
            info={"colanderalchemy": {"title": "Identifiant de remise en banque"}},
            nullable=True,
        )

    @declared_attr
    def exported(cls):
        return Column(Boolean(), default=False)

    # Non-database fields

    @property
    def parent(self):
        raise NotImplementedError

    def get_amount(self):
        return self.amount


class PaymentMode(DBBASE):
    """
    Payment mode entry
    """

    __colanderalchemy_config__ = {
        "title": "Modes de paiement",
        "description": "",
        "seq_widget_options": {
            "add_subitem_text_template": "Ajouter un mode de paiement",
        },
        "help_msg": "Configurer les modes de paiement pour la saisie des \
encaissements des factures.\n Vous pouvez les réordonner par glisser-déposer.",
        "validation_msg": "Les modes de paiement ont bien été configurés",
    }
    __tablename__ = "paymentmode"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": forms.get_hidden_field_conf()},
    )
    label = Column(String(50), info={"colanderalchemy": {"title": "Libellé"}})
    order = Column(
        Integer,
        nullable=False,
        default=0,
        info={"colanderalchemy": forms.get_hidden_field_conf()},
    )

    @classmethod
    def query(cls, *args):
        query = super(PaymentMode, cls).query(*args)
        query = query.order_by("order")
        return query


class BankAccount(ConfigurableOption):
    """
    Bank accounts used for payment registry
    """

    __colanderalchemy_config__ = {
        "title": "Comptes bancaires",
        "seq_widget_options": {
            "add_subitem_text_template": "Ajouter un compte bancaire",
        },
        "validation_msg": "Les comptes bancaires ont bien été configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")
    code_journal = Column(
        String(120),
        info={
            "colanderalchemy": {
                "title": "Code journal Banque",
                "description": """Code journal utilisé pour les exports
                des encaissements et des paiements des notes de dépenses""",
            }
        },
        nullable=False,
    )
    compte_cg = Column(
        String(120),
        info={"colanderalchemy": {"title": "Compte général Banque"}},
        nullable=False,
    )
    iban = Column(
        String(35),
        info={"colanderalchemy": {"title": "IBAN"}},
        nullable=True,
    )
    bic = Column(
        String(15),
        info={"colanderalchemy": {"title": "BIC"}},
        nullable=True,
    )
    default = Column(
        Boolean(),
        default=False,
        info={"colanderalchemy": {"title": "Utiliser ce compte par défaut"}},
    )
    payments = relationship(
        "Payment",
        order_by="Payment.date",
        info={"colanderalchemy": {"exclude": True}},
    )

    @property
    def rib_bank_code(self):
        # code établissement du RIB
        if self.iban:
            return self.iban[4:9]
        else:
            return ""

    @property
    def rib_bank_office(self):
        # code guichet du RIB
        if self.iban:
            return self.iban[9:14]
        else:
            return ""

    @property
    def rib_account_number(self):
        # numéro de compte du RIB
        if self.iban:
            return self.iban[14:-2]
        else:
            return ""

    @property
    def rib_account_key(self):
        # clé du RIB
        if self.iban:
            return self.iban[-2:]
        else:
            return ""


class Bank(ConfigurableOption):
    """
    Third parties bank list
    """

    __colanderalchemy_config__ = {
        "title": "Banques clients",
        "seq_widget_options": {
            "add_subitem_text_template": "Ajouter une banque",
        },
        "validation_msg": "Les banques clients ont bien été configurés",
    }
    id = get_id_foreignkey_col("configurable_option.id")

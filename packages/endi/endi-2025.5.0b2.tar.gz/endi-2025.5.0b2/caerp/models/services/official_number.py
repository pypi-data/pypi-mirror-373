import logging
import string
from typing import Dict

from pyramid_retry import RetryableException
from caerp_base.models.mixins import OfficialNumberMixin

from caerp.models.sequence_number import SequenceNumber
from caerp.utils.strings import get_keys_from_template

logger = logging.getLogger(__name__)

ALLOWED_VARS = ["YYYY", "YY", "MM", "ANA"]

# Âge maximum du lock pour la numérotation des factures, au-delà on considère
# qu'il y a eu un problème lors du release
LOCK_TIMEOUT = 180


class LockException(RetryableException):
    pass


class OfficialNumberFormatter(string.Formatter):
    """
    str.format()-like but with custom vars to allow applying an node number
    template. containing vars and sequence numbers.
    """

    def __init__(self, node, sequences_map):
        self._node = node
        self._sequences_map = sequences_map

    def _get_var_value(self, key):
        if key == "YYYY":
            return "{:%Y}".format(self._node.validation_date)
        elif key == "YY":
            return "{:%y}".format(self._node.validation_date)
        elif key == "MM":
            return "{:%m}".format(self._node.validation_date)
        elif key == "ANA":
            return "{}".format(self._node.company.code_compta)

    def _get_seq_value(self, key):
        return self._sequences_map[key].get_next_index(self._node)

    def get_value(self, key, args, kwargs):
        if key in ALLOWED_VARS:
            return self._get_var_value(key)
        elif key in self._sequences_map:
            return self._get_seq_value(key)
        else:
            return super().get_value(key, args, kwargs)


class AbstractNumberService:
    """
    Expose a method to assign templated and unique numbers to a class instance

    Must be implemented once per document type (OfficialNumberMixin child
    class) that needs its own numbering scheme.
    """

    lock_name = None

    @classmethod
    def get_sequences_map(cls) -> Dict[str, SequenceNumber]:
        """
        returns: must include following keys : 'SEQGLOBAL', 'SEQYEAR',
          'SEQMONTH', 'SEQMONTHANA'
        """
        raise NotImplementedError

    @classmethod
    def sequences_map(cls):
        """
        Memoized on first call ; this is to avoid import loops.
        """
        # @property with @classmethod is only suported since Python 3.9
        # Meanwhile, we use a @classmethod only
        if not hasattr(cls, "_sequences_map"):
            cls._sequences_map = cls.get_sequences_map()
        return cls._sequences_map

    @classmethod
    def allowed_keys(cls):
        # @property with @classmethod is only suported since Python 3.9
        # Meanwhile, we use a @classmethod only
        return ALLOWED_VARS + list(cls.sequences_map().keys())

    @classmethod
    def _validate_variable_names(cls, tpl_vars):
        for key in tpl_vars:
            if key is not None and key not in cls.allowed_keys():
                raise ValueError(
                    "{{{}}} n'est pas une clef valide (disponibles : {})".format(
                        key,
                        ", ".join("{{{}}}".format(i) for i in cls.allowed_keys()),
                    )
                )

    @classmethod
    def _vars_ensure_unicity(cls, var_names):
        """
        Test if the given template vars ensures number uniqueness

        :param list var_names: The list of variables
        :rtype: bool
        """

        def has(var_name):
            return var_name in var_names

        reqs = [
            ["SEQGLOBAL", True],
            ["SEQYEAR", has("YYYY") or has("YY")],
            ["SEQMONTH", (has("YYYY") or has("YY")) and has("MM")],
            [
                "SEQMONTHANA",
                (has("YYYY") or has("YY")) and has("MM") and has("ANA"),
            ],
        ]
        unicity = False
        for var_name, req in reqs:
            if var_name in var_names and req:
                unicity = True
        return unicity

    @classmethod
    def _validate_generated_nums_uniqueness(cls, tpl_vars):
        """
        Check the given tpl_vars ensure uniqueness

        :raises ValueError: When the vars doesn't ensure uniqueness
        """
        unicity = cls._vars_ensure_unicity(tpl_vars)

        if not unicity:
            raise ValueError("Ce gabarit produit des numéros non uniques.")

    @classmethod
    def validate_template(cls, template):
        """
        Validate the correctness of the invoice number template
        """
        try:
            tpl_vars = get_keys_from_template(template)
        except ValueError as e:
            raise ValueError(
                f'Erreur dans la syntaxe du gabarit (accolade non refermée ?). Erreur brute : "{str(e)}"'
            )
        else:
            cls._validate_variable_names(tpl_vars)
            cls._validate_generated_nums_uniqueness(tpl_vars)

    @classmethod
    def get_involved_sequences(cls, invoice, template):
        """
        Tell which sequences are to be used and what indexes they will give

        :returns: the sequences that would be used by this template and their
           next index
        :rtype: list of couples [<sequence>, <sequence_number>, <sequence_key>]
        """
        out = []
        used_sequences = set()  # to avoid duplicates in out
        tpl_vars = get_keys_from_template(template)

        for key in tpl_vars:
            if key in cls.sequences_map():

                seq = cls.sequences_map()[key]
                if seq not in used_sequences:
                    out.append(
                        [
                            seq,
                            seq.get_next_index(invoice),
                            seq.get_key(invoice),
                        ]
                    )
                    used_sequences.add(seq)

        return out

    @classmethod
    def assign_number(cls, request, node: OfficialNumberMixin, template):
        """
        This function should be run within an SQL transaction to enforce
        sequence index unicity.
        """
        if node.official_number:
            raise ValueError("This node already have an official number")

        import caerp
        from caerp_celery.tasks.utils import check_alive
        from caerp_celery.locks import is_locked, acquire_lock
        from caerp_celery.tasks.locks import release_lock_after_commit

        use_lock = cls.lock_name and not caerp._called_from_test
        if use_lock:
            # On teste si celery est dispo, on ne veut pas bloquer la validation
            use_lock = check_alive()[0]

        if use_lock and is_locked(cls.lock_name, LOCK_TIMEOUT):
            logger.error(f"Lock {cls.lock_name} is already acquired")
            raise LockException(f"Lock {cls.lock_name} is already acquired")

        if use_lock:
            acquire_lock(cls.lock_name)

        formatter = OfficialNumberFormatter(node, cls.sequences_map())
        official_number = formatter.format(template)

        involved_sequences = cls.get_involved_sequences(node, template)

        # Create SequenceNumber objects (the index useages have not been
        # booked until now).
        for sequence, next_index, key in involved_sequences:
            sn = SequenceNumber(
                sequence=sequence.db_key,
                index=next_index,
                node_id=node.id,
                key=key,
            )
            request.dbsession.add(sn)
        node.official_number = official_number
        request.dbsession.merge(node)
        # Only check for nodes using this number if the current
        # node number template should ensure unicity
        tpl_vars = get_keys_from_template(template)

        if cls._vars_ensure_unicity(tpl_vars):
            cls._ensure_not_used(request, node.id, official_number)
        if use_lock:
            release_lock_after_commit.delay(cls.lock_name)
        return official_number

    @classmethod
    def _ensure_not_used(cls, request, node_id, official_number):
        result = cls.is_already_used(request, node_id, official_number)
        if result:
            # This case is exceptionnal, we can afford a crash here
            # Context manager will take care of rolling back
            # subtransaction.
            raise RetryableException(
                f"Official number collision {official_number} rolling back to avoid it."
            )

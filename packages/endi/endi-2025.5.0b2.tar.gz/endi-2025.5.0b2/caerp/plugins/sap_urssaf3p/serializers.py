"""
Serializers pour se mapper sur les modèles de données de l'URSSAF API Tiers de Paiement

On utilise les schémas colander pour faire la sérialization.
Cela présente des limites, par exemple dans le sens « sérialisation », les
validateurs ne sont pas appliqués.


spec suivie :
https://portailapi.urssaf.fr/index.php?option=com_apiportal&view=apitester&usage=api&apitab=tests&apiName=API+Tiers+de+prestations&apiId=0c533e48-daa7-4e50-ae5a-c0afe41cc061&managerId=1&type=rest&apiVersion=1.30.3&menuId=181&renderTool=2&Itemid=181
"""
import logging
from copy import deepcopy
import re
from decimal import (
    Decimal,
    ROUND_UP,
    ROUND_DOWN,
)
from caerp.utils.compat import Iterable
from typing import Union

import colander
from unidecode import unidecode

from caerp.compute import math_utils
from caerp.models.config import Config
from caerp.models.task import (
    Invoice,
    TaskLine,
)
from caerp.models.third_party import Customer
from caerp.utils.strings import is_hours
from caerp.plugins.sap_urssaf3p.models.customer import UrssafCustomerData


logger = logging.getLogger(__name__)


class ActualFloat(colander.Float):
    """
    colander serialize the number back to str. Lets revert to number.
    """

    def serialize(self, node, appstruct):
        ret = super().serialize(node, appstruct)
        if isinstance(ret, str):
            return float(ret)
        else:
            return appstruct


class URSSAFDateTime(colander.DateTime):
    """
    URSSAF only supports a subset of ISO8601 syntax

    Eg. for Timezone, the presence of the UTC zulu marker (final Z) seems mandatory.
    """

    RE_NUMERIC_UTC_SHIFT = re.compile(r"\+\d\d:\d\d$")

    def serialize(self, node, appstruct):
        out = super().serialize(node, appstruct)
        if self.RE_NUMERIC_UTC_SHIFT.search(out):
            out = self.RE_NUMERIC_UTC_SHIFT.sub("Z", out)
        return out


class URSSAFASCIIString(colander.String):
    """
    URSSAF string with very limited charset

    Described by URSSAF as:
    - ne doit pas comporter de chiffres, ni de caractères spéciaux à l’exception de l’apostrophe (‘), du tiret (-) et de l’espace ( ).
    - ne doit ni commencer ni finir par un caractère spécial.",

    Serialization will take care of removing/replacing everything not matching that.
    """

    INVALID_BODY_CHAR = re.compile(r"[^A-z'\- ]")
    INVALID_START_CHARS = re.compile(r"^[^A-z]+")
    INVALID_END_CHARS = re.compile(r"[^A-z]+$")

    def serialize(self, node, appstruct: Union[str, None]):
        out = appstruct
        if out:
            # Eg: é -> e
            out = unidecode(appstruct)
            # replace other specials
            # Eg: "?" -> " "
            out = self.INVALID_BODY_CHAR.sub(" ", out)
            # Remove forbidden start/end
            out = self.INVALID_START_CHARS.sub("", out)
            out = self.INVALID_END_CHARS.sub("", out)

        return super().serialize(node, out)


def _is_dom_com(code_commune_insee: str):
    return code_commune_insee[:2] in ("97", "98")


def _urssaf_code_commune(code_commune_insee: str) -> str:
    """
    For birthplace, URSSAF uses only the right part of the code commune.

    :param code_commune_insee: un code commune au sens de l'INSEE

    Includes a workaround ; quote from URSSAF support :

    > Pour ce qui est du contournement, vous pouvez remplacer le premier chiffre du codeCommune par 0.
    > Pour l’exemple de Saint Denis de la réunion : le code INSEE est 97411, en théorie il faudrait indiquer codeCommune : 411 & departementNaissance : 974, or ce n’est pas le cas.
    > Pour contourner l'anomalie (en cours de correction), veuillez indiquer codeCommune : 011 (remplacer le premier chiffre par 0) & departementNaissance : 974

    >>> _urssaf_code_commune("97411")
    '011'
    >>> _urssaf_code_commune("77288")
    '288'
    """
    if _is_dom_com(code_commune_insee):
        # zero-pad (workaround, may be dropped at some point if urssaf API evolve)
        return f"0{code_commune_insee[3:]}"
    else:
        return code_commune_insee[2:]


def _urssaf_code_departement(code_departement_insee: str):
    """
    A department code, formated the URSSAF way
    cer le premier chiffre par 0) & departementNaissance : 974

    >>> _urssaf_code_departement("97411")
    '974'
    >>> _urssaf_code_departement("77288")
    '077'
    """
    if _is_dom_com(code_departement_insee):
        # zero-pad (workaround, may be dropped at some point if urssaf API evolve)
        return code_departement_insee[:3]
    else:
        return f"{code_departement_insee[:2]:0>3}"


class CaerpDecimalRepresentation(colander.SchemaType):
    """
    Serialize an enDi decimal-as-integer to JS Number with two decimals
    """

    def __init__(self, *args, **kwargs):
        self.precision = kwargs.pop("precision", 2)
        super().__init__(*args, **kwargs)

    def serialize(self, node, appstruct: int):
        as_float = math_utils.integer_to_amount(appstruct, default=0, precision=5)
        return math_utils.round(as_float, precision=self.precision)


class URSSAFWorkUnit(colander.String):
    """
    Sérialize une unité au sens caerp vers l'unité au sens URSSAF
    """

    def serialize(self, node, appstruct: str):
        """
        :param appstruct: une unité de prestation au sens enDi du terme
        :return: one of "HEURE" or "FORFAIT"
        """
        if is_hours(appstruct):
            out = "HEURE"
        else:
            out = "FORFAIT"
        return super().serialize(node, out)


class URSSAFCivilite(colander.String):
    map = {
        "Monsieur": "1",
        "Madame": "2",
    }

    def serialize(self, node, appstruct: str):
        assert appstruct in self.map, "Unknown URSSAF civilite, {appstruct}"
        return super().serialize(node, self.map[appstruct])


class InputPrestationSchema(colander.MappingSchema):
    """Serializer for URSSAF InputPrestationSerializer

    InputPrestationSerializer as described from v1.30.3 is bellow
    {
      "type" : "object",
      "required" : [
         "codeNature",
         "mntPrestationHT",
         "mntPrestationTTC",
         "mntPrestationTVA",
         "mntUnitaireTTC",
         "quantite",
         "unite"
      ],
      "properties" : {
        "codeActivite" : {
          "type" : "string",
          "example" : "01",
          "description" : "Code d'activité lié à la nature de l'emploi"
        },
        "codeNature" : {
          "type" : "string",
          "example" : "ENF",
          "description" : "Code nature qui correspond aux natures d'emploi définit pas le code du travail (article D7231-1)"
        },
        "quantite" : {
          "type" : "number",
          "example" : 1.75,
          "description" : "Nombre d'unitée pour cette prestation."
        },
        "unite" : {
          "type" : "string",
          "example" : "HEURE",
          "description" : "Correspond à l'unité de la prestation effectuée. Peut avoir deux valeurs : 'HEURE' si la prestation correspond à un nombre d'heures effectuées ou 'FORFAIT' s'il s'agit d'un forfait."
        },
        "mntUnitaireTTC" : {
          "type" : "number",
          "example" : 20.0,
          "title" : "Montant du prix unitaire de la prestation."
        },
        "mntPrestationTTC" : {
          "type" : "number",
          "example" : 120.0,
          "title" : "Montant TTC de cette prestation =  mntUnitaireTTC x quantite"
        },
        "mntPrestationHT" : {
          "type" : "number",
          "example" : 100.0,
          "title" : "Montant Hors Taxes de cette prestation"
        },
        "mntPrestationTVA" : {
          "type" : "number",
          "example" : 20.0,
          "title" : "Montant des Taxes pour cette prestation"
        },
        "dateDebutEmploi" : {
          "type" : "string",
          "format" : "date",
          "example" : "2019-11-01T00:00:00Z",
          "title" : "Date de début  de cette prestation."
        },
        "dateFinEmploi" : {
          "type" : "string",
          "format" : "date",
          "example" : "2019-11-30T00:00:00Z",
          "title" : "Date de fin  de cette  prestation de la demande de paiement."
        },
        "complement1" : {
          "type" : "string",
          "example" : "Complément 1 ",
          "title" : "Contenu informatif concernant cette prestation."
        },
        "complement2" : {
          "type" : "string",
          "example" : "Complément 2 ",
          "title" : "Contenu informatif concernant cette prestation."
        }
      }
    },
    """

    # Only mandatory fields are implemented for now
    codeNature = colander.SchemaNode(colander.String())
    mntPrestationHT = colander.SchemaNode(CaerpDecimalRepresentation())
    mntPrestationTTC = colander.SchemaNode(CaerpDecimalRepresentation())
    mntPrestationTVA = colander.SchemaNode(CaerpDecimalRepresentation())
    mntUnitaireTTC = colander.SchemaNode(CaerpDecimalRepresentation(precision=3))
    quantite = colander.SchemaNode(ActualFloat())
    unite = colander.SchemaNode(URSSAFWorkUnit())
    complement2 = colander.SchemaNode(colander.String())

    def to_appstruct(self, task_line: TaskLine) -> dict:

        qte = task_line.quantity
        total_ht = math_utils.floor_to_precision(task_line.total_ht())
        if task_line.mode == "ttc":
            unit_ttc = math_utils.floor_to_precision(task_line.unit_ttc(), precision=3)
            total_ttc = math_utils.floor_to_precision(unit_ttc * qte)
        else:
            total_ttc = math_utils.floor_to_precision(task_line.total())
            unit_ttc = math_utils.floor_to_precision(
                total_ttc / qte if qte != 0 else 0, precision=3
            )
        total_tva = total_ttc - total_ht

        return dict(
            codeNature=task_line.product.urssaf_code_nature,
            mntPrestationHT=total_ht,
            mntPrestationTTC=total_ttc,
            mntPrestationTVA=total_tva,
            mntUnitaireTTC=unit_ttc,
            quantite=qte,
            unite=task_line.unity,
            complement2="SIR{}".format(
                Config.get_value("cae_business_identification", "").replace(" ", "")
            ),
        )

    def serialize_task_line(self, task_line: TaskLine) -> dict:
        """
        :return: cstruct
        """
        out = self.serialize(self.to_appstruct(task_line))

        unit_ttc = out["mntUnitaireTTC"]
        ttc = out["mntPrestationTTC"]
        qty = out["quantite"]

        if math_utils.round(unit_ttc * qty, precision=2) != ttc:
            logger.warning(
                f"Possible rounding issue with {task_line.task.official_number},"
                " as {unit_ttc} x {qty} ≠ {ttc} "
                "URSSAF API may reject it. "
                "Possible solution if so: use less decimals or use TTC mode."
            )
        return out


class InputPrestationSequenceSchema(colander.SequenceSchema):
    prestation = InputPrestationSchema()

    def to_appstruct(self, lines: Iterable[TaskLine]) -> list:
        return [self["prestation"].to_appstruct(i) for i in lines]

    def serialize_task_lines(self, lines: Iterable[TaskLine]) -> list:
        return self.serialize(self.to_appstruct(lines))


class InputDemandePaiementSchema(colander.MappingSchema):
    """Serializer for URSSAF InputDemandePaiementSerializer

    InputDemandePaiementSerializer as described from v1.30.3 is bellow
    {
        "type": "object",
        "required": [
            "dateDebutEmploi",
            "dateFacture",
            "dateFinEmploi",
            "dateNaissanceClient",
            "idClient",
            "idTiersFacturation",
            "inputPrestations",
            "mntFactureHT",
            "mntFactureTTC",
            "numFactureTiers"
        ],
        "properties": {
            "idTiersFacturation": {
                "type": "string",
                "example": "1081230",
                "title": "Identifiant du tiers de prestation qui recevra le paiement, identifiant SI ."
            },
            "idClient": {
                "type": "string",
                "example": "11000000000104",
                "title": "Identifiant du client du tiers de prestation, identifiant SI ."
            },
            "dateNaissanceClient": {
                "type": "string",
                "format": "date",
                "example": "1986-11-30T00:00:00Z",
                "title": "Date de naissance du client du tiers de prestation. Utilisé pour vérifier la cohérence des informations."
            },
            "numFactureTiers": {
                "type": "string",
                "example": "11000000000104",
                "title": "Numéro de la facture, identifiant SI Tiers de prestation. ."
            },
            "dateFacture": {
                "type": "string",
                "format": "date",
                "example": "2019-12-01T00:00:00Z",
                "title": "Date à laquelle la facture a été émise par le partenaire."
            },
            "dateDebutEmploi": {
                "type": "string",
                "format": "date",
                "example": "2019-11-01T00:00:00Z",
                "title": "Date de début  de la première prestation de la demande de paiement."
            },
            "dateFinEmploi": {
                "type": "string",
                "format": "date",
                "example": "2019-11-30T00:00:00Z",
                "title": "Date de fin  de la dernière prestation de la demande de paiement."
            },
            "mntAcompte": {
                "type": "number",
                "example": 100,
                "title": "Montant de l'acompte que le client aurait pu verser au tiers de prestation"
            },
            "dateVersementAcompte": {
                "type": "string",
                "format": "date",
                "example": "2019-11-25T00:00:00Z",
                "title": "Date à laquelle le client aurait pu verser un acompte au tiers de prestation."
            },
            "mntFactureTTC": {
                "type": "number",
                "example": 2000,
                "title": "Montant total de la facture Toutes Taxes Comprises."
            },
            "mntFactureHT": {
                "type": "number",
                "example": 1800,
                "title": "Montant total de la facture Hors Taxes."
            },
            "inputPrestations": {
                "type": "array",
                "description": "Listes des prestations effectuées pour cette demande de paiement pour ce client.",
                "items": {
                    "$ref": "#/definitions/InputPrestation"
                }
            }
        }
    }
    """

    # Only mandatory fields are implemented for now
    dateDebutEmploi = colander.SchemaNode(URSSAFDateTime())
    dateFacture = colander.SchemaNode(URSSAFDateTime())
    dateFinEmploi = colander.SchemaNode(URSSAFDateTime())
    dateNaissanceClient = colander.SchemaNode(URSSAFDateTime())
    idClient = colander.SchemaNode(colander.String())
    # idTiersFacturation hardcodé, à virer un jour.
    #
    # Selon l'URSSAF :
    # > Le champ est actuellement obligatoire dans le contrat de service de
    # l’API mais n’a pas vocation a être renseigné lors de l’appel à l’API. Le
    # temps que le swagger de l’API soit mise à jour, il est alors nécessaire
    # de saisir une valeur aléatoire tel que « menage.fr »
    idTiersFacturation = colander.SchemaNode(colander.String(), default="enDI")
    inputPrestations = InputPrestationSequenceSchema()
    mntFactureHT = colander.SchemaNode(CaerpDecimalRepresentation())
    mntFactureTTC = colander.SchemaNode(CaerpDecimalRepresentation())
    numFactureTiers = colander.SchemaNode(colander.String())

    def serialize_invoice(self, invoice: Invoice):
        serialized = self.serialize(
            dict(
                dateDebutEmploi=invoice.min_lines_date(),
                dateFinEmploi=invoice.max_lines_date(),
                dateFacture=invoice.date,
                dateNaissanceClient=invoice.customer.urssaf_data.birthdate,
                idClient=invoice.customer.urssaf_data.client_id,
                inputPrestations=self["inputPrestations"].to_appstruct(
                    invoice.all_lines
                ),
                mntFactureHT=invoice.total_ht(),
                mntFactureTTC=invoice.total_ttc(),
                numFactureTiers=invoice.official_number,
            )
        )
        return fix_tva_rounding(serialized)


class InputCommuneDTO(colander.MappingSchema):
    """
    {
      "type" : "object",
      "required" : [ "codeCommune" ],
      "properties" : {
        "codeCommune" : {
          "type" : "string",
          "example" : "001",
          "description" : "Code INSEE de la commune de naissance, 3 caractères numériques (DOM), 2 caractères numériques (TOM) (cf nomenclature INSEE). Obligatoire. Aucun contrôle n'est effectué  sur l'existence du code. La validité de l'information est de la responsabilité du tiers de prestation.",
          "minLength" : 3,
          "maxLength" : 3,
          "pattern" : "^[0-9]{3}$"
        },
        "libelleCommune" : {
          "type" : "string",
          "example" : "Lyon",
          "description" : "Libellé de la commune de naissance. Facultatif. Aucun contrôle n'est effectué  sur l'existence du libellé. La validité de l'information est de la responsabilité du tiers de prestation.",
          "minLength" : 1,
          "maxLength" : 50
        }
      }
    }
    """

    codeCommune = colander.SchemaNode(colander.String())
    libelleCommune = colander.SchemaNode(colander.String())

    def serialize_sap_customer_data(self, urssaf_data: UrssafCustomerData):
        # Used for birthplace
        return self.serialize(
            dict(
                # part of insee code : 80899 -> 899
                codeCommune=_urssaf_code_commune(urssaf_data.birthplace_city_code),
                libelleCommune=urssaf_data.birthplace_city,
            )
        )


class InputLieuNaissancoDTOSchema(colander.MappingSchema):
    """
    {
      "type": "object",
      "required": [
        "codePaysNaissance"
      ],
      "properties": {
        "codePaysNaissance": {
          "type": "string",
          "example": "99100",
          "description": "Code INSEE du pays sur 5 caractères numériques (cf nomenclature INSEE). Obligatoire",
          "minLength": 5,
          "maxLength": 5,
          "pattern": "^[0-9]{5}$"
        },
        "departementNaissance": {
          "type": "string",
          "example": "069",
          "description": "Code INSEE du département à la date de naissance ou TOM (si pays = France) Format : 3 caractères alphanumériques : 001, 040, 976. 02B pour le département de Haute-Corse. Précision : cette donnée est obligatoire si et seulement si le code Pays de naissance correspond à celui de la France. Facultatif",
          "minLength": 3,
          "maxLength": 3,
          "pattern": "^[09][0-9][0-9abAB]$"
        },
        "communeNaissance": {
          "description": "Commune de naissance. Précision : cette donnée est obligatoire si et seulement si le code Pays de naissance correspond à celui de la France. Facultatif",
          "$ref": "#/definitions/InputCommuneDTO"
        }
      }
    }
    """

    codePaysNaissance = colander.SchemaNode(colander.String())
    departementNaissance = colander.SchemaNode(colander.String(), default=colander.drop)
    communeNaissance = InputCommuneDTO(default=colander.drop)

    def serialize_sap_customer_data(self, urssaf_data: UrssafCustomerData):
        if urssaf_data.birthplace_country_code == "99100":  # FRANCE
            data = dict(
                codePaysNaissance=urssaf_data.birthplace_country_code,
                communeNaissance=self["communeNaissance"].serialize_sap_customer_data(
                    urssaf_data
                ),
                # part of insee code, padded : 80899 -> 080
                departementNaissance=_urssaf_code_departement(
                    urssaf_data.birthplace_city_code
                ),
            )
        else:
            data = dict(
                codePaysNaissance=urssaf_data.birthplace_country_code,
            )

        return self.serialize(data)


class InputCoordonneeBancaireDTOSchema(colander.MappingSchema):
    """
    {
      "type" : "object",
      "required" : [ "bic", "iban", "titulaire" ],
      "properties" : {
        "bic" : {
          "type" : "string",
          "example" : "BNAPFRPPXXX",
          "description" : "Identifiant BIC. Obligatoire. Le BIC est constitué : d’un code banque sur 4 caractères, d’un code pays (ISO 3166) sur 2 caractères, d’un code emplacement sur 2 caractères, d’un code branche, optionnel, sur 3 caractères. Celui-ci peut être facultativement complété avec trois X pour que le BIC soit sur 11 caractères",
          "minLength" : 8,
          "maxLength" : 11,
          "pattern" : "^[a-zA-Z]{6}[0-9a-zA-Z]{2}([0-9a-zA-Z]{3})?$"
        },
        "iban" : {
          "type" : "string",
          "example" : "FR7630006000011234567890189",
          "description" : "identifiant IBAN. Obligatoire. L’IBAN est constitué : d’un code pays (ISO 3166) sur 2 caractères,d’une clé de contrôle sur 2 caractères, permettant de s’assurer de l’intégrité du compte, d’un BBAN sur 14 à 34 caractères (23 caractères pour les comptes français (ancien format du RIB))",
          "minLength" : 18,
          "maxLength" : 38,
          "pattern" : "^[a-zA-Z]{2}[0-9]{2}[a-zA-Z0-9]{4}[0-9]{7}([a-zA-Z0-9]?){0,16}$"
        },
        "titulaire" : {
          "type" : "string",
          "example" : "Mme Jeanne Martin",
          "description" : "titulaire du compte, civilité, nom et prénom. Obligatoire",
          "minLength" : 1,
          "maxLength" : 100
        }
      }
    }
    """

    bic = colander.SchemaNode(colander.String())
    iban = colander.SchemaNode(colander.String())
    titulaire = colander.SchemaNode(colander.String())

    def serialize_customer(self, customer: Customer):
        return self.serialize(
            dict(
                bic=customer.bank_account_bic,
                iban=customer.bank_account_iban,
                titulaire=customer.bank_account_owner,
            )
        )


class InputAdresseDTOSchema(colander.MappingSchema):
    """
    {
      "type" : "object",
      "required" : [ "codeCommune", "codePays", "codePostal", "libelleCommune" ],
      "properties" : {
        "numeroVoie" : {
          "type" : "string",
          "example" : "8",
          "description" : "Numéro de la voie. Facultatif",
          "maxLength" : 20,
          "pattern" : "^(?!^0$)([0-9]){0,20}$"
        },
        "lettreVoie" : {
          "type" : "string",
          "example" : "B",
          "description" : "Lettre associée au numéro de voie (B pour Bis, T pour Ter, Q pour Quater, C pour Quinquiès). Facultatif",
          "maxLength" : 1
        },
        "codeTypeVoie" : {
          "type" : "string",
          "example" : "R",
          "description" : "Code type de voie. Facultatif. 4 caratères alphanumeriques maximum.",
          "maxLength" : 4,
          "pattern" : "^([0-9A-Za-z]){0,4}$"
        },
        "libelleVoie" : {
          "type" : "string",
          "example" : "du Soleil",
          "description" : "Nom de la voie. Facultatif",
          "maxLength" : 28
        },
        "complement" : {
          "type" : "string",
          "example" : "Batiment A",
          "description" : "Complément d'adresse. Facultatif",
          "maxLength" : 38
        },
        "lieuDit" : {
          "type" : "string",
          "example" : "Le Beyssat",
          "description" : "Lieu-dit. Facultatif",
          "maxLength" : 38
        },
        "libelleCommune" : {
          "type" : "string",
          "example" : "LYON 01",
          "description" : "Libelle de la commune. Obligatoire. Précision : les libellés attendus sont ceux du code officiel géographique INSEE. Aucun contrôle n'est effectué sur le libellé. La validité de l'information est de la responsabilité du tiers de prestation.",
          "minLength" : 1,
          "maxLength" : 50
        },
        "codeCommune" : {
          "type" : "string",
          "example" : "69101",
          "description" : "Code INSEE de la commune (cf nomenclature INSEE). Obligatoire. Aucun contrôle n'est effectué  sur l'existence du code. La validité de l'information est de la responsabilité du tiers de prestation.",
          "minLength" : 5,
          "maxLength" : 5,
          "pattern" : "^[0-9][0-9a-bA-B][0-9]{3}$"
        },
        "codePostal" : {
          "type" : "string",
          "example" : "69001",
          "description" : "Code postal de la commune (exemple : 75001 pour Paris 1er arrondissement). Obligatoire",
          "minLength" : 5,
          "maxLength" : 5,
          "pattern" : "^[0-9]{5}$"
        },
        "codePays" : {
          "type" : "string",
          "example" : "99100",
          "description" : "Code INSEE du pays sur 5 caractères numériques (cf nomenclature INSEE). Obligatoire. Aucun contrôle n'est effectué  sur l'existence du code. La validité de l'information est de la responsabilité du partenaire.",
          "minLength" : 5,
          "maxLength" : 5,
          "pattern" : "^[0-9]{5}$"
        }
      }
    """

    codeCommune = colander.SchemaNode(colander.String())
    libelleCommune = colander.SchemaNode(colander.String())
    # Do not support non-french adress for a prestation
    codePays = colander.SchemaNode(colander.String(), default="99100")
    codePostal = colander.SchemaNode(colander.String())

    # One of those three is required
    # 1.
    complement = colander.SchemaNode(colander.String())
    # 2.
    lieuDit = colander.SchemaNode(colander.String())
    # 3.
    numeroVoie = colander.SchemaNode(colander.String())
    lettreVoie = colander.SchemaNode(colander.String())
    codeTypeVoie = colander.SchemaNode(colander.String())
    libelleVoie = colander.SchemaNode(colander.String())

    def serialize_customer(self, customer: Customer):
        return self.serialize(
            dict(
                codeCommune=customer.city_code,
                libelleCommune=customer.city,
                codePays=customer.country_code,
                codePostal=customer.zip_code,
                complement=customer.additional_address,
                lieuDit=customer.urssaf_data.lieu_dit,
                codeTypeVoie=customer.urssaf_data.street_type,
                libelleVoie=customer.urssaf_data.street_name,
                numeroVoie=customer.urssaf_data.street_number,
                lettreVoie=customer.urssaf_data.street_number_complement,
            )
        )


class InputParticulierDTOSchema(colander.MappingSchema):
    """
    {
        "type": "object",
        "required": [
            "adresseMail",
            "adressePostale",
            "civilite",
            "coordonneeBancaire",
            "dateNaissance",
            "lieuNaissance",
            "nomNaissance",
            "numeroTelephonePortable",
            "prenoms"
        ],
        "properties": {
            "civilite": {
                "type": "string",
                "example": "\"1\"",
                "description": "Civilite du client, valeurs possibles : 1 = masculin (Monsieur) ou 2 = féminin (Madame). Obligatoire",
                "enum": [
                    "1",
                    "2"
                ]
            },
            "nomNaissance": {
                "type": "string",
                "example": "Durand",
                "description": "Nom de naissance du client. 100 caractères maximum.  Obligatoire. Le nom ne doit pas comporter de chiffres, ni de caractères spéciaux à l’exception de l’apostrophe (‘), du tiret (-) et de l’espace ( ). Il ne doit ni commencer ni finir par un caractère spécial.",
                "minLength": 1,
                "maxLength": 80,
                "pattern": "^[\\pL]+(([\\pL'\\- ])*)+([\\pL])|(^[\\pL])$"
            },
            "nomUsage": {
                "type": "string",
                "example": "Martin",
                "description": "Nom d'usage du client. Facultatif si n’est pas différent du nom de naissance, attendu si différent. Le nom ne doit pas comporter de chiffres, ni de caractères spéciaux à l’exception de l’apostrophe (‘), du tiret (-) et de l’espace ( ). Il ne doit ni commencer ni finir par un caractère spécial.",
                "maxLength": 80,
                "pattern": "^[\\pL]+(([\\pL'\\- ])*)+([\\pL])|(^[\\pL])$"
            },
            "prenoms": {
                "type": "string",
                "example": "Eric-Antoine Derc'hen Jean alain",
                "description": "Les prenoms du client séparés par un espace. Il est attendu les prénoms d’usage du particulier s’il s’agit de prénom composé, le premier prénom sinon. Obligatoire. Le prénom ne doit pas comporter de chiffres, ni de caractères spéciaux à l’exception de l’apostrophe (‘), du tiret (-) et de l’espace ( ). Il ne doit ni commencer ni finir par un caractère spécial.",
                "minLength": 1,
                "maxLength": 80,
                "pattern": "^[\\pL]+(['\\-]*[\\pL]+)*((\\ ){1}[\\pL]+(['\\-]*[\\pL]+)*)*$"
            },
            "dateNaissance": {
                "type": "string",
                "format": "date",
                "example": "1980-03-29T00:00:00.000Z",
                "description": "Date de naissance du client. Obligatoire"
            },
            "lieuNaissance": {
                "description": "Lieu de naissance du client. Obligatoire",
                "$ref": "#/definitions/InputLieuNaissanceDTO"
            },
            "numeroTelephonePortable": {
                "type": "string",
                "example": "0605040302",
                "description": "Numéro de téléphone portable du client. Obligatoire. 10 chiffres (ou jusqu'à 12 caractères si le premier caractère est un +), sans espaces. Commence par 06 ou 07 ou +33",
                "pattern": "^(0|\\+33)[6-7]([0-9]{2}){4}$"
            },
            "adresseMail": {
                "type": "string",
                "example": "jeanne.durand@contact.fr",
                "description": "Adresse mail du client. Obligatoire. Structure de l'adresse mail respectée (avec un @ et un nom de domaine)",
                "pattern": "^[-A-Za-z0-9_]+(\\.[-A-Za-z0-9_]+)*@[A-Za-z0-9]+((-|\\.)[A-Za-z0-9]+)*\\.[A-Za-z]+$"
            },
            "adressePostale": {
                "description": "Adresse postale du client. Obligatoire",
                "$ref": "#/definitions/InputAdresseDTO"
            },
            "coordonneeBancaire": {
                "description": "Coordonnées bancaires du client. Obligatoire",
                "$ref": "#/definitions/InputCoordonneeBancaireDTO"
            }
        }
    }
    """

    adresseMail = colander.SchemaNode(colander.String())
    adressePostale = InputAdresseDTOSchema()
    civilite = colander.SchemaNode(URSSAFCivilite())
    coordonneeBancaire = InputCoordonneeBancaireDTOSchema()
    dateNaissance = colander.SchemaNode(URSSAFDateTime())
    lieuNaissance = InputLieuNaissancoDTOSchema()
    nomNaissance = colander.SchemaNode(URSSAFASCIIString())
    nomUsage = colander.SchemaNode(URSSAFASCIIString(), default=colander.drop)
    numeroTelephonePortable = colander.SchemaNode(colander.String())
    prenoms = colander.SchemaNode(URSSAFASCIIString())

    def serialize_customer(self, customer: Customer):
        fields = dict(
            adresseMail=customer.email,
            adressePostale=self["adressePostale"].serialize_customer(customer),
            civilite=customer.civilite,
            coordonneeBancaire=self["coordonneeBancaire"].serialize_customer(customer),
            dateNaissance=customer.urssaf_data.birthdate,
            lieuNaissance=self["lieuNaissance"].serialize_sap_customer_data(
                customer.urssaf_data
            ),
            numeroTelephonePortable=customer.mobile,
            prenoms=customer.firstname,
        )
        if customer.urssaf_data.birth_name:
            fields["nomNaissance"] = customer.urssaf_data.birth_name
            fields["nomUsage"] = customer.lastname
        else:
            fields["nomNaissance"] = customer.lastname

        return self.serialize(fields)


def serialize_customer(customer: Customer) -> dict:
    serializer = InputParticulierDTOSchema()
    return serializer.serialize_customer(customer)


def serialize_invoice(invoice: Invoice) -> dict:
    serializer = InputDemandePaiementSchema()
    return serializer.serialize_invoice(invoice)


def fix_tva_rounding(cstruct: dict) -> dict:
    """
    Fix TVA/TTC amounts to pass URSSAF checks

    URSSAF enforces two consistency checks:

    1. invoice-level: sum(product.mntPrestationTTC for product in inputPresations) == mntFactureTTC
    2. line-level : mntUnitaireTTC * quantite  == mntPrestationTTC

    The way we compute TVA (on the sum, groupped by TVA rate, and not
    per-line) will in certain cases fail to match check #1 : can lead to
    extra-cent in total.

    There is no perfect option. Workaround here is to tweak the first line of the invoice to
    add/remove the extra-cent in it. Thus modifying for first line:

    - mntPrestationTTC
    - mntUnitaireTTC
    - mntPrestationTVA.

    :param cstruct: cstruct of the demande

    :returns: cstruct with rounded parameters.
    """

    def quantize(f: float, format, *args, **kwargs) -> float:
        """
        Quantize at two decimals, avoiding floating errors
        >>> 47.51-0.02 == 47.49
        False
        >>> quantize(47.51-0.02, "1.00") == 47.49
        True
        """
        return float(Decimal(f).quantize(Decimal(format), *args, **kwargs))

    sum_ttc = sum(p["mntPrestationTTC"] for p in cstruct["inputPrestations"])
    invoice_ttc = cstruct["mntFactureTTC"]

    # may be positive or negative
    delta_ttc = invoice_ttc - sum_ttc
    # avoid rounding errors: we want a rounded number of cents
    delta_ttc = quantize(delta_ttc, "1.000")

    if delta_ttc != 0:
        logger.warning(
            f"Fixing a delta of {delta_ttc}€ for {cstruct['numFactureTiers']}"
        )
        fixed_cstruct = deepcopy(cstruct)
        first_line = fixed_cstruct["inputPrestations"][0]
        first_line["mntPrestationTTC"] = quantize(
            first_line["mntPrestationTTC"] + delta_ttc, "1.00"
        )
        first_line["mntPrestationTVA"] = quantize(
            first_line["mntPrestationTVA"] + delta_ttc, "1.00"
        )
        unit_ttc = (
            first_line["mntPrestationTTC"] / first_line["quantite"]
            if first_line["quantite"] != 0
            else 0
        )

        # 3 decimals are allowed for mntUnitaireTTC
        unit_ttc_rounded_up = quantize(unit_ttc, "1.000", ROUND_UP)
        unit_ttc_rounded_down = quantize(unit_ttc, "1.000", ROUND_DOWN)

        if (
            quantize(unit_ttc_rounded_up * first_line["quantite"], "1.00")
            == first_line["mntPrestationTTC"]
        ):
            first_line["mntUnitaireTTC"] = unit_ttc_rounded_up
        elif (
            quantize(unit_ttc_rounded_down * first_line["quantite"], "1.00")
            == first_line["mntPrestationTTC"]
        ):
            first_line["mntUnitaireTTC"] = unit_ttc_rounded_down
        else:
            # unclear if this case can actually occur
            first_line["mntUnitaireTTC"] = unit_ttc_rounded_down
            logger.error(
                "Impossible de corriger les prix unitaire TTC pour satisfaire la "
                "validation de L'URSSAF, la demande va probablement être rejetée."
            )
        return fixed_cstruct

    else:
        return cstruct

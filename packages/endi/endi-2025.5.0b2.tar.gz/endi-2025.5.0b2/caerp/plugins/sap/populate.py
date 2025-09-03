from caerp.models.populate import PopulateRegistry


DEFAULT_DOCUMENT_HELP = """
* A reporter dans la case de votre déclaration de revenus correspondant à votre situation :

- 7DB (vous, et votre conjoint, avez exercé une activité professionnelle ou avez été demandeur d'emploi),
- 7DF (vous, et votre conjoint, avez été retraité ou inactif,
- 7DD (vous avez engagé des dépenses pour un ascendant de plus de 65 ans bénéficiaire de l'APA).

* Attention : Pour certaines activités le crédit d'impôt est plafonné à
-  500 € pour les prestations de bricolage
- 3000 € pour les prestations informatiques
- 5 000€ pour le jardinage
Ainsi par exemple si le montant de la prestation de bricolage est de 1500 € pour l'année, le crédit d'impôt sera
plafonné à 500 €.

* Pour les personnes utilisant le Chèque emploi service universel, seul le montant financé personnellement est déductible. Une attestation est délivrée par les établissements qui préfinancent le CESU.
"""

DEFAULT_SIGNEE = "Madame XXXXX, gérante de YYYYY"


def populate_sap_config(session):
    from caerp.models.config import Config

    config_defaults = [
        ("sap_attestation_document_help", DEFAULT_DOCUMENT_HELP),
        ("sap_attestation_signee", DEFAULT_SIGNEE),
    ]

    for key, value in config_defaults:
        if not Config.get(key):
            Config.set(key, value)
    session.flush()


def includeme(config):
    PopulateRegistry.add_function(populate_sap_config)

import colander
from caerp.forms import (
    lower_string_preparer,
    strip_string_preparer,
)


class SmtpSettingsSchema(colander.MappingSchema):
    sender_email = colander.SchemaNode(
        colander.String(),
        title="Adresse e-mail d'envoi",
        description="L'adresse mail de l’expéditeur pour l'’envoi des e-mails "
        "(celle que verront les clients)",
        validator=colander.Email(),
        preparer=lower_string_preparer,
    )
    smtp_host = colander.SchemaNode(
        colander.String(),
        title="Adresse du serveur SMTP",
        description="L’adresse du serveur SMTP de votre fournisseur "
        "(ex: smtp.mondomaine.com)",
        validator=colander.Length(max=255),
        preparer=strip_string_preparer,
    )
    smtp_port = colander.SchemaNode(
        colander.Integer(),
        title="Port du serveur SMTP",
        description="Les ports les plus courants sont 25, 587, 465, 587 ou 993",
        validator=colander.Range(min=1, max=65535),
        preparer=strip_string_preparer,
    )
    smtp_user = colander.SchemaNode(
        colander.String(),
        title="Nom d’utilisateur",
        description="Nom d’utilisateur pour se connecter au serveur SMTP (généralement "
        "identique à l’adresse mail)",
        validator=colander.Length(max=255),
        preparer=strip_string_preparer,
    )
    smtp_password = colander.SchemaNode(
        colander.String(),
        title="Mot de passe",
        description="Mot de passe pour se connecter au serveur SMTP (pour certains"
        ' fournisseurs, des mots de passe "d’application" doivent être utilisés)',
        validator=colander.Length(max=255),
    )
    smtp_ssl = colander.SchemaNode(
        colander.Boolean(), title="Activer SSL", missing=False
    )
    smtp_tls = colander.SchemaNode(
        colander.Boolean(), title="Activer TLS", missing=False
    )


def get_add_edit_smtp_settings_schema(edit=False):
    schema = SmtpSettingsSchema().clone()
    schema["smtp_password"].missing = colander.drop if edit else colander.required
    if edit:
        schema[
            "smtp_password"
        ].description = "Laisser vide pour conserver le mot de passe actuel"
    return schema

import colander
import deform
from caerp.forms import textarea_node
from caerp.models.node import Node
from caerp.forms.custom_types import CustomSet


def validate_list_of_emails(node, value):
    for email in value:
        colander.Email(f"L'adresse e-mail {email} n'est pas valide.")(node, email)


class SendMailSchema(colander.Schema):
    recipient_email = colander.SchemaNode(
        colander.String(),
        title="Adresse e-mail du destinataire",
        description="Entrez l’adresse mail du destinataire à qui le document "
        "sera envoyé.",
        validator=colander.Email(),
    )
    save_recipient = colander.SchemaNode(
        colander.Boolean(),
        title="Mémoriser l'adresse du client ?",
        description="Si l’adresse mail est différente, l’enregistrer dans "
        "la fiche client.",
        default=True,
    )
    copy_to = colander.SchemaNode(
        CustomSet(),
        title="Adresse(s) e-mail à mettre en copie",
        description="Vous pouvez saisir plusieurs adresses e-mails en les séparant "
        "par des virgules.",
        validator=validate_list_of_emails,
        widget=deform.widget.TextInputWidget(),
        missing=colander.drop,
    )
    reply_to = colander.SchemaNode(
        colander.String(),
        title="Répondre à",
        description="Entrez l’adresse e-mail à laquelle vous souhaitez que "
        "le destinataire réponde.",
        validator=colander.Email(),
        missing=colander.drop,
    )
    subject = colander.SchemaNode(
        colander.String(),
        title="Sujet",
        description="Entrez le sujet de l’e-mail",
        validator=colander.Length(min=1, max=100),
    )
    body = textarea_node(
        richtext=True,
        title="Corps de l’e-mail qui sera envoyé à votre client",
        description="Adaptez le corps de l’e-mail (le contenu par "
        "défaut est défini au niveau de la CAE)",
        widget_options={"rows": 10},
    )


def get_send_mail_schema(request, context: Node):
    schema = SendMailSchema()
    return schema

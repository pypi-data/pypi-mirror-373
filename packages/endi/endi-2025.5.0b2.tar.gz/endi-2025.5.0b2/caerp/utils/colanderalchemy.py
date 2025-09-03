import colander
import logging

from sqlalchemy import inspect

logger = logging.getLogger(__name__)


def patched_objectify(self, dict_, context=None):
    # Workaround ColanderAlchemy bug #101 (FlushError)
    # https://github.com/stefanofontanelli/ColanderAlchemy/issues/101
    # A PR is ongoing, if merged/released, that function/file should be removed
    # https://github.com/stefanofontanelli/ColanderAlchemy/pull/103
    def get_context(obj, session, class_, pk):
        """return context of obj in session"""
        if isinstance(pk, tuple):
            ident = tuple(obj.get(v, None) for v in pk)
        else:
            ident = obj.get(pk, None)
        context = session.query(class_).get(ident) if ident else None

        return context

    mapper = self.inspector
    context = context if context else mapper.class_()
    insp = inspect(context, raiseerr=False)
    session = insp.session if (insp and insp.session) else None

    for attr in dict_:
        if attr in mapper.relationships.keys():
            # handle relationship
            prop = mapper.get_property(attr)
            prop_class = prop.mapper.class_
            prop_pk = tuple(v.key for v in inspect(prop_class).primary_key)
            if len(prop_pk) == 1:
                prop_pk = prop_pk[0]

            if prop.uselist:
                # relationship is x_to_many, value is list
                subschema = self[attr].children[0]
                value = [
                    patched_objectify(
                        subschema, obj, get_context(obj, session, prop_class, prop_pk)
                    )
                    for obj in dict_[attr]
                ]
            else:
                # relationship is x_to_one, value is not a list
                subschema = self[attr]
                obj = dict_[attr]
                value = patched_objectify(
                    subschema, obj, get_context(obj, session, prop_class, prop_pk)
                )

        elif attr in mapper.columns.keys():
            # handle column
            value = dict_[attr]
            if value is colander.null:
                value = None

        else:
            # Ignore attributes if they are not mapped
            logger.debug(
                "SQLAlchemySchemaNode.objectify: %s not found on "
                "%s. This property has been ignored.",
                attr,
                self,
            )
            continue

        # persist value
        setattr(context, attr, value)
    return context


def get_model_columns_list(model: object, exclude: list = ["id"]) -> list:
    """
    Return the list of the columns of given model

    :param obj model: An SqlAlchemy model object
    :param list exclude: List of columns names we don't want to return

    :returns: A list of column objects
    """
    columns_list = []
    for column in model.__table__.columns:
        if column.name not in exclude:
            columns_list.append(column)
    return columns_list


def get_colanderalchemy_column_info(column: object, info: str) -> str:
    """
    Return the colanderalchemy specified 'info' data for the given model's column

    :param obj column: An SqlAlchemy model's column object
    :param str info: The info we want from the column ("title", "section", ...)

    :returns: The value of the info (string)
    """
    column_info = None
    if "colanderalchemy" in column.info:
        if info in column.info["colanderalchemy"]:
            if column.info["colanderalchemy"][info] != "":
                column_info = column.info["colanderalchemy"][info]
    return column_info


def get_colanderalchemy_model_sections(
    model: object, exclude_columns: list = ["id"]
) -> list:
    """
    Return all colanderalchemy's sections of given model

    :param obj model: An SqlAlchemy model object
    :param list exclude_columns: List of columns names we don't want to get section from

    :returns: A list of sections (string)
    """
    sections = []
    for column in get_model_columns_list(model, exclude_columns):
        column_section = get_colanderalchemy_column_info(column, "section")
        if column_section:
            if column_section not in sections:
                sections.append(column_section)
    sections.sort()
    return sections


def get_model_columns_by_colanderalchemy_section(
    model: object, section_name: str, exclude_columns: list = ["id"]
) -> list:
    """
    Return sqlalchemy columns of a model with specific section

    :param obj model: An SqlAlchemy model object
    :param str section_name: The section we want the column
    :param list exclude_columns: List of columns names we don't want to return

    :returns: A list of column objects
    """
    section_columns = []
    for column in get_model_columns_list(model, exclude_columns):
        column_section = get_colanderalchemy_column_info(column, "section")
        if column_section == section_name:
            section_columns.append(column)
    return section_columns

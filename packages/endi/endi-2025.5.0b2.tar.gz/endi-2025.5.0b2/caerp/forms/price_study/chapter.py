from colanderalchemy import SQLAlchemySchemaNode

from caerp.models.price_study.chapter import PriceStudyChapter


def get_chapter_add_edit_schema():
    """
    Build the schema used to add or edit a PriceStudyChapter
    """
    return SQLAlchemySchemaNode(
        PriceStudyChapter,
        includes=(
            "title",
            "description",
            "order",
            "display_details",
        ),
    )

import logging

logger = logging.getLogger(__name__)


def navigation_panel(context, request):
    """
    Show the navigation panel

    Breadcrumb
    Alternative links
    Back link
    """
    logger.debug(" -> Navigation panel")
    logger.debug(request.navigation.get_back_link())
    return dict(
        links=request.navigation.links,
        back_link=request.navigation.get_back_link(),
        breadcrumb=request.navigation.breadcrumb,
    )


def includeme(config):
    config.add_panel(
        navigation_panel,
        name="navigation",
        renderer="caerp:templates/panels/navigation.pt",
    )

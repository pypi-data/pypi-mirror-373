"""
Panel listant les activités d'un accompagnateur
"""
from caerp.models.activity import Activity
from caerp.forms.user.user import User


def manage_dashboard_activities_panel(context, request):
    """
    Collect manager's activities
    """
    user_id = request.identity.id
    query = Activity.query()
    query = query.join(Activity.conseillers)
    query = query.filter(Activity.conseillers.any(User.id == user_id))
    query = query.filter(Activity.status == "planned")
    query = query.order_by(Activity.datetime).limit(10)
    activities = query.all()
    for activity in activities:
        activity.url = request.route_path("activity", id=activity.id)
    return {"activities": activities}


def includeme(config):
    config.add_panel(
        manage_dashboard_activities_panel,
        "manage_dashboard_activities",
        renderer="caerp:templates/panels/manage" "/manage_dashboard_activities.mako",
    )
    config.add_panel(
        manage_dashboard_activities_panel,
        "manage_dashboard_activity_resume",
        renderer="caerp:templates/panels/manage"
        "/manage_dashboard_activity_resume.mako",
    )

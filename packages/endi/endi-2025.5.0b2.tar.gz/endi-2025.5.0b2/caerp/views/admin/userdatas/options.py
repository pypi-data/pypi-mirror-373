from caerp.consts.permissions import PERMISSIONS
from caerp.models.user.userdatas import (
    ZoneOption,
    ZoneQualificationOption,
    StudyLevelOption,
    SocialStatusOption,
    ActivityTypeOption,
    PcsOption,
    PrescripteurOption,
    NonAdmissionOption,
    ParcoursStatusOption,
    SocialDocTypeOption,
    CaeSituationOption,
    AntenneOption,
    CareContractOption,
    AidOrganismOption,
)
from caerp.models.career_path import (
    TypeContratOption,
    EmployeeQualityOption,
    TypeSortieOption,
    MotifSortieOption,
)
from caerp.views.admin.tools import (
    get_model_admin_view,
)
from caerp.views.admin.userdatas import (
    USERDATAS_URL,
    UserDatasIndexView,
)


def includeme(config):
    """
    Configure route and views for userdatas management
    """
    for model in (
        CaeSituationOption,
        AntenneOption,
        ZoneOption,
        ZoneQualificationOption,
        StudyLevelOption,
        SocialStatusOption,
        EmployeeQualityOption,
        ActivityTypeOption,
        PcsOption,
        PrescripteurOption,
        NonAdmissionOption,
        ParcoursStatusOption,
        MotifSortieOption,
        SocialDocTypeOption,
        TypeSortieOption,
        TypeContratOption,
        CareContractOption,
        AidOrganismOption,
    ):
        view = get_model_admin_view(model, r_path=USERDATAS_URL)
        setattr(view, "permission", PERMISSIONS["global.config_userdatas"])
        config.add_route(view.route_name, view.route_name)
        config.add_admin_view(
            view,
            parent=UserDatasIndexView,
        )

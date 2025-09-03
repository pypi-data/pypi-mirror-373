import inspect
from typing import List, Optional

from pyramid.authentication import SessionAuthenticationHelper
from pyramid.authorization import ACLAllowed, ACLDenied, Authenticated, Everyone
from pyramid.security import ACLPermitsResult, Allow
from pyramid.util import is_nonstr_iter

from caerp.models.user import User
from caerp.services.company import find_company_id_from_model

from .identity import get_identity


def get_user_principals(request, context, user: User) -> List[str]:
    """
    Compute the principals for the current authenticated user
    """
    principals = [Everyone]
    principals.append(Authenticated)
    principals.append(user.login.login)
    principals.append(f"user:{user.id}")
    principals.append(f"login:{user.login.id}")
    for group in user.login._groups:
        principals.append(f"group:{group.name}")
        for access_right in group.access_rights:
            principals.append(f"access_right:{access_right.name}")
    for company in user.companies:
        if company.active:
            principals.append(f"company:{company.id}")
    return principals


def global_permits(request, context, identity: Optional[User], permission: str) -> bool:
    """
    Check if the user has globally access to the given permission
    The permission should be in the form "global.<permission>"
    """
    if identity:
        if permission == "global.authenticated":
            return True
        for group in identity.login._groups:
            for access_right in group.access_rights:
                if permission in access_right.global_permissions:
                    return True
    return False


def get_global_permission(company_permission: str) -> str:
    return "global.company_{}".format(company_permission.split(".")[1])


def company_permits(
    request, context, identity: Optional[User], permission: str
) -> bool:
    """
    Check if the user has the permission needed on the context regarding his companies

    permission should be in the form "company.<permission>"
    """
    if identity:
        global_permission = get_global_permission(permission)
        # Si on a un droit global.company_<permission> c'est ok
        if global_permits(request, context, identity, global_permission):
            return True
        # Sinon on vérifie si c'est l'enseigne de l'utilisateur
        company_id = find_company_id_from_model(request, context)
        if company_id is None:
            raise Exception(
                f"Check permission 'company.view' : Can't retrieve the company_id "
                f"for the current context.{context} with id {context.id}"
            )
        for company in identity.companies:
            if company.id == company_id:
                return True
    return False


def default_acl_denied(context, permission, principals):
    return ACLDenied(
        "<default deny>",
        f"<{context.__class__} has no __acl__>",
        permission,
        principals,
        context,
    )


def acl_permits(request, context, principals, permission: str) -> ACLPermitsResult:
    """
    Teste si les acls du context donne la permission "permission" à l'utilisateur disposant des identifiants "principals"
    """
    try:
        acl_func = context.__acl__
    except AttributeError:
        return default_acl_denied(context, permission, principals)

    if acl_func and callable(acl_func):
        params = {}
        acl_func_args = inspect.signature(acl_func).parameters
        if "request" in acl_func_args:
            params["request"] = request

        acl: list = acl_func(**params)
    else:
        acl: list = acl_func
    for ace in acl:
        ace_action, ace_principal, ace_permissions = ace
        if ace_principal in principals:
            if not is_nonstr_iter(ace_permissions):
                ace_permissions = [ace_permissions]
            if permission in ace_permissions:
                if ace_action == Allow:
                    return ACLAllowed(ace, acl, permission, principals, context)
                else:
                    return ACLDenied(ace, acl, permission, principals, context)
    return default_acl_denied(context, permission, principals)


class SessionSecurityPolicy:
    def __init__(self):
        self.helper = SessionAuthenticationHelper()

    def identity(self, request):
        """Return app-specific user object."""
        userid = self.helper.authenticated_userid(request)
        if userid is None:
            return None

        if getattr(request, "_cached_identity", None) is None:
            request._cached_identity = get_identity(request, userid)
        return request._cached_identity

    def authenticated_userid(self, request):
        """Return a string ID for the user."""

        identity = self.identity(request)

        if identity is None:
            return None

        return str(identity.id)

    def permits(self, request, context, permission):
        """Allow access to everything if signed in."""
        identity = self.identity(request)

        if permission.startswith("global."):
            return global_permits(request, context, identity, permission)

        if permission.startswith("company."):
            return company_permits(request, context, identity, permission)

        if identity is not None:
            principals = get_user_principals(request, context, identity)
        else:
            principals = [Everyone]

        return acl_permits(request, context, principals, permission)

    def remember(self, request, userid, **kw):
        return self.helper.remember(request, userid, **kw)

    def forget(self, request, **kw):
        # Clean le cache
        if hasattr(request, "_cached_identity"):
            del request._cached_identity
        return self.helper.forget(request, **kw)

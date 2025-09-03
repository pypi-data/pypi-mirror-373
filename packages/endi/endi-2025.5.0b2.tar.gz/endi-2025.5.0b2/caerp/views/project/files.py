"""
Attached files related views
"""

from caerp.consts.permissions import PERMISSIONS
from typing import List

from pyramid.httpexceptions import HTTPFound
from pyramid.csrf import get_csrf_token

from caerp.models.files import File
from caerp.models.task import Task
from caerp.models.project import Project
from caerp.models.project.file_types import BusinessTypeFileTypeTemplate
from caerp.models.files import FileType

from caerp.export.task_pdf import ensure_task_pdf_persisted

from caerp.resources import sale_files_js

from caerp.views import BaseView, TreeMixin
from caerp.views.files.views import FileUploadView, BaseZipFileView
from caerp.views.project.routes import (
    PROJECT_ITEM_FILE_ZIP_ROUTE,
    PROJECT_TREE_API,
    PROJECT_ITEM_FILE_ROUTE,
    PROJECT_ITEM_ADD_FILE_ROUTE,
)
from .controller import ProjectTreeController
from .project import ProjectListView


class ProjectFileAddView(FileUploadView, TreeMixin):
    route_name = PROJECT_ITEM_ADD_FILE_ROUTE

    def __init__(self, *args, **kw):
        FileUploadView.__init__(self, *args, **kw)
        self.populate_navigation()

    def redirect(self, come_from):
        return HTTPFound(
            self.request.route_path(
                self.route_name,
                id=self.context.id,
            )
        )


class ProjectFilesView(BaseView, TreeMixin):
    route_name = PROJECT_ITEM_FILE_ROUTE

    @property
    def title(self):
        return "Fichiers attachés au dossier {0}".format(self.context.name)

    @property
    def tree_url(self):
        return self.request.route_path(self.route_name, id=self.context.id)

    def get_project_id(self):
        return self.context.id

    def _get_js_app_options(self):
        return {
            "collection_url": self.request.route_path(
                PROJECT_TREE_API, id=self.get_project_id()
            ),
            "form_config_url": self.request.route_path(
                PROJECT_TREE_API,
                id=self.get_project_id(),
                _query={"form_config": 1},
            ),
            "csrf_token": get_csrf_token(self.request),
            "project_id": self.get_project_id(),
            "title": self.title,
        }

    def __call__(self):

        sale_files_js.need()
        self.populate_navigation()

        result = dict(title=self.title, js_app_options=self._get_js_app_options())
        return result


def business_py3o_list_view(request, context: Project) -> list:
    """
    Return a list of available templates for a given business
    """
    business_types = context.get_all_business_types(request)
    available_templates = BusinessTypeFileTypeTemplate.query()
    available_templates = (
        available_templates.filter_by(
            business_type_id.in_([btype.id for btype in business_types])
        )
        .join(FileType)
        .order_by(FileType.label)
    )
    return available_templates.all()


class ProjectZipFileView(BaseZipFileView):
    def __init__(self, context, request=None):
        super().__init__(context, request)
        self.tree_controller = ProjectTreeController(self.request, project=self.context)

    def filename(self):
        return f"{self.context.name}_archive.zip"

    def collect_files(self) -> List[File]:
        files = []
        for node in self.tree_controller.get_all_project_nodes():
            files.extend(node.files)
            if isinstance(node, Task) and node.status == "valid":
                if node.pdf_file is None:
                    ensure_task_pdf_persisted(node, self.request)
                files.append(node.pdf_file)

        files.extend(self.context.files)
        return files


def includeme(config):
    config.add_tree_view(
        ProjectFileAddView,
        parent=ProjectFilesView,
        request_param="action=attach_file",
        layout="default",
        renderer="caerp:templates/base/formpage.mako",
        context=Project,
        permission=PERMISSIONS["context.add_file"],
    )
    config.add_tree_view(
        ProjectFilesView,
        parent=ProjectListView,
        renderer="caerp:templates/project/files.mako",
        layout="project",
        context=Project,
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        ProjectZipFileView,
        route_name=PROJECT_ITEM_FILE_ZIP_ROUTE,
        context=Project,
        permission=PERMISSIONS["company.view"],
    )

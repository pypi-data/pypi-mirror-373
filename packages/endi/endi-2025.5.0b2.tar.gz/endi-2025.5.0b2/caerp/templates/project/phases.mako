<%inherit file="${context['main_template'].uri}" />

<%block name='actionmenucontent'>
% if api.has_permission("context.edit_project", layout.current_project_object):
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        <div role='group'>
            <a class='btn btn-primary icon' href="${layout.edit_url}">
                ${api.icon('pen')}
                Modifier le dossier
            </a>
        </div>
    </div>
</div>
% endif
</%block>

<%block name='mainblock'>
<div id="project_phases_tab" class='project-view'>
	<div class="content_vertical_double_padding">
        <button class='btn btn-primary icon' onclick="toggleModal('new_phase_form'); return false;">
            ${api.icon('plus')}
            Créer un sous-dossier
        </button>
    </div>

    <div class="content_vertical_double_padding separate_top" id='phase_accordion'>
        % for phase in phases:
            % if phase.id == latest_phase_id:
                <% 
                    section_hidden = ''
                    expanded = 'true'
                %>
            % else:
                <% 
                    section_hidden = 'hidden'
                    expanded = 'false'
                %>
            % endif
            <div class='collapsible separate_bottom'>
                <h3 class='collapse_title'>
                    <a href="javascript:void(0);" onclick="toggleCollapse( this );" aria-expanded="${expanded}">
                        <span class="icon folder-open">${api.icon('folder-open')}</span>
                        <span class="icon folder">${api.icon('folder')}</span>
                        ${phase.label()}
                        ${api.icon('chevron-down','arrow')}
                    </a>
                    <div class="collapse_title_buttons">
                        
                        <a class="btn icon unstyled" href="${request.route_path('/phases/{id}', id=phase.id)}" title="Modifier le libellé du sous-dossier ${phase.label()}" aria-label="Modifier le libellé du sous-dossier ${phase.label()}">
                            ${api.icon('pen')}
                        </a>
                        
                        % if api.has_permission('context.delete_phase', phase):
                            <a class="btn icon negative unstyled" href="${request.route_path('/phases/{id}', id=phase.id, _query=dict(action='delete'))}"
                                onclick="return confirm('Êtes-vous sûr de vouloir supprimer le sous-dossier ${phase.label()} ?');"
                                title="Supprimer le sous-dossier ${phase.label()}"
                                aria-label="Supprimer le sous-dossier ${phase.label()}"                            >
                                ${api.icon('trash-alt')}
                            </a>
                        % endif
                    </div>
                </h3>
                <div class="collapse_content" ${section_hidden}>
                    <div class='content'>
                        ${request.layout_manager.render_panel(
                          'phase_estimations',
                          phase=phase,
                          estimations=tasks_by_phase[phase.id]['estimations'],
                        )}
                        ${request.layout_manager.render_panel(
                          'phase_invoices',
                          phase=phase,
                          invoices=tasks_by_phase[phase.id]['invoices'],
                        )}
                    </div>
                </div>
            </div>
        % endfor
    </div>

    % if not project.phases or tasks_without_phases['estimations'] or tasks_without_phases['invoices']:
	<div class='panel panel-default no-border'>
		<div class='panel-body'>
			${request.layout_manager.render_panel(
              'phase_estimations',
              phase=None,
              estimations=tasks_without_phases['estimations'],
            )}
			${request.layout_manager.render_panel(
              'phase_invoices',
              phase=None,
              invoices=tasks_without_phases['invoices'],
            )}
		</div>
	</div>
    % endif

</div>

<section id="new_phase_form" class="modal_view size_small" style="display: none;">
    <div role="dialog" id="phase-forms" aria-modal="true" aria-labelledby="phase-forms_title">
        <div class="modal_layout">
            <header>
                <button class="icon only unstyled close" title="Fermer cette fenêtre" aria-label="Fermer cette fenêtre" onclick="toggleModal('new_phase_form'); return false;">
                    ${api.icon('times')}
                </button>
                <h2 id="phase-forms_title">Créer un sous-dossier</h2>
            </header>
            <div class="modal_content_layout">
                ${phase_form.render()|n}
            </div>
        </div>
    </div>
</section>
</%block>

<%block name="footerjs">
$( function() {
    if (window.location.hash == "#showphase"){
        $("#project-addphase").addClass('in');
    }
});
</%block>

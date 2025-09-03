<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="definition_list" />
<%namespace file="/base/utils.mako" import="format_mail" />
<%namespace file="/base/utils.mako" import="format_filelist_table" />

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        <% activity = request.context %>
    	<div role='group'>
    		<button class='btn btn-primary icon_only_mobile' title="Modifier ce rendez-vous" aria-label="Modifier ce rendez-vous" onclick="toggleModal('edition_form'); return false;">
                ${api.icon('pen')}
    			Modifier
    		</button>
            <a class='btn icon_only_tablet'
                href="${request.route_path('activity', id=activity.id, _query=dict(action='attach_file'))}"
                onclick="return confirm('En quittant cette page, vous perdrez toutes modifications non enregistrées. Voulez-vous continuer ?');"
                title="Attacher un fichier à ce rendez-vous"
                aria-label="Attacher un fichier à ce rendez-vous">
                ${api.icon('paperclip')}
                Attacher un fichier
            </a>
    		<button class="btn icon_only_tablet" title="Programmer un nouveau rendez-vous avec cet entrepreneur" aria-label="Programmer un nouveau rendez-vous avec cet entrepreneur" onclick="toggleModal('next_activity_form'); return false;">
                ${api.icon('plus')}
    			Nouveau rendez-vous
    		</button>
    	</div>
        <div role='group'>
          <button id='icn-terminate' class="btn btn-primary icon only" title="Terminer ce rendez-vous et quitter" aria-label="Terminer ce rendez-vous et quitter">
            ${api.icon('check')}
          </button>

          <button id='icn-save' class="btn icon only" title="Sauvegarder et continuer" aria-label="Sauvegarder et continuer">
            ${api.icon('save')}
          </button>
          
          <% pdf_url = request.route_path("activity.pdf", id=activity.id) %>
          % if activity.status != 'planned':
          <a class='btn icon only' href='${pdf_url}' title="Voir le PDF" aria-label="Voir le PDF">
            ${api.icon('file-pdf')}
          </a>
          % else:
          <a id='icn-pdf' class='btn icon only' href='${pdf_url}' title="Enregistrer et voir le PDF" aria-label="Enregistrer et voir le PDF">
            ${api.icon('file-pdf')}
          </a>
          % endif
        </div>
    </div>
</div>
</%block>

<%block name="headtitle">
<div class="header_content layout flex" title="${title}">
  <h1>${title}</h1>
</div>
</%block>

<%block name="content">
<% activity = request.context %>
<div class='data_display separate_bottom'>
    <h2>Informations générales</h2>
    <div class='layout flex two_cols'>
        <div>
            <% companies = set() %>
                <h3>Participants</h3>
                <ul>
                % for participant in activity.participants:
                    <li>
                    <% url = request.route_path("/users/{id}", id=participant.id) %>
                    <a href="${url}" target="_blank" title="Voir ce participant dans une nouvelle fenêtre" aria-label="Voir ce participant dans une nouvelle fenêtre">
                    ${api.format_account(participant)}</a> (${ format_mail(participant.email) })
                    </li>
                    % for company in participant.companies:
                        <% companies.add(company) %>
                    % endfor
                %endfor
                </ul>
            </div>
            <div>
                <h3>Activités</h3>
                <div class="layout flex two_cols">
                % for company in companies:
                    <div>
                        <h4>${company.name}</h4>
                        <ul class="no_bullets content_vertical_padding">
                        % for label, route, description, icon in ( \
                        ('Factures', '/companies/{id}/invoices', 'les factures', 'file-invoice-euro'), \
                        ('Devis', '/companies/{id}/estimations', 'les devis', 'file-alt',), \
                        ('Gestion commerciale', 'commercial_handling', 'la gestion commerciale', 'chart-line'), \
                            ):
                            <li>
                                <% url = request.route_path(route, id=company.id) %>
                                <a href="${url}" target="_blank" title="Voir ${description} de l’enseigne ${company.name} dans une nouvelle fenêtre" aria-label="Voir ${description} de l’enseigne ${company.name} dans une nouvelle fenêtre">
                                	<span class="icon">${api.icon(icon)}</span>${label}
                                </a>
                            </li>
                        % endfor
                        </ul>
                    </div>
                % endfor
                </div>
            </div>
            % if activity.files:
            <div>
                <h3>Fichiers attachés</h3>
                <div>
                    ${format_filelist_table(activity)}
                </div>
            </div>
            % endif
            <div>
                <% resulting_companies = set(activity.companies).difference(companies) %>
                % if resulting_companies:
                    <h3>Autres entreprises concernées</h3>
                    <ul>
                    % for company in resulting_companies:
                        <li>
                            <a href="${request.route_path('/companies/{id}', id=company.id)}" target="_blank" title="La fiche de cette enseigne s’ouvrira dans une nouvelle fenêtre" aria-label="La fiche de cette enseigne s’ouvrira dans une nouvelle fenêtre">
                                ${company.name}
                            </a>
                        </li>
                    % endfor
                    </ul>
                % endif
            </div>
        </div>
    </div>
    <div>
        <h2>Configuration du rendez-vous</h2>
        <% items = (\
        ('Conseiller(s)', ', '.join([api.format_account(conseiller) for conseiller in activity.conseillers])), \
            ('Horaire', api.format_datetime(activity.datetime)), \
            ('Action', "%s %s" % (activity.action_label, activity.subaction_label)), \
            ("Nature du rendez-vous", activity.type_object.label), \
            ("Mode d'entretien", activity.mode), \
            )\
        %>
        ${definition_list(items)}
    </div>
	<div>
		<h2>Saisie des données</h2>
		<div>
			${record_form|n}
		</div>
	</div>
</div>

<section
    id="edition_form"
    class="modal_view size_middle"
    % if not formerror:
    style="display: none;"
    % endif
    >
    <div role="dialog" id="edition-forms" aria-modal="true" aria-labelledby="edition-forms_title">
        <div class="modal_layout">
            <header>
                <button class="icon only unstyled close" title="Fermer cette fenêtre" aria-label="Fermer cette fenêtre" onclick="toggleModal('edition_form'); return false;">
                	${api.icon('times')}
                </button>
                <h2 id="edition-forms_title">Modifier le rendez-vous</h2>
            </header>
            <div class="modal_content_layout">
            	${form|n}
            </div>
        </div>
    </div>
</section>

<section id="next_activity_form" class="modal_view size_middle" style="display: none;">
    <div role="dialog" id="next_activity-forms" aria-modal="true" aria-labelledby="next_activity-forms_title">
        <div class="modal_layout">
            <header>
                <button class="icon only unstyled close" title="Fermer cette fenêtre" aria-label="Fermer cette fenêtre" onclick="toggleModal('next_activity_form'); return false;">
                	${api.icon('times')}
                </button>
                <h2 id="next_activity-forms_title">Nouveau rendez-vous</h2>
            </header>
            <div class="modal_content_layout">
                <div id="next_activity_message"></div>
                ${next_activity_form|n}
            </div>
        </div>
    </div>
</section>

</%block>

<%block name="footerjs">
<% activity = request.context %>
<% pdf_url = request.route_path("activity.pdf", id=activity.id) %>
setAuthCheckBeforeSubmit('#record_form');
if(window.location.search.indexOf("show=pdf") != -1) window.open("${pdf_url}");

</%block>

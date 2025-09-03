<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="definition_list" />
<%namespace file="/base/utils.mako" import="format_mail" />
<%namespace file="/base/utils.mako" import="format_text" />
<%namespace file="/base/utils.mako" import="format_filelist_table" />
<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        <a class='btn' href='${request.route_path("activity.pdf", id=request.context.id)}' title='Télécharger la fiche de rendez-vous au format PDF'>
            ${api.icon('file-pdf')}
            <span class="screen-reader-text">Télécharger la fiche de rendez-vous au format </span>
            PDF
        </a>
    </div>
</div>
</%block>

<%block name="content">
	<div class='data_display separate_bottom'>
        <h2>Informations</h2>
		<% items = (\
		('Conseiller(s)', ', '.join([api.format_account(conseiller) for conseiller in activity.conseillers])), \
			('Horaire', api.format_datetime(activity.datetime)), \
			("Action financée", "%s %s" % (activity.action_label, activity.subaction_label)), \
			("Nature du rendez-vous", activity.type_object.label), \
			("Mode d'entretien", activity.mode), \
			)
		%>
        ${definition_list(items)}
    </div>
	<div class='data_display separate_bottom'>
        <h2>Fichiers attachés</h2>
        ${format_filelist_table(activity)}
    </div>
	<div class='data_display separate_bottom'>
        <h2>Participants</h2>
        % for participant in activity.participants:
		<dl>
			<dt>${api.format_account(participant)}</dt>
			<dd class='hidden-print'>${ format_mail(participant.email) }</dd>
		</dl>
        %endfor
    </div>
	<div class='data_display separate_bottom'>
        <% options = (\
                ("Point de suivi", "point"),\
                ("Définition des objectifs", "objectifs"), \
                ("Plan d’action et préconisations", "action" ),\
                ("Documents produits", "documents" ),\
                )
        %>
        % for label, attr in options:
            <h3>${label}</h3>
            ${format_text(getattr(activity, attr))}
        % endfor
    </div>
</%block>

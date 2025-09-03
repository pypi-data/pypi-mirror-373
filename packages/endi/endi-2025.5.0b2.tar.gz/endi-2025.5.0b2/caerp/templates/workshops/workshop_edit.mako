<%inherit file="/workshops/workshop_base.mako" />
<%namespace file="/base/utils.mako" name="utils"/>
<%def name="format_group_mail(participants, subject)">
    <%doc>
    Render a button to send a grouped email to the workshop attendances
    </%doc>
    <% from urllib.parse import urlencode, quote %>
    <% bcc = ",".join([participant.email for participant in participants if participant.email]) %>
    <% querystring = urlencode(dict(bcc=bcc, subject=subject), quote_via=quote) %>

    <% tooltip = """Envoyer un e-mail groupé aux inscrits

⚠ Particularité avec Outlook : il vous faudra paramétrer, dans outlook, la virgule comme séparateur d'adresses
""" %>
    % if bcc !="":
        <a class='btn icon only'
            href="mailto:?${querystring}"
            title="${tooltip}"
            aria-label=${tooltip}
            target="_blank"
            rel="noreferrer"
        >
            ${api.icon('envelope')}
        </a>
    % endif
</%def>

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
<% workshop = request.context %>
	<div class='layout flex main_actions'>
		<div role='group'>
			<a class='btn btn-primary'
				href='${request.route_path("workshop.pdf", id=workshop.id)}'
				title='Télécharger la feuille d’émargement globale'
				aria-label='Télécharger la feuille d’émargement globale'>
				${api.icon('file-pdf')}
				Feuille d’émargement<span class="no_mobile">&nbsp;globale</span>
			</a>
			<button
				class='btn icon_only_mobile'
				data-target='#edition_form'
				onclick='toggleModal("edition_form"); return false;'
				title='Modifier les données relatives à l’atelier'
				aria-label='Modifier les données relatives à l’atelier'>
				${api.icon('pen')}
				Modifier
			</button>
	    </div>
	    <div role='group'>
	        ${format_group_mail(workshop.participants, f"Atelier « {workshop.name} » du {workshop.datetime:%d/%m/%Y}")}
	        <% duplicate_workshop_url = request.route_path("workshop", id=workshop.id, _query=dict(action="duplicate")) %>
	        <%utils:post_action_btn url="${duplicate_workshop_url}" icon="copy"
	          _class="btn icon only"
			  title='Dupliquer cet atelier'
			  aria_label='Dupliquer cet atelier'
	        >
	        </%utils:post_action_btn>

			<a class='btn icon only'
			   href="${request.route_path('workshop', id=workshop.id, _query=dict(action='attach_file'))}"
			   onclick="return confirm('En quittant cette page vous perdrez toute modification non enregistrées. Voulez-vous continuer ?)"
			   title="Attacher un fichier"
			   aria-label="Attacher un fichier">
				${api.icon('paperclip')}
			</a>
		</div>
	</div>
</div>
</%block>

<%block name="details_modal">
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
                <h2 id="edition-forms_title">Modifier les données relatives à l’atelier</h2>
            </header>
            <div class="modal_content_layout">
            	${form|n}
            </div>
        </div>
    </div>
</section>

</%block>
<%block name="after_details">
<% workshop = request.context %>
<div class="separate_top content_vertical_padding">
    <h2>
    Émargement
    </h2>
    <form method='POST'
        class="deform" accept-charset="utf-8"
        enctype="multipart/form-data" action="${request.route_path('workshop',\
        id=workshop.id, _query=dict(action='record'))}">

        <input type="hidden" name="__start__" value="attendances:sequence" />
		<ul class='nav nav-tabs' role='tablist'>
			% for timeslot in workshop.timeslots:
				<li \
				% if loop.first:
					class='active' \
				% endif
				>
					<a href='#tab_${timeslot.id}' data-toggle='tab' role='tab' aria-controls='#tab_${timeslot.id}' id='#tab_${timeslot.id}-tabtitle' \
					% if loop.first:
						 aria-selected='true' \
					% endif
					>
						${timeslot.name}
					</a>
				</li>
			% endfor
		</ul>
		<div class='tab-content'>
		% for timeslot in workshop.timeslots:
			<div class='tab-pane \
				% if loop.first:
					active \
				% endif
					' id='tab_${timeslot.id}' aria-labelledby='#tab_${timeslot.id}-tabtitle'>
				<h3>Émargement de la tranche horaire ${timeslot.name}</h3>
				<p class="content_vertical_padding">
					<strong>Horaires&nbsp;: </strong>
					% if timeslot.start_time.date() == timeslot.end_time.date():
le ${api.format_date(timeslot.start_time)} \
de ${api.format_datetime(timeslot.start_time, timeonly=True)} \
à ${api.format_datetime(timeslot.end_time, timeonly=True)}
					% else:
de ${api.format_datetime(timeslot.start_time, timeonly=False)} \
à ${api.format_datetime(timeslot.start_time, timeonly=False)}
					% endif
					(${timeslot.duration[0]}h${timeslot.duration[1]})
				</p>
				<div class="content_vertical_padding">
					<a class='btn'
						href='${request.route_path("timeslot.pdf", id=timeslot.id)}'
						title='Télécharger la feuille d’émargement pour cette tranche horaire'
						aria-label='Télécharger la feuille d’émargement pour cette tranche horaire'>
					${api.icon('file-pdf')}
					Télécharger la feuille d’émargement<span class="no_mobile">&nbsp;pour cette tranche horaire</span>
					</a>
				</div>
				% for attendance in timeslot.sorted_attendances:
				<input type="hidden" name="__start__" value="attendance:mapping" />
				<% participant = attendance.user %>
				<% participant_url = request.route_path('/users/{id}', id=participant.id) %>
				<% status = attendance.status %>

				<% tag_id = "presence_%s_%s" % (timeslot.id, participant.id) %>
				<input type='hidden' name='account_id' value='${participant.id}' />
				<input type='hidden' name='timeslot_id' value='${timeslot.id}' />
				<div class='row form-group timeslot_attendee'>
					<label for="${tag_id}" class="control-label">
						<a href='${participant_url}' title='Voir le compte de ce participant' aria-label='Voir le compte de ce participant'>
							${api.format_account(participant)}
						</a>
						% if is_multi_antenna_server:
							<br/>
							<small>
								antenne
								% if is_multi_antenna_server:
										% if participant.userdatas and participant.userdatas.situation_antenne:
													${participant.userdatas.situation_antenne.label}
												% else:
													non renseignée
												% endif
									% endif
							</small>
						% endif
					</label>
					<div class="radio">
						<input type='hidden' value='status:rename' name='__start__' />
						% for index, value  in enumerate(available_status):
						<% val, label = value %>
							<label class='radio-inline' >
								<input id='${tag_id}' name='${tag_id}' type='radio' \
								% if status == val:
									 checked \
								% endif
								value='${val}' />
								<span>${label}</span>
							 </label>
						% endfor
						<input type='hidden' name='__end__' />
					</div>
				</div>
				<input type='hidden' name='__end__' value='attendance:mapping' />
				% endfor
			</div>
			% endfor
		</div>
		<input type="hidden" name="__end__" value='attendances:sequence'/>
		<div class='content_vertical_padding'>
			<button id="deformsubmit" class="btn btn-primary" value="submit" type="submit" name="submit" title="Enregistrer l’émargement" aria-label="Enregistrer l’émargement">
				${api.icon('save')}
				Enregistrer
			</button>
		</div>
	</form>
</div>
</%block>

<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="table_btn"/>
<%namespace file="/base/utils.mako" import="company_list_badges"/>
<%namespace file="/base/utils.mako" import="login_disabled_msg"/>
<%namespace file="/base/utils.mako" import="format_phone"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='actionmenucontent'>
% if api.has_permission('global.create_user'):
<div class='main_toolbar action_tools'>
	<div class='layout flex main_actions'>
		<div role='group'>
			% if api.has_permission('global.create_user') and request.has_module('userdatas'):
				<a class='btn btn-primary' href="${request.route_path('/userdatas/add')}">
					${api.icon('plus')}Ajouter un entrepreneur
				</a>
			% endif
			% if api.has_permission('global.create_user'):
				<a class='btn' href="${request.route_path('/users/add/manager')}">
					${api.icon('plus')}Ajouter un permanent
				</a>
			% endif
		</div>
		<div role='group'>
			% if api.has_permission('global.create_user'):
				<a class='btn' title="Voir l'historique des connexions utilisateurs" href="${request.route_path('/users/connections')}">
					${api.icon('chart-line')}Utilisateurs actifs
				</a>
			% endif
		</div>
	</div>
</div>
% endif
</%block>

<%block name="headtitle">
<h1>
% if api.has_permission('global.company_view'):
	Annuaire des utilisateurs
% else:
	Annuaire
% endif
</h1>
</%block>

<%block name='content'>

${searchform()}

% if api.has_permission('global.company_view'):
<div>
% else:
<ul class="nav nav-tabs" role="tablist">
	<li role="presentation" class="active">
		<a href="#list-container" aria-controls="list-container" role="tab" data-toggle="tab">
			<span class="icon">${api.icon('list')}</span>
			Liste des entrepreneurs
		</a>
	</li>
	<li role="presentation">
		<a href="/companies_map" role="tab">
			<span class="icon">${api.icon('map-location-dot')}</span>
			Carte des enseignes
		</a>
	</li>
</ul>

<div class="tab-content content">
	<div id="list-container" class="tab-pane fade in active" role="tabpanel">

% endif
	    <div>
	    	${records.item_count} Résultat(s)
	    </div>
	    <div class='table_container'>

			<table class="hover_table top_align_table">
					% if records:
					<thead>
						<tr>
							<th scope="col" class="col_avatar no_mobile" title="Photo"><span class="screen-reader-text">Photo</span></th>
							<th scope="col" class="col_text">${sortable("Nom", "name")}</th>
							<th scope="col" class="col_text">Enseigne</th>
							<th scope="col" class="col_text">Activité</th>
							<th scope="col" class="col_text"><span class="icon">${api.icon('envelope')}</span> E-mail</th>
							<th scope="col" class="col_text phone">Téléphone</th>
							<th scope="col" class="col_text">Code postal</th>
							% if api.has_permission('global.create_user'):
								<th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
							% endif
						</tr>
					</thead>
					<tbody>
						% for id, user in records:
							% if user.companies or api.has_permission('global.create_user'):
								<% url = request.route_path('/users/{id}', id=user.id) %>
								<tr>
									<td class="col_avatar no_mobile">
							            % if user.photo_file and user.photo_is_publishable:
								    	    <span class='user_avatar photo'>
								                <img src="${api.img_url(user.photo_file)}" 
								                    title="${api.format_account(user)}" 
								                    alt="Photo de ${api.format_account(user)}" 
								                    width="48" height="48" />
								        	</span>
							            % else:
								        	<span class='user_avatar'>${api.icon('user')}</span>
							            % endif
									</td>
									<td class="col_text">
										% if api.has_permission('context.view_user', user):
											<a href="${url}">
												${api.format_account(user)}
												% if user.login is None:
													<small>
														<span class="icon">
															${api.icon('exclamation-circle')}
															Ce compte ne dispose pas d’identifiants
														</span>
													</small>
												% elif not user.login.active:
													<small>${login_disabled_msg()}</small>
												% endif
											</a>
										% else:
											${api.format_account(user)}
										% endif
									</td>
									<td class="col_text">
										% if user.companies:
											<ul class="list-unstyled">
												% for company in user.companies:
													<% company_url = request.route_path('/companies/{id}', id=company.id) %>
													<li>
														% if api.has_permission('company.view', company):
															<a href="${company_url}">
																${company.name}
																% if api.has_permission('global.company_view', company):
																	<small>${company_list_badges(company)}</small>
																% endif
															</a>
														% else:
															${company.name}
														% endif
													</li>
												% endfor
											</ul>
										% else:
											<em>Aucune enseigne</em>
										% endif
									</td>
									<td class="col_text">
										<ul class="list-unstyled">
											% for company in user.companies:
												% if company.goal and company.goal != "":
													<li>${company.goal}</li>
												% endif
											% endfor
										</ul>
									</td>
									<td class="col_text">
										<ul>
											% for company in user.companies:
												% if company.email and company.email != "":
													<li><a href="mailto:${company.email}" title="Envoyer un e-mail à cette adresse" aria-label="Envoyer un e-mail à cette adresse">${company.email}</a></li>
												% endif
											% endfor
										</ul>
									</td>
									<td class="col_text phone">
										<ul>
											% for company in user.companies:
												% if company.phone and company.phone != "":
													<li>
														<span class="icon">${api.icon('phone')}</span> ${format_phone(company.phone, 'none')}</li>
												% endif
												% if company.mobile and company.mobile != "":
													<li><span class="icon">${api.icon('mobile-alt')}</span> ${format_phone(company.mobile, 'none')}</li>
												% endif
											% endfor
										</ul>
									</td>
									<td class="col_text">
										<ul class="list-unstyled">
											% for company in user.companies:
												% if company.zip_code and company.zip_code != "":
													<li>${company.zip_code}</li>
												% endif
											% endfor
										</ul>
									</td>
									% if api.has_permission('global.create_user'):
									${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(user))}
									% endif
								</tr>
							% endif
						% endfor
					</tbody>
				% else:
					<tbody>
						<tr>
							<td class="col_text"><center><em>Aucun utilisateur</em></center></td>
						</tr>
					</tbody>
				% endif
			</table>

		</div>
		${pager(records)}

% if api.has_permission('global.company_view'):
<div>
% else:
	</div>
</div>
% endif
</%block>

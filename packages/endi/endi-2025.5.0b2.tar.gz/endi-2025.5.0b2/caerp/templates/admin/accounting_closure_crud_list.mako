<%doc>
:param str addurl: The url for adding items
:param str actions: List of actions buttons in the form [(url, label, icon, css, btn_type)]
:param list columns: The list of columns to display
:param list items: A list of dict {'id': <element id>, 'columns': (col1, col2), 'active': True/False}
:param obj stream_columns: A factory producing column entries [labels]
:param obj stream_actions: A factory producing action entries [(url, label, title, icon)]

:param str warn_msg: An optionnal warning message
:param str help_msg: An optionnal help message
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%block name='actionmenucontent'>
% if (addurl is not UNDEFINED and addurl is not None) or actions is not UNDEFINED:
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        % if addurl is not UNDEFINED and addurl is not None:
        <a class='btn btn-primary'
            href="${addurl}"
            title="Ajouter un élément à la liste"
        >
            ${api.icon('plus')}
            Ajouter
        </a>
        % endif
        % if actions is not UNDEFINED:
        <div role="group">
        % for link in actions:
            ${request.layout_manager.render_panel(link.panel_name, context=link)}
        % endfor
        </div>
        % endif
    </div>
</div>
% endif
</%block>
<%block name='afteradminmenu'>
    <div class='alert alert-warning'>
        <span class="icon">${api.icon('danger')}</span>
        Attention, une fois un exercice comptable clôturé, l'opération est définitive et irréversible !<br />
    </div>
    <div class='alert alert-info'>
        <span class="icon">${api.icon('info-circle')}</span>
        Clôturer un exercice permet de ne plus prendre en compte l'exercice précédent dans le calcul des états de trésorerie. La clôture suppose donc que les écritures de reports d'à-nouveaux aient été faites.<br /><br />
        L'année à saisir est l'année de fin de l'exercice.<br />
        <i><u>Exemple :</u> dans le cas d'un exercice fiscal se terminant le 31/03, si vous saisissez 2019, cela correspond à la clôture de l'exercice courant du 01/04/2018 au 31/03/2019.</i><br /><br />
        Pour clôturer un exercice, cliquez sur <i>Ajouter</i> en haut à gauche, saisissez l'année de fin de l'exercice que vous souhaitez clôturer puis cliquez sur <i>Valider</i>. L'année de fin d'exercice que vous venez de saisir apparaît maintenant dans le tableau ci-dessous, cliquez sur l'icône avec trois petit points puis sur <i>clôturer définitivement</i>.
    </div>
<div>
    ${request.layout_manager.render_panel('help_message_panel', parent_tmpl_dict=context.kwargs)}
</div>
</%block>
<%block name='content'>
    <div>
        % if widget is not UNDEFINED:
        ${request.layout_manager.render_panel(widget)}
        % endif
		<div class='table_container limited_width width40'>
			<table>
                <thead>
                	<tr>
						<th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
					% for column in columns:
						<th scope="col" class="col_text">${column}</th>
					% endfor
						<th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                	</tr>
                </thead>
                <tbody>
                % for item in items:
                    <tr>
                        % if hasattr(item, 'active') and not item.active:
                    	<td>
                        % else:
                    	<td class="col_status">
                        <span class="icon status closed" title="Exercice clôturé" aria-label="Exercice clôturé">${api.icon('lock')}</span>
                        % endif
                    	</td>
                        % for value in stream_columns(item):
                            <td class="col_text">
                            % if value is not None:
                                ${ value|n }
                            % endif
                            </td>
                        % endfor
                        <td class='col_actions width_one'>
                        % if hasattr(item, 'active') and not item.active:
                        ${request.layout_manager.render_panel('menu_dropdown', label="Actions", links=stream_actions(item))}
                        % endif
                        </td>
                    </tr>
                % endfor
                % if not items:
                    <tr><td colspan='${len(columns) + 1}' class="col_text">
                        % if nodata_msg is not UNDEFINED and nodata_msg is not None:
                            ${nodata_msg|n}
                        % else:
                            <em>Aucun élément configuré</em>
                        % endif
                    </td></tr>
                % endif
                </tbody>
			</table>
		</div>
    </div>
</%block>

<%inherit file="${context['main_template'].uri}" />
<%namespace file="caerp:templates/base/utils.mako" import="format_text" />
<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
	<div class="layout flex main_actions">
	    <a class='btn hidden-print' href='#print' onclick="window.print()">
	    	${api.icon('print')}
	        Imprimer
	    </a>
	</div>
</div>
</%block>
<%block name="content">
<div>
    <img src="/public/competence_header.png" style="width:auto;max-height:200px;" alt=''/>
</div>
<div class="content_vertical_padding">
    <p>
            <strong>Nom Prénom&nbsp;:</strong> ${request.context.contractor.label}
    </p>
    % if request.context.contractor.userdatas is not None and request.context.contractor.userdatas.situation_follower is not None:
    <p>
            <strong>Référent&nbsp;:</strong> ${api.format_account(request.context.contractor.userdatas.situation_follower)}
    </p>
    % endif
</div>
<div class='content_vertical_padding'>
    <div class='table_container'>
        <table>
            <tbody>
                <tr>
                % for grid in grids:
                    <td>Date d’auto évaluation ${grid.deadline.label}&nbsp;:  ${api.format_date(grid.updated_at)}</td>
                % endfor
                </tr>
            </tbody>
        </table>
    </div>
</div>
<div class='content_vertical_padding'>
    <h2 class='align_center'>Cartographie des compétences auto-évaluées</h2>
    <div class='content_vertical_padding'>
        <div id='radar' class='align_center' style='page-break-after:always;'>
        </div>
    </div>
</div>
<div class='content_vertical_padding'>
    <h2 class='align_center'>Grille d’autonomie</h2>
</div>
<div class='content_vertical_padding'>
	<h3 class='align_center'>
		Auto-évaluation et évolution des compétences entrepreneuriales
	</h3>
</div>

% for item in grids[0].items:
<% option = item.option %>
<div class='content_vertical_padding' style='page-break-after:always;'>
	<div class="table_container">
		<table class='hover_table'>
			<caption>
			    ${option.label}
			</caption>
			<thead>
				<tr>
					<th scope='col' style='width: 30%'></th>
					% for deadline in deadlines:
						<th scope='col'
							% if not loop.last:
							colspan='${len(scales)}'
							% else:
							colspan='${len(scales) + 1}'
							% endif
							>
							Évaluation ${deadline.label}
						</th>
						% if not loop.last:
							<th scope='col' class='separator'></th>
						% endif
					% endfor
				</tr>
				<tr>
					<th scope='col'>Compétences entrepreneuriales</th>
					% for deadline in deadlines:
						% for scale in scales:
							<th scope='col'>
								${scale.label}
							</th>
						% endfor
						% if not loop.last:
							<th scope='col' class='separator'></th>
						% endif
					% endfor
					<th scope='col'>Argumentaires / Preuves</th>
				</tr>
			</thead>
			<tbody>
				% for suboption in option.children:
					<tr>
						<td class='col_text'>${suboption.label}</td>
						% for grid in grids:
							<% grid_subitem = grid.ensure_item(option).ensure_subitem(suboption) %>
							% for scale in scales:
								<td class='align_center' style='min-width:15px'>
									% if grid_subitem.scale.id == scale.id:
									<span class='icon'>${api.icon('check')}</span>
									% endif
								</td>
							% endfor
							<td>
								% if loop.last:
									${format_text(grid_subitem.comments)}
								% endif
							</td>
						% endfor
					</tr>
				% endfor
			</tbody>
		</table>
	</div>
</div>
% endfor
<div class='content_vertical_padding' style='page-break-after:avoid;'>
	<div class="table_container">
		<table>
			<caption>
			    Axe de progrès identifiés
			</caption>
			<thead>
				<tr>
					<th scope="col" class="col_text">Compétences</th>
					<th scope="col" class="col_text">Axe de progrès</th>
				</tr>
			</thead>
			<tbody>
				% for item in grids[-1].items:
					<tr>
						<td class="col_text" style='width: 30%'>${item.option.label}</td>
						<td class="col_text">${format_text(item.progress)}</td>
					</tr>
				% endfor
			</tbody>
		</table>
    </div>
</div>
</%block>
<%block name="footerjs">
AppOptions = {};
AppOptions['loadurl'] = "${loadurl}";
</%block>

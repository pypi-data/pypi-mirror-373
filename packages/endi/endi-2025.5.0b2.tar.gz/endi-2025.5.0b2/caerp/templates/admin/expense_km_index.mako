<%inherit file="${context['main_template'].uri}" />
<%block name='afteradminmenu'>
    <div class='alert alert-info'>
    <span class="icon">${api.icon('info-circle')}</span> 
    Les grilles de frais kilométriques sont configurées de manière annuelle.<br />
    Choisissez l’année que vous voulez administrer.<br />
    Note : Il est possible de dupliquer les types de dépense d’une année vers l'autre.
    </div>
</%block>
<%block name='content'>
<div>
	<h2>
	Choisir une année
	</h2>
	<div class='content_vertical_padding'>
		<div class='btn-group'>
		% for year in years:
			<a
				class='btn'
				href="${request.route_path(admin_path, year=year)}"
				>
				${year}
			</a>
		 % endfor
		 </div>
	</div>
</div>
</%block>

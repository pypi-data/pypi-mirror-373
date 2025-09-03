<%inherit file="/layouts/default.mako" />
<%block name='afteractionmenu'>

% if info_message != UNDEFINED:
<div>
	<div class="alert alert-success">
		<span class="icon">${api.icon('success')}</span> 
		${info_message|n}
	</div>
</div>
% endif
% if warn_message != UNDEFINED:
<div>
	<div class="alert alert-warning">
		<span class="icon">${api.icon('danger')}</span> 
		${warn_message|n}
	</div>
</div>
% endif
% if help_message != UNDEFINED:
<div>
	<div class='alert alert-info'>
	<span class="icon">${api.icon('info-circle')}</span> 
	${help_message|n}
	</div>
</div>
% endif
${request.layout_manager.render_panel('admin_index_nav', context=navigation)}
<%block name='afteradminmenu'>
</%block>
</%block>

<%doc>
    Admin common page template
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="format_text"/>
<%block name="afteradminmenu">
% if not message is UNDEFINED and message:
    <div class='alert alert-info'>
        <span class="icon">${api.icon('info-circle')}</span> 
        ${format_text(message)}
    </div>
% endif
</%block>
<%block name='content'>
% if not form is UNDEFINED:
    <div class='limited_width width40'>
    % if request.is_popup:
        <h2>${title}</h2>
        <div>
    	    ${form|n}
        </div>
    % else:
        ${form|n}
    % endif
	</div>
% endif
</%block>

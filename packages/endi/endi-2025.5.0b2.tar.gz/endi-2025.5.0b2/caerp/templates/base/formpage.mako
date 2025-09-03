<%doc>
    Simple page for form rendering
</%doc>

<%inherit file="${context['main_template'].uri}" />

<%block name="content">
    ${request.layout_manager.render_panel(
        'help_message_panel',
        parent_tmpl_dict=context.kwargs
    )}
    
    <% widthclass = 'width' + width if width is not UNDEFINED else 'width40' %>

    <div class="limited_width ${widthclass}">
        ${form|n}
    </div>
</%block>

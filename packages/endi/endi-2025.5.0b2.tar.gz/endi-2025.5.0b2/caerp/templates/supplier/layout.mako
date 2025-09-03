<%inherit file="/layouts/default.mako" />

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        ${request.layout_manager.render_panel('action_buttons', links=main_actions)}
        ${request.layout_manager.render_panel('action_buttons', links=more_actions)}
    </div>
</div>
</%block>

<%block name='content'>
<div class="layout flex two_cols separate_bottom content_vertical_padding">
    <div class='document_summary'>
        <h2>Informations générales</h2>
        ${request.layout_manager.render_panel('third_party_general_info', context=supplier)}
    </div>
    <div class="status_history hidden-print memos">
        Chargement des mémos…
    </div>
</div>
<div class="layout flex two_cols content_vertical_padding">
    <div class='documents_summary'>
        <h2>Informations comptables</h2>
        ${request.layout_manager.render_panel('third_party_accounting_info', context=supplier)}
    </div>
</div>

<div class="data_display separate_top">
    <div class='tabs' id='subview'>
        <%block name='rightblock'>
            ${request.layout_manager.render_panel('tabs', layout.docs_menu)}
        </%block>
    </div>
    <div class='tab-content'>
        <%block name='mainblock'></%block>
    </div>
</div>

</%block>


<%block name='footerjs'>
AppOption = {};
% for key, value in js_app_options.items():
AppOption["${key}"] = "${value}"
% endfor;
</%block>

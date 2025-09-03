<%inherit file="/layouts/default.mako" />

<%block name="headtitle">
<h1>Client : ${layout.current_customer_object.label}</h1>
</%block>

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
    <div class="layout flex main_actions">
        ${request.layout_manager.render_panel('action_buttons', links=layout.stream_main_actions())}
        ${request.layout_manager.render_panel('action_buttons', links=layout.stream_other_actions())}
    </div>
</div>
</%block>

<%block name='content'>
<% customer =  layout.current_customer_object %>
<div class="totals grand-total">
    <div class="layout flex">
        <div>
            <p><strong>Nom :</strong> ${customer.label}</p>
               
            % if customer.is_internal():
                <p>
                    <small>Enseigne interne à la CAE</small>
                </p>
            % endif
        </div>
        <div>
            ${request.layout_manager.render_panel(
                'business_metrics_totals', 
                instance=customer, 
                tva_on_margin=customer.has_tva_on_margin_business())}
        </div>
    </div>
</div>

<div>
    <div class='tabs'>
        <%block name='rightblock'>
        ${request.layout_manager.render_panel('tabs', layout.menu)}
        </%block>
    </div>
    <div class='tab-content'>
        <%block name='mainblock'>
        </%block>
    </div>
</div>
</%block>

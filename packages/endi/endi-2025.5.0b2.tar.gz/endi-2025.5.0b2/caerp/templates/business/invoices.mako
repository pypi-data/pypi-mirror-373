<%doc>
    Invoice List for a given company
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='mainblock'>

<div id="business_invoices_tab">

    ${searchform()}

    <div>
        <div>
            ${records.item_count} Résultat(s)
        </div>
        <div class='table_container'>
            ${request.layout_manager.render_panel('task_list', records, datatype="invoice", is_admin_view=is_admin, is_project_view=True, is_business_view=True, tva_on_margin_display=request.context.business_type.tva_on_margin)}
        </div>
        ${pager(records)}
    </div>
</div>

</%block>

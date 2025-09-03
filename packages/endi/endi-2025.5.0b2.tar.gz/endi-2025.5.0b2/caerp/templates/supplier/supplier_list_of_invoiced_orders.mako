<!-- -
<%inherit file="${context['main_template'].uri}" />

<%block name='mainblock'>
<div class="table_container" id="invoiced_orders_tab">
    ${request.layout_manager.render_panel(
      'supplier_order_list',
      records,
      stream_actions=stream_actions,
      is_supplier_view=True,
    )}
</div>
</%block>

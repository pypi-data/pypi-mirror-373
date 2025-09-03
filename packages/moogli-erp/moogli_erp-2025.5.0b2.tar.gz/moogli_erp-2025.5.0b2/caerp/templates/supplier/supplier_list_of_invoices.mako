<!-- -
<%inherit file="${context['main_template'].uri}" />

<%block name='mainblock'>
<div class="table_container" id="invoices_tab"> ${request.layout_manager.render_panel('supplier_invoice_list', records, stream_actions=stream_actions, is_supplier_view=True)}
</div>
</%block>

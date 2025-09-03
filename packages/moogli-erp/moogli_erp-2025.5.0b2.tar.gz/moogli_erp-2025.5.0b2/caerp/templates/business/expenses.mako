<%inherit file="${context['main_template'].uri}" />

<%block name='mainblock'>
<div id="business_expenses_tab">

    <!-- Display linked expenses (from expense sheets and supplier invoices) based on context -->
    ${request.layout_manager.render_panel('linked_expenses')}

</div>
</%block>

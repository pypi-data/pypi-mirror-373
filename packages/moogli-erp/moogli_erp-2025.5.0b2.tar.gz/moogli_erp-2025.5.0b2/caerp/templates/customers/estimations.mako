<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="format_text" />
<%namespace file="/base/searchformlayout.mako" import="searchform"/>


<%block name='mainblock'>
<div id="customer_estimations_tab">
    ${searchform()}

    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
    ${request.layout_manager.render_panel('task_list', records, datatype="estimation", is_admin_view=is_admin)}
  </div>
    ${pager(records)}
</div>
</%block>

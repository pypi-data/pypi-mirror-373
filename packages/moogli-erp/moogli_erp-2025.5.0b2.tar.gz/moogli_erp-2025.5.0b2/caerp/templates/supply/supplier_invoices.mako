<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        ${request.layout_manager.render_panel('action_buttons', links=stream_main_actions())}
        ${request.layout_manager.render_panel('menu_dropdown', label="Exporter", links=stream_more_actions(), display_label=True, icon="file-export")}
    </div>
</div>
</%block>

<%block name='content'>
    ${searchform()}
    <% is_search_filter_active = '__formid__' in request.GET %>
    <div>
        <div>${records.item_count} Résultat(s)</div>
        <div class='table_container'>
            ${request.layout_manager.render_panel('supplier_invoice_list', records, is_admin_view=is_admin_view, stream_actions=stream_actions)}
            ${pager(records)}
        </div>
    </div>
</%block>

<%block name='footerjs'>
    $(function(){
    $('input[name=search]').focus();
    });
</%block>

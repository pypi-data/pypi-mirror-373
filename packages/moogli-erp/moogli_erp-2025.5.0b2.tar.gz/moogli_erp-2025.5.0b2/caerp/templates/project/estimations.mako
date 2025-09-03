<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="format_text" />
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='actionmenucontent'>
% if api.has_permission("context.edit_project", layout.current_project_object):
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        <div role='group'>
            <a class='btn btn-primary icon' href="${layout.edit_url}">
                ${api.icon('pen')}
                Modifier le dossier
            </a>
        </div>
    </div>
</div>
% endif
</%block>

<%block name='mainblock'>
<div id="project_estimations_tab">
    <div class='content_vertical_padding separate_bottom_dashed'>
        <a class='btn btn-primary icon' href='${add_url}'>
            ${api.icon('file-list')}
            Créer un devis
        </a>
    </div>

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

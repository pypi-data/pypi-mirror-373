<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item" />
<%namespace file="/base/pager.mako" import="pager" />
<%namespace file="/base/pager.mako" import="sortable" />
<%namespace file="/base/searchformlayout.mako" import="searchform" />

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        <div role='group'>
            <a class='btn btn-primary' href="${request.route_path('/userdatas/add')}"
                title="Nouvelle entrée de Gestion sociale">
                ${api.icon("plus")}
                Nouvelle entrée<span class="screen-reader-text"> de Gestion sociale</span>
            </a>
            % if request.has_module('csv_import') and api.has_permission('global.view_userdata_details'):
            <a class='btn icon_only_mobile' href="${request.route_path('import_step1')}" title="Importer des données">
                ${api.icon("file-import")}
                Importer
            </a>
            % endif
        </div>
        <div role='group'>
            <% args=request.GET %>
            <% url_xlsx=request.route_path('/userdatas.xlsx', _query=args) %>
            <% url_ods=request.route_path('/userdatas.ods', _query=args) %>
            <% url_csv=request.route_path('/userdatas.csv', _query=args) %>
            <a class='btn icon_only_mobile' href='javascript:void(0);'
                onclick="window.openPopup('${url_xlsx}');"
                title="Exporter les éléments de la liste au format Excel (xlsx) dans une nouvelle fenêtre"
                aria-label="Exporter les éléments de la liste au format Excel (xlsx) dans une nouvelle fenêtre">
                ${api.icon("file-excel")}
                Excel
            </a>
            <a class='btn icon_only_mobile' href='javascript:void(0);'
                onclick="window.openPopup('${url_ods}');"
                title="Exporter les éléments de la liste au format Open Document (ods) dans une nouvelle fenêtre"
                aria-label="Exporter les éléments de la liste au format Open Document (ods) dans une nouvelle fenêtre">
                ${api.icon("file-spreadsheet")}
                ODS
            </a>
            <a class='btn icon_only_mobile' href='javascript:void(0);'
                onclick="window.openPopup('${url_csv}');"
                title="Exporter les éléments de la liste au format csv dans une nouvelle fenêtre"
                aria-label="Exporter les éléments de la liste au format csv dans une nouvelle fenêtre">
                ${api.icon("file-csv")}
                CSV
            </a>
        </div>
    </div>
</div>
</%block>

<%block name="content">

    ${searchform()}

    <div>
        <div>
            ${records.item_count} Résultat(s)
        </div>
        <div class='table_container'>
            <table class="hover_table">
                <thead>
                    <tr>
                        <th scope="col" class="col_text">${sortable("Nom", "lastname")}</th>
                        <th scope="col" class="col_text">${sortable("Situation CAE", "situation")}</th>
                        <th scope="col" class="col_text">${sortable("Accompagnateur", "follower")}</th>
                        <th scope="col" class="col_date"><span class="screen-reader-text">Date de dernière mise à
                                jour</span>${sortable("Mise à jour", "updated_at")}</th>
                        % if is_multi_antenna_server:
                        <th scope="col" class='col_text'>${sortable("Antenne", "antenna")}</th>
                        % endif
                        <th scope="col" class="col_actions" title="Actions"><span
                                class="screen-reader-text">Actions</span></th>
                    </tr>
                </thead>
                <tbody>
                    % for userdata in records:
                    <% url=get_edit_url(userdata) %>
                        <% onclick="document.location='{url}'" .format(url=url) %>
                            <% tooltip_title="Cliquer pour voir ou modifier" %>
                                <tr class='white_tr'>
                                    <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                                        ${api.format_account(userdata)}</td>
                                    <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                                        % if userdata.situation_situation:
                                        ${userdata.situation_situation.label}
                                        % endif
                                    </td>
                                    <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                                        ${api.format_account(userdata.situation_follower)}</td>
                                    <td class="col_date" onclick="${onclick}" title="${tooltip_title}">
                                        ${api.format_date(userdata.updated_at)}
                                    </td>
                                    % if is_multi_antenna_server:
                                    <td class="col_text" onclick="${onclick}" title="${tooltip_title}">

                                        ${userdata.situation_antenne.label if userdata.situation_antenne else "Inconnue"}
                                    </td>
                                    % endif
                                    ${request.layout_manager.render_panel('action_buttons_td',
                                    links=stream_actions(userdata))}
                                </tr>
                                % endfor
                </tbody>
            </table>
        </div>
        ${pager(records)}
    </div>
</%block>
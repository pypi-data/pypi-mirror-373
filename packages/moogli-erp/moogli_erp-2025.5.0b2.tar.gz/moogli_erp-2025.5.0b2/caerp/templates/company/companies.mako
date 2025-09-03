<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%namespace file="/base/utils.mako" import="company_list_badges"/>
<%namespace file="/base/utils.mako" import="login_disabled_msg"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>

${searchform()}

<ul class="nav nav-tabs" role="tablist">
    <li role="presentation" class="active">
        <a href="#list-container" aria-controls="list-container" role="tab">
            <span class="icon">${api.icon('list')}</span>
            Liste des enseignes
        </a>
    </li>
    <li role="presentation">
        <a href="/companies_map" role="tab">
            <span class="icon">${api.icon('map-location-dot')}</span>
            Carte des enseignes
        </a>
    </li>
</ul>

<div class="tab-content content">
    <div id="list-container" class="tab-pane fade in active" role="tabpanel">
        <div>
            ${records.item_count} Résultat(s)
        </div>
        <div class='table_container'>
            <table class="hover_table">
                <thead>
                    <tr>
                        <th scope="col" class="col_text">${sortable("Nom", "name")}</th>
                        <th scope="col" class="col_text"><span class="icon">${api.icon('envelope')}</span>Adresse e-mail</th>
                        <th scope="col" class="col_text">Entrepreneur(s)</th>
                        <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                    </tr>
                </thead>
                <tbody>
                    % for company in records:
                        <tr>
                            <td class="col_text">
                                <% company_url = request.route_path('/companies/{id}', id=company.id) %>
                                % if api.has_permission('company.view', company):
                                    <a href="${company_url}"><strong>${company.name}</strong> (<small>${company.goal}</small>)</a>
                                    % if api.has_permission('global.company_view', company):
                                        ${company_list_badges(company)}
                                    % endif
                                % else:
                                    ${company.name} (<small>${company.goal}</small>)
                                % endif
                            </td>
                            <td class="col_text">
                                <a href="mailto:${company.email}" title="Envoyer un e-mail à cette adresse" aria-label="Envoyer un e-mail à cette adresse">
                                    ${company.email}
                                </a>
                            </td>
                            <td class="col_text">
                                <ul>
                                    % for user in company.employees:
                                        <li>
                                            % if api.has_permission('context.view_user', user):
                                                <a href="${request.route_path('/users/{id}', id=user.id)}">
                                                    ${api.format_account(user)}
                                                </a>
                                                % if user.login is None:
                                                    <small>
                                                        <span class="icon tag caution">
                                                            ${api.icon('exclamation-circle')}
                                                            Ce compte ne dispose pas d’identifiants
                                                        </span>
                                                    </small>
                                                % elif not user.login.active:
                                                    <br><small>${login_disabled_msg()}</small>
                                                % endif
                                            % else:
                                                ${api.format_account(user)}
                                            % endif
                                        </li>
                                    % endfor
                                </ul>
                            </td>
                            ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(company))}
                        </tr>
                    % endfor
                </tbody>
            </table>
        </div>
        ${pager(records)}
    </div>
</div>
</%block>

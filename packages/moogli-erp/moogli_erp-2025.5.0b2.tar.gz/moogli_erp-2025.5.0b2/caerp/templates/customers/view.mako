<%inherit file="${context['main_template'].uri}" />


<%block name='mainblock'>
<div id="customer_general_tab">
    <div class="layout flex two_cols separate_bottom content_vertical_padding">
        <div class='document_summary'>
            <h2>Informations générales</h2>
            ${request.layout_manager.render_panel('third_party_general_info', context=customer)}
            % if hasattr(next, 'after_summary'):
                ${next.after_summary()}
            % endif
        </div>
        <div class="status_history hidden-print memos">
            Chargement des mémos…
        </div>
    </div>

    <div class="layout flex two_cols content_vertical_padding">
        <div class='documents_summary'>
            <h2>Informations comptables</h2>
            ${request.layout_manager.render_panel('third_party_accounting_info', context=customer)}
        </div>
        <div class="folders">
            <h2>Dossiers</h2>
            <div class='panel-body'>
                <table class="${'hover_table' if customer.projects else ''}">
                %if customer.projects:
                    <thead>
                        <tr>
                            <th scope="col">Code</th>
                            <th scope="col" class="col_text">Nom</th>
                            <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                        </tr>
                    </thead>
                    <tbody>
                %else:
                    <tbody>
                        <tr>
                            <td class="col_text">
                                <em>Aucun dossier n’a été initié avec ce client</em>
                            </td>
                        </tr>
                %endif
                    % for project in customer.projects:
                        <% url = request.route_path('/projects/{id}', id=project.id) %>
                        <% onclick = "document.location='{url}'".format(url=url) %>
                        <% tooltip_title = "Cliquer pour voir ou modifier le dossier « " + project.name + " »" %>
                        %if project.archived:
                            <tr class='row_archive' id="${project.id}">
                        %else:
                            <tr id="${project.id}">
                        %endif
                                <td onclick="${onclick}" title="${tooltip_title}">${project.code}</td>
                                <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                                    ${project.name}
                                    %if project.archived:
                                        (ce dossier a été archivé)
                                    %endif
                                </td>
                                ${request.layout_manager.render_panel(
                                  'action_buttons_td',
                                  links=stream_project_actions(project),
                                )}
                            </tr>
                        %endfor
                    </tbody>
                    <tfoot>
                        <tr>
                            <td class="col_actions" colspan="3">
                                <a class='btn icon' href='${add_project_url}' title="Créer un nouveau dossier avec ce client" aria-label="Créer un nouveau dossier avec ce client">
                                    ${api.icon('folder-plus')}
                                    Nouveau dossier
                                </a>
                            </td>
                        </tr>
                        <tr>
                            <td class="col_text" colspan="3">
                                <div class="content_vertical_padding deform_inline_flex" id='add-project-form'>
                                    ${project_form.render()|n}
                                </div>
                            </td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>
    </div>
</div>
</%block>

<%block name='footerjs'>
AppOption = {};
% for key, value in js_app_options.items():
AppOption["${key}"] = "${value}"
% endfor;
</%block>

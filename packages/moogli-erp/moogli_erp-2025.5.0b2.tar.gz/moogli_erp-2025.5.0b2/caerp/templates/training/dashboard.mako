<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>

% if trainer_datas_links:
    <div class="separate_bottom">
        <h3>Liens utiles</h3>
        <div>
            % for link in trainer_datas_links:
                ${request.layout_manager.render_panel('link', context=link)}
            % endfor
        </div>
    </div>
% endif

${searchform()}

<div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
        <table class="top_align_table hover_table">
            <thead>
                <tr>
                    <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
                    <th scope="col" class="col_text">Intitulé de la formation</th>
                    <th scope="col" class="col_text">Enseigne</th>
                    <th scope="col" class="col_text">Client</th>
                    <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                </tr>
            </thead>
            <tbody>
            % if records:
                % for id_, record in records:
                    <tr>
                        <td class="col_status"
                        % if record.status == 'success':
                            title="Complète"
                            aria-label="Complète"
                        % else:
                            title="Des éléménts sont manquants"
                            aria-label="Des éléménts sont manquants"
                        % endif
                        >
                            <span class='icon status ${record.status}'>${api.icon(record.status)}</span>
                        </td>
                        <td class="col_text">${record.name | n}</td>
                        <td class="col_text">${record.project.company.full_label | n}</td>
                        <td class="col_text">
                            % if record.tasks:
                                ${record.tasks[0].customer.label | n}
                            % else:
                                <em>Cette affaire est vide</em>
                            % endif
                        </td>
                        <td class='col_actions width_one'>
                            ${request.layout_manager.render_panel(
                              'menu_dropdown',
                              label="Actions",
                              links=stream_actions(record),
                            )}
                        </td>
                    </tr>
                % endfor
            % else:
                <tr>
                    <td colspan="4" class="col_text"><em>Aucun élément n'a été retrouvé</em></td>
                </tr>
            % endif
            </tbody>
        </table>
    </div>
    ${pager(records)}
</div>
</%block>

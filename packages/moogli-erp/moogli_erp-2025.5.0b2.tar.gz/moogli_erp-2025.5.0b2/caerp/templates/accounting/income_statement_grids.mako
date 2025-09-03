<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>

${searchform()}

% if records is not None:
    <div>
        <div>
            ${records.item_count} Résultat(s)
        </div>
        <div class='table_container'>
            % if records:
            <table class="hover_table">
                <thead>
                    <tr>
                        <th scope="col" class="col_text">${sortable("Enseigne", "company")}</th>
                        <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                    </tr>
                </thead>
                <tbody>
                    % for record in records:
                        <tr>
                            <td class="col_text">Compte de résultat de l'enseigne ${record.name}</td>
                            ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(record))}
                        </tr>
                    % endfor
                </tbody>
            </table>
            % else:
            <table>
                <tbody>
                    <tr>
                        <td class="col_text">Aucun état n'a été généré</td>
                    </tr>
                </tbody>
            </table>
             % endif
        </div>
        ${pager(records)}
    </div>
% endif
</%block>

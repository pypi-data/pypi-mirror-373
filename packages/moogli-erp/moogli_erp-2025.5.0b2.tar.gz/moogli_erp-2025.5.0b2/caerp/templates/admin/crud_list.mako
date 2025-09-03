<%doc>
:param str addurl: The url for adding items
:param str actions: List of actions buttons in the form [(url, label, icon, css, btn_type)]
:param list columns: The list of columns to display
:param list items: A list of dict {'id': <element id>, 'columns': (col1, col2), 'active': True/False}
:param obj stream_columns: A factory producing column entries [labels]
:param obj stream_actions: A factory producing action entries [(url, label, title, icon)]

:param str warn_msg: An optionnal warning message
:param str help_msg: An optionnal help message
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%block name='actionmenucontent'>
% if (addurl is not UNDEFINED and addurl is not None) or actions is not UNDEFINED:
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        % if addurl is not UNDEFINED and addurl is not None:
        <a class='btn btn-primary'
            href="${addurl}"
            title="Ajouter un élément à la liste"
        >
        ${api.icon('plus')} Ajouter
        </a>
        % endif
        % if actions is not UNDEFINED:
        <div role="group">
        % for link in actions:
            ${request.layout_manager.render_panel(link.panel_name, context=link)}
        % endfor
        </div>
        % endif
    </div>
</div>
% endif
</%block>
<%block name='afteradminmenu'>
<div>
    ${request.layout_manager.render_panel('help_message_panel', parent_tmpl_dict=context.kwargs)}
</div>
</%block>
<%block name='content'>
    <div>
        % if widget is not UNDEFINED:
        ${request.layout_manager.render_panel(widget)}
        % endif
        % if column_width is UNDEFINED:
            % if len(columns) > 4:
                % if len(columns) > 6:
                <% column_width_css = "width80" %>
                % else:
                <% column_width_css = "width60" %>
                % endif
            % else:
                <% column_width_css = "width40" %>
            % endif
        % else:
        <% column_width_css = column_width %>
        % endif
        <div class='table_container limited_width ${column_width_css}'>
            <table class='top_align_table hover_table'>
                <thead>
                    <tr>
                    % for column in columns:
                        % if isinstance(column, dict):
                        <th scope="col" class="${column.get('css')}">
                            ${column.get('label', "")}
                        </th>
                        % else:
                            % if loop.first:
                            <% css = "col_text" %>
                            % else:
                            <% css = "col_icon" %>
                            % endif
                            <th scope="col" class="${css}">
                                ${column}
                            </th>
                        % endif
                    % endfor
                        <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                    </tr>
                </thead>
                <tbody>
                % for item in items:
                    <tr
                        % if hasattr(item, 'active') and not item.active:
                            class="locked" title="Cet élément est désactivé"
                        % endif
                    >
                        % for index, value in enumerate(stream_columns(item)):
                            <% column = columns[index] %>
                            % if isinstance(column, dict):
                                <% css = column.get('css', 'col_text') %>
                            % else:
                               % if loop.first:
                                <% css = "col_text" %>
                              % else:
                                <% css = "col_icon" %>
                              % endif  
                            % endif
                            <td class="${css}">
                                % if loop.first and hasattr(item, 'active') and not item.active and  value is not None:
                                <span class="icon">${api.icon('lock')}</span>${ value|n }
                                % elif value is not None:
                                    ${ value|n }
                                % endif
                            
                            </td>
                        % endfor
                        ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(item))}
                    </tr>
                % endfor
                % if not items:
                    <tr><td colspan='${len(columns) + 1}' class="col_text">
                        % if nodata_msg is not UNDEFINED and nodata_msg is not None:
                            ${nodata_msg|n}
                        % else:
                            <em>Aucun élément configuré</em>
                        % endif
                    </td></tr>
                % endif
                </tbody>
            </table>
        </div>
    </div>
</%block>

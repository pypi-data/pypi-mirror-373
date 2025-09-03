<%doc>
    Administration des rôles de l’application
</%doc>

<%inherit file="${context['main_template'].uri}" />

<%block name='actionmenucontent'>
% if (addurl is not UNDEFINED and addurl is not None) or actions is not UNDEFINED:
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        % if addurl is not UNDEFINED and addurl is not None:
            <a class='btn btn-primary' href="${addurl}" title="Ajouter un nouveau rôle dans l’application">
                ${api.icon('plus')} Ajouter un rôle
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

<%block name='content'>
    % for group in items:
        <% data=stream_columns(group) %>
        <div class='collapsible separate_top content_vertical_double_padding'>
            <h2 class="collapse_title">
                <a href="javascript:void(0);" 
                    onclick="toggleCollapse( this );"
                    aria-expanded="false"
                    title="Afficher le détail des droits du rôle « ${group.label} »">
                    % if not group.editable:
                        <small class="icon" title="Ce rôle n’est pas modifiable">${api.icon('lock')}<span class="screen-reader-text">Ce rôle n’est pas modifiable</span></small>
                    % endif
                    <span class="screen-reader-text">Afficher le détail des droits du rôle </span>
                    ${group.label}
                    ${api.icon('chevron-down','arrow')}
                </a>
                <small>
                    % if data["account_types"]:
                        <span class="screen-reader-text">Ce rôle est proposé à la création d'un compte : </span>
                    % endif
                    % for account_type in data["account_types"]:
                        <span class='icon tag neutral'
                            title="Ce rôle est proposé à la création d'un compte : ${account_type}"><small>${account_type}</small></span>
                    % endfor
                    % if data['user_count'] == 0:
                        <em> Aucun utilisateur ne dispose de ce rôle</em>
                    % elif data['user_count'] == 1:
                        <em> ${data['user_count']} utilisateur dispose de ce rôle</em>
                    % else:
                        <em> ${data['user_count']} utilisateurs disposent de ce rôle</em>
                    % endif
                </small>
            </h2>
            <div class="collapse_content" hidden="">
                <div class="content_vertical_padding capabilities">

                    % if group.name =='admin':
                        <div class="alert alert-warning">
                            Seul un membre du groupe admin peut créer des comptes de ce groupe
                        </div>
                    % endif

                    <div class="layout flex two_cols content_vertical_padding">
                        <div class="align_right vertical_align_center">
                            ${request.layout_manager.render_panel("action_buttons", stream_actions(group))}
                        </div>
                    </div>

                    % for category in categories.values():
                        % if category in data['rights']:
                            <% rights=data['rights'][category] %>
                            <div>
                                <h4>${api.icon('cog','icon')} ${category}</h4>
                                <ul>
                                    % for right in rights:
                                        <li>
                                            <strong>
                                                ${right['label']}
                                                % if right.get('rgpd'):
                                                    <span class="icon tag caution"
                                                        title="Ce droit donne accès à des données personnelles sensibles">RGPD
                                                        <span class="screen-reader-text">Ce droit donne accès à des données
                                                            personnelles sensibles</span>
                                                    </span>
                                                % endif
                                            </strong><br/>
                                            <small>${right['description']}</small>
                                        </li>
                                    % endfor
                                </ul>
                            </div>
                        % endif
                    % endfor

                </div>
            </div>
        </div>
    % endfor
</%block>

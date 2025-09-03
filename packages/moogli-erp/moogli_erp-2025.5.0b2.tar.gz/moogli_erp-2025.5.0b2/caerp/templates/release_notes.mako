<%inherit file="${context['main_template'].uri}" />

<%block name="content">
<div class="content_vertical_double_padding">
    % if version_es:
        <a class="btn icon" href="release_notes">
            ${api.icon('eye')} Afficher les notes de version complètes
        </a>
    % else:
        <a class="btn icon" href="release_notes?version_es">
            ${api.icon('eye')} Afficher la version dédiée aux entrepreneurs
        </a>
    % endif
</div>
<br/>
% for version in release_notes:
    <%
    if version['is_last_version']:
        visibility = ""
        expanded = "true"
        tooltip = "Masquer cette version"
    else:
        visibility = "hidden"
        expanded = "false"
        tooltip = "Afficher cette version"
    %>
    <div class="version collapsible">
        <div class="separate_block">
            <h2 class="title collapse_title">
                <a href="javascript:void(0);" onclick="toggleCollapse( this );" aria-expanded="${expanded}" title="${tooltip}" aria-label="${tooltip}">
                    ${api.icon("chevron-down", "arrow")}
                    Version ${version["version"]} <small>${version["date"]}</small>
                </a>
            </h2>
            <div class="collapse_content" ${visibility}>
                <div class="content">
                % if len(version["notes"]) > 0:
                    <ul class="version_notes">
                    % for note in version["notes"]:
                        <li>
                            <h4>
                                % if note["category"] == "bugfix":
                                    <span class="icon">${api.icon("wrench")}</span>
                                % else:
                                    <span class="icon">${api.icon("star")}</span>
                                % endif
                                ${note["title"]}
                                % for sponsor in note["sponsors"]:
                                    <span class="icon tag neutral" title="Financé par ${sponsor}">${api.icon("euro-sign")}<span class="screen-reader-text">Financé par</span> ${sponsor}</span>
                                % endfor
                            </h4>
                            % for description in note["description"]:
                                % if len(note["description"]) > 1:
                                    <p class="note_description">&bull; ${description}</p>
                                % else:
                                    <p class="note_description">${description}</p>
                                % endif
                            % endfor
                            % if "link" in note:
                                <span class="icon">${api.icon("link")}</span>
                                <a class="note_link" href="${note['link']['url']}" target="_blank">${note["link"]['title']}</a>
                            % endif
                        </li>
                    % endfor
                    </ul>
                % endif
                </div>
            </div>
        </div>
    </div>
% endfor
</%block>

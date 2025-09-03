<div id="project_files_tab">
    % if api.has_permission(add_perm):
    	<div class="content_vertical_padding separate_bottom_dashed">
    		<button class="btn btn-primary" onclick="window.openPopup('${add_url}');" title="Ajouter un fichier (s’ouvrira dans une nouvelle fenêtre)" aria-label="Ajouter un fichier (s’ouvrira dans une nouvelle fenêtre)">
    			${api.icon("paperclip")}
    			Ajouter un fichier
    		</button>
    	</div>
    % endif

    % if help_message is not UNDEFINED and help_message is not None:
        <div class='alert alert-info'>
            <span class="icon">${api.icon("info-circle")}</span>
            ${help_message | n}
        </div>
    % endif

    <div class="table_container">
        <table class="hover_table">
            % if files.count() > 0:
            <thead>
                % if show_parent:
                    <th scope="col" class="col_text">Est attaché à</th>
                % endif
                <th scope="col" class="col_text">Type de document</th>
                <th scope="col" class="col_text">Nom du fichier</th>
                <th scope="col" class="col_date">Déposé le</th>
                <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
            </thead>
            % endif
            <tbody>
            % for doc in files:
    			<% url = request.route_path("/users/{id}/userdatas/filelist/{id2}", id=request.context.id, id2=doc.id) %>
    			<% onclick = "document.location='{url}'".format(url=url) %>
    			<% tooltip_title = "Cliquer pour voir ou modifier ce document" %>
                <tr>
                    % if show_parent:
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${parent_label(doc)}</td>
                    % endif
                    <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                        % if doc.file_type_id:
                            ${doc.file_type.label}
                        % else:
                            <em>Non spécifié</em>
                        % endif
                    </td>
                    <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${doc.name}</td>
                    <td class="col_date" onclick="${onclick}" title="${tooltip_title}">${api.format_date(doc.updated_at)}</td>
                    ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(request, doc))}
                </tr>
            % endfor
            % if files.count() == 0:
                % if show_parent:
                    <% nb_cols = 6 %>
                % else:
                    <% nb_cols = 5 %>
                % endif
                <tr>
                    <td class="col_text" colspan="${nb_cols}"><em>Aucun fichier disponible</em></td>
                </tr>
            % endif
            </tbody>
        </table>
    </div>
</div>
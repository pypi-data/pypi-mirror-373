<%def name="showfile(file_object)">
<div>
    <dl class='dl-horizontal'>
        <dt>Description du fichier</dt><dd>${file_object.description}</dd>
        <dt>Taille du fichier</dt><dd>${api.human_readable_filesize(file_object.size)}</dd>
        <dt>Dernière modification</dt><dd>${api.format_date(file_object.updated_at)}</dd>
    </dl>
    ${request.layout_manager.render_panel('menu_dropdown', label="Actions", links=stream_actions(request, file_object))}
</div>
</%def>
<div role="tabpanel" class="tab-pane row" id="attached_files" aria-labelledby="attached_files-tabtitle">
    <div class="content_vertical_padding separate_bottom">
        <button class='btn btn-primary'
            onclick="window.openPopup('${add_url}')"
            title="Attacher un fichier (s’ouvrira dans une nouvelle fenêtre)"
            aria-label="Attacher un fichier (s’ouvrira dans une nouvelle fenêtre)">
            ${api.icon("paperclip")}
            Attacher un fichier
        </button>
    </div>
    <div class="content_vertical_padding">
        <h3>${title}</h3>
        <div class='table_container'>
            <table class='hover_table'>
            	% if files:
            	<thead>
            		<tr>
            			<th scope="col" class="col_text">Description</th>
            			<th scope="col" class="col_number" title="Taille du fichier">Taille<span class="screen-reader-text"> du fichier</span></th>
            			<th scope="col" class="col_date" title="Date de la dernière modification"><span class="screen-reader-text">Date de la dernière </span>Modification</th>
						<th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
            		</tr>
            	</thead>
            	% endif
                <tbody>
	            	% if files:
						% for file_object in files:
						<% url = request.route_path("userdatas_file", id=request.context.id, id2=file_object.id) %>
						<% onclick = "document.location='{url}'".format(url=url) %>
						<% tooltip_title = "Cliquer pour voir ou modifier ce fichier" %>
						<tr>
							<td class="col_text" onclick="${onclick}" title="${tooltip_title}">${file_object.description}</td>
							<td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.human_readable_filesize(file_object.size)}</td>
							<td class="col_date" onclick="${onclick}" title="${tooltip_title}">${api.format_date(file_object.updated_at)}</td>
							<td class="col_actions width_one">
								${request.layout_manager.render_panel('menu_dropdown', label="Actions", links=stream_actions(request, file_object))}
							</td>
						</tr>
						% endfor
					% else:
						<tr>
							<td class="col_text" colspan="4"><em>Aucun fichier</em></td>
						</tr>
			        % endif
                </tbody>
            </table>
        </div>
    </div>
</div>

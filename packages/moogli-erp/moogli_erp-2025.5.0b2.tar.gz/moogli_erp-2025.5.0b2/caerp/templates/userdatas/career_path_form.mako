<%doc>
    Career path form rendering
</%doc>

<%inherit file="${context['main_template'].uri}" />

<%block name="mainblock">
    ${request.layout_manager.render_panel(
        'help_message_panel',
        parent_tmpl_dict=context.kwargs
    )}
    <div>
        ${form|n}
    </div>



    % if files:
	<div class="content_vertical_padding separate_top">
		<h3>Documents attachés à cette étape</h3>
		<div class="table_container">
			<table class='hover_table'>
				<thead>
					<th scope="col" class="col_text">Fichier</th>
					<th scope="col" class="col_number" title="Taille du fichier">Taille<span class="screen-reader-text"> du fichier</span></th>
		            <th scope="col" class="col_date">Modifié le</th>
					<th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
				</thead>
				<tbody>
				% for file in files:
					<% edit_url = request.route_path('/users/{id}/userdatas/filelist/{id2}', id=request.context.userdatas.id, id2=file.id) %>
	                <% onclick = "document.location='{edit_url}'".format(edit_url=edit_url) %>
		 			<% tooltip_title = "Cliquer pour modifier le fichier « " + file.description + " »"  %>
					<% del_url = request.route_path('/files/{id}', id=file.id, _query=dict(action='delete')) %>
					<tr>
						<td class="col_text" onclick="${onclick}" title="${tooltip_title}">${file.description}</td>
						<td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.human_readable_filesize(file.size)}</td>
						<td class="col_date" onclick="${onclick}" title="${tooltip_title}">${api.format_date(file.updated_at)}</td>
						<td class="col_actions width_two">
							<ul>
								<li>
									<a href="${edit_url}" class="btn icon only" title="Modifier ce document" aria-label="Modifier ce document">
										${api.icon("pen")}
									</a>
								</li>
								<li>
									<a href="${del_url}" class="btn icon only negative" onclick="return confirm('Êtes vous sûr de vouloir supprimer ce document ?')" title="Supprimer ce document" aria-label="Supprimer ce document">
										${api.icon("trash-alt")}
									</a>
								</li>
							</ul>
						</td>
					</tr>
				% endfor
				</tbody>
			</table>
		</div>
	</div>
    % endif


    <script type='text/javascript'>
    $( function() {
        const setParcoursSalaryValue = () => {
            const hourly_rate = $('input[name=taux_horaire]').val();
            const num_hours = $('input[name=num_hours]').val();
            $('input[name=parcours_salary]')
                    .val(hourly_rate * num_hours).attr('readonly', true)
        }
        $('input[name=parcours_salary]').attr('readonly', true)
        $('input[name=taux_horaire], input[name=num_hours]').change(
                function () {
                    setParcoursSalaryValue();
                }
        );
    });
    </script>

</%block>

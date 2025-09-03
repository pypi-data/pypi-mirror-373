<%inherit file="${context['main_template'].uri}" />
<%block name='content'>
<div class='row'>
    <% keys = list(documents.keys()) %>
    <% keys.sort(reverse=True) %>
    % for year in keys:
	<% subdirs = documents[year] %>
    % if year in current_years:
    <% 
        section_hidden = ''
        expanded = 'true'
        tooltip = 'Masquer cette année'
    %>
    %else:
    <% 
        section_hidden = 'hidden'
        expanded = 'false'
        tooltip = 'Afficher cette année'
    %>
    %endif
	<div class='collapsible panel panel-default page-block'>
		<h2 class='collapse_title panel-heading'>
           <a href="javascript:void(0);" onclick="toggleCollapse( this );" aria-expanded='${expanded}' title='${tooltip}' aria-label='${tooltip}'>
                <span class="icon">${api.icon('folder-open')}</span>
                ${year}
			</a>
		</h2>
		<div class='table_container' ${section_hidden}>
			<table class="hover_table">
				<thead>
					<tr>
						<th scope="col" class="col_text">Mois</th>
						<th scope="col" class="col_text">Nom du fichier</th>
						<th scope="col" class="col_number">Taille</th>
						<th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
					</tr>
				</thead>
				<tbody>
			<% months = list(subdirs.keys()) %>
			<% months.sort(key=lambda m:int(m), reverse=True) %>
			% for month in months:
				<% files = subdirs[month] %>
				% for file_ in files:
					<tr>
						<td class="col_text">${api.month_name(int(month))}</td>
						<td class="col_text">${file_.name}</td>
						<td class="col_number">${file_.size}</td>
						<td class="col_actions width_one">
							<a href="${file_.url(request)}" class="btn icon only" title="Télécharger" aria-label="Télécharger">
                            	${api.icon('download')}
							</a>
						</td>
					</tr>
				% endfor
			% endfor
			% if not months:
					<tr><td colspan='4' class='col_text' tabindex='0'><em>Aucun document n’est disponible</em></td></tr>
			% endif
				</tbody>
			</table>
		</div>
	</div>
    % endfor
    % if not keys:
    <div class='panel panel-default page-block'>
        <div class='panel-body' tabindex='0'><em>Aucun document n’est disponible</em></div>
    </div>
    % endif
</div>
</%block>

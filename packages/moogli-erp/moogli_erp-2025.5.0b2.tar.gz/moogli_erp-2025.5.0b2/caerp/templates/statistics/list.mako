<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="table_btn"/>

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
	<div class='layout flex main_actions'>
		${request.layout_manager.render_panel('action_buttons', links=links)}
	</div>
</div>
</%block>

<%block name='afteractionmenu'>
<div class="alert alert-warning">
	<span class="icon">${api.icon('exclamation-triangle')}</span>
	Cet outil est obsolète.<br>
	Vous pouvez utiliser le menu <a href="/dataqueries">Requêtes statistiques</a> qui présente une liste de requêtes. Si vous ne trouvez pas de requête répondant à votre besoin, vous pouvez contacter le support pour en faire développer une.
</div>
<div class="alert alert-info">
	<span class="icon">${api.icon('info-circle')}</span>
	Configuration des modèles statistiques :
	<ul>
		<li>Ajouter une feuille de statistiques</li>
		<li>Composer vos entrées statistiques à l’aide de un ou plusieurs critères</li>
		<li>Générer les fichiers de sorties</li>
	</ul>
</div>
</%block>

<%block name='content'>
<div class="content_vertical_padding limited_width width40">
    <div class="table_container">
		<table class='hover_table'>
		<thead>
			<tr>
				<th scope="col" class="col_text">Nom de la feuille de statistiques</th>
				<th scope="col" class="col_date">Modifiée le</th>
				<th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
			</tr>
		</thead>
		<tbody>
		% for sheet in sheets:
			<tr
				% if not sheet.active:
					class="locked"
				% endif
				>
				<td class="col_text">${sheet.title}</td>
				<td class="col_date">${api.format_date(sheet.updated_at)}</td>
                ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(sheet))}
			</tr>
		% endfor
		</tbody>
		</table>
    </div>
</div>
</%block>

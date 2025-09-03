<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%block name='afteradminmenu'>
</%block>
<%block name='content'>
<div>
	<div class='search_filters'>
		<form class='form-search form-inline' method='GET'>
			<div class='form-group'>
				<label class='control-label' for='business_filter'>Type d'affaire</label>
				<select id='business_filter' class='form-control' name='business'>
					<option value='0'>Tous les types d'affaire</option>
					% for business_type in business_types_all:
						% if business_filter == business_type.id:
							<option value='${business_type.id}' selected>${business_type.label}</option>
						% else:
							<option value='${business_type.id}'>${business_type.label}</option>
						% endif
					% endfor
				</select>
			</div>
			<div class='form-group'>
				<label class='control-label' for='file_filter'>Type de fichier</label>
				<select id='file_filter' class='form-control' name='file'>
					<option value='0'>Tous les types de fichier</option>
					% for file_type in file_types_all:
						% if file_filter == file_type.id:
							<option value='${file_type.id}' selected>${file_type.label}</option>
						% else:
							<option value='${file_type.id}'>${file_type.label}</option>
						% endif
					% endfor
				</select>
			</div>
			<div>
				<button class='btn btn-primary' type='submit'>Rechercher</button>
			</div>
		</form>
	</div>
	<form method='POST'
		class="deform  deform" accept-charset="utf-8"
		enctype="multipart/form-data">
		<input type='hidden' name='__start__' value='items:sequence' />
		% for business_type in business_types:
		<h2>${business_type.label}</h2>
		<div class="table_container separate_bottom">
			<table class='top_align_table'>
				<thead>
					<tr>
						<th scope="col" class="col_text">Type de fichier</th>
						<th scope="col" class="col_action">Modèle de document</th>
						% if business_type.name != 'default':
							<th scope="col" class="col_text">Affaire</th>
						% endif
						<th scope="col" class="col_text">Devis</th>
						<th scope="col" class="col_text">Factures</th>
						<th scope="col" class="col_text">Avoirs</th>
					</tr>
				</thead>
				<tbody>
				% for file_type in file_types:
					<% file_type_items = items.get(file_type.id, {}) %>
					<tr>
						<td class="col_text form">
							${file_type.label}							
						</td>
						<td class="col_action">
							<% file_type_templates = templates.get(file_type.id, {}) %>
							<% template = file_type_templates.get(business_type.id, {}) %>
							% if template:
								<div class='content_vertical_padding'>
									<a href="/files/${template['file_id']}?action=download"  title="Télécharger ce fichier" aria-label="Télécharger ce fichier">
										<span class="icon">${api.icon('download')}</span>
										${template['file_name']}
									</a>
								</div>
								<button class='btn btn-primary negative icon only' name='del_template' type='submit' value='${business_type.id}__${file_type.id}' title='Supprimer le modèle « ${template['file_name']} »' aria-label='Supprimer le modèle « ${template['file_name']} »'>
									${api.icon('trash-alt')}
								</button>
							% else:
								<div class='content_vertical_padding'><em>Aucun modèle défini</em></div>
								<button class='btn btn-primary icon only' type='button' onclick='window.openPopup("${add_template_url}?business=${business_type.id}&file=${file_type.id}");' title="Ajouter un modèle (s’ouvrira dans une nouvelle fenêtre)" aria-label="Ajouter un modèle (s’ouvrira dans une nouvelle fenêtre)">
									${api.icon('plus')}
								</button>
							% endif
						</td>
						<% btype_items = file_type_items.get(business_type.id, {}) %>
						% for doctype in ('business', 'estimation', 'invoice', 'cancelinvoice'):
							% if business_type.name == 'default' and doctype == 'business':
							<% continue %>
							% endif
						<% requirement_type = btype_items.get(doctype, {}).get('requirement_type', -1) %>
						<% validation = btype_items.get(doctype, {}).get('validation') %>
						<% tag_id = "requirement_type_%s_%s_%s" % (file_type.id, business_type.id, doctype) %>
						<td class="col_text">
							<input type='hidden' name='__start__' value='item:mapping' />
							<input type='hidden' name='file_type_id' value='${file_type.id}' />
							<input type='hidden' name='business_type_id' value='${business_type.id}'/>
							<input type='hidden' name='doctype' value='${doctype}' />
							<select name="requirement_type" class="form-control" id="requirement_type">
							
							<option value=''
								% if requirement_type == -1:
								selected
								% endif
								>N'est pas proposé
							</option>
							
							% for option, label in (\
								('optionnal', 'Est proposé'), \
								('recommended', 'Est recommandé'), \
								('mandatory', 'Est requis systématiquement'), \
								('business_mandatory', "Est requis dans l'affaire"), \
								('project_mandatory', "Est requis dans le dossier")):
								% if doctype == 'business' and option == 'mandatory':
								<% continue %>
								% endif
								<option value="${option}"
									% if requirement_type == option:
									selected
									% endif
									>
									${label}
								</option>
							% endfor
							</select>
							<hr />
							<div class="checkbox">
							<label>
							  <input type="checkbox" name="validation"
							  % if validation:
							  checked
							  % endif
							  >
							  <span>Exige une validation&nbsp;?</span>
							</label>
							</div>
						<input type='hidden' name='__end__' value='item:mapping' />
						</td>
					% endfor
					</tr>
					% endfor
				</tbody>
			</table>
		</div>
		% endfor
		<input type='hidden' name='__end__' value='items:sequence' />
		<div class='form-actions'>
		   <button id="deformsubmit" class="btn btn-primary" value="submit" type="submit" name="submit"> Enregistrer </button>
		</div>
	</form>
</div>
</%block>

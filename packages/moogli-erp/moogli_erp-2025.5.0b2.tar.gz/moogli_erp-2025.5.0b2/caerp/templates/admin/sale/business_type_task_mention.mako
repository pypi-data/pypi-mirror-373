<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%block name='afteradminmenu'>
</%block>
<%block name='content'>
<div>
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
						<th scope="col" class="col_text">Mentions</th>
						<th scope="col" class="col_text">Devis</th>
						<th scope="col" class="col_text">Factures</th>
						<th scope="col" class="col_text">Avoirs</th>
					</tr>
				</thead>
				<tbody>
				% for mention in mentions:
					<% mention_items = items.get(mention.id, {}) %>
					<tr>
						<th scope="row" class="col_text">${mention.label}</th>
						<% btype_items = mention_items.get(business_type.id, {}) %>
						% for doctype in ('estimation', 'invoice', 'cancelinvoice'):
						<% mandatory = btype_items.get(doctype, -1) %>
						<% tag_id = "mandatory_%s_%s_%s" % (mention.id, business_type.id, doctype) %>
						<td class="col_text">
							<input type='hidden' name='__start__' value='item:mapping' />
							<input type='hidden' name='task_mention_id' value='${mention.id}' />
							<input type='hidden' name='business_type_id' value='${business_type.id}'/>
							<input type='hidden' name='doctype' value='${doctype}' />
							<select class='form-control' name='mandatory'>
								<option value=''
								% if mandatory == -1:
								selected
								% endif
								>
								Non utilisée</option>
								<option value='false'
								% if not mandatory:
								selected
								% endif
								>
								Facultative</option>
								<option value='true'
								% if mandatory == True:
								selected
								% endif
								>
								Obligatoire
							</option>
							</select>
							 
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

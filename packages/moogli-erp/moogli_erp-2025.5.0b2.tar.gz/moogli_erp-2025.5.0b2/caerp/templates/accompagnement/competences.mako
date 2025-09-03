<%inherit file="${context['main_template'].uri}" />
<%block name="content">
<div>
	<form method='POST' enctype="multipart/form-data" accept-charset="utf-8">
		<div class="limited_width width40">
			% if api.has_permission('global.manage_competence', request.context):
			<div class="form-group content_vertical_padding">
				<label for="contractor_id">Entrepreneur à évaluer</label>
				<select name='contractor_id' class='form-control'>
					% for id, label in user_options:
						<option value='${id}'>${label}</option>
					% endfor
				</select>
			</div>
			% else:
			<h2>Mes compétences</h2>
			<input type="hidden" name='contractor_id' value="${request.context.id}" />
			% endif
			<div class="content_vertical_padding">
				<span class="label">Choisissez une échéance</span>
				<div class='btn-group' role='group'>
					<ul>
						% for deadline in deadlines:
						<li>
							<button
								class='btn'
								type='submit'
								name='deadline'
								value='${deadline.id}'>
								${deadline.label}
							</button>
						</li>
						% endfor
					</ul>
				</div>
			</div>
		</div>
	</form>
</div>
</%block>
<%block name="footerjs">
% if api.has_permission('global.manage_competence', request.context):
$('select[name=contractor_id]').select2({language: $.fn.select2.amd.require("select2/i18n/fr")});
% endif
</%block>

<%inherit file="/workshops/workshop_base.mako" />
<%namespace file="/base/utils.mako" import="definition_list"/>

<%block name='actionmenucontent'>
% if action_buttons:
	<div class='main_toolbar action_tools'>
		<div class='layout flex main_actions'>
    		${request.layout_manager.render_panel("action_buttons", links=action_buttons)}
		</div>
	</div>
% endif
</%block>

<%block name="after_details">
<div>
    <h2>Horaires et présence</h2>
    <div class="table_container">
		<table class="hover_table">
			<thead>
				<tr>
					<th scope="col" class="col_text">Nom de la tranche horaire</th>
					<th scope="col" class="col_text">Dates et horaires</th>
					<th scope="col" class="col_text">Votre statut</th>
				</tr>
			</thead>
			<tbody>
				% for label, time_str, status in timeslots_datas:
					<tr>
						<td class="col_text">${label}</td>
						<td class="col_text">${time_str}</td>
						<td class="col_text">${status}</td>
					</tr>
				% endfor
			</tbody>
		</table>
    </div>
</div>
</%block>

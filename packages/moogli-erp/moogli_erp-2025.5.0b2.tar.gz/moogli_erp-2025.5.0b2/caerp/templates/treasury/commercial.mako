<%inherit file="${context['main_template'].uri}" />
<%block name='content'>
<div class="separate_bottom flex layout two_cols third">
	<div class="year_filter">
		${year_form.render()|n}
	</div>
	<div>
		<h2>
			Résumé
		</h2>
		<table class="spaced_table">
			<tr>
				<th scope="row">Nombre de devis rédigés</th>
				<td class="col_number">${estimations}</td>
			</tr>
			<tr>
				<th scope="row">Nombre de devis concrétisés</th>
				<td class="col_number">${validated_estimations}</td>
			</tr>
			<tr>
				<th scope="row">Nombre de clients</th>
				<td class="col_number">${customers}</td>
			</tr>
		</table>
	</div>
</div>
<div>
	<div class='text_block'>
		<h2>
    		Année ${year}
		</h2>
	</div>
	<div class='table_container scroll_hor'>
		<table class='hover_table'>
			<thead>
				<th scope="col" class="col_text">Description</th>
				% for i in range(1, 13):
					<th scope="col" class="col_number" title="${api.month_name(i).capitalize()}" aria-label="${api.month_name(i).capitalize()}">${api.short_month_name(i).capitalize()}</th>
				% endfor
				<th scope="col" class="col_number" title="Total annuel">Total<span class="screen-reader-text"> annuel</span></th>
			</thead>
			<tbody>
				<tr>
					<th scope="col" class="col_text">CA prévisionnel</th>
					% for i in range(1, 13):
						<% turnover = turnover_projections.get(i) %>
							% if turnover:
								<td id='ca_prev_${i}' title='${turnover.comment}' class='col_number with_edit_button'>
									<span>${api.format_amount(turnover.value, trim=True, precision=5)}</span>
							% else:
								<td id='ca_prev_${i}' class='col_number with_edit_button'>
							% endif
							<a href='#setform'
								class='btn icon unstyled'
								% if turnover:
									title='${turnover.comment}' onclick='setTurnoverProjectionForm("${i}", "${api.month_name(i)}", "${year}", "${api.format_amount(turnover.value, grouping=False, precision=5)}", this);'>
								% else:
									title='Modifier le CA du mois de ${api.month_name(i).capitalize()}'
									onclick='setTurnoverProjectionForm("${i}", "${api.month_name(i)}", "${year}");'>
								% endif
								${api.icon('pen')}
								<span class="screen-reader-text">Modifier le CA du mois de ${api.month_name(i).capitalize()}</span>
							</a>
						</td>
					% endfor
					<td class="col_number total">
						${api.format_amount(turnover_projections['year_total'], trim=True, precision=5)}
					</td>
				</tr>
				<tr>
					<th scope="col" class="col_text">CA réalisé</th>
					% for i in range(1, 13):
						<td class='col_number'>${api.format_amount(turnovers[i], trim=True, precision=5)}</td>
					% endfor
					<td class='col_number total'>
						${api.format_amount(turnovers['year_total'], trim=True, precision=5)}
					</td>
				</tr>
				<tr>
					<th scope="col" class="col_text">Écart</th>
					% for i in range(1, 13):
						<td id='gap_${i}' class='col_number'>
							${api.format_amount(compute_turnover_difference(i, turnover_projections, turnovers), trim=True, precision=5)}
						</td>
					% endfor
					<td class='col_number total'>
						${api.format_amount(turnovers['year_total'] - turnover_projections['year_total'], trim=True, precision=5)}
					</td>
				</tr>
				<tr>
					<th scope="col" class="col_text">Pourcentage</th>
					% for i in range(1, 13):
						<td id='gap_percent_${i}' class='col_number'>
							${compute_turnover_percent(i, turnover_projections, turnovers)}&nbsp;%
						</td>
					% endfor
					<td class='col_number total'>
						${compute_percent(turnovers['year_total'], turnover_projections['year_total'], 0)}&nbsp;%
					</td>
				</tr>
			</tbody>
		</table>
	</div>
</div>

<section id="form_container" class="modal_view">
	<div role="dialog" id="prevision_add_form" aria-modal="true" aria-labelledby="prevision-forms_title">
		<div class="modal_layout">
			<header>
				<button class="icon only unstyled close" title="Fermer cette fenêtre" aria-label="Fermer cette fenêtre" onclick="$('#form_container').fadeOut('slow');">
					${api.icon('times')}
				</button>
				<h2 id="prevision-forms_title">CA prévisionnel</h2>
			</header>
			<div class="modal_content_layout" id="previsionForm">
				${form.render()|n}
			</div>
		</div>
	</div>
</section>

</%block>

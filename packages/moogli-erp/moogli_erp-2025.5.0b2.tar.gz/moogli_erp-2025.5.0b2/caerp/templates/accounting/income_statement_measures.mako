<%inherit file="${context['main_template'].uri}" />

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        <div role='group'></div>
        <div role='group'>
            <a class='btn' onclick="window.openPopup('${export_xls_url}');" href='javascript:void(0);' title="Export au format Excel (xlsx) dans une nouvelle fenêtre" aria-label="Export au format Excel (xlsx) dans une nouvelle fenêtre">
            	${api.icon('file-excel')}
                Excel
            </a>
            <a class='btn' onclick="window.openPopup('${export_ods_url}');" href='javascript:void(0);' title="Export au format Open Document (ods) dans une nouvelle fenêtre" aria-label="Export au format Open Document (ods) dans une nouvelle fenêtre">
    			${api.icon('file-spreadsheet')}        
                ODS
            </a>
        </div>
    </div>
</div>
</%block>

<%block name='content'>

<div class='search_filters'>
    ${form|n}
</div>
<div class='text_block'>
    <h2>
    	Année <strong>${selected_year}</strong>
        % if not grid.is_void and grid.get_updated_at() is not None:
            <small>Mis à jour le <strong>${grid.get_updated_at().strftime("%d/%m/%y")}</strong></small>
        % endif

        % if current_year != selected_year:
            <% url = request.route_path("/companies/{id}/accounting/income_statement_measure_grids", id=request.context.id) %>
            <small>(<a href="${url}">voir l’année courante</a>)</small>
        % endif
    </h2>
</div>

<div>
    % if not grid.is_void:
        <div class='table_container scroll_hor'>
            <button class="fullscreen_toggle small" title="Afficher le tableau en plein écran" aria-label="Afficher le tableau en plein écran" onclick="toggleTableFullscreen(this);return false;">
                ${api.icon('expand')}
                ${api.icon('compress')}
                <span>Plein écran</span>
            </button>
            <table class="compte_resultat">
                <thead>
                    <tr class="row_month">
                        <th scope="col" class="col_text" title="Indicateur"><span class="screen-reader-text">Indicateur</span></th>
                        % for i in range(1, 13):
                            <%
                            year, month = grid.columns_index[i]
                            full_label = api.month_name(month).capitalize()
                            short_label = api.short_month_name(month).capitalize()
                            if display_years_in_headers:
                                full_label += " {}".format(str(year))
                                short_label += " {}".format(str(year)[2:])
                            %>
                            <th scope="col" class="col_number" title="${full_label}" aria-label="${full_label}">${short_label}</th>
                        % endfor
                        <th scope="col" class="col_number" title="Total annuel">Total<span class="screen-reader-text"> annuel</span></th>
                        <th scope="col" class="col_number" title="Pourcentage du Chiffre d’Affaires" aria-label="Pourcentage du Chiffre d’Affaires">% CA</th>
                    </tr>
                </thead>
                <tbody
                    % if not show_decimals:
                       class="hide-decimals"
                   % endif
                >
                    % for type_, contains_only_zeroes, row in grid.rows:
                        <tr
                        % if type_.is_total:
                            class='row_recap row_number'
                        % else:
                            class='row_number'
                        % endif
                        >
                            % if show_zero_rows or not contains_only_zeroes:
                                <th scope="row">${type_.label |n }</th>
                                % for cell in row:
                                    <td class='col_number'>${cell | n}</td>
                                % endfor
                            % endif
                        </tr>
                    % endfor
                </tbody>
            </table>
        </div>
    % else:
        <h4>Aucun compte de résultat n'est disponible</h4>
    % endif
    </div>
</div>
</%block>

<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/searchformlayout.mako" import="searchform"/>
<%namespace file="/base/utils.mako" import="company_list_badges"/>

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        <div role='group'></div>
        <div role='group'>
            <a class='btn' href='${export_xls_url}' title="Export au format Excel (xlsx) dans une nouvelle fenêtre" aria-label="Export au format Excel (xlsx) dans une nouvelle fenêtre">
                ${api.icon('file-excel')} Excel
            </a>
            <a class='btn' href='${export_ods_url}' title="Export au format Open Document (ods) dans une nouvelle fenêtre" aria-label="Export au format Open Document (ods) dans une nouvelle fenêtre">
                ${api.icon('file-spreadsheet')} ODS
            </a>
        </div>
    </div>
</div>
</%block>

<%block name='content'>

<div class='search_filters'>
    ${form|n}
</div>

<div>
    <div class="table_container scroll_hor">
        <button class="fullscreen_toggle small" title="Afficher le tableau en plein écran" aria-label="Afficher le tableau en plein écran" onclick="toggleTableFullscreen(this);return false;">
            ${api.icon('expand')}
            ${api.icon('compress')}
            <span>Plein écran</span>
        </button>
        <table class="hover_table">
            <thead>
                <tr>
                    <% current_exercice_period_label = "du {} au {}".format(current_exercice['start_label'], current_exercice['end_label']) %>
                    <% previous_exercice_period_label = "du {} au {}".format(previous_exercice['start_label'], previous_exercice['end_label']) %>
                    <th scope="col" class="col_text min10" title="Vous trouverez des précisions sur les données affichées en survolant les en-têtes des colonnes">
                        Enseigne <span class="icon">${api.icon('question-circle')}</span> 
                        <span class="screen-reader-text">Vous trouverez des précisions sur les données affichées en survolant les en-têtes des colonnes</span>
                    </th>
                    <th scope="col" class="col_text min10" title="Domaine d'activité principal de l'enseigne">
                        Activité principale
                    </th>
                    <th scope="col" class="col_number" title="Total HT des factures MoOGLi ${current_exercice_period_label}">
                        C<span class="screen-reader-text">hiffre d'</span>A<span class="screen-reader-text">ffaire</span><br><small>${current_exercice['label']}</small>
                    </th>
                    <th scope="col" class="col_number archive" title="Total HT des factures MoOGLi ${previous_exercice_period_label}">
                        C<span class="screen-reader-text">hiffre d'</span>A<span class="screen-reader-text">ffaire</span><br><small>${previous_exercice['label']}</small>
                    </th>
                    <th scope="col" class="col_number" title="Écart en pourcentage entre les chiffres d'affaire des 2 exercices">
                        Écart<span class="screen-reader-text"> entre les 2</span> C<span class="screen-reader-text">hiffre d'</span>A<span class="screen-reader-text">ffaire</span>
                    </th>
                    <th scope="col" class="col_number" title="Total HT des notes de dépenses MoOGLi ${current_exercice_period_label}">
                        Dépenses<br><small>${current_exercice['label']}</small>
                    </th>
                    <th scope="col" class="col_number archive" title="Total HT des notes de dépenses MoOGLi ${previous_exercice_period_label}">
                        Dépenses<br><small>${previous_exercice['label']}</small>
                    </th>
                    <th scope="col" class="col_number" title="Total HT des factures fournisseur MoOGLi ${current_exercice_period_label}">
                        Achats<br><small>${current_exercice['label']}</small>
                    </th>
                    <th scope="col" class="col_number archive" title="Total HT des factures fournisseur MoOGLi ${previous_exercice_period_label}">
                        Achats<br><small>${previous_exercice['label']}</small>
                    </th>
                    <th scope="col" class="col_number" title="CA - Dépenses - Achats ${current_exercice_period_label}">
                        TOTAL<br><small>${current_exercice['label']}</small>
                    </th>
                    <th scope="col" class="col_number archive" title="CA - Dépenses - Achats ${previous_exercice_period_label}">
                        TOTAL<br><small>${previous_exercice['label']}</small>
                    </th>
                    <th scope="col" class="col_number" title="Total des kilomètres saisis dans MoOGLi ${current_exercice_period_label}">
                        N<span class="screen-reader-text">om</span>b<span class="screen-reader-text">re de</span>&nbsp;K<span class="screen-reader-text">ilo</span>m<span class="screen-reader-text">ètres</span><br><small>${current_exercice['label']}</small>
                    </th>
                    <th scope="col" class="col_number archive" title="Total des kilomètres saisis dans MoOGLi ${previous_exercice_period_label}">
                        N<span class="screen-reader-text">om</span>b<span class="screen-reader-text">re de</span>&nbsp;K<span class="screen-reader-text">ilo</span>m<span class="screen-reader-text">ètres</span><br><small>${previous_exercice['label']}</small>
                    </th>
                    <th scope="col" class="col_number" title="Montant de l'indicateur mis en avant dans le dernier état de trésorerie à ce jour">
                        Trésorerie
                    </th>
                </tr>
                <tr class="row_recap">
                    <th class="col_text min10" colspan="2">TOTAL (${nb_companies} enseignes)</th>
                    <td class="col_number">
                        ${api.format_float(aggregate_datas["current_turnover"], 2)}&nbsp;€
                    </td>
                    <td class="col_number archive">
                        ${api.format_float(aggregate_datas["previous_turnover"], 2)}&nbsp;€
                    </td>
                    %if aggregate_datas["turnover_diff"] < 0:
                        <td class="col_number negative">
                            <small>${api.format_float(aggregate_datas["turnover_diff"], 2)}&nbsp;%</small>
                        </td>
                    %else:
                        <td class="col_number positive">
                            <small>+${api.format_float(aggregate_datas["turnover_diff"], 2)}&nbsp;%</small>
                        </td>
                    %endif
                    <td class="col_number">
                        ${api.format_float(aggregate_datas["current_expenses"], 2)}&nbsp;€
                    </td>
                    <td class="col_number archive">
                        ${api.format_float(aggregate_datas["previous_expenses"], 2)}&nbsp;€
                    </td>
                    <td class="col_number">
                        ${api.format_float(aggregate_datas["current_purchases"], 2)}&nbsp;€
                    </td>
                    <td class="col_number archive">
                        ${api.format_float(aggregate_datas["previous_purchases"], 2)}&nbsp;€
                    </td>
                    <td class="col_number">
                        ${api.format_float(aggregate_datas["current_turnover"]-aggregate_datas["current_expenses"]-aggregate_datas["current_purchases"], 2)}&nbsp;€
                    </td>
                    <td class="col_number archive">
                        ${api.format_float(aggregate_datas["previous_turnover"]-aggregate_datas["previous_expenses"]-aggregate_datas["previous_purchases"], 2)}&nbsp;€
                    </td>
                    <td class="col_number">
                        ${api.remove_kms_training_zeros(api.format_amount(aggregate_datas["current_kms"]))}
                    </td>
                    <td class="col_number archive">
                        ${api.remove_kms_training_zeros(api.format_amount(aggregate_datas["previous_kms"]))}
                    </td>
                    <td class="col_number">
                           &nbsp;
                    </td>
                </tr>
            </thead>
            <tbody>
                % for data in companies_datas:
                    <tr>
                        <th scope="row" class="col_text min10">
                            <% company_url = request.route_path('/companies/{id}', id=data["company"].id) %>
                            <a href="${company_url}">${data["company"].full_label}</a> 
                            <small>${company_list_badges(data["company"])}</small>
                        </th>
                        <td scope="row" class="col_text">
                            ${data["company"].main_activity}
                        </td>
                        <td class="col_number">
                            ${api.format_float(data["current_turnover"], 2)}&nbsp;€
                        </td>
                        <td class="col_number archive">
                            ${api.format_float(data["previous_turnover"], 2)}&nbsp;€
                        </td>
                        %if data["turnover_diff"] < 0:
                            <td class="col_number negative">
                                <small>${api.format_float(data["turnover_diff"], 2)}&nbsp;%</small>
                            </td>
                        %else:
                            <td class="col_number positive">
                                <small>+${api.format_float(data["turnover_diff"], 2)}&nbsp;%</small>
                            </td>
                        %endif
                        <td class="col_number">
                            ${api.format_float(data["current_expenses"], 2)}&nbsp;€
                        </td>
                        <td class="col_number archive">
                            ${api.format_float(data["previous_expenses"], 2)}&nbsp;€
                        </td>
                        <td class="col_number">
                            ${api.format_float(data["current_purchases"], 2)}&nbsp;€
                        </td>
                        <td class="col_number archive">
                            ${api.format_float(data["previous_purchases"], 2)}&nbsp;€
                        </td>
                        <td class="col_number">
                            ${api.format_float(data["current_turnover"]-data["current_expenses"]-data["current_purchases"], 2)}&nbsp;€
                        </td>
                        <td class="col_number archive">
                            ${api.format_float(data["previous_turnover"]-data["previous_expenses"]-data["previous_purchases"], 2)}&nbsp;€
                        </td>
                        <td class="col_number">
                            ${api.remove_kms_training_zeros(api.format_amount(data["current_kms"]))}
                        </td>
                        <td class="col_number archive">
                            ${api.remove_kms_training_zeros(api.format_amount(data["previous_kms"]))}
                        </td>
                        %if data['treasury_datas'] is None:
                            <td class="col_number" title="Pas de données">-</td>
                        %else:
                            <td class="col_number" title="${data['treasury_datas']['label']} du ${data['treasury_datas']['date'].strftime('%d/%m/%Y')}">
                                ${api.format_float(data["treasury_datas"]["value"], 2)}&nbsp;€
                            </td>
                        %endif
                    </tr>
                % endfor
            </tbody>
        </table>
    </div>
</div>

</%block>

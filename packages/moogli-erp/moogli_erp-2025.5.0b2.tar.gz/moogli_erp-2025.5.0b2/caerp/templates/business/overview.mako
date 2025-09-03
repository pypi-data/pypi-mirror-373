<%inherit file="${context['main_template'].uri}" />
<%namespace name="utils" file="/base/utils.mako" />
<%block name='mainblock'>

<div id="overview_tab">

<% business = layout.current_business_object %>
    % if switch_invoicing_mode_link:
    <div class="content_vertical_padding">
    % if business.invoicing_mode == business.CLASSIC_MODE:
    L'affaire est en mode de facturation <strong>classique</strong>
    % else:
    L'affaire est en mode de facturation <strong>à l'avancement</strong>
    % endif
        ${request.layout_manager.render_panel(switch_invoicing_mode_link.panel_name, context=switch_invoicing_mode_link)}
    <div class="alert alert-warning">
        Vous ne pourrez plus changer de mode de facturation lorsque vous aurez commencé à facturer. 
    </div>
    </div>
    % endif
    
    <p>
        <em>
            Reste à facturer : 
            ${api.format_amount(to_invoice_ht, precision=5) | n}&nbsp;€ HT 
            <small>(${api.format_amount(to_invoice_ttc, precision=5) | n}&nbsp;€ TTC)</small>
        </em>
    </p>
    

    <div class="content_vertical_padding">
    % if business.invoicing_mode == business.CLASSIC_MODE:
        <%  panel_name = "payment_deadline_timeline" %>
        % for estimation in active_estimations:
        ${request.layout_manager.render_panel(panel_name, context=business, estimation=estimation, show_totals=len(active_estimations) > 1)}
        % endfor
        ${request.layout_manager.render_panel("payment_deadline_timeline", context=business, estimation=None)}
    % else:
        <%  panel_name = "progress_invoicing_timeline" %>
        ${request.layout_manager.render_panel(panel_name, context=business)}
    % endif
    

    <div class='separate_top content_vertical_padding'>
    
        % if not estimations:
        <p>
            <em>Aucun devis n’est associé à cette affaire</em>
        </p>
        % else:
        
        <h4>Ensemble des devis émis dans cette affaire</h4>
                
        <div class='table_container'>
            <table>
                <thead>
                    <tr>
                        <th scope="col" class='col_text'>
                        Nom
                        </th>                        
                        <th scope="col" class='col_text'>
                        Statut
                        </th>
                        <th scope="col" class='col_number' title="Montant Hors Taxes" aria-label="Montant Hors Taxes">
                        H<span class="screen-reader-text">ors </span>T<span class="screen-reader-text">axes</span>
                        </th>
                        <th scope="col" class='col_number' title="Montant Toutes Taxes Comprises" aria-label="Montant Toutes Taxes Comprises">
                        T<span class="screen-reader-text">outes </span>T<span class="screen-reader-text">axes </span></span>C<span class="screen-reader-text">omprises</span>
                        </th>
                        <th scope="col" class="col_actions width_two" title="Actions">
                        <span class="screen-reader-text">Actions</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    % for estimation in estimations:
                    <tr>
                        <td class='col_text'>
                            <a
                                class="link"
                                href="${request.route_path('/estimations/{id}', id=estimation.id)}"
                                >
                                ${estimation.name} (<small>${estimation.get_short_internal_number()}</small>)
                            </a>
                        </td>
                        
                        <td class='col_text'>
                            ${api.format_status(estimation)}
                        </td>
                        <td class='col_number'>
                            ${api.format_amount(estimation.ht, precision=5) | n}&nbsp;€
                        </td>
                        <td class='col_number'>
                            ${api.format_amount(estimation.ttc, precision=5) | n}&nbsp;€
                        </td>
                        <td class='col_actions width_two'>
                            <div class='btn-group'>
                                <a
                                    class='btn icon only'
                                    href="${api.task_url(estimation)}"
                                    title="Voir le devis"
                                    aria-label="Voir le devis"
                                    >
                                    ${api.icon('arrow-right')}
                                </a>
                                <a
                                    class='btn icon only'
                                    href="${api.task_url(estimation, suffix='.pdf')}"
                                    title="Télécharger le PDF du devis"
                                    aria-label="Télécharger le PDF du devis"
                                    >
                                    ${api.icon('file-pdf')}
                                </a>
                            </div>
                        </td>
                        </tr>
                    % endfor
                </tbody>
            </table>
        </div>
        % endif
        % if estimation_add_link or invoice_add_link or corrective_invoice_add_link:
        <div class="actions align_right">
        % if corrective_invoice_add_link:
        ${request.layout_manager.render_panel(corrective_invoice_add_link.panel_name, context=corrective_invoice_add_link)}
        % endif
        % if invoice_add_link:
        ${request.layout_manager.render_panel(invoice_add_link.panel_name, context=invoice_add_link)}
        % endif
        ${request.layout_manager.render_panel(estimation_add_link.panel_name, context=estimation_add_link)}
        </div>
        % endif
        
    </div>

    ## Facturation à l'avnancement uniquement
    % if invoice_list:
    <div class='content_vertical_padding'>
        <h3>Factures</h3>
        <p>
            <em>
                Reste à facturer : 
                ${api.format_amount(business.amount_to_invoice('ht'), precision=5) | n}&nbsp;€ HT 
                <small>(${api.format_amount(business.amount_to_invoice('ttc'), precision=5) | n}&nbsp;€ TTC)</small>
            </em>
        </p>
        <div class='table_container'>
            <table>
                <thead>
                    <tr>
                        <th scope='col' class='col_text'>
                        Nom
                        </th>
                        <th scope='col' class='col_text'>
                        Statut
                        </th>
                        <th scope='col' class='col_number' title='Montant Hors Taxes' aria-label='Montant Hors Taxes'>
                        H<span class='screen-reader-text'>ors </span>T<span class='screen-reader-text'>axes</span>
                        </th>
                        <th scope='col' class='col_actions width_two' title='Actions'>
                        <span class='screen-reader-text'>Actions</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    % for invoice in invoice_list:
                    <tr>
                        <td class='col_text'>${invoice.name}</td>
                        <td class='col_text'>${api.format_status(invoice)}</td>
                        <td class='col_number'>${api.format_amount(invoice.ht, precision=5)}&nbsp;€</td>
                        <td class='col_actions width_two'>
                            <div class='btn-container'>
                                <a
                                    class='btn icon only'
                                    href="${api.task_url(invoice)}"
                                    title="Voir la facture"
                                    aria-label="Voir la facture"
                                    >
                                    ${api.icon('arrow-right')}
                                </a>
                                <a
                                    class='btn icon only'
                                    href="${api.task_url(invoice, suffix='.pdf')}"
                                    title="Télécharger le PDF de la facture"
                                    aria-label="Télécharger le PDF de la facture"
                                    >
                                    ${api.icon('file-pdf')}
                                </a>
                            </div>
                        </td>
                    </tr>
                    % endfor
                </tbody>
            </table>
        </div>
    </div>
    %endif

    <div class='separate_top content_vertical_padding'>
        % if file_requirements or custom_indicators:
        <h3>Indicateurs</h3>
        <div id='indicator-table' class="table_container">
            <table>
                <thead>
                % if custom_indicators:
                    <tr>
                        <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
                        <th scope="col" class="col_status" title="Domaine d’application de l’indicateur"><span class="screen-reader-text">Domaine d’application de l’indicateur</span></th>
                        <th scope="col" class="col_text">Libellé</th>
                        <th scope="col" class="col_actions width_one" title="Actions">
                            <span class="screen-reader-text">Actions</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    % for indicator in custom_indicators:
                        ${request.layout_manager.render_panel('custom_indicator', indicator=indicator)}
                    % endfor
                </tbody>
                % endif
                % if file_requirements:
                <tbody>
                    <tr>
                    <% business_file_status = business.get_file_requirements_status() %>
                        <td class="col_status" >
                            <span class='icon status ${api.indicator_status_css(business_file_status)}'>
                                ${api.icon(api.indicator_status_icon(business_file_status))}
                            </span>
                        </td>
                        <td class='col_status'>
                        </td>
                        <td class="col_text">
                            % if status not in ('danger', 'invalid'):
                            Des documents sont manquants
                            % elif status not in ('warning', 'warn'):
                            Des documents sont recommandés
                            % else:
                            Tous les fichiers ont été fournis
                            % endif
                        </td>
                        <td class='col_actions width_one'>
                            ${request.layout_manager.render_panel(file_tab_link.panel_name, context=file_tab_link)}
                        </td>
                    </tr>
                % endif
                </tbody>
            </table>
        </div>
        % endif
    </div>
</div>
</%block>

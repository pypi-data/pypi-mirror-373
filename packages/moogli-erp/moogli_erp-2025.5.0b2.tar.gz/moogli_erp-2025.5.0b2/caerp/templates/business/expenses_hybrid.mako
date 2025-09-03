<!--
OBSOLÈTE
--------

Replacé par l'utilisation du panel 'linked_expenses'.

Ce fichier, ainsi que la vue associée ('views/business/expense_old.py'), 
sont conservés au cas où l'association/dissociation d'achats directement depuis les 
fiches affaires / dossier / client soient réclamés par les utilisateurs.

-->

<%inherit file="${context['main_template'].uri}" />
<%namespace name="utils" file="/base/utils.mako" />
<%block name='mainblock'>
<div id="expenses_tab">
    <% business = layout.current_business_object %>
    <div class='totals grand-total'>
        <div class="totals form-section business_expenses">
            <div class="layout flex two_cols third_reverse">
                <div>
                    <h3>Total des lignes associées</h3>
                    <small>factures fournisseur + dépenses</small>
                </div>
                <div>
                    <p>
                        <strong>${api.format_amount(business.get_total_expenses(), precision=2)}&nbsp;€ HT</strong>
                    </p>
                </div>
                % if business.business_type.tva_on_margin:
                <div>
                    <p>
                        Éligibles à la TVA sur marge
                    </p>
                </div>
                <div>
                    <p>
                        <strong>${api.format_amount(business.get_total_expenses(tva_on_margin=True), precision=2)}&nbsp;€ TTC</strong>
                    </p>
                </div>
                <div>
                    <p>
                        Non éligibles à la TVA sur marge
                    </p>
                </div>
                <div>
                    <p>
                        <strong>${api.format_amount(business.get_total_expenses(tva_on_margin=False), precision=2)}&nbsp;€ TTC</strong>
                    </p>
                </div>
                % endif
            </div>
        </div>
    </div>
    <div class='content_vertical_padding'>
        <h3>Dépenses associées</h3>
        <p>Issues de notes de dépenses</p>
        <div class='table_container'>
            <table>
                <thead>
                % if expense_lines.count() > 0:
                    <tr>
                        <th scope='col' class='col_text'></th>
                        <th scope='col' class='col_text'>
                            Type et description
                        </th>
                        <th scope="col" class="col_text">
                            Note de dépense parente
                        </th>
                        % if business.business_type.tva_on_margin:
                            <th scope='col' class='col_text'>
                                TVA sur marge
                            </th>
                        % endif
                        <th scope='col' class='col_number'>
                            TTC
                        </th>
                        <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                    </tr>
                </thead>
                % endif
                <tbody>
                    <tr>
                        % if business.business_type.tva_on_margin:
                            <% nb_cols_expense = 6 %>
                        % else:
                            <% nb_cols_expense = 5 %>
                        % endif
                        <td colspan="${nb_cols_expense}" class="col_actions">
                            <button
                                class='btn icon'
                                onclick="toggleModal('expense_line_link_modal'); return false;"
                            >
                                ${api.icon('link')}
                                Associer à une dépense
                            </button>
                        </td>
                    </tr>
                    % if expense_lines.count() == 0:
                        <tr>
                            <td class="col_text" colspan="${nb_cols_expense}"><em>Aucune dépense associée</em></td>
                        </tr>
                    % else:
                        % for line in expense_lines:
                        <tr>
                            <% expense_sheet_url = request.route_path('/expenses/{id}', id=line.sheet_id) %>
                            <td class='col_status'>
                                <span class="icon status ${api.status_css_class(line.sheet)}">
                                    ${api.icon(api.status_icon(line.sheet))}
                                </span>
                            </td>
                            <td class='col_text'>
                                <strong>${line.expense_type.label}</strong>
                            % if line.description:
                                <br />
                                ${line.description}
                            % endif
                            </td>
                            <td class='col_text'>
                                <a href="${expense_sheet_url}">
                                    Note de dépense pour ${line.sheet.month} ${line.sheet.year}
                                </a>
                            </td>
                            % if business.business_type.tva_on_margin:
                                <td class='col_text'>
                                    % if line.expense_type.tva_on_margin:
                                        Oui
                                    % else:
                                        Non
                                    % endif
                                </td>
                            % endif
                            <td class='col_number'>${api.format_amount(line.total, precision=2)}&nbsp;€</td>
                            <td class='col_actions width_one'>
                                ${request.layout_manager.render_panel(
                                'post_button',
                                context=get_unlink_line_link(line),
                                extra_classes='btn icon only negative',
                                )}
                            </td>
                        % endfor
                    % endif
                </tbody>
            </table>
        </div>
    </div>
    <div class='content_vertical_padding'>
        <h3>Lignes de factures fournisseur associées</h3>
        <div class='table_container'>
            <table>
                <thead>
                % if supplier_invoice_lines.count() > 0:
                    <tr>
                        <th scope='col' class='col_text'></th>
                        <th scope='col' class='col_text'>
                            Type et description
                        </th>
                        <th scope="col" class="col_text">
                            Facture fournisseur parente
                        </th>
                        <th scope="col" class="col_date">
                            Date
                        </th>
                        % if business.business_type.tva_on_margin:
                            <th scope='col' class='col_text'>
                                TVA sur marge
                            </th>
                        % endif
                        <th scope='col' class='col_number'>
                            TTC
                        </th>
                        <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                    </tr>
                % endif
                    <tr>
                        % if business.business_type.tva_on_margin:
                            <% nb_cols_line = 7 %>
                        % else:
                            <% nb_cols_line = 6 %>
                        % endif
                        <td colspan="${nb_cols_line}" class="col_actions">
                            <button
                                class='btn icon'
                                onclick="toggleModal('supplier_invoice_line_link_modal'); return false;"
                            >
                                ${api.icon('link')}
                                Associer à une ligne de facture fournisseur
                            </button>

                        </td>
                    </tr>
                </thead>
                <tbody>
                    % if supplier_invoice_lines.count() == 0:
                        <tr>
                            <td class="col_text" colspan="${nb_cols_line}"><em>Aucune ligne de facture fournisseur associée</em></td>
                        </tr>
                    % else:
                        % for line in supplier_invoice_lines:
                        <tr>
                            <% supplier_invoice_url = request.route_path('/supplier_invoices/{id}', id=line.supplier_invoice.id) %>
                            <td class='col_status'>
                                <span class="icon status ${api.status_css_class(line.supplier_invoice)}">
                                    ${api.icon(api.status_icon(line.supplier_invoice))}
                                </span>
                            </td>
                            <td class='col_text'>
                                <strong>${line.expense_type.label}</strong>
                            % if line.description:
                                <br />
                                ${line.description}
                            % endif
                            </td>
                            <td class='col_text'>
                                <a href="${supplier_invoice_url}">
                                    ${line.supplier_invoice.name}
                                </a>
                            </td>
                            % if business.business_type.tva_on_margin:
                                <td scope='col' class='col_text'>
                                    % if line.expense_type.tva_on_margin:
                                        Oui
                                    % else:
                                        Non
                                    % endif
                                </td>
                            % endif
                            <td class='col_date'>${api.format_date(line.supplier_invoice.date)}</td>
                            <td class='col_number'>${api.format_amount(line.total, precision=2)}&nbsp;€</td>
                            <td class='col_actions width_one'>
                                ${request.layout_manager.render_panel(
                                  'post_button',
                                  context=get_unlink_line_link(line),
                                  extra_classes='btn icon only negative',
                                )}
                            </td>
                        % endfor
                    % endif
                </tbody>
            </table>
        </div>

        <section id="expense_line_link_modal" class="modal_view size_middle" style="display: none;">
            <div role="dialog" id="expense_line_link-forms" aria-modal="true" aria-labelledby="expense_line_link_modal_title">
                <div class="modal_layout">
                    <header>
                        <button class="icon only unstyled close" title="Fermer cette fenêtre" aria-label="Fermer cette fenêtre" onclick="toggleModal('expense_line_link_modal'); return false;">
                            ${api.icon('times')}
                        </button>
                        <h2 id="expense_line_link_modal_title">Associer à une dépense</h2>
                    </header>
                    <div class="modal_content_layout">
                        <div class="alert alert-info">
                            <span class="icon">${api.icon('info-circle')}</span>
                            Les dépenses déjà rattachées à une autre affaire, client ou dossier ne sont pas proposées.
                        </div>
                        ${link_to_expense_form.render()|n}
                    </div>
                </div>
            </div>
        </section>
        <section id="supplier_invoice_line_link_modal" class="modal_view size_middle" style="display: none;">
            <div role="dialog" id="supplier_invoice_line_link-forms" aria-modal="true" aria-labelledby="supplier_invoice_line_link_modal_title">
                <div class="modal_layout">
                    <header>
                        <button class="icon only unstyled close" title="Fermer cette fenêtre" aria-label="Fermer cette fenêtre" onclick="toggleModal('supplier_invoice_line_link_modal'); return false;">
                            ${api.icon('times')}
                        </button>
                        <h2 id="supplier_invoice_line_link_modal_title">Associer à une ligne de facture fournisseur</h2>
                    </header>
                    <div class="modal_content_layout">
                        <div class="alert alert-info">
                            <span class="icon">${api.icon('info-circle')}</span>
                            Les lignes déjà rattachées à une autre affaire, client ou dossier ne sont pas proposées.
                        </div>
                        ${link_to_supplier_invoice_line_form.render()|n}
                    </div>
                </div>
            </div>
        </section>
    </div>
</div>
</%block>

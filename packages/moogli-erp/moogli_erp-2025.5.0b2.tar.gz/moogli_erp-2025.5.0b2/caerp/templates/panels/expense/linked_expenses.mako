
<div id="linked_expenses_panel">

    <!-- TOTAUX -->
    <div class='table_container totals grand-total'>
        <table class="top_align_table spaced_table">
            <tr>
                <th scope="row" class="col_text align_right">Total des achats liés</th>
                <td class="col_number">
                    ${api.format_amount(total_ht, precision=2)}&nbsp;€ 
                    <small>H<span class="screen-reader-text">ors </span>T<span class="screen-reader-text">axes</span> &nbsp;</small>
                </td>
            </tr>
            <tr>
                <th scope="row" class="col_text align_right">&nbsp;</th>
                <td class="col_number">
                    ${api.format_amount(total_ttc, precision=2)}&nbsp;€ 
                    <small>T<span class="screen-reader-text">outes </span>T<span class="screen-reader-text">axes </span></span>C<span class="screen-reader-text">omprises</span></small>
                </td>
            </tr>
            % if with_tva_on_margin:
                <tr>
                    <td colspan=2>&nbsp;</td>
                </tr>
                <tr>
                    <th scope="row" class="col_text align_right">Éligible à la TVA sur marge</th>
                    <td class="col_number">
                        ${api.format_amount(total_tva_on_margin, precision=2)}&nbsp;€ 
                        <small>T<span class="screen-reader-text">outes </span>T<span class="screen-reader-text">axes </span></span>C<span class="screen-reader-text">omprises</span></small>
                    </td>
                </tr>
                <tr>
                    <th scope="row" class="col_text align_right">Hors TVA sur marge</th>
                    <td class="col_number">
                        ${api.format_amount(total_ttc - total_tva_on_margin, precision=2)}&nbsp;€ 
                        <small>T<span class="screen-reader-text">outes </span>T<span class="screen-reader-text">axes </span></span>C<span class="screen-reader-text">omprises</span></small>
                    </td>
                </tr>
            % endif
        </table>
    </div>

    <!-- LIGNES DE NOTES DE DÉPENSES -->
    <div class='content_vertical_double_padding'>
        <h3>Lignes de notes de dépense associées</h3>
        <div class='table_container'>
            <table>
                % if len(expense_lines) > 0:
                    <thead>
                        <tr>
                            <th scope='col' class='col_text'></th>
                            <th scope="col" class="col_date">Date</th>
                            <th scope='col' class='col_text'>Type et description</th>
                            <th scope="col" class="col_text min10">Note de dépense</th>
                            % if with_tva_on_margin:
                                <th scope='col' class='col_text'>TVA sur marge</th>
                            % endif
                            <th scope='col' class='col_number'>HT</th>
                            <th scope='col' class='col_number'>TTC</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="row_recap">
                            <td colspan=4>&nbsp;</td>
                            % if with_tva_on_margin:
                                <td>&nbsp;</td>
                            % endif
                            <td class='col_number'>${api.format_amount(expenses_ht, precision=2)}&nbsp;€</td>
                            <td class='col_number'>${api.format_amount(expenses_ttc, precision=2)}&nbsp;€</td>
                        </tr>
                        % for line in expense_lines:
                            <tr>
                                <% expense_sheet_url = request.route_path('/expenses/{id}', id=line.sheet_id) %>
                                <td class='col_status'>
                                    <span class="icon status ${api.status_css_class(line.sheet)}">
                                        ${api.icon(api.status_icon(line.sheet))}
                                    </span>
                                </td>
                                <td class='col_date'>${api.format_date(line.date)}</td>
                                <td class='col_text'>
                                    <strong>${line.expense_type.label}</strong>
                                    % if line.description:
                                        <br />
                                        ${line.description}
                                    % endif
                                </td>
                                <td class='col_text'>
                                    <a href="${expense_sheet_url}">${api.month_name(line.sheet.month).capitalize()} ${line.sheet.year}</a>
                                    % if line.sheet.title:
                                        <br />
                                        <small>${line.sheet.title}</small>
                                    % endif
                                </td>
                                % if with_tva_on_margin:
                                    <td class='col_text'>
                                        % if line.expense_type.tva_on_margin:
                                            <span class="icon only tag positive">${api.icon('check-circle')}</span>
                                        % else:
                                            <span class="icon only tag negative">${api.icon('times-circle')}</span>
                                        % endif
                                    </td>
                                % endif
                                <td class='col_number'>${api.format_amount(line.ht, precision=2)}&nbsp;€</td>
                                <td class='col_number'>${api.format_amount(line.total, precision=2)}&nbsp;€</td>
                        % endfor
                    </tbody>
                % else:
                    <tr><td class="col_text align_center"><em>Aucune ligne de note de dépense associée</em></td></tr>
                % endif
            </table>
        </div>
    </div>

    <!-- LIGNES DE FACTURES FOURNISSEUR -->
    <div class='content_vertical_double_padding'>
        <h3>Lignes de factures fournisseur associées</h3>
        <div class='table_container'>
            <table>
                % if len(supplier_invoice_lines) > 0:
                    <thead>
                        <tr>
                            <th scope='col' class='col_text'></th>
                            <th scope="col" class="col_date">Date</th>
                            <th scope='col' class='col_text'>Type et description</th>
                            <th scope="col" class="col_text min14">Fournisseur</th>
                            <th scope="col" class="col_text min10">Facture</th>
                            % if with_tva_on_margin:
                                <th scope='col' class='col_text'>TVA sur marge</th>
                            % endif
                            <th scope='col' class='col_number'>HT</th>
                            <th scope='col' class='col_number'>TTC</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="row_recap">
                            <td colspan=5>&nbsp;</td>
                            % if with_tva_on_margin:
                                <td>&nbsp;</td>
                            % endif
                            <td class='col_number'>${api.format_amount(supplier_invoices_ht, precision=2)}&nbsp;€</td>
                            <td class='col_number'>${api.format_amount(supplier_invoices_ttc, precision=2)}&nbsp;€</td>
                        </tr>
                        % for line in supplier_invoice_lines:
                            <tr>
                                <% supplier_invoice_url = request.route_path('/supplier_invoices/{id}', id=line.supplier_invoice.id) %>
                                <td class='col_status'>
                                    <span class="icon status ${api.status_css_class(line.supplier_invoice)}">
                                        ${api.icon(api.status_icon(line.supplier_invoice))}
                                    </span>
                                </td>
                                <td class='col_date'>${api.format_date(line.supplier_invoice.date)}</td>
                                <td class='col_text'>
                                    <strong>${line.expense_type.label}</strong>
                                    % if line.description:
                                        <br />
                                        ${line.description}
                                    % endif
                                </td>
                                <td class='col_text'>
                                    ${line.supplier_invoice.supplier.label}
                                </td>
                                <td class='col_text'>
                                    <a href="${supplier_invoice_url}">${line.supplier_invoice.remote_invoice_number}</a>
                                </td>
                                % if with_tva_on_margin:
                                    <td scope='col' class='col_text'>
                                        % if line.expense_type.tva_on_margin:
                                            <span class="icon only tag positive">${api.icon('check-circle')}</span>
                                        % else:
                                            <span class="icon only tag negative">${api.icon('times-circle')}</span>
                                        % endif
                                    </td>
                                % endif
                                <td class='col_number'>${api.format_amount(line.ht, precision=2)}&nbsp;€</td>
                                <td class='col_number'>${api.format_amount(line.total, precision=2)}&nbsp;€</td>
                            </tr>
                        % endfor
                    </tbody>
                % else:
                    <tr><td class="col_text align_center"><em>Aucune ligne de facture fournisseur associée</em></td></tr>
                % endif
            </table>
        </div>
    </div>

</div>


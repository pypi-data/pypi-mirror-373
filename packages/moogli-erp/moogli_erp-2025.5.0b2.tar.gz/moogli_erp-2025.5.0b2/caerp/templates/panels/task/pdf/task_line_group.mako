<%doc>
TaskLineGroup html representation
</%doc>

<%namespace file="/base/utils.mako" import="format_text" />

<table>
    <tbody>
        % if len(description_lines) > 1:
            <!-- On a une description de groupe découpée en plusieurs blocks -->
            %if group.title != "":
                <tr class="group_description">
                    <td class="col_text description rich_text">
                        <h2>${group.title}</h2>
                    </td>
                </tr>            
            % endif
            % for description_line in description_lines:
                <tr class="long_description">
                    <td class="col_text description rich_text">
                        ${format_text(description_line, False)}
                    </td>
                </tr>
            % endfor
        % elif group.title != '' or group.description != '':
            <!-- On a un titre et/ou une description simple -->
            <tr class="group_description">
                <td class="col_text description rich_text">
                %if group.title != "":
                    <h2>${group.title}</h2>
                % endif
                % if group.description != "":
                    ${format_text(group.description, False)}
                % endif
                </td>
            </tr>
        % else:
            <!-- On n'a ni titre ni description à afficher -->
            <tr class="group_description">
                <td class="empty">&nbsp;</td>
            </tr>
        % endif
    </tbody>
</table>
<table>
    <tbody class="table_head">
        <tr>
            % if columns['date']:
                <th scope="col" class="col_date date">Date de prestation</th>
            % endif
            <th scope="col" class="col_text description">Description</th>
            %if columns['units']:
                % if is_tva_on_margin_mode or (task.mode == 'ttc' and columns['ttc']):
                    <th scope="col" class="col_number price" title="Prix Unitaire">Prix Unit<span class="screen-reader-text">aire</span></th>
                % else:
                    <th scope="col" class="col_number price" title="Prix Unitaire Hors Taxes">P<span class="screen-reader-text">rix</span> U<span class="screen-reader-text">nitaire</span> H<span class="screen-reader-text">ors </span>T<span class="screen-reader-text">axes</span></th>
                % endif
                <th scope="col" class="col_number quantity" title="Quantité">Q<span class="screen-reader-text">uanti</span>té</th>
                <th scope="col" class="col_text unity">Unité</th>
            % endif
            % if show_progress_invoicing:
                %if columns['units']:
                    % if has_deposit:
                    <th scope="col" class="col_number deposit" title="Acompte déjà facturé"><span class="screen-reader-text">Montant de l’</span>Acompte</th>
                    % endif
                % endif
                % if show_previous_invoice:
                <th scope="col" class="col_number progress_invoicing" title="Pourcentage d’avancement déjà facturé"><span class="screen-reader-text">Pourcentage d’avancement </span>Déjà facturé</th>
                % endif
                <th scope="col" class="col_number progress_invoicing" title="Pourcentage d’avancement à facturer"><span class="screen-reader-text">Pourcentage d’avancement </span>À facturer</th>
                <th scope="col" class="col_number progress_invoicing" title="Pourcentage d’avancement restant à facturer"><span class="screen-reader-text">Pourcentage d’avancement </span>Restant<span class="screen-reader-text"> à facturer</span></th>
            % endif
            % if is_tva_on_margin_mode:
                <th scope="col" class="col_number price_total">Prix</th>
            % else:
                <th scope="col" class="col_number price_total">Prix HT</th>
            % endif
            % if columns['tvas']:
                <th scope="col" class="col_number tva" title="Taux de TVA"><span class="screen-reader-text">Taux de </span>TVA</th>
            % endif
            % if columns['ttc']:
                <th scope="col" class="col_number price">Prix TTC</th>
            % endif
        </tr>
    </tbody>
    <tbody class="lines">
        % for line in group.lines:
            ${request.layout_manager.render_panel(
                get_line_panel_name(line),
                context=task,
                line=line,
                columns=columns,
                show_previous_invoice=show_previous_invoice,
                show_progress_invoicing=show_progress_invoicing,
                is_tva_on_margin_mode=is_tva_on_margin_mode
            )}
        % endfor

% if display_subtotal:
            <tr>
                <th scope="row" colspan="${columns['first_column_colspan']}" class="col_text align_right">
                    % if columns['ttc'] or is_tva_on_margin_mode:
                        Sous-total
                    % else:
                        Sous-total HT
                    % endif
                </th>
                <th class="col_number price_total">
                    % if is_tva_on_margin_mode:
                        ${task.format_amount(group.total_ttc(), trim=False, precision=5)}&nbsp;€
                    % else:
                        ${task.format_amount(group.total_ht(), trim=False, precision=5)}&nbsp;€
                    % endif
                </th>
                % if columns['tvas']:
                    <th class="col_number tva">&nbsp;</th>
                % endif
                % if columns['ttc']:
                    <th class="col_number price">
                        ${task.format_amount(group.total_ttc(), trim=False, precision=5)}&nbsp;€
                    </th>
                % endif
            </tr>
        <%doc>Ici on ne ferme pas le tableau, ce qui sera fait plus tard dans le template parent </%doc>
        </tbody>
    </table>
% endif

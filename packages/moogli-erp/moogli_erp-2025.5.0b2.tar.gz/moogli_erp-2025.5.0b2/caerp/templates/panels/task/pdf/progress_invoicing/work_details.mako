<%doc>
Renders a TaskLine object
</%doc>

<%namespace file="/base/utils.mako" import="format_text" />

% for description_line in description_lines:
% if loop.first:
<%doc>
La première ligne contient la première ligne de la description 
et l'ensemble des données de facturation
</%doc>
<tr>
    <td class="col_text description rich_text">${format_text(description_line, False)}</td>
    % if columns['units']:
        <td class="col_number price">${task.format_amount(unit_ht, trim=False, precision=5)}&nbsp;€</td>
        <td class="col_number quantity">${api.format_quantity(quantity)}</td>
        <td class="col_text unity">${unity}</td>
        % if has_deposit:
        <td class="col_number deposit archive">
            ${task.format_amount(deposit, trim=False, precision=5)}&nbsp;€
        </td>
        % endif
    % endif
    % if show_previous_invoice:
        <td class="col_number progress_invoicing archive">
        % if invoiced_percentage is not None:
            ${invoiced_percentage}&nbsp;%
        % endif
        </td>
    % endif
    <td class="col_number progress_invoicing">
        % if percentage is not None:
            ${percentage}&nbsp;%
        % endif
    </td>
    <td class='col_number progress_invoicing archive'>
        % if left_percentage is not None:
            ${left_percentage}&nbsp;%
        % endif
    </td>
    <td class="col_number price_total">
        ${task.format_amount(total_ht, trim=False, precision=5)}&nbsp;€
    </td>
    % if columns['tvas']:
        <td class="col_number tva">
            ${task.format_amount(tva_value, precision=2)}&nbsp;%
        </td>
    % endif
    % if columns['ttc']:
        <td class="col_number price">${task.format_amount(total, trim=False, precision=5)}&nbsp;€</td>
    % endif
</tr>
% else:
<%doc>
Les lignes suivantes servent uniquement à afficher les autres lignes de la description
</%doc>
<tr class='long_description'>
    % if columns['date']:
        <td class="col_date date"></td>
    % endif
    <td class="col_text description rich_text">${format_text(description_line, False)}</td>
    % if columns['units'] == 1:
    <td class="col_number price"></td>
    <td class="col_number quantity"></td>
    <td class="col_text unity"></td>
    % if has_deposit:
    <td></td>
    % endif
    % endif
    % if show_previous_invoice:
    <td class="col_number progress_invoicing archive"></td>
    % endif
    <td class="col_number progress_invoicing"></td>
    <td class="col_number progress_invoicing"></td>
    <td class="col_number price_total"></td>
    % if columns['tvas']:
        <td class="col_number tva"></td>
    % endif
    % if columns['ttc']:
        <td class="col_number price"></td>
    % endif
</tr>
% endif 
% endfor
<tbody class='lines'>
% for work_item in work.items:
${request.layout_manager.render_panel(
    'progress_invoicing_pdf_work_item',
    context=task,
    work_item=work_item,
    columns=columns,
    work=work,
    show_previous_invoice=show_previous_invoice
)}
% endfor
</tbody>
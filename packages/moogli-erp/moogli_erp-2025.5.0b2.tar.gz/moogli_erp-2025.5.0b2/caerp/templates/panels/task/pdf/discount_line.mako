<%namespace file="/base/utils.mako" import="format_text" />

<tr>
    <td colspan="${columns['first_column_colspan']}" class='col_text description rich_text'>
        ${format_text(description)}
    </td>
    <td class='col_number price'>
        ${task.format_amount(total_ht, trim=False, precision=5)}&nbsp;€
    </td>
    % if columns['tvas']:
        <td class='col_number tva'>
            ${task.format_amount(tva_value, precision=2)}&nbsp;%
        </td>
    % endif
    % if columns['ttc']:
        <td class="col_number price">
        ${task.format_amount(total, trim=False, precision=5)}&nbsp;€
        </td>
    % endif
</tr>
<%namespace file="/base/utils.mako" import="format_text" />

% if task.status != "valid":
    <img src="${request.static_url('caerp:static/watermark.svg', _app_url='')}" alt="Prévisualisation : document sans valeur juridique ou marchande" class="wtmk" />
% endif

<%def name="table(title, datas, css='')">
    <div class='pdf_mention_block'>
        <h4 class="title ${css}">${title}</h4>
        <p class='content'>${format_text(datas)}</p>
    </div>
</%def>

${request.layout_manager.render_panel("task_pdf_header", context=task)}

<main class='task_view'>
    <div class="information_intro">
        Le ${api.format_date(task.date, False)},<br />
        <%block name='information'></%block>
    </div>
    <div class='pdf_spacer'><br></div>
    <div class='row pdf_task_table'>
        % for group in groups:
            % if group.display_details:
            <% panel = "task_pdf_task_line_group" %>
            % else:
            <% panel = "task_pdf_task_line_group_resume" %>
            % endif
            ${request.layout_manager.render_panel(
            panel,
            context=task,
            group=group,
            columns=columns,
            show_previous_invoice=show_previous_invoice,
            show_progress_invoicing=show_progress_invoicing,
            is_tva_on_margin_mode=is_tva_on_margin_mode
            )}
        % endfor
        % if len(groups) > 1:
            </div>
            <div class='pdf_spacer'><br></div>
            <div class='pdf_task_table'>
                <table>
                    <tbody>
        % else:
        <%doc>Ici le tbody du groupe est toujours ouvert</%doc>
        % endif
        % if task.expenses_ht not in (0, None):
            <tr>
                <td class='col_text description' colspan="${columns['first_column_colspan']}">
                    Frais forfaitaires
                </td>
                <td class="col_number price">
                    ${task.format_amount(task.expenses_ht, precision=5)}&nbsp;€
                </td>
                % if columns['tvas']:
                    <td class='col_number tva'>
                        ${task.format_amount(task.expenses_tva, precision=2)}&nbsp;%
                    </td>
                % endif
                % if columns['ttc']:
                    <td class="col_number price">&nbsp;</td>
                % endif
            </tr>
             </tbody>
              <tbody>
        % endif
            %if hasattr(task, "discounts") and task.discounts:
                % if not is_tva_on_margin_mode:
                    <tr>
                        <th scope="row" colspan="${columns['first_column_colspan']}" class='col_text align_right'>
                            Total HT
                        </th>
                        <td class='col_number price_total'>
                            ${task.format_amount(task.groups_total_ht() + task.expenses_ht, trim=False, precision=5)}&nbsp;€
                        </td>
                        % if columns['tvas']:
                            <td class="col_number tva">&nbsp;</td>
                        % endif
                        % if columns['ttc']:
                            <td class="col_number price">&nbsp;</td>
                        % endif
                    </tr>
                % endif
                <% discounts_with_tva = False %>
                % for discount in task.discounts:
                    % if discount.tva > 0:
                        <% discounts_with_tva = True %>
                    % endif
                    ${request.layout_manager.render_panel(
                        "task_pdf_discount_line",
                        context=task,
                        discount=discount,
                        columns=columns
                    )}
                % endfor
                % if discounts_with_tva:
                    <tr>
                        <th scope="row" colspan="${columns['first_column_colspan']}" class='col_text align_right'>
                            % if is_tva_on_margin_mode:
                                Total après remise
                            % else:
                                Total HT après remise
                            % endif
                        </th>
                        <td class='col_number price_total'>
                            ${task.format_amount(task.total_ht(), precision=5)}&nbsp;€
                        </td>
                        % if columns['tvas']:
                            <td class="col_number tva">&nbsp;</td>
                        % endif
                        % if columns['ttc']:
                            <td class="col_number price">&nbsp;</td>
                        % endif
                    </tr>
                % endif
            % else:
                % if not is_tva_on_margin_mode:
                    <tr>
                        <th scope="row" colspan="${columns['first_column_colspan']}" class='col_text align_right'>
                            Total HT
                        </th>
                        <td class='col_number price_total'>
                            ${task.format_amount(task.total_ht(), precision=5)}&nbsp;€
                        </td>
                        % if columns['tvas']:
                            <td class="col_number tva">&nbsp;</td>
                        % endif
                        % if columns['ttc']:
                            <td class="col_number price">&nbsp;</td>
                        % endif
                    </tr>
                % endif
            % endif
            <%doc>
            Si l'on a qu'un seul taux de TVA dans le document, on affiche
            une seule ligne avec du texte pour les tvas à 0%

            Pour les documents avec plusieurs taux de TVA, on affiche le montant par taux de tva
            </%doc>
            <% tva_objects_dict = task.get_tva_objects() %>
            % if not is_tva_on_margin_mode:
                %for tva, tva_amount in task.get_tvas().items():
                    <% tva_object = tva_objects_dict.get(tva) %>
                        <tr>
                            <th scope="row" colspan="${columns['first_column_colspan']}" class='col_text align_right'>
                                % if tva_object:
                                    % if tva_object.mention:
                                        ${format_text(tva_object.mention)}
                                    % else:
                                        ${tva_object.name}
                                    % endif
                                % else:
                                    TVA (${api.format_amount(tva, precision=2)} %)
                                % endif
                            </th>
                            <td class='col_number price'>
                                % if tva > 0:
                                    ${task.format_amount(tva_amount, precision=5)}&nbsp;€
                                % else:
                                    0,00&nbsp;€
                                % endif
                            </td>
                            % if columns['tvas']:
                                <td class="col_number tva">&nbsp;</td>
                            % endif
                            % if columns['ttc']:
                                <td class="col_number price">&nbsp;</td>
                            % endif
                        </tr>
                % endfor
            % endif
            %if task.expenses:
                <tr>
                    <th scope="row" colspan="${columns['first_column_colspan']}" class='col_text align_right'>
                        Frais réels
                    </th>
                    <td class='col_number price'>
                        ${task.format_amount(task.expenses_amount(), precision=5)}&nbsp;€
                    </td>
                    % if columns['tvas']:
                        <td class="col_number tva">&nbsp;</td>
                    % endif
                    % if columns['ttc']:
                        <td class="col_number price">&nbsp;</td>
                    % endif
                </tr>
            % endif
            % if not task.post_ttc_lines:
            <tr class="row_total">
            % else:
            <tr>
            % endif
                <th scope="row" colspan="${columns['first_column_colspan']}" class='col_text align_right'>
                    % if is_tva_on_margin_mode:
                        Total
                    % else:
                        Total TTC
                    % endif
                </th>
                <td class='col_number price_total'>
                    ${task.format_amount(task.total(), precision=5)}&nbsp;€
                </td>
                % if columns['tvas']:
                    <td class="col_number tva">&nbsp;</td>
                % endif
                % if columns['ttc']:
                    <td class="col_number price">&nbsp;</td>
                % endif
            </tr>
            %if hasattr(task, "post_ttc_lines") and task.post_ttc_lines:
                % for post_ttc_line in task.post_ttc_lines:
                    ${request.layout_manager.render_panel(
                        "task_pdf_post_ttc_line",
                        context=task,
                        post_ttc_line=post_ttc_line,
                        columns=columns
                    )}
                % endfor
                <tr class="row_total">
                    <th scope="row" colspan="${columns['first_column_colspan']}" class='col_text align_right'>
                        Net à payer
                    </th>
                    <td class='col_number price_total'>
                        ${task.format_amount(task.total_due(), precision=5)}&nbsp;€
                    </td>
                    % if columns['tvas']:
                        <td class="col_number tva">&nbsp;</td>
                    % endif
                    % if columns['ttc']:
                        <td class="col_number price">&nbsp;</td>
                    % endif
                </tr>
            % endif
        </tbody>
        </table>
    </div>

    <div class='pdf_spacer'><br></div>

    %if task.notes:
        ${table("Notes", task.notes)}
    %endif
    <%block name="notes_and_conditions">
    ## All infos beetween document lines and footer text (notes, payment conditions ...)
    </%block>

    % for mention in mentions:
        % if task.type_ == 'estimation' and loop.last :
		## Create a wrapper to put last mention and signature side by side
		<div class="estimation_last_mention">
        % endif
        % if mention.full_text is not None:
			<div class="pdf_mention_block">
			% if mention.title:
				<h4>${mention.title}</h4>
            % endif
				<p>${format_text(api.compile_template_str(mention.full_text, mention_tmpl_context), False)}</p>
			</div>
        % endif
        % if task.type_ == 'estimation' and loop.last :
			<%block name="end_document">
			## Add infos at the end of the document (signature block)
			</%block>
		</div>
        % endif
	% endfor
</main>

% if with_cgv:
${request.layout_manager.render_panel('task_pdf_cgv', context=task)}
% endif

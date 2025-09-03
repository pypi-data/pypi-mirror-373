<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" name="utils" />

<%block name='beforecontent'>
<div class='main_toolbar'>
    <div class='layout flex main_actions'>
        ${request.layout_manager.render_panel('action_buttons', links=stream_main_actions())}
    </div>
</div>
</%block>

<%block name='content'>
<% bank_remittance = request.context %>
<% bank_label = "<em>Non défini</em>" %>
% if bank_remittance.bank:
    <% bank_label = bank_remittance.bank.label %>
% endif
<div>
    <h2>Remise en banque n° ${bank_remittance.id}</h2>
    <dl class="dl-horizontal">
        % if bank_remittance.closed:
            <dt>Statut</dt>
            <dd><span class='icon status valid'>${api.icon('lock')}</span> Clôturée</dd>
        % else:
            <dt>Statut</dt>
            <dd><span class='icon status wait'>${api.icon('lock-open')}</span> Ouverte</dd>
        % endif
        <dt>Créée le</dt><dd>${api.format_date(bank_remittance.created_at)}</dd>
        <dt>Mode de paiement</dt><dd>${api.format_paymentmode(bank_remittance.payment_mode)}</dd>
        <dt>Compte bancaire</dt><dd>${bank_label | n}</dd>
        % if bank_remittance.remittance_date:
            <dt>Date de dépôt</dt><dd>${api.format_date(bank_remittance.remittance_date)}</dd>
        % endif
    </dl>
    % if bank_remittance.is_exported():
        <div class="alert alert-warning">
            <span class='icon'>${api.icon('exclamation-triangle')}</span>
            Cette remise en banque a été exportée en comptabilité
        </div>
    % endif
</div>
<hr />
<div>
    % if records:
        <div class="table_container">
            <table>
                <thead>
                    <th scope="col" class="col_date">${sortable("Date", "date")}</th>
                    <th scope="col" class="col_text">${sortable("Enseigne", "company")}</th>
                    <th scope="col" class="col_text">${sortable("Client", "customer")}</th>
                    <th scope="col" class="col_text">${sortable("Code facture", "invoice")}</th>
                    <th scope="col" class="col_text">Banque client</th>
                    <th scope="col" class="col_text" title="Numéro de chèque">N<span class="screen-reader-text">umér</span><sup>o</sup> chèque</th>
                    <th scope="col" class="col_number">${sortable("Montant", "amount")}</th>
                </thead>
                % if records.item_count > 5:
                    <thead>
                        <tr class="row_recap">
                            <th scope="col" class="col_text" colspan="6">${records.item_count} encaissement(s)</th>
                            <th scope="col" class="col_number">${api.format_amount(bank_remittance.get_total_amount(), precision=5)}&nbsp;€</th>
                        </tr>
                    </thead>
                % endif
                <tbody>
                    % for payment in records:
                        <tr>
                            <td class="col_date">${api.format_date(payment.date)}</td>
                            <td class="col_text">${payment.task.company.full_label}</td>
                            <td class="col_text">${payment.task.customer.label}</td>
                            <td class="col_text document_number">
                                <a href="${api.task_url(payment.task)}/preview" title="${payment.task.official_number}" aria-label="${payment.task.official_number}">${payment.task.official_number}</a>
                            </td>
                            <td class="col_text">
                                % if payment.customer_bank is not None:
                                    ${payment.customer_bank.label}
                                % endif
                            </td>
                            <td class="col_text">${payment.check_number}</td>
                            <td class="col_number">${api.format_amount(payment.amount, precision=5)}&nbsp;€</td>
                        </tr>
                    % endfor
                </tbody>
                <tfoot>
                    <tr class="row_recap">
                        <th scope="col" class="col_text" colspan="6">${records.item_count} encaissement(s)</th>
                        <th scope="col" class="col_number">${api.format_amount(bank_remittance.get_total_amount(), precision=5)}&nbsp;€</th>
                    </tr>
                </tfoot>
            </table>
        </div>
    % else:
        <em>Aucun encaissement n'est attaché à cette remise</em>
    % endif
</div>

<section id="remittance_close_form" class="modal_view size_small" style="display: none;">
    <div role="dialog" id="remittance-forms" aria-modal="true" aria-labelledby="remittance-forms_title">
        <div class="modal_layout">
            <header>
                <button class="icon only unstyled close" title="Fermer cette fenêtre" aria-label="Fermer cette fenêtre" onclick="toggleModal('remittance_close_form'); return false;">
                    ${api.icon('times')}
                </button>
                <h2 id="remittance-forms_title">Clôture de la remise en banque</h2>
            </header>
            <form method="POST" action="${request.route_path('/accounting/bank_remittances/{id}', id=bank_remittance.id, _query=dict(action='close'))}" class="modal_content_layout layout">
                <div class="modal_content">
                    <div class="form-group">
                        <label for="remittance_date">Date de dépôt</label>
                        <input type="text" name="remittance_date_fr" id="remittance_date_fr" class="form-control" />
                        <input type="hidden" name="remittance_date" id="remittance_date" />
                    </div>
                </div>
                <footer>
                    <button name="submit" type="submit" class="btn btn-primary" value="submit">Valider</button>
                    <button type="button" class="btn" onclick="toggleModal('remittance_close_form'); return false;">Annuler</button>
                </footer>
            </form>
        </div>
    </div>
</section>
</%block>

<%block name='footerjs'>
$(function(){
    $('#remittance_date').val(new Date().toISOString().slice(0, 10));
    $('#remittance_date_fr').val(new Date().toLocaleDateString());
    $('#remittance_date_fr').datepicker({
        'altField': '#remittance_date',
        'altFormat': 'yy-mm-dd',
        'dateFormat': 'dd/mm/yy'
    });
});
</%block>

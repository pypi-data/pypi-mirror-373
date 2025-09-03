<%doc>
 Task list panel template
</%doc>
<%namespace file="/base/utils.mako" import="format_text" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/utils.mako" import="format_customer" />
<%namespace file="/base/utils.mako" import="format_project" />
<%namespace file="/base/utils.mako" import="table_btn"/>
<div class='dash_elem'>
    <h2>
        <span class='icon'>${api.icon('clock')}</span>
        <span>Dernières activités sur vos documents</span>
    </h2>
    <div class='panel-body'>
         <p style="display: none;">
           Afficher <select id='number_of_tasks'>
              % for i in (5, 10, 15, 50):
              <option value='${i}'
              % if tasks.items_per_page == i:
                selected=true
              % endif
              >
              ${i}
              </option>
              % endfor
            </select>
            éléments à la fois
         </p>
         % if tasks:
         <table class='hover_table'>
         % else:
         <table>
         % endif
            % if tasks:
            <thead>
                <th scope="col" class="col_status" title="Statut">
                    <span class="screen-reader-text">Statut</span>
                </th>
                <th scope="col" class="col_text">
                    Statut<span class="screen-reader-text"> suite à la dernière modification</span>
                </th>
                <th scope="col" class="col_icon" title="Type de document">
                    <span class="screen-reader-text">Type</span>
                </th>
                <th scope="col" class="col_text" title="Nom du document">
                    Nom<span class="screen-reader-text"> du document</span>
                </th>
                <th scope="col" class="col_text">
                    Client
                </th>
                <th scope="col" class="col_actions" title="Actions">
                    <span class="screen-reader-text">Actions</span>
                </th>
            </thead>
            % endif
            <tbody>
                % for task in tasks:
                    <% status_text = api.format_status(task, full=False) %>
                    <% status_date = api.format_date(task.status_date) %>
                    <% task_typetext = api.format_task_type(task) %>
                    <% task_type = task.type_ %>
                    <% task_status = task.global_status %>
                    <tr>
                        <% url = api.task_url(task) %>
                        
                        <% onclick = "document.location='{url}'".format(url=url) %>
                        <% tooltip_title = "Cliquer pour voir le document « " + task.name + " »" %>
                        <td class="col_status" onclick="${onclick}" title="Statut suite à la dernière modification le ${status_date} : ${status_text} - ${tooltip_title}">
                            <span class="icon status ${task_status}">
                                ${api.icon(api.status_icon(task))}
                            </span>
                        </td>
                        <td class="col_text" onclick="${onclick}" title="Statut suite à la dernière modification le ${status_date} : ${status_text} - ${tooltip_title}"">
                            ${status_text} <small>le ${status_date}</small>
                        </td>
                        <td class="col_icon" onclick="${onclick}" title="${task_typetext} - ${tooltip_title}"">
                            % if task_type:
                                <span class="icon">
                                % if task_type == 'estimation':
                                    ${api.icon('file-list')}
                                % endif
                                % if task_type == 'invoice' or task_type == 'cancelinvoice':
                                    ${api.icon('file-invoice-euro')}
                                % endif
                                % if task_type == 'expense':
                                    ${api.icon('credit-card')}
                                % endif
                                % if task_type == 'supplierorder':
                                    ${api.icon('box')}
                                % endif
                                % if task_type == 'supplierinvoice':
                                    ${api.icon('box-euro')}
                                % endif
                                </span>
                            % endif
                        </td>
                        <td class="col_text">
                            <a href="${url}" title="${tooltip_title}" aria-label="${tooltip_title}">${task.name}</a>
                        </td>
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                            ${format_customer(task.customer, False)}
                        </td>
                        ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(task))}
                    </tr>
                % endfor
            </tbody>
        </table>
    </div>
</div>

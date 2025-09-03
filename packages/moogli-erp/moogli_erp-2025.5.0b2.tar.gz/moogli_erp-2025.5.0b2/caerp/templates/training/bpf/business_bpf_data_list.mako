<%doc>
BPF datas list.
This is displayed if and only if there are datas for several years
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="table_btn"/>
<%block name='mainblock'>
<div id="bpf_data_tab">
    ${request.layout_manager.render_panel(
    'help_message_panel',
    parent_tmpl_dict=context.kwargs
    )}
    <div class='content_vertical_padding'>
        <h3>${title}</h3>
        <div class='content_vertical_padding'>
            <p>
                Lorsqu’une formation est à cheval sur plusieurs années, il faut
                renseigner des données BPF pour chacune des années.
            </p>
        </div>
        <div class='content_vertical_padding layout flex two_cols'>
            <div>
                <div class='content_vertical_padding'>
                    ${new_bpfdata_menu.render(request)|n}
                </div>
            </div>
            <div class='table_container'>
                <table class='hover_table'>
                    <tr>
                        <th scope="col" class="col_number">Année</th>
                        <th scope="col" class="col_text">Document cible</th>
                        <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                    </tr>
                    % for bpf_data, form_link, delete_link in bpf_datas_links:
                        <tr>
                            <td class="col_number">
                                BPF ${bpf_data.financial_year}
                            </td>
                            <td class="col_text">
                                Cerfa ${bpf_data.cerfa_version}
                            </td>
                            <td class="col_actions width_two">
                            	<ul>
                            		<li>
    		                            ${table_btn(
                                            form_link, 
                                            f"Modifier les données BPF pour {bpf_data.financial_year}",
                                            f"Modifier les données BPF pour {bpf_data.financial_year}",
                                            icon='pen',
                                        )}
                            		</li>
                            		<li>
    		                            ${table_btn(
                                            delete_link, 
                                            f"Supprimer les données pour {bpf_data.financial_year}", 
                                            f"Supprimer les données pour {bpf_data.financial_year}", 
                                            icon="trash-alt", 
                                            css_class="negative", 
                                            method='post'
                                        )}
                            		</li>
                            	</ul>
                            </td>
                        </tr>
                    % endfor
                </table>
            </div>
        </div>
    </div>
</div>
</%block>

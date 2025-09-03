<%namespace file="/base/utils.mako" import="format_address" />
<%namespace file="/base/utils.mako" import="format_text" />
<header class='pdf_header task_header'>
    % if has_header:
        <img src='${api.img_url(company.header_file)}' alt='${company.name}' class='full_banner' />
    % else:
        <table role="presentation" class="pdf_logo">
            <tbody>
                <tr>
                % if company.logo_file:
                    <td class='logo_cell'>
                        <img src='${api.img_url(company.logo_file)}' alt='Logo de ${company.name}' class='logo_img' />
                    </td>
                % endif
                    <td class='company_cell'>
                        <h4 class="cae-details">${config.get('cae_business_name', '')}</h4>
                        <div class="company-details">
                            <address>
                                <strong>${company.name}</strong><br />
                                ${format_address(company, multiline=True)}
                            </address>
                            <p>
                                ${company.email}<br />
                                ${company.phone}<br />
                                ${company.mobile}<br />
                            </p>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    % endif
    <div class='pdf_address_block'>
        <div>
            ${format_text(task.address)}
			<span class="corner top left"></span>
			<span class="corner top right"></span>
			<span class="corner bottom left"></span>
			<span class="corner bottom right"></span>
        </div>
    </div>
</header>
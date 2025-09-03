<%namespace file="caerp:templates/base/utils.mako" import="format_text" />

<header class="pdf_header task_header">
    % if has_header:
        <img src="${url}"
             alt="${request.config.get('cae_business_name', '')}"
             longdesc="${request.config.get('cae_business_name', '')}
${request.config.get('cae_address')}
${request.config.get('cae_zipcode')} ${request.config.get('cae_city')}"
            class="full_banner"
        />
    % else:
        <table role="presentation" class="pdf_logo">
            <tbody>
            <tr>
                <td class='logo_cell'>
                <img src="/public/logo.png"
                     alt=""
                     class="cae_logo logo_img"
                />
                </td>
                <td class='company_cell'>
                    <strong>
                        ${request.config.get('cae_business_name', '')}
                    </strong>

                    <address>
                        ${request.config.get('cae_address')}<br />
                        ${request.config.get('cae_zipcode')}
                        ${request.config.get('cae_city')}<br />
                    </address>
                </td>
                </tr>
            </tbody>
        </table>
    % endif

    <div class='pdf_address_block'>
        <div>
            ${format_text(attestation.customer.full_address)}
			<span class="corner top left"></span>
			<span class="corner top right"></span>
			<span class="corner bottom left"></span>
			<span class="corner bottom right"></span>
        </div>
    </div>

</header>

% if not message is UNDEFINED:
    <div class='text-center'>
        <div id='msg-div' class="alert alert-success" tabindex='1' aria-live='polite'>
            <button class="icon only unstyled close" title="Masquer ce message" aria-label="Masquer ce message" data-dismiss="alert" type="button">
                ${api.icon('times')}
            </button>
            <span class="icon">${api.icon('success')}</span>
            ${api.clean_html(message)|n}
        </div>
      </div>
% endif
% if not form is UNDEFINED:
    ${form|n}
% endif
<script type='text/javascript'>
    $('#msg-div').focus();
</script>

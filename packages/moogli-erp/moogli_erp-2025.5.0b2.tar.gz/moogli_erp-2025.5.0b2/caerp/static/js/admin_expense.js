
var ExpenseList = {
    popup_selector: null,
    get_status_url: function(expensesheet_id){
        return "/expenses/" + expensesheet_id + "/addpayment";
    },
    payment_form: function(expensesheet_id, total){
        var popup = $(this.popup_selector);
        var form = popup.find('form');
        var url = this.get_status_url(expensesheet_id);
        form.attr('action', url);
        form.find('input[name=amount]').val(total);
        //popup.dialog('open');
        toggleModal('payment_form');
    },
    setExpenseJustified: function(){
        var btngroup = $(this).parent().parent();
        var url = btngroup.data('href');
        let stringVal = $(this).val();
        let boolVal = stringVal == 'true' ? true : false;
        ajax_request(url, {'submit': boolVal}, 'POST');
    },
    setExpenseJustifiedBehaviour: function(){
        $('.expense-justify :input').change(this.setExpenseJustified);
    },
    setup(){
        this.setExpenseJustifiedBehaviour();
    },
};
$(function(){
    ExpenseList.setup();
});

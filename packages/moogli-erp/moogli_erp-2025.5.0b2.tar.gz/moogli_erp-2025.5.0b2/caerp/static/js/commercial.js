
function setTurnoverProjectionForm(month_num, month_name, year, value, el){
  /*"""
   *  Display the CAE Prevision Form and set default values
   */
  var container = $('#form_container');
  hideFormError($('#setform'));
  container.find("input[name=month]").val(month_num);
  container.find("h2").html("CA prévisionnel du mois de "+month_name+" "+year);
  // setting defaults
  var comment = "";
  if (value == undefined){
    value = "";
  }else{
    comment = $(el).attr('title');
  }
  container.find("input[name=value]").val(value);
  container.find("textarea").val(comment);
  // animation
  if (container.is(':visible')){
    container.animate({borderWidth:"10px"}, 400).animate({borderWidth:"1px"}, 200);
  }else{
    $('#form_container').fadeIn("slow");
  }
  $('#form_container').find("input[name=value]").focus();
}

// Page initialisation
$(function(){
  $('#year_form').find('select').change(function(){
    $('#year_form').submit();
  });
  if ($('#setform').find(".alert").length === 0){
    $('#form_container').hide();
  }
});

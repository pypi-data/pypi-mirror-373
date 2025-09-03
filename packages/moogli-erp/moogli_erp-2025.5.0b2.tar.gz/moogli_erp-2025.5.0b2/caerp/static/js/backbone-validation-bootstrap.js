
function showError(control, error){
  /*"""
   * shows error 'message' to the group group in a twitter bootstrap
   * friendly manner
   */
  var group = control.parents(".form-group");
  group.addClass("has-error");
  if (group.find(".help-block").length === 0){
    group.append(
    "<span class=\"help-block error-message\"></span>");
  }
  var target = group.find(".help-block");
  return target.text(error);
}
function hideFormError(form){
  /*"""
   * Remove bootstrap style errors from the whole form
   */
    form.find(".alert").remove();
    var groups = form.find(".form-group");
    groups.removeClass("has-error");
    groups.find(".error-message").remove();
    return form;
}
function hideFieldError(control){
  /*"""
   */
   var group = control.parents(".form-group");
   group.removeClass("has-error");
   group.find(".error-message").remove();
   return control;
}
function BootstrapOnValidForm(view, attr, selector){
    var control, group;
    control = view.$('[' + selector + '=' + attr + ']');
    hideFieldError(control);
}
function BootstrapOnInvalidForm(view, attr, error, selector) {
    var control, group, position, target;
    control = view.$('[' + selector + '=' + attr + ']');
    showError(control, error);
}
function setUpBbValidationCallbacks(bb_module){
    _.extend(bb_module, {
        valid: BootstrapOnValidForm,
        invalid: BootstrapOnInvalidForm
    });
}
setUpBbValidationCallbacks(Backbone.Validation.callbacks);

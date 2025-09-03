
function _displayServerMessage(options){
  /*
   * """ Display a message from the server
   */
  var msgdiv = Handlebars.templates['serverMessage.mustache'](options);
  $(msgdiv).prependTo("#messageboxes").fadeIn('slow').delay(8000).fadeOut(
  'fast', function() { $(this).remove(); });
}
function displayServerError(msg){
  /*
   *  Show errors in a message box
   */
  _displayServerMessage({msg:msg, error:true});
}
function displayServerSuccess(msg){
  /*
   *  Show errors in a message box
   */
  _displayServerMessage({msg:msg});
}

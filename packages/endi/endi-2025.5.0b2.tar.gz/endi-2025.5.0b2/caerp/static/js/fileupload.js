
$(
  function(){
    var description_input = $('input[name=description]');
    var file_input = $('input[type=file]');
    file_input.change(
      function(){
        var filename = this.value.replace(/^.*[\\\/]/, '');
        description_input.val(filename);
      }
    );
  }
);

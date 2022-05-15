window.onload = function() {

    $("#especialidad").change(function() {
        $("#medico option").show();
        $("#medico option[selected='selected'").removeAttr("selected")
        $("#medico option[especialidad!='"+$('option:selected', this).val()+"']").hide();
        $("#medico option[especialidad='"+$('option:selected', this).val()+"']").first().attr("selected", true);
      });
    $("#especialidad").change();
  };

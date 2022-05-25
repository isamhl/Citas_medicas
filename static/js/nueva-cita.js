window.onload = function() {
    fechaHoy();
    $("#div-hora").hide();
    $('#fecha').val("");
    $("#especialidad").change(function() {
        $("#enviar").attr("disabled", true);
        $("#medico option").show();
        $("#medico option[selected='selected'").removeAttr("selected")
        $("#medico option[especialidad!='"+$('option:selected', this).val()+"']").hide();
        $("#medico option[especialidad='"+$('option:selected', this).val()+"']").first().attr("selected", true);
      });

    $("#especialidad, #medico").change(function(){
      $("#fecha").val("");
      $("#div-hora").hide()
      $("#hora").empty();
      $(".errorhoras").hide();
    });

    $("#fecha").change(function(){
      $(".errorhoras").hide()
      $.ajax({
        url:"/horas",
        type:"POST",
        data: {"medico": $("#medico option[selected='selected'").val(), "fecha": $("#fecha").val()},
        success: function(response){
          if(response != 0){
            var jsonhoras = JSON.parse(response);

            if(jsonhoras.length==7){
              $("#div-hora").hide();
              $(".errorhoras").show()
            }else{
              $("#div-hora").show();
              $("#hora").removeAttr("disabled");
              $("#enviar").removeAttr("disabled");
              let array = new Array(0);
              for(var i = 0 ; i < Object.keys(jsonhoras).length; i++ ){
                array.push(jsonhoras[i].hora);
              }
              crearoptions(array);
            }
          }else{
            $("#div-hora").show();
            $("#hora").removeAttr("disabled");
            $("#enviar").removeAttr("disabled");
            crearoptions0();
          }
        },
        error: function(error){
          console.log(error);
        },
      });
    });

    
      $("#enviar").removeAttr("disabled");
    

    $("#especialidad").change();
  };

function fechaHoy(){
  var today = new Date();
  var dd = today.getDate();
  var mm = today.getMonth() + 1; //January is 0!
  var yyyy = today.getFullYear();

  if (dd < 10) {
    dd = '0' + dd;
  }

  if (mm < 10) {
    mm = '0' + mm;
  } 
      
  today = yyyy + '-' + mm + '-' + dd;
  document.getElementById("fecha").setAttribute("min", today);
}

function crearoptions(horas){
  var html="";
  for(var i = 8 ; i < 15; i++ ){
    html += `<option value=${i}>${i}-${i+1}</option>`
  }
  $("#hora").html(html);
  for (var i=0;i<=horas.length;i++) {
    $(`#hora option[value='${horas[i]}']`).hide();
  }
  console.log
  $("#hora option[selected='selected'").removeAttr("selected")
  $(`#hora :not([style*="display: none"])`).first().attr("selected", true);
}

function crearoptions0(){
  var html="";
  for(var i = 8 ; i < 15; i++ ){
    html += `<option value=${i}>${i}-${i+1}</option>`
  }
  $("#hora").html(html);
}

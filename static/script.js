$(document).ready(function () {

    $('#envoyer').click(function () {
        var titre = $("#titre").val();
        var identifiant = $("#identifiant").val();
        var auteur = $("#auteur").val();
        var date_publication = $("#date_publication").val();
        var paragraphe = $("#paragraphe").val();
        var body =JSON.stringify({"titre":titre,"identifiant":identifiant,"auteur":auteur,
            "date_publication":date_publication,"auteur":auteur,"paragraphe":paragraphe});
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function () {

            if (xhttp.readyState === 4) {
                if (xhttp.status === 201){
                    document.getElementById("container").innerHTML = xhttp.responseText;
                }else{
                    var reponse =(xhttp.responseText);
                    var elt = document.getElementById("erreur");
                    elt.innerHTML = xhttp.responseText;
                }
            }
        };
        xhttp.open("POST", "http://localhost:5000/inserer", true);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(body);
    });

    $("#titre").blur(function(){
        var titre = $("#titre").val();

        var body = JSON.stringify({"title":titre});

        if (titre != ""){
            var xhttp  = new XMLHttpRequest();
            xhttp.onreadystatechange = function () {
                if (xhttp.readyState == 4){
                    if(xhttp.status == 200){
                        var identifiant = document.getElementById("identifiant");
                        $("#identifiant").val(xhttp.responseText);
                    }else{

                    }
                }
            }
            xhttp.open("POST", "http://localhost:5000/identifiant", true);
            xhttp.setRequestHeader("Content-Type", "application/json");
            xhttp.send(body);
        }
    });

     $("#identifiant").blur(function(){
        var identifiant = $("#identifiant").val();
        var body = JSON.stringify({"identifiant":identifiant});
        var xhttp  = new XMLHttpRequest();
        xhttp.onreadystatechange = function () {
             if (xhttp.readyState == 4){
                 if(xhttp.responseText == 400){
                      var identifier = document.getElementById("erreurIdentifiant");
                      identifier.innerHTML = xhttp.responseText;
                 }else{

                 }
             }
        }
        xhttp.open("POST", "http://localhost:5000/identifiant/verification", true);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(body);

    });

});

function identifiantUnique() {
    var xhttp = new XMLHttpRequest();
    xhttp.open(method,url,true);
    xhttp.onreadystatechange=(function () {
        if (xhttp.readyState == 4){
            if(xhttp.status == 201){

            }else{

            }
        }
    });
     xhttp.setRequestHeader("Content-Type", "application/json");
     xhttp.send(body);
}


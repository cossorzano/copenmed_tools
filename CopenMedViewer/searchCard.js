/* TODO: Change add cards to search cards in parent */

var cardId = 1;

$(document).ready(function(){
    $("#addLabel").click(function(){
        var str = $("#divInput").val();
        var id = cardId;
        div = document.createElement('div');
        $(div).addClass("card").html(str).hide().fadeIn('slow');
        $(div).attr({"id": "card-"+id});
        // $(div).attr({"draggable": "true", "ondragstart": "dragStart(event)", "id": "card-"+id});
        $("#userList").append(div);
        $(".modal").css("display", "none");
        cardId++;
    });
});

$(document).on('keypress',function(e) {
    if(e.which == 13 && $(".modal").css('display') == 'block') {
        var str = $("#divInput").val();
        var id = cardId;
        div = document.createElement('div');
        $(div).addClass("card").html(str).hide().fadeIn('slow');
        $(div).attr({"id": "card-"+id});
        // $(div).attr({"draggable": "true", "ondragstart": "dragStart(event)", "id": "card-"+id});
        $("#userList").append(div);
        $(".modal").css("display", "none");
        cardId++;
    }
});
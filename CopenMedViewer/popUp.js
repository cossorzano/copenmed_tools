$(document).ready(function(){
    $(".addCard").click(function() {
        $(this).parents("#page-cell").find(".copenMed_container > div").each(function() {
            var str = $(this).text().replace("done", "");
            div = document.createElement('div');
            $(div).attr({"id": "not-selected"});
            $(div).css({"width": "100px"});
            $(div).addClass("card").html(str).hide().fadeIn('slow');
            $(".container-options").append(div);
        });
        $(this).parents("#page-cell").find(".user_selection > div").each(function() {
            var str = $(this).text().replace("done", "");
            div = document.createElement('div');;
            $(div).attr({"id": "selected"});
            $(div).css({"width": "100px", "border": "2px solid #3700B3"});
            $(div).addClass("card").html(str).hide().fadeIn('slow');
            $(".container-options").append(div);
        });
        $("#modal-search").css({"display": "flex", "align-items": "center", "justify-content": "center"});
    });
});

$(document).ready(function(){
    $(window).click(function(event) {
        if (event.target == $('#modal-search')[0]) {
            $('#modal-search').css("display", "none");
            // $(".container-options").find("#selected").each(function(){

            // });
            $(".container-options").empty();
        }
    });
});

$(document).ready(function(){
    $(".close").click(function() {
        $("#modal-search").css("display", "none");
        $(".container-options").empty();
    });
});


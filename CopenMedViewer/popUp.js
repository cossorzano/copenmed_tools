$(document).ready(function(){
    $(".addCard").click(function() {
        $("#modal-search").css({"display": "flex", "align-items": "center", "justify-content": "center"});
    });
});

$(document).ready(function(){
    $(window).click(function(event) {
        if (event.target == $('#modal-search')[0]) {
            $('#modal-search').css("display", "none");
        }
    });
});

$(document).ready(function(){
    $(".close").click(function() {
        $("#modal-search").css("display", "none");
    });
});


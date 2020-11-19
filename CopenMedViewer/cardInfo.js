$(document).ready(function() {
    $(".card").dblclick(function() {
        $("#modal-card-info").css({"display": "flex", "align-items": "center", "justify-content": "center"});
    });
});

$(document).ready(function() {
    $(window).click(function(event) {
        if (event.target == $('#modal-card-info')[0]) {
            $('#modal-card-info').css("display", "none");
        }
    });
});

$(document).ready(function() {
    $(".close").click(function() {
        $("#modal-card-info").css("display", "none");
    });
});
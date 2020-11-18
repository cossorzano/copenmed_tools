$(document).ready(function(){
    $(".addCard").click(function() {
        $(".modal").css("display", "block");
    });
});

$(document).ready(function(){
    $(window).click(function(event) {
        if (event.target == $('.modal')[0]) {
            $('.modal').css("display", "none");
        }
    });
});

$(document).ready(function(){
    $(".close").click(function() {
        $(".modal").css("display", "none");
    });
});


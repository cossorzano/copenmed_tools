$(document).ready(function(){
    $(".check").on("click", function(e) {
        var check = $(this);
        var card = $(check).closest(".card");
        var container_new;
        if (($(check).parents(".copenMed_container").length)) {
            // var container = $(this).closest(".copenMed_container");
            container_new = $(check).closest(".container").children(".user_selection");
            $(check).css({color: "#3700B3"});
        }
        else {
            // var container = $(this).closest(".user_selection");
            container_new = $(check).closest(".container").children(".copenMed_container");
            $(check).css({color: "#292929"});
        }
        $(check).hide();
        $(card).slideUp('normal', function() {
            $(card).detach().appendTo(container_new);
            $(card).slideDown('normal', function() {$(check).show()});
        });
        // $(card).detach().appendTo(container_new);
    });
});
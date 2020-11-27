$(document).ready(function(){
    $(".check").on("click", function(e) {
        var check = $(this);
        var card = $(check).closest(".card");
        var cross = $(card).find(".cross");
        var container_new;
        if ($(check).parents(".copenMed_container").length && hexc($(cross).css("color")) == "#292929") {
            // var container = $(this).closest(".copenMed_container");
            container_new = $(check).closest(".container").children(".user_selection");
            $(check).css({color: "#3700B3"});
            $(check).hide();
            $(cross).hide();
            $(card).slideUp('normal', function() {
                $(card).detach().appendTo(container_new);
                $(card).slideDown('normal', function() {
                    $(check).show();
                    $(cross).show();
                });
            });
        }
        else if ($(check).parents(".user_selection").length && hexc($(cross).css("color")) == "#292929") {
            // var container = $(this).closest(".user_selection");
            container_new = $(check).closest(".container").children(".copenMed_container");
            $(check).css({color: "#292929"});
            $(check).hide();
            $(cross).hide();
            $(card).slideUp('normal', function() {
                $(card).detach().appendTo(container_new);
                $(card).slideDown('normal', function() {
                    $(check).show();
                    $(cross).show();
                });
            });
        }
        else if (($(check).parents(".user_selection").length) && hexc($(cross).css("color")) == "#FF0000") {
            // var container = $(this).closest(".copenMed_container");
            container_new = $(cross).closest(".container").children(".copenMed_container");
            $(cross).css({color: "#292929"});
            $(check).css({color: "#3700B3"});
        }
        // $(card).detach().appendTo(container_new);
    });
    $(".cross").on("click", function(e) {
        var cross = $(this);
        var card = $(cross).closest(".card");
        var check = $(card).find(".check");
        var container_new;
        if ($(cross).parents(".copenMed_container").length && hexc($(check).css("color")) == "#292929") {
            // var container = $(this).closest(".copenMed_container");
            container_new = $(cross).closest(".container").children(".user_selection");
            $(cross).css({color: "red"});
            $(check).hide();
            $(cross).hide();
            $(card).slideUp('normal', function() {
                $(card).detach().appendTo(container_new);
                $(card).slideDown('normal', function() {
                    $(check).show();
                    $(cross).show();
                });
            });
        }
        else if ($(cross).parents(".user_selection").length && hexc($(check).css("color")) == "#292929") {
            // var container = $(this).closest(".user_selection");
            container_new = $(cross).closest(".container").children(".copenMed_container");
            $(cross).css({color: "#292929"});
            $(check).hide();
            $(cross).hide();
            $(card).slideUp('normal', function() {
                $(card).detach().appendTo(container_new);
                $(card).slideDown('normal', function() {
                    $(check).show();
                    $(cross).show();
                });
            });
        }
        else if (($(cross).parents(".user_selection").length) && hexc($(check).css("color")) == "#3700B3") {
            // var container = $(this).closest(".copenMed_container");
            container_new = $(cross).closest(".container").children(".copenMed_container");
            $(cross).css({color: "red"});
            $(check).css({color: "#292929"});
        }
        // $(card).detach().appendTo(container_new);
    });
});


function hexc(colorval) {
    var parts = colorval.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    delete(parts[0]);
    for (var i = 1; i <= 3; ++i) {
        parts[i] = parseInt(parts[i]).toString(16);
        if (parts[i].length == 1) parts[i] = '0' + parts[i];
    }
    color = '#' + parts.join('');

    return color.toUpperCase();
}
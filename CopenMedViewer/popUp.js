var cardContainer;
var selectedCard;
var container_new;

$(document).ready(function(){
    $(".addCard").click(function() {
        cardContainer = $(this).parents("#page-cell");
        $(this).parents("#page-cell").find(".copenMed_container > div").each(function() {
            var str = $(this).text().replace("done", "").replace("clear", "");
            div = document.createElement('div');
            $(div).attr({"id": "not-selected"});
            $(div).css({"width": "100px"});
            $(div).addClass("card").html(str).hide().fadeIn('slow');
            $(".container-options").append(div);
        });
        $(this).parents("#page-cell").find(".user_selection > div").each(function() {
            var str = $(this).text().replace("done", "").replace("clear", "");
            div = document.createElement('div');
            if (hexc($(this).find(".check").css("color")) == "#3700B3") {
                $(div).attr({"id": "selected-true"});
                $(div).css({"width": "100px", "border": "2px solid #3700B3"});
            }
            else if ((hexc($(this).find(".cross").css("color")) == "#FF0000")) {
                $(div).attr({"id": "selected-false"});
                $(div).css({"width": "100px", "border": "2px solid red"});
            }
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
            $(".container-options").empty();
        }
    });
});

$(document).ready(function() {
    $("#addLabel").on("click", function() {
        $(".container-options").children("#selected-true").each(function(){
            selectedCard = this;
            $(cardContainer).find(".copenMed_container > div").each(function(){
                var str = $(this).text().replace("done", "").replace("clear", "");
                if (str == $(selectedCard).text()) {
                    container_new = $(cardContainer).find(".user_selection");
                    if (hexc($(this).find(".cross").css("color")) == "#FF0000") {
                        $(this).find(".check").css({color: "#3700B3"});
                        $(this).find(".cross").css({color: "#292929"});
                    }
                    else if (hexc($(this).find(".cross").css("color")) == "#292929")
                    {
                        $(this).find(".check").css({color: "#3700B3"});
                        $(this).find(".cross").css({color: "#292929"});
                        $(this).detach().appendTo(container_new) 
                    }
                }
            });
        });
        $(".container-options").children("#selected-false").each(function(){
            selectedCard = this;
            $(cardContainer).find(".copenMed_container > div").each(function(){
                var str = $(this).text().replace("done", "").replace("clear", "");
                if (str == $(selectedCard).text()) {
                    container_new = $(cardContainer).find(".user_selection");
                    if (hexc($(this).find(".check").css("color")) == "#3700B3") {
                        $(this).find(".check").css({color: "#292929"});
                        $(this).find(".cross").css({color: "red"});
                    }
                    else if (hexc($(this).find(".check").css("color")) == "#292929")
                    {
                        $(this).find(".check").css({color: "#292929"});
                        $(this).find(".cross").css({color: "red"});
                        $(this).detach().appendTo(container_new) 
                    }
                }
            });
        });
        $(".container-options").children("#not-selected").each(function(){
            selectedCard = this;
            $(cardContainer).find(".user_selection > div").each(function(){
                var str = $(this).text().replace("done", "").replace("clear", "");
                if (str == $(selectedCard).text()) {
                    container_new = $(cardContainer).find(".copenMed_container");
                    $(this).find(".check").css({color: "#292929"});
                    $(this).find(".cross").css({color: "#292929"});
                    $(this).detach().appendTo(container_new)
                }
            });
        });
        $('#modal-search').css("display", "none");
        $(".container-options").empty();
    });
});

$(document).ready(function(){
    $(".container-options").on('click', '.card', function() {
        if (this.id == "selected-true") {
            $(this).css({"border": "none"});
            $(this).attr({"id": "not-selected"});
        }
        else if ((this.id == "not-selected")) {
            $(this).css({"border": "2px solid #3700B3"});
            $(this).attr({"id": "selected-true"});
        }
        else if ((this.id == "selected-false")) {
            $(this).css({"border": "none"});
            $(this).attr({"id": "not-selected"});
        }
    });
});

$(document).ready(function(){
    $(".container-options").on('dblclick', '.card', function() {
        if (this.id == "selected-true") {
            $(this).css({"border": "2px solid red"});
            $(this).attr({"id": "selected-false"});
        }
        else if ((this.id == "not-selected")) {
            $(this).css({"border": "2px solid red"});
            $(this).attr({"id": "selected-false"});
        }
    });
});

// $(document).ready(function(){
//     $(".close").click(function() {
//         $("#modal-search").css("display", "none");
//         $(".container-options").empty();
//     });
// });


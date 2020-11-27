$(document).ready(function() {
    var list = $(".container").map(function(){
        var childs = $(this).children("div").toArray();
        var ids = [];
        for (var i = 0; i < childs.length; i++) {
            if (childs[i].id !== "")
                ids.push("#" + childs[i].id);
        }
        $(this).children("div").map(function() {
            $(this).sortable({
                placeholder: 'placeholder',
                revert: 150,
                connectWith: ids.join(","),
                start: function(e, ui){
                    placeholderHeight = ui.item.outerHeight();
                    ui.placeholder.height(placeholderHeight + 15);
                    $('<div class="slide-placeholder-animator" data-height="' + placeholderHeight + '"></div>').insertAfter(ui.placeholder);
                
                },
                change: function(event, ui) {
                    ui.placeholder.stop().height(0).animate({
                        height: ui.item.outerHeight() + 15
                    }, 100);
                    placeholderAnimatorHeight = parseInt($(".slide-placeholder-animator").attr("data-height"));
                    $(".slide-placeholder-animator").stop().height(placeholderAnimatorHeight + 15).animate({
                        height: 0
                    }, 100, function() {
                        $(this).remove();
                        placeholderHeight = ui.item.outerHeight();
                        $('<div class="slide-placeholder-animator" data-height="' + placeholderHeight + '"></div>').insertAfter(ui.placeholder);
                    });
                    
                },
                stop: function(e, ui) {
                    // var check = $(this).data().uiSortable.currentItem.children("div").children("span");
                    var check = $(ui.item).children("div").children(".check");
                    var cross = $(ui.item).children("div").children(".cross");
                    if (($(ui.item).parents(".copenMed_container").length)) {
                        $(check[0]).animate({color: "#292929"}, 50);
                        $(cross[0]).animate({color: "#292929"}, 50);
                    }
                    else
                        $(check[0]).animate({color: "#3700B3"}, 50);
                    $(".slide-placeholder-animator").remove(); 
                },
            });
        });
    });
});

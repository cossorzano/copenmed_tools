$(document).ready(function(){
    if ($(window).width() >= 950) {
        $('header').hover(function() {
            $(document.body).stop(true).animate({'padding-left':'300px'}, 500);
        }, function() {
            $(document.body).stop(true).animate({'padding-left':'200px'}, 500);
        });
    }
    else {
        $('header').unbind('mouseenter mouseleave'); 
    }
});

$(window).resize(function(){
    if ($(window).width() >= 950) {
        $('header').hover(function() {
            $(document.body).stop(true).animate({'padding-left':'300px'}, 500);
        }, function() {
            $(document.body).stop(true).animate({'padding-left':'200px'}, 500);
        });
    }
    else {
        $('header').unbind('mouseenter mouseleave'); 
    }
});
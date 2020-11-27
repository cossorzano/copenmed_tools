$(document).ready(function(){
    $("#searchCards > input").on("keyup", function() {
        var key = this.value;
        $(".container-options").children(".card").each(function() {
           var $this = $(this);
           $this.toggle($(this).text().indexOf(capitalizeFirstLetter(key)) >= 0);
        });
    });
});

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

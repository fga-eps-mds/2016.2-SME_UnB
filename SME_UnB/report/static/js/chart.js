(function(){
    $(document).ready(function(){
        $.ajax({
            url: "/reports/list_transductors",
            type: "GET",
            success: function(response){
                console.log(response)
            }
        })
    })


})();

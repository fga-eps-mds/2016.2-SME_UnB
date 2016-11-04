$(function() {
    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
       The functions below will create a header with csrftoken
       */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    $('#reset_btn').on('click', function(event){
        event.preventDefault();
        confirm_email();
    });

    function add_pass_fields(email){

        $("#myModalLabel")[0].textContent = "Alterar senha";

        var tittle = "<h2 class='form-signin-heading text-center'>Nova senha</h2>";
        var email = "<input id='email' type='hidden' value='" + email + "' name='email' />"

        var div_new_pass = "<div id='form-group-confirm' class='form-group'></div>";
        var div_confirm_pass = "<div id='form-group' class='form-group'></div>";

        var form = "<form  id='form-pass' class='form-signin'></form>";
        var button_pass = "<button id='reset_pass' class='btn btn-lg btn-primary btn-block'>Trocar senha</button>";

        var label_new_pass = "<label for='inputPassword' class='sr-only'>{% trans 'Password' %}</label>";
        var input_new_pass = "<input type='password' id='inputPassword' name='password'" +
            "class='form-control' placeholder='Password' required>";

        var label_confirm_pass = "<label for='confirmPassword' class='sr-only'>Confirm Password</label>";
        var input_confirm_pass = "<input type='confirmPassword' id='confirmPassword' name='confirmPassword'" +
            " class='form-control' placeholder='Confirm Password' required>";

        $('#content-form').append(form);

        $('#form-pass').append(tittle);
        $('#form-pass').append(div_confirm_pass);
        $('#form-pass').append(div_new_pass);
        $('#form-pass').append(email);

        $('#form-group').append(label_new_pass);
        $('#form-group').append(input_new_pass);

        $('#form-group-confirm').append(label_confirm_pass);
        $('#form-group-confirm').append(input_confirm_pass);

        $('#form-pass').append(button_pass);

        $('#reset_pass').on('click', function(event){
            reset_password();
        });
    };


    // AJAX for posting
    function reset_password() {
        $.ajax({
            url : "/accounts/reset_pass/", // the endpoint
            type : "POST", // http method
            data : {
                pass: $('#inputPassword').val(),
                confirm_pass: $('#confirmPassword').val(),
                email: $('#email').val(),
            }, // data sent with the post request

            // handle a successful response
            success : function(json) {
                alert(json.message);
            },

            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    };

    // AJAX for posting
    function confirm_email() {
        $.ajax({
            url : "/accounts/reset/0/", // the endpoint
            type : "POST", // http method
            data : {
                email: $('#email').val(),
                token: $('#token').val(),
            }, // data sent with the post request

            // handle a successful response
            success : function(json) {
                if(json.is_valid == "yes"){
                    $("#content-form").empty();
                    add_pass_fields(json.email);
                }
                else{
                    $("#tittle-confirm")[0].textContent = json.message;
                    $("#email").remove();
                    $("#reset_btn").remove();
                }
            },

            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    };
});

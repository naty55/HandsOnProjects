console.log("login page ajax acting");

$(document).ready(function() {

    $('#btn-login').on('click', function() {

        $.ajax({
            url: $('form').attr('action'),
            type: 'post',
            data: $('form').serialize(),
            success: function(data) {
                 // here i should add some code to handle the error
                 if (data.status == -1 ){
                     alert('username/password are not correct')
                 }
                else
                {
                    $('form').submit();
                }
            },
            error: function() {
                alert('There has been an error, please alert us immediately');
            }
        });

        return false
    });
});
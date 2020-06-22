console.log("Register page ajax acting")

$(document).ready(function() {

    $('#btn-login').on('click', function() {

        $.ajax({
            url: $('form').attr('action'),
            type: 'post',
            data: $('form').serialize(),
            success: function(data) {
                if (data.status)
                {
                 // here i should add some code to handle the error
                 if (data.status == -3 ){
                     console.log("this mail is already in use")
                 }
                 else if (data.status == -2){
                     console.log("this name is already in use")
                 }

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
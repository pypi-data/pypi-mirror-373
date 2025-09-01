$(function () {

    $("#id_upfile").on('change', init_guess_csv_properties);


    function init_guess_csv_properties() {

        init_form();
        guess_csv_properties(false);

    }

    function guess_csv_properties(changed_delimiter) {
        let file = $('#id_upfile')[0].files[0];
        if (!file) return;

        if(changed_delimiter){

            Papa.parse(file, {
                preview: 2,
                header: true,
                delimiter: $('#id_delimiter').val(),
                complete: on_complete
            });
        }
        else{

            Papa.parse(file, {
                preview: 2,
                header: true,
                complete: on_complete
            });
        }

     
    }

    function on_complete(results, config){

        init_form();
        if (results.errors.length > 0){
            print_errors(results.errors)
        } else {
            // Disable delimiter field
            $('#id_delimiter').prop('readonly', true);
        }

        if(results.meta.delimiter!=''){

            // Set guessed delimiter to delimiter input field
            if(results.meta.delimiter == '\t'){
                delimiter = '<Tab>';
            } else if(results.meta.delimiter == ' '){
                delimiter = '<Space>';
            } else {
                delimiter = results.meta.delimiter;
            }
            $('#id_delimiter').val(delimiter);

        }

        first_row_values = results.data[0];
        // Add file headers to each header select fields
        // selecting the value that is equal to expected header, if any
        let headers = results.meta.fields;
        $("#headers_mapping select").children().remove();
        $.each($("#headers_mapping select"), function(key, select_item){
            id = select_item.id;
            label = $("label[for='" + select_item.id + "']").text();
            $(select_item).append('<option value="">-----</option>');
            headers.forEach(function(header){
                let is_selected = '';
                if (label == header){
                    is_selected = 'selected'
                }
                $(select_item).append('<option value="' + header +'" ' + is_selected +">" + header + "</option>");
            });
            $(select_item).closest('.header_field').find('.first-row').html(first_row_values[label]);
        });
    
    }

    function print_errors(errors){
        errors.forEach(function(error){
            if (error.type == 'FieldMismatch') {
                $('#errors_headers_mapping').append(error.message + "<br />");
            } else {
                $('#errors_csv_options').append(error.message + "<br />");
            }
        });
    }

    function init_form(){
        $('#id_delimiter').prop('readonly', false);
        $('#errors_csv_options').empty();
        $('#errors_headers_mapping').empty();
        $('.first-row').html('');
    }

    function show_error_popover(element, error_message){
        let options = {
            content: '<span class="text-danger">' + error_message + '</span>',
            html: true,
            trigger: 'focus',
        }
        element.popover(options);
        element.popover('show');
        element.addClass('is-invalid');
    }

    // Validate mapping:
    // * Headers are required
    // * Headers cannot be repeated
    $("#submit").on('click', function(){
        let no_error = true;
        let chosen_header_fields = [];

        $.each($("#headers_mapping select"), function(key, select_item){
            header = $(select_item).val();
            if (header == '') {
                show_error_popover($(select_item), 'This field is required.');
                no_error = false;
            } else {
                if (chosen_header_fields.includes(header)) {
                    show_error_popover($(select_item), 'This header is repeated.');
                    no_error = false;
                } else {
                    chosen_header_fields.push(header);
                }
            }
        });
        return no_error;
    });

    // Remove popup errors
    $("#headers_mapping select").on("change", function(){
        $(this).popover('dispose');
        $(this).removeClass('is-invalid');
        $(this).closest(".header_field").find(".first-row").html(first_row_values[$(this).val()]);
    });


    $('#id_delimiter').keyup(function(event){
        
        init_form();
        guess_csv_properties(true);

      });

});
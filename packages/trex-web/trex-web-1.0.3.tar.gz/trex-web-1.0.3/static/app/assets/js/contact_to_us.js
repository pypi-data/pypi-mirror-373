function initContactToUs(){
	validateContactToUsForm();
	
	$('#contact_to_us_button').click(function(e){
		e.preventDefault();
		$('#contact_to_us_form').submit();
		
	});
}

function validateContactToUsForm(){
	
	$('#contact_to_us_form').validate({
						rules:{
        					name:{
                				required    		: true,
								minlength			: 3,
                				maxlength   		: 200
							},
							email:{
								email				: true,
								required    		: true,
                				maxlength			: 150
							},
							purpose:{
								required    		: true
							},
                            message:{
                                required            : true,
                                maxlength           : 3000
                            }
						},
						errorClass	: "help-block error",
				        validClass 	: "success",
				        errorElement: "div",
				        highlight:function(element, errorClass, validClass) {
				            $(element).parents('.control-group').addClass('error').removeClass(validClass);
				        },
				        unhighlight: function(element, errorClass, validClass) {
				            $(element).parents('.error').removeClass('error').addClass(validClass);
				        },
				        submitHandler : function(form) {
				            submitContactToUsForm(form);
				        }//end submitHandler
    });
}

function submitContactToUsForm(form){
	var $contact_to_us_button 			= $('#contact_to_us_button');
	var contact_to_us_data 				= $(form).serializeJSON();
	
	$.console.log('contact_to_us_data='+JSON.stringify(contact_to_us_data));
	
	
	showLoading();
	
	$contact_to_us_button.disabled();
	
	$.ajax({
            url 		: form.action,
            type 		: form.method,
			dataType 	: 'json', 
            data 		: contact_to_us_data,
            success 	: function(response) {
				$.console.log('after submitted with success ='+ JSON.stringify(response));
				
				hideLoading();
				$contact_to_us_button.enabled();
				
				notify('success', 'Hurray~!', createNotifyMessageHTML(response));
				
				window.location = '/thank-you-for-contact-us';
					
				

            },
	        error : function(jqXHR, textStatus, errorThrown) {
	           	$.console.log('after submitted with error ='+ JSON.stringify(jqXHR));
				var error_message = jqXHR.responseText;
				var error_message_in_json = JSON.parse(error_message);
				$.console.log('error error_message_in_json='+error_message_in_json);
				hideLoading();
				$contact_to_us_button.enabled();
				notify('error', 'Failed to contact', createNotifyMessageHTML(error_message_in_json.msg));
	        },
	        beforeSend : function(xhr) {
	        	
	        }            
    });
	
}
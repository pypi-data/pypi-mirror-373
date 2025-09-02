function initDemoRequest(){
	validateDemoRequestForm();
	
	$('#demo_request_button').click(function(e){
		e.preventDefault();
		$('#demo_request_form').submit();
		
	});
}

function validateDemoRequestForm(){
	
	$('#demo_request_form').validate({
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
				            submitDemoRequestForm(form);
				        }//end submitHandler
    });
}

function submitDemoRequestForm(form){
	var $demo_request_button 			= $('#demo_request_button');
	var demo_request_data 				= $(form).serializeJSON();
	
	$.console.log('demo_request_data='+JSON.stringify(demo_request_data));
	
	
	showLoading();
	
	$demo_request_button.disabled();
	
	$.ajax({
            url 		: form.action,
            type 		: form.method,
			dataType 	: 'json', 
            data 		: demo_request_data,
            success 	: function(response) {
				$.console.log('after submitted with success ='+ JSON.stringify(response));
				
				hideLoading();
				$demo_request_button.enabled();
				
				notify('success', 'Hurray~!', createNotifyMessageHTML(response));
				
				window.location = '/thank-you-for-contact-us';
					
				

            },
	        error : function(jqXHR, textStatus, errorThrown) {
	           	$.console.log('after submitted with error ='+ JSON.stringify(jqXHR));
				var error_message = jqXHR.responseText;
				var error_message_in_json = JSON.parse(error_message);
				$.console.log('error error_message_in_json='+error_message_in_json);
				hideLoading();
				$demo_request_button.enabled();
				notify('error', 'Failed to contact', createNotifyMessageHTML(error_message_in_json.msg));
	        },
	        beforeSend : function(xhr) {
	        	
	        }            
    });
	
}
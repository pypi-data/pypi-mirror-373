function initJoinAsPartner(){
	validateJoinAsPartnerForm();
	
	$('#join_as_partner_button').click(function(e){
		e.preventDefault();
		$('#join_as_partner_form').submit();
		
	});
}

function validateJoinAsPartnerForm(){
	
	$('#join_as_partner_form').validate({
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
				            submitJoinAsPartnerForm(form);
				        }//end submitHandler
    });
}

function submitJoinAsPartnerForm(form){
	var $join_as_partner_button 			= $('#join_as_partner_button');
	var join_as_partner_data 				= $(form).serializeJSON();
	
	$.console.log('join_as_partner_data='+JSON.stringify(join_as_partner_data));
	
	
	showLoading();
	
	$join_as_partner_button.disabled();
	
	$.ajax({
            url 		: form.action,
            type 		: form.method,
			dataType 	: 'json', 
            data 		: join_as_partner_data,
            success 	: function(response) {
				$.console.log('after submitted with success ='+ JSON.stringify(response));
				
				hideLoading();
				$join_as_partner_button.enabled();
				
				notify('success', 'Hurray~!', createNotifyMessageHTML(response));
				
				window.location = '/thank-you-for-contact-us';
					
				

            },
	        error : function(jqXHR, textStatus, errorThrown) {
	           	$.console.log('after submitted with error ='+ JSON.stringify(jqXHR));
				var error_message = jqXHR.responseText;
				var error_message_in_json = JSON.parse(error_message);
				$.console.log('error error_message_in_json='+error_message_in_json);
				hideLoading();
				$join_as_partner_button.enabled();
				notify('error', 'Failed to contact', createNotifyMessageHTML(error_message_in_json.msg));
	        },
	        beforeSend : function(xhr) {
	        	
	        }            
    });
	
}
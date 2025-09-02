function initSignInPage(){
	validateSignInForm();
	
	$('#signin_button').click(function(e){
		e.preventDefault();
		$('#signin_form').submit();
	});
	
}

function validateSignInForm(){
	
	$('#signin_form').validate({
						rules:{
        					signin_email:{
								email				: true,
								required    		: true,
                				maxlength			: 150
							},
							password	:{
								required    		: true,
                				maxlength   		: 30,
								minlength			: 6
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
				            submitSignInForm(form);
				        }//end submitHandler
    });
}

function submitSignInForm(form){
	var signin_data 				= $(form).serializeJSON();
	var password					= signin_data['password'];
	var $signin_button 				= $('#signin_button');
	$.console.log('password='+password);
	
	var hashed_password				= CryptoJS.MD5(password).toString();
	
	$.console.log('hashed_password='+hashed_password);
	
	signin_data['password'] 		= hashed_password;
	
	$.console.log('signin_data='+JSON.stringify(signin_data));
	
	showLoading();
	$signin_button.disabled();
	
	
	$.ajax({
            url 		: form.action,
            type 		: form.method,
			dataType 	: 'json', 
            data 		: signin_data,
            success 	: function(response) {
				$.console.log('after submitted with success ='+ JSON.stringify(response));
				hideLoading();
				window.location = DASHBOARD_URL;
				
				
				
            },
	        error : function(jqXHR, textStatus, errorThrown) {
	           	$.console.log('after submitted with error ='+ JSON.stringify(jqXHR));
				var error_message = jqXHR.responseText;
				var error_message_in_json = JSON.parse(error_message);
				$.console.log('error error_message_in_json='+error_message_in_json);
				hideLoading();
				$signin_button.enabled();
				notify('error', 'Failed to signin', createNotifyMessageHTML(error_message_in_json.msg));
	        },
	        beforeSend : function(xhr) {
	        	
	        }            
    });
}
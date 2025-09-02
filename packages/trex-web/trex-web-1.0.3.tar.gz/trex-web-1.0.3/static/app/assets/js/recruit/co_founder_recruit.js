function initCoFounderRecruit(){
	$.console.log('---initCoFounderRecruit---');
	validateCoFounderRecruitForm();
	
	$('#co_founder_recruit_button').click(function(e){
		e.preventDefault();
		$('#co_founder_recruit_form').submit();
		
	});
	$('#other').click(function(event){
		if($(this).is(":checked")){
			$('#other_skill').enabled();
		}else{
			$('#other_skill').disabled();
		}
	});
	
	
	
}

function validateCoFounderRecruitForm(){
	
	$('#co_founder_recruit_form').validate({
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
							involved_in_founding:{
								required    		: true
							},
                            address:{
                                required            : true,
                                maxlength           : 1000
                            },
							employment_time:{
								required    		: true
								
							},
							skill:{
								required    		: true
								
							},
							linkedin_profile:{
								required    		: true,
								maxlength           : 1000
							},
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
				            submitCoFounderRecruitForm(form);
				        }//end submitHandler
    });
}

function submitCoFounderRecruitForm(form){
	var $co_founder_recruit_button 				= $('#co_founder_recruit_button');
	var co_founder_recruit_data 				= $(form).serializeJSON();

	let selected_skills_list = [];
	
	$('input:checkbox[name=skill]').each(function() 
	{    
	    if($(this).is(':checked'))
	      selected_skills_list.push($(this).val());
	});
	co_founder_recruit_data['skill'] = selected_skills_list.join(',');
	$.console.log('co_founder_recruit_data='+JSON.stringify(co_founder_recruit_data));
	
	
	showLoading();
	
	$co_founder_recruit_button.disabled();
	
	$.ajax({
            url 		: form.action,
            type 		: form.method,
			dataType 	: 'json', 
            data 		: co_founder_recruit_data,
            success 	: function(response) {
				$.console.log('after submitted with success ='+ JSON.stringify(response));
				let next_page = response.next_page;
				hideLoading();
				$co_founder_recruit_button.enabled();
				
				//notify('success', 'Hurray~!', createNotifyMessageHTML(response));
				
				window.location = next_page;
				
					
				

            },
	        error : function(jqXHR, textStatus, errorThrown) {
	           	$.console.log('after submitted with error ='+ JSON.stringify(jqXHR));
				var error_message = jqXHR.responseText;
				var error_message_in_json = JSON.parse(error_message);
				$.console.log('error error_message_in_json='+error_message_in_json);
				hideLoading();
				$co_founder_recruit_button.enabled();
				//notify('error', 'Failed to submit', createNotifyMessageHTML(error_message_in_json.msg));
				notify('error', 'Failed to submit', error_message_in_json.msg);
	        },
	        beforeSend : function(xhr) {
	        	
	        }            
    });
	
}
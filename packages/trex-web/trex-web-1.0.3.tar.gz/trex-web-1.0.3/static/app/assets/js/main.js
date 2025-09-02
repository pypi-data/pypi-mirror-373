/**
 * Created by jacklok on 3/14/16.
 */
function initLandingPage(){
	$.console.log('---initLandingPage---');
    $('#copyright_year').html(new Date().getFullYear());
	initMagnifyPopup();	
}

function initMagnifyPopup(){
	
	$('.open-popup').magnificPopup({ 
                type: "image",
			    removalDelay: 160,
			    preloader: false,
			    fixedContentPos: false,
				closeBtnInside: true, 
				mainClass: 'mfp-fade',
			    
  
                 
            });
	
	$('.popup-video').magnificPopup({ 
                disableOn: 700,
        		type: 'iframe',
			    removalDelay: 160,
			    preloader: false,
			    fixedContentPos: false,
				closeBtnInside: true, 
				mainClass: 'mfp-fade',
				iframe: {
		            patterns: {
		                youtube_short: {
		                  index: 'youtu.be/',
		                  id: 'youtu.be/',
		                  src: '//www.youtube.com/embed/%id%?autoplay=1'
		                }
		            }
		        }	    
  	
                 
            });
	
}

function initGravatarFetch(gravata_url){
	$.console.log('---initGravatarFetch---');
	$.console.log('gravata_url='+gravata_url)
	
	$("#gravatar_image").attr("src", gravata_url);
	$.ajax({
	    url: gravata_url,
	    type: "GET",
	    success: function(response){
	        $("#gravatar_image").lazyload({ 
	              effect : "fadeIn"
	        });
	    }
	});
}

function initPagination(){
	$(document).on('click', '.page-link', function(event){
		event.preventDefault();
		$.console.log('clicked pagination link');
		var pagination_url = $(this).data('page-url');
		$.console.log('pagination_url='+pagination_url);
		
		var target_selector = $(this).data('target-selector');
		$.console.log('target_selector='+target_selector);
		
		//$(target_selector).overlay();
		$(target_selector).html(SHOW_LOAD_OVERLAY_TEMPLATE);
		
		$(target_selector).load(pagination_url, function(){
			$(target_selector).overlay('hide');
		}).hide().fadeIn();
		
	});
}

function initMultTabs(){
	$(document).on('click','.nav-tabs a',function (event) {
	    event.preventDefault();
	    var url 		= $(this).data("url");
		var $pane 		= $(this);
		var panel_id	= this.hash;
		
		$.console.log('tab url='+url);
		$.console.log('tab panel_id='+panel_id);
		
	    if (typeof url !== "undefined") {
	        
			var href 		= this.hash;
			var is_loaded 	= $pane.data('is-loaded');
			
			$.console.log('tab is_loaded='+is_loaded);
			if(is_loaded){
				$pane.tab('show');
				
			}else{
				
				$(panel_id).html(SHOW_LOAD_OVERLAY_TEMPLATE);
				
		        // ajax load from data-url
		        /*
				$(panel_id).load(url,function(result){      
		            $pane.tab('show');
					$pane.data('is-loaded', true);
		        });
				*/
				$(panel_id).load(url, function(response, status, xhr){
			
					handleRequestForLoadContent(response, status, xhr, 
									function(){
										$(panel_id).html('');
									},
									function(){
										$pane.tab('show');
										$pane.data('is-loaded', true);
									}
									)
				}).hide().fadeIn();

			}
	    } else {
	        $pane.tab('show');
	    }
	});
	
	
}

function initBase(){
	  
	$(document).on('click', '#page_href', function(event){
		event.preventDefault();
		$.console.log('click page refresh');
		var target_url = $(this).data('page-url');
		
		showLoading({target_selector: '#content'});
		/*
		$('#content').load(target_url, function(){
			hideLoading();
		}).hide().fadeIn();
		*/
		$('#content').load(target_url, function(response, status, xhr){
			
			handleRequestForLoadContent(response, status, xhr, 
							function(){
								hideLoading();
							},
							function(){
								hideLoading();
							}
							)
		}).hide().fadeIn();
		
	});
	
	
}

function initInputBase(){
	$('.datepicker').datetimepicker({
        format				: 'DD/MM/YYYY',
		showTodayButton		: true,
		showClose 			: true,
		showClear			: true,
		//locale				: 'zh',
		icons				: {
								time 		: 'fa fa-clock-o',
								date 		: 'fa fa-calendar',
								up 			: 'fa fa-chevron-up',
								down 		: 'fa fa-chevron-down',
								previous 	: 'fa fa-chevron-left',
								next 		: 'fa fa-chevron-right',
								today 		: 'fa fa-calendar-day',
								clear 		: 'fa fa-trash',
								close 		: 'fa fa-times'
								},
		//debug				: true,
								
    });
	
	$('.open-datetimepicker').click(function(event){
	    event.preventDefault();
		$(this).closest('.input-group').find('.datepicker').data("DateTimePicker").show();    
	});
	
	
}

function initSideMenuContentSwitch(){
	$.console.log('---initSideMenuContentSwitch---');
	
	$('#pushmenu').PushMenu({ expandOnHover: true })
	
	$('#pushmenu').click(function(event){
		var toggle_mode = $(this).data('toggle-mode');
		//$.console.log('toggle_mode='+toggle_mode);
		
		$(this).PushMenu('toggle');
		/*
	    if(toggle_mode!=null){
			$(this).data('toggle-mode',!toggle_mode);
		}else{
			$(this).data('toggle-mode',false);
		}*/		
	});
	
	$('.main-sidebar a.nav-menu').click(function(event){
		event.preventDefault();
		var $clicking_side_menu = $(this);
		var $clicked_side_menu	= $('.main-sidebar a.nav-menu.active');
		var target_url = $clicking_side_menu.data('target-url');
		$.console.log('side menu navigation target url='+target_url);
		var is_sidebar_menu_collapse = $("body").hasClass('sidebar-collapse');
		$.console.log('is_sidebar_menu_collapse='+is_sidebar_menu_collapse);
		
		showLoading({target_selector: '#content'});
		//$('#content').overlay();
		//showLoading();
		
		
		$('#content').load(target_url, function(response, status, xhr){
			handleRequestForLoadContent(response, status, xhr, 
							function(){
								$.console.log('---error callback---');
								hideLoading();
							},
							function(){
								$.console.log('---success callback---');
								$clicked_side_menu.removeClass('active');
								$clicking_side_menu.addClass('active');
								hideLoading();
							}
							)
		}).hide().fadeIn();
		
	});
}

function createNotifyMessageHTML(message_list, other_html){
	var construct_message_content = ''; 
	if (typeof message_list == "string") {
		construct_message_content+='<li>'+message_list+'</li>';
	}else{
		$.each(message_list, function(key, value) {
			construct_message_content+='<li>'+value+'</li>';     
		});
	}
	if(other_html){
		construct_message_content+='<li>'+other_html+'</li>';     
	}
	
	
	return '<ul class="notify-messages" style="list-style: none;">'+construct_message_content+'</ul>';
}

function createNextButtonHTML(next_url, button_label){
	if(button_label==null){
		button_label = NEXT;
	}
	return '<a href="'+next_url+'" class="btn btn-small btn-primary">'+button_label+'</a>';
}


function showLoading(opts){
	$.console.log('LOADING_IMAGE_PATH='+LOADING_IMAGE_PATH);
	var is_sidebar_menu_collapse = $("body").hasClass('sidebar-collapse');
	var left_margin = 0;
	/*
	var left_margin = 250;
	if(is_sidebar_menu_collapse){
		left_margin = 74;
	}
	*/
	var default_opts = {
							imgPath: LOADING_IMAGE_PATH,
							text:'Please wait while we are handling your request ...',
							style: {
						        position	: 'fixed',
								//position	: 'sticky',
						        width		: '100%',
						        height		: '100%',
						        background	: 'rgba(247, 247, 247, .8)',
						        left   		: left_margin,
						        top    		: 0,
						        //zIndex 		: 10000
						    }
						};
	$.extend(default_opts, opts);
	$.loadingBlockShow(default_opts);
	
}

function hideLoading(){
	$.loadingBlockHide();
}


function openTopModal($open_modal_element, content_url ){
	$open_modal_element.disabled();
	$.console.log('content_url='+content_url);
	
	var $modal_body 	= $('#top_modal .modal-body');
	
	$modal_body.overlay();
	
	$modal_body.load(content_url, function(response, status, xhr){
		handleRequestForLoadContent(response, status, xhr, 
							function(){
								$open_modal_element.enabled();
							},
							function(){
								$(this).overlay('hide');
								$('#top_modal').modal('show');
								$open_modal_element.enabled();
							}
							)
	});
	
}

function openInfoModal($open_modal_element, title, content_url ){
	$open_modal_element.disabled();
	$.console.log('title='+title);
	$.console.log('content_url='+content_url);
	
	var $modal_body 	= $('#info_modal .modal-body');
	var $modal_title 	= $('#info_modal .modal-title');
	
	$modal_title.text(title);
	$modal_body.overlay();
	
	$modal_body.load(content_url, function(response, status, xhr){
		handleRequestForLoadContent(response, status, xhr, 
							function(){
								$open_modal_element.enabled();
							},
							function(){
								$(this).overlay('hide');
								$('#info_modal').modal('show');
								$open_modal_element.enabled();
							}
							);
	});
	
}

//function openFullWidthModal($open_modal_element, title, content_url, callback ){
function openFullWidthModal(options ){
    var $open_modal_element = options.open_modal_element;
    var title               = options.title;
    var content_url         = options.content_url;
    var callback            = options.callback;

	$open_modal_element.disabled();
	$.console.log('title='+title);
	$.console.log('content_url='+content_url);
	
	var $modal_body 	= $('#full_width_modal .modal-body');
	var $modal_title 	= $('#full_width_modal .modal-title');
	
	$modal_title.text(title);
	$modal_body.overlay();
	
	$modal_body.load(content_url, function(response, status, xhr){
		handleRequestForLoadContent(response, status, xhr, 
							function(){
								$open_modal_element.enabled();
							},
							function(){
								$(this).overlay('hide');
								$('#full_width_modal').modal('show');
								$open_modal_element.enabled();
							}
							);
		if(callback){
		    callback();
		}
	});
	
}

function openDetailsModal($open_modal_element, title, content_url ){
	$open_modal_element.disabled();
	$.console.log('title='+title);
	$.console.log('content_url='+content_url);
	
	var $modal_body 	= $('#details_modal .modal-body');
	var $modal_title 	= $('#details_modal .modal-title');
	
	$modal_title.text(title);
	$modal_body.overlay();
	
	$modal_body.load(content_url, function(response, status, xhr){
		handleRequestForLoadContent(response, status, xhr, 
							function(){
								$open_modal_element.enabled();
							},
							function(){
								$(this).overlay('hide');
								$('#details_modal').modal('show');
								$open_modal_element.enabled();
							}
							)
	});
	
}

function handleErrorRequestForAjaxCall(jqXHR, textStatus, errorThrown, error_callback){
	
	var response 	= jqXHR.responseText;
	var status		= textStatus;
	var status_code = jqXHR.status;
	
	handleErrorRequest(response, status, status_code, error_callback);
	
}

function handleRequestForLoadContent(response, status, xhr, error_callback, success_callback){
	
	handleRequest(response, status, xhr.status, error_callback, success_callback);
	
}

function handleRequest(response, status, status_code, error_callback, success_callback){
	$.console.log('response='+JSON.stringify(response));
	$.console.log('status='+status);
	$.console.log('status_code='+status_code);
		
	if ( status == "error" || status == "timeout") {
		if(status_code==0){
				notify('error', CANNOT_PROCESS_YOUR_REQUEST);
		}else
		if(status_code==401){
			var next_url_button_html = createNextButtonHTML(SIGNIN_URL, SIGNIN);
			notify('error', NOT_AUTHORIZED_TO_PROCEED, createNotifyMessageHTML(message, next_url_button_html));
		}else{
			var response_json = JSON.parse(response);
			
			var message = xhr.statusText;
			if(response_json.msg){
				message = response_json.msg;
			}
			$.console.log('message='+message);
			notify('error', SORRY, createNotifyMessageHTML(message));
			
		}
		
		if(error_callback){
			$.console.log('Going to call error_callback');
			var error_message = response;
			error_callback(error_message);
		}
		
	}else{
		if(success_callback){
			$.console.log('Going to call success_callback');
			success_callback();
		}
	}
	
}

jQuery.fn.enter = function (fnc) {
    return this.each(function () {
        $(this).keypress(function (ev) {
            var keycode = (ev.keyCode ? ev.keyCode : ev.which);
            if (keycode == '13') {
                fnc.call(this, ev);
            }
        });
    });
} 

jQuery.fn.countDown = function(fnc){
	$(this).live('change', function(event){
		$.console.log('count down changed');
	});
}

jQuery.fn.is_empty = function(fnc){
    var value = $.trim($(this).val());
    if(value==''){
        return true;
    }else{
        return false;
    }
}

jQuery.fn.disabled = function(fnc){
    $(this).attr('disabled', 'disabled');
}

jQuery.fn.enabled = function(fnc){
    $(this).removeAttr('disabled');
}

jQuery.fn.invisible = function(fnc){
    $(this).css('visibility', 'hidden');
}

jQuery.fn.visible = function(fnc){
    $(this).css('visibility', 'visible');
}

jQuery.fn.displayAroundMouseClicked = function(fnc, modal_selector){
    
    $(this).live('click', function(event) {
        event.preventDefault();
        var small_device_media = isSmallDevice();
        $.console.log('small_device_media=' + small_device_media);
        if(small_device_media) {
            var H = $(document).height();
            var M = $(modal_selector).height();
            var Y = event.pageY;
            var R = H - Y;
            var F = 0;
            var remain_as_original = false;
            if((H - Y) > M / 2 && Y > (M / 2)) {
                //we can display modal in the middle of clicked position
                F = Y - M / 2
            } else if((H - Y) < M / 2) {
                F = Y - (M - (H - Y));
            } else {
                remain_as_original = true;
            }

            if(!remain_as_original) {
                //$.console.log('Going to call function now.');
                fnc.call(this, F);
            }
        } else {
            //$.console.log('Skip as it is not a small device.');
        }
    });
}

jQuery.extend({
	randomString: function (length, special) {
	    var iteration = 0;
	    var password = "";
	    var randomNumber;
	    if(special == undefined){
	        var special = false;
	    }
	    while(iteration < length){
	        randomNumber = (Math.floor((Math.random() * 100)) % 94) + 33;
	        if(!special){
	            if ((randomNumber >=33) && (randomNumber <=47)) { continue; }
	            if ((randomNumber >=58) && (randomNumber <=64)) { continue; }
	            if ((randomNumber >=91) && (randomNumber <=96)) { continue; }
	            if ((randomNumber >=123) && (randomNumber <=126)) { continue; }
	        }
	        iteration++;
	        password += String.fromCharCode(randomNumber);
	    }
	    return password;
    },
	http_hostname_URL: function(url){
		var m = ((url||'')+'').match(/^http:\/\/[^/]+/);
    	return m ? m[0] : null;
	},
	hostname: function(url){
        var a = document.createElement('a');
        a.href = url;
        return a.hostname;
    },
    htmlEncode: function (value) {
      if(value){
          return jQuery('<div/>').text(value).html();    
      }else{
          return '';
      }
    
    },
    htmlDecode: function (value) {
      if(value){
          var e = document.createElement('div');
		  e.innerHTML = value;
		  return e.childNodes.length === 0 ? "" : e.childNodes[0].nodeValue;
      }else{
          return '';
      }
    
    },
    urlEncode: function (value) {
      if(value){
          return encodeURIComponent(value);   
      }else{
          return '';
      }
    
    },
    truncateIfExceed: function (value, max_length){
      if(value){
      	  if(value.length>max_length){
          	var substr_value = value.substring(0, max_length) + "...";
          	return substr_value;    
          }else{
         	return value;
          }
      }else{
          return '';
      }
    
    },
    scrollToTop: function () {
    	$('html, body').animate({scrollTop:0}, 'slow');
    },
    appendArray: function(dest_array, append_array){
    	$.each(append_array,function(index, value){
	  	  if ($.inArray(value, dest_array)==-1) {
		  	dest_array.push(value);
		  }
		});
    },
    removeArray: function(dest_array, removing_array){
	  	$.each(removing_array,function(index, value){
	  		var found_index = $.inArray(value, dest_array);
	  		dest_array.splice(found_index,1);
	  	});
    },
    is_exist: function(selector){
    	return $(selector).length>0;
    },
    is_vertical_oriented: function(){
    	var window_height 	= window.innerHeight;
    	var window_width 	= window.innerWidth;
    	//$.console.log('window_height='+window_height);
    	//$.console.log('window_width='+window_width);
    	return window_width<window_height;
    },
    init_rotate_event: function(callback){
    	var supportsOrientationChange = "onorientationchange" in window,
        orientationEvent = supportsOrientationChange ? "orientationchange" : "resize";

    	window.addEventListener(orientationEvent, function() {
    		if(callback){
    			callback();
    		}
    		
    	}, false);
    },
    is_small_device: function(small_device_width){
    	var window_height 	= window.innerHeight;
    	var window_width 	= window.innerWidth;
    	if(window_height>window_width){
    		$.console.log('comparing window_height='+window_height+' and small_device_width='+small_device_width);
    		return window_height<=small_device_width;
    	}else{
    		$.console.log('comparing window_width='+window_width+' and small_device_width='+small_device_width);
    		return window_width<=small_device_width;
    	}
    }
}); 

function dataURItoBlob(dataURI) {
    var ab, bb, byteString, i, ia, mimeString, _ref;
    if(!( typeof ArrayBuffer != "undefined" && ArrayBuffer !== null)) {
        return null;
    }
    byteString = atob(dataURI.split(',')[1]);
    mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    ab = new ArrayBuffer(byteString.length);
    ia = new Uint8Array(ab);
    for( i = 0, _ref = byteString.length; (0 <= _ref ? i < _ref : i > _ref); (0 <= _ref ? i += 1 : i -= 1)) {
        ia[i] = byteString.charCodeAt(i);
    }
    bb = window.BlobBuilder ? new BlobBuilder() : window.WebKitBlobBuilder ? new WebKitBlobBuilder() : window.MozBlobBuilder ? new MozBlobBuilder() :
    void 0;
    if(bb != null) {
        bb.append(ab);
        return bb.getBlob(mimeString);
    } else {
        return null;
    }
};

jQuery.Format = function jQuery_dotnet_string_format(text) {
    //check if there are two arguments in the arguments list
    if (arguments.length <= 1) {
        //if there are not 2 or more arguments there's nothing to replace
        //just return the text
        return text;
    }
    //decrement to move to the second argument in the array
    var tokenCount = arguments.length - 2;
    for (var token = 0; token <= tokenCount; ++token) {
        //iterate through the tokens and replace their placeholders from the text in order
        text = text.replace(new RegExp("\\{" + token + "\\}", "gi"), arguments[token + 1]);
    }
    return text;
};

jQuery.range = function (start, stop, step) {
    var a = [start], b = start;
    while (b < stop) {
        b += step;
        a.push(b)
    }
    return a;
}

jQuery.escapeHTML = function escape_xss_for_html(string) {
    return $('<div/>').text(string).html();
};

jQuery.monthName = function(month_value){
    if(month_value>=0 && month_value<=12) {
        var month   = new Array(12);
        month[0]    = month_January;
        month[1]    = month_February;
        month[2]    = month_March;
        month[3]    = month_April;
        month[4]    = month_May;
        month[5]    = month_June;
        month[6]    = month_July;
        month[7]    = month_August;
        month[8]    = month_September;
        month[9]    = month_October;
        month[10]   = month_November;
        month[11]   = month_December;
        return month[month_value - 1]
    }else{
        return month_value;
    }
};

jQuery.string = {
    Format: function(text) {
        //check if there are two arguments in the arguments list
        if (arguments.length <= 1) {
            //if there are not 2 or more arguments there's nothing to replace
            //just return the text
            return text;
        }
        //decrement to move to the second argument in the array
        var tokenCount = arguments.length - 2;
        for (var token = 0; token <= tokenCount; ++token) {
            //iterate through the tokens and replace their placeholders from the text in order
            var reg = new RegExp("\\{" + token + "\\}", "gi");
            var value = arguments[token + 1];
            text = text.replace(reg, value);

        }
        return text;
    }
};

jQuery.httputil = {
    is_valid_url: function(url){
        var pattern = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
        return $.trim(url)==0 || pattern.test(url);
    }
};

jQuery.inpututil = {
    is_valid_phone_no: function(phone_no, phone_regex){
    	$.console.log('phone_regex='+phone_regex)
        var pattern = phone_regex;///[0-9\+\-\s]$/;
        var is_valid =  $.trim(phone_no)=='' || pattern.test(phone_no);
        $.console.log("is_valid="+is_valid+" for phone_no="+ phone_no);
        return is_valid;
    },
    is_valid_username: function(username){
        var pattern = /^[a-zA-Z0-9\-\_\.]+$/i;
        return $.trim(username)==0 || pattern.test(username);
    },
    is_valid_date_format: function(date_value, date_format){
    	try{
    		return $.datepicker.parseDate(date_format, date_value);
    	}catch(error){
    		return false;
    	}
    	
    },
    is_valid_date_range: function(date_from_str, date_to_str, date_format){
    	try{
    		var date_from = $.datepicker.parseDate(date_format, date_from_str);
    		var date_to = $.datepicker.parseDate(date_format, date_to_str);
    		return date_from<=date_to;
    	}catch(error){
    		return false;
    	}
    }
};

(function ($) {
	$.event.special.load = {
		add: function (hollaback) {
			if ( this.nodeType === 1 && this.tagName!=null && this.tagName.toLowerCase() === 'img' && this.src !== '' ) {
				// Image is already complete, fire the hollaback (fixes browser issues were cached
				// images isn't triggering the load event)
				if ( this.complete || this.readyState === 4 ) {
					hollaback.handler.apply(this);
				}

				// Check if data URI images is supported, fire 'error' event if not
				else if ( this.readyState === 'uninitialized' && this.src.indexOf('data:') === 0 ) {
					$(this).trigger('error');
				}
				
				else {
					$(this).bind('load', hollaback.handler);
				}
			}
		}
	};
}(jQuery));

jQuery.imgutil = {
    url_preview: function(options){
      var image_url, callback_after_image_loaded;
      if(options){
          image_url                     = options.image_url;
          callback_after_image_loaded   = options.callback_after_image_loaded;
      }  
      
      
    },
    preview: function(options){
        var image_file_object, callback_after_image_loaded;
        if(options){
            image_file_object           = options.image_file_object;
            callback_after_image_loaded = options.callback_after_image_loaded;
            
        }
        var reader = new FileReader();

        reader.onload = function(event) {
            //show preview image
            if(callback_after_image_loaded){
                callback_after_image_loaded(event);
            }
        }

        reader.readAsDataURL(image_file_object);
    },
    upload_in_blob: function(options){
    	var image_obj, upload_url, file_input_name, filename, form_param_json, success_callback, error_callback;
        var canvas_width = 656;
        var canvas_height = 492;
        var photo_input = 'photo_to_upload';
        if(options){
            image_obj           = options.image_obj;
            upload_url          = options.upload_url;
            file_input_name     = options.file_input_name;
            filename            = options.filename;
            form_param_json     = options.form_param_json;
            success_callback    = options.success_callback;
            error_callback      = options.error_callback;
            if(options.canvas_width){
            	canvas_width		= options.canvas_width;	
            }
            
            if(options.canvas_height){
            	canvas_height		= options.canvas_height;	
            }
            if(options.photo_input){
            	photo_input = options.photo_input;
            }
            
        }
        var canvas      = document.createElement('canvas');
        
        //canvas.width    = image_obj.naturalWidth;
        //canvas.height   = image_obj.naturalHeight;
        canvas.width    = canvas_width;
        canvas.height   = canvas_height;
        
        $.console.log('canvas='+canvas);
        $.console.log('canvas.width='+canvas.width);
        $.console.log('canvas.height='+canvas.height);
        $.console.log('image_obj='+image_obj);
        $.console.log('upload_url='+upload_url);
        
        
        var ctx = canvas.getContext("2d").drawImage(image_obj, 0, 0, canvas.width, canvas.height);
        
        
        if(canvas.toBlob){
        	canvas.toBlob(function(blob){
        		//usually browser that support canvas should support FormData
        		var formData = new FormData();
        		formData.append(photo_input, blob, filename);
        		if(form_param_json) {
		            $.console.log(form_param_json);
		            for(var key in form_param_json) {
		                formData.append(key, form_param_json[key]);
		            }
		        }
		        
		        $.ajax({
				    url: upload_url,
				    data: formData,
				    cache: false,
				    contentType: false,
				    processData: false,
				    type: 'POST',
				    success: function(data){
				        $.console.log('data after upload_in_blob='+data);
				        if(success_callback) {
		                	success_callback(data);
		                }
				    },
				    error: function(jqXHR, textStatus, errorThrown){
				        if(error_callback){
				            error_callback(jqXHR, textStatus, errorThrown);
				        }
				    },
				    beforeSend : function(xhr) {
				    	clear_message();
	                    xhr.setRequestHeader('X-CSRF-TOKEN',get_csrf_token());
	                }
				});
		        
		        
        	}, "image/jpeg");
        }else{
        	$.console.log('Not support canvas.toBlob');
        }
        
    },
    upload_in_base64 : function(options) {
        var image_obj, upload_url, file_input_name, filename, form_param_json, success_callback, error_callback;
        if(options){
            image_obj           = options.image_obj;
            upload_url          = options.upload_url;
            file_input_name     = options.file_input_name;
            filename            = options.filename;
            form_param_json     = options.form_param_json;
            success_callback    = options.success_callback;
            error_callback      = options.error_callback;
        }
        var canvas      = document.createElement('canvas');
        
        //canvas.width    = image_obj.naturalWidth;
        //canvas.height   = image_obj.naturalHeight;
        canvas.width    = 656;
        canvas.height   = 492;
        var ctx = canvas.getContext("2d").drawImage(image_obj, 0, 0, canvas.width, canvas.height);
        
        $.console.log('canvas='+canvas);
        $.console.log('canvas.width='+canvas.width);
        $.console.log('canvas.height='+canvas.height);
        
        var type = 'image/jpeg';
        var image_data = canvas.toDataURL(type, 0.5);
        image_data = image_data.replace('data:' + type + ';base64,', '');

        var xhr = new XMLHttpRequest();
        xhr.open('POST', upload_url, true);
        var boundary = 'WebKitFormBoundary' + $.randomString(15);

        xhr.setRequestHeader('Content-Type', 'multipart/form-data; boundary=' + boundary);

        var image_file_input = ['--' + boundary, 'Content-Disposition: form-data; name="' + file_input_name + '"; filename="' + filename + '"', 'Content-Transfer-Encoding: base64', 'Content-Type: ' + type, '', image_data, ''];
        var image_request_data = image_file_input.join('\r\n');
        var request_data = image_request_data;
        if(form_param_json) {
            $.console.log(form_param_json);
            for(var key in form_param_json) {
                request_data += ((['', '--' + boundary, 'Content-Disposition: form-data; name="' + key + '"', '', form_param_json[key]]).join('\r\n'));
            }
        }
        request_data += ('\r\n--' + boundary + '--\r\n')
        $.console.log(request_data);
        xhr.send(request_data);

        xhr.onreadystatechange = function() {
            if(xhr.readyState == 4) {
                $.console.log('xhr.responseText='+xhr.responseText);
                var json_response = $.parseJSON(xhr.responseText);
                $.console.log('json_response.status='+json_response.status);
                if(json_response.status == 200 ) {
                    if(success_callback) {
                        success_callback(xhr.responseText);
                    }
                } else {
                    if(error_callback) {
                        error_callback(xhr.responseText);
                    }
                }
            }
        };
    }
};


(function($) {

    var keyString = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";

    var uTF8Encode = function(string) {
        string = string.replace(/\x0d\x0a/g, "\x0a");
        var output = "";
        for(var n = 0; n < string.length; n++) {
            var c = string.charCodeAt(n);
            if(c < 128) {
                output += String.fromCharCode(c);
            } else if((c > 127) && (c < 2048)) {
                output += String.fromCharCode((c >> 6) | 192);
                output += String.fromCharCode((c & 63) | 128);
            } else {
                output += String.fromCharCode((c >> 12) | 224);
                output += String.fromCharCode(((c >> 6) & 63) | 128);
                output += String.fromCharCode((c & 63) | 128);
            }
        }
        return output;
    };
    var uTF8Decode = function(input) {
        var string = "";
        var i = 0;
        var c = c1 = c2 = 0;
        while(i < input.length) {
            c = input.charCodeAt(i);
            if(c < 128) {
                string += String.fromCharCode(c);
                i++;
            } else if((c > 191) && (c < 224)) {
                c2 = input.charCodeAt(i + 1);
                string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
                i += 2;
            } else {
                c2 = input.charCodeAt(i + 1);
                c3 = input.charCodeAt(i + 2);
                string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
                i += 3;
            }
        }
        return string;
    }

    $.extend({
        base64Encode : function(input) {
            var output = "";
            var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
            var i = 0;
            input = uTF8Encode(input);
            while(i < input.length) {
                chr1 = input.charCodeAt(i++);
                chr2 = input.charCodeAt(i++);
                chr3 = input.charCodeAt(i++);
                enc1 = chr1 >> 2;
                enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
                enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
                enc4 = chr3 & 63;
                if(isNaN(chr2)) {
                    enc3 = enc4 = 64;
                } else if(isNaN(chr3)) {
                    enc4 = 64;
                }
                output = output + keyString.charAt(enc1) + keyString.charAt(enc2) + keyString.charAt(enc3) + keyString.charAt(enc4);
            }
            return output;
        },
        base64Decode : function(input) {
            var output = "";
            var chr1, chr2, chr3;
            var enc1, enc2, enc3, enc4;
            var i = 0;
            input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");
            while(i < input.length) {
                enc1 = keyString.indexOf(input.charAt(i++));
                enc2 = keyString.indexOf(input.charAt(i++));
                enc3 = keyString.indexOf(input.charAt(i++));
                enc4 = keyString.indexOf(input.charAt(i++));
                chr1 = (enc1 << 2) | (enc2 >> 4);
                chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
                chr3 = ((enc3 & 3) << 6) | enc4;
                output = output + String.fromCharCode(chr1);
                if(enc3 != 64) {
                    output = output + String.fromCharCode(chr2);
                }
                if(enc4 != 64) {
                    output = output + String.fromCharCode(chr3);
                }
            }
            output = uTF8Decode(output);
            return output;
        }
    });
})(jQuery);

jQuery.fn.overlay = function (hide_show_indicator) {
	var overlay_div = $(this).find('#common_overlay');
	var is_overlay_div_created = overlay_div.length>0;
	
	$.console.log('is_overlay_div_created='+is_overlay_div_created);
	$.console.log('hide_show_indicator='+hide_show_indicator);
	
	if(!hide_show_indicator){
		hide_show_indicator = 'show';
	}
	
	if(hide_show_indicator=='show'){
		var the_div_height = $(this).height();
		if(is_overlay_div_created==false){
	    	$(this).append(SHOW_LOAD_OVERLAY_TEMPLATE);
	    	if(!$(this).hasClass('modal')){
	    		$(this).css({'position':'relative'});	
	    	}
	    	overlay_div = $(this).find('#common_overlay');
	    	var loading_image = overlay_div.find('img');
	    	loading_image.css({'margin-top': 0.4*the_div_height});
	    	overlay_div.show();
	    }else{
	    	var loading_image = overlay_div.find('img');
	    	loading_image.css({'margin-top': 0.4*the_div_height});
	    	overlay_div.show();
	    }
	}else
	if(hide_show_indicator=='hide'){
		if(is_overlay_div_created){
			overlay_div.hide();
		}
	}
};

jQuery.fn.extend({
	insertAtCaret: function(myValue){
	  return this.each(function(i) {
	    if (document.selection) {
	      //For browsers like Internet Explorer
	      this.focus();
	      var sel = document.selection.createRange();
	      sel.text = myValue;
	      this.focus();
	    }
	    else if (this.selectionStart || this.selectionStart == '0') {
	      //For browsers like Firefox and Webkit based
	      var startPos = this.selectionStart;
	      var endPos = this.selectionEnd;
	      var scrollTop = this.scrollTop;
	      this.value = this.value.substring(0, startPos)+myValue+this.value.substring(endPos,this.value.length);
	      this.focus();
	      this.selectionStart = startPos + myValue.length;
	      this.selectionEnd = startPos + myValue.length;
	      this.scrollTop = scrollTop;
	    } else {
	      this.value += myValue;
	      this.focus();
	    }
	  });
	}
});

jQuery.fn.intl_telephone = function(fnc){

    $(this).intlTelInput({
                utilsScript: '/js/intl-tel-input/12.2.0/utils.js',
                autoPlaceholder: true,
                preferredCountries: [DEFAULT_COUNTRY_CODE],
                allowDropdown: true,
                formatOnInit: true
            });

}

jQuery.fn.numeric_input = function (fnc) {
	$(this).filter_input({regex:'[0-9\.,]'});
};

jQuery.fn.ascii_input = function (fnc) {
	$(this).filter_input({regex:'[A-Za-z0-9+#-\.\/:]'});
};

jQuery.fn.any_input = function (fnc) {
	$(this).filter_input({regex:'[\w]'});
};

jQuery.fn.serializeJSON = function (fnc) {
	var unindexed_array = $(this).serializeArray();
    var json_obj = {};

    $.map(unindexed_array, function(n, i){
        json_obj[n['name']] = n['value'];
    });

    return json_obj;
};


jQuery.fn.filter_item = function (events, filter_container_selector, filter_element_selector, filter_attr_name) {
	console.log('the selector='+this.selector);
	$(document).on(events, this.selector, function(){
		$.console.log('event trigger');
        var filter_value = $(this).attr(filter_attr_name);
        $(filter_container_selector).hide();
        $(filter_element_selector).show();
        $(filter_element_selector).not('.'+filter_value).hide();
        $(filter_container_selector).fadeIn(1000);
	});
};

jQuery.fn.currency_round_up = function (options) {
	var currency_value          = options.currency_value;
    var currency_code           = options.currency_code;
	var round_up_currency_value = currency_value;
    if(currency_code) {
        $.console.log('currency_value='+currency_value);
        $.console.log('options.currency_code='+options.currency_code);
        $.console.log('options.currency_floating_point='+options.currency_floating_point);
        $.console.log('options.currency_thousand_separator='+options.currency_thousand_separator);
        $.console.log('options.currency_decimal_separator='+options.currency_decimal_separator);
        if (currency_code == 'MYR') {
            //round up to 5 cents
            round_up_currency_value = currency_value * 20;
            round_up_currency_value = Math.ceil(round_up_currency_value);
            round_up_currency_value = round_up_currency_value / 20;

        }
        //$(this).val($.formatNumber(parsed_currency_value, {format:currency_pattern}));
        var currency_formatted_value = accounting.formatMoney(
            round_up_currency_value,
            "",
            options.currency_floating_point,
            options.currency_thousand_separator,
            options.currency_decimal_separator
        );
        $(this).val(currency_formatted_value);
    }
};

jQuery.currency_deformat = function(CURRENCY_DECIMAL_SEPARATOR, currency_value){

    if('.'==CURRENCY_DECIMAL_SEPARATOR){
        currency_value = Number(currency_value.replace(/[^0-9\.-]+/g,""));
    }else
    if(','==CURRENCY_DECIMAL_SEPARATOR){
        currency_value = Number(currency_value.replace(/[^0-9\,-]+/g,""));
    }
    return 0;
};

jQuery.fn.std_datepicker = function (options){
	var settings = $.extend({
							format 		        : 'dd/mm/yyyy',
							onChangeCallback 	: null,
                            orientation         : 'top'


	}, options);
	
	$(this).datepicker(settings)
        .on('changeDate', function(event){
		//$.console.log(event);
		$(this).datepicker('hide');
		if(settings.onChangeCallback){
			settings.onChangeCallback(event);
		}
		
	});

};

jQuery.lazy_content = function (options) {
	
	var settings = $.extend({
							target_selector 		: null,
							request_url 			: 'data-url',
							param_names				: 'data-param-names',
							param_values			: 'data-param-values',
							param_format			: 'query', //[query, path]
							fadeIn_interval 		: 1000,
							default_loading_height 	: 0,
							callback				: null
							
							
	}, options);
	
	var lazy_load_content = function($target_element){
		if($target_element){
			var isloaded = $target_element.attr('data-loaded')=='true';
			if(isloaded==false){
				var param_names_array = null;
				if(settings.param_names){
					 var param_names_attr = $target_element.attr(settings.param_names);
					 if(param_names_attr){
						 param_names_array = param_names_attr.split(",");
					 }
					 
				}
				
				var param_values_array = null;
				if(settings.param_values){
					var param_values_attr = $target_element.attr(settings.param_values);
					 if(param_values_attr){
						 param_values_array = param_values_attr.split(",");
					 }
				}
				
				var target_url = settings.request_url;
				if(target_url){
					if('query'==settings.param_format){
						if(target_url.indexOf('?')<0){
							target_url+='?'
						}
						if(param_values_array){
							for(index in param_names_array){
								target_url+=('&'+param_names_array[index]+'='+param_values_array[index]);
							}
						}
					}else
					if('path'==settings.param_format){
						if(param_values_array){
							for(index in param_names_array){
								target_url = target_url.replace('{'+param_names_array[index]+'}', param_values_array[index])
							}
						}
						
					}
					
					$target_element.html(SHOW_LOAD_IMAGE_TEMPLATE);
					$target_element.load(target_url, function(response, status, xhr){
						$target_element.attr('data-loaded','true');
						if(settings.callback){
				    		settings.callback($target_element, response, status, xhr);
				    	}
				    });
				}
			}
		}
	}
	
	if(settings.target_selector){
		$.each($(settings.target_selector), function(index, element){
			lazy_load_content($(element));
		});
	}
	
};

jQuery.popupWindow = function jQuery_dotnet_string_format(target_url, callback) {
    $.console.log('target_url='+target_url);
    $.fancybox({
			'href'				: target_url,
			'autoScale'     	: true,
			'transitionIn'		: 'elastic',
			'transitionOut'		: 'elastic',
			'type'				: 'iframe',
			'overlayColor'		: '#000',
			'overlayOpacity'	: 0.5,
			'scrolling'   		: 'no',
			'width'  			: '100%',
            'height'  			: '100%',
            'enableEscapeButton': true,
            'afterLoad'         : function(){
                $.console.log('--popupWindow: afterLoad--');
                if(callback){
                    callback();
                }
            }
		});
}




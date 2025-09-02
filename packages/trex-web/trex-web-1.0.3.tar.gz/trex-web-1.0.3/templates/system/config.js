var LOADING_IMAGE_PATH 				= '{{ LOADING_IMAGE_PATH }}';
var SHOW_LOAD_IMAGE_TEMPLATE		= '<img class="center-block" src="{{ LOADING_IMAGE_PATH }}" class="loading-image" alt="loading image">';
var LOADING_TEXT					= '{{ LOADING_TEXT }}';

var SHOW_LOAD_OVERLAY_TEMPLATE		= '<div id="common_overlay" class="container-fluid overlay">'
									+ '<div class="row justify-content-center">' 
									+ '<div class="col-md-6">'
									+ SHOW_LOAD_IMAGE_TEMPLATE
									+ '<p class="center-align">'
									+ LOADING_TEXT
									+ '</p>'
									+ '</div>'
									+ '</div>'
									+ '</div>';

/*global $, _, PDFJS */
odoo.define('website.stl_viewer', function (require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var time = require('web.time');
var Widget = require('web.Widget');
var local_storage = require('web.local_storage');
require('root.widget');

var _t = core._t;
var page_widgets = {};

(function () {
    var widget_parent = $('body');


     var StlViewerButton = Widget.extend({
        setElement: function($el){
            this._super.apply(this, arguments);
            this.$el.on('click', this, _.bind(this.apply_action, this));
        },
        apply_action: function(ev){
            var button = $(ev.currentTarget);
            var document_id = button.data('document-id');
            var div = this.$el[0].parentNode;
            while (div.firstChild) {
				div.removeChild(div.firstChild);
			}
			if ('myScene' in xeogl.scenes) {
				xeogl.getDefaultScene().destroy();
				delete xeogl.scenes['myScene'];
				
			}
			
				
				
		        var canvas = document.createElement('canvas');
		        
		        canvas.id = "myCanvas";
		        canvas.style.cssText = 'width:100%;height:300px;background-color:#F9F9F9;';
		        
		        div.appendChild(canvas);
	        
	       
				var scene = new xeogl.Scene({
							transparent:true,
					        canvas:'myCanvas',
					        id:'myScene',

					    });
				xeogl.setDefaultScene(scene);
	        
			var model = new xeogl.STLModel({
				    
				    src: "/web/content/"+document_id,
				    smoothNormals: true,
				    smoothNormalsAngleThreshold: 45,
				    combineGeometry: true,
				    quantizeGeometry: true
				    // Some example loading options (see "Options" below)
				   
			});
			new xeogl.CameraControl();
			    // Initial camera position
			    var scene = xeogl.getDefaultScene();
			    var camera = scene.camera;
			    camera.eye = [0, 0, 80.02];
//			    camera.look = [10.90, 10.90, 8];
//			    camera.up = [-0.58, 4, 1];
			    // Orbit camera
			    scene.on("tick", function () {
			     //   camera.orbitYaw(-0.2);
			    });
        },
        
    });

    page_widgets['stlViewerButton'] = new StlViewerButton(widget_parent).setElement($('.oe_stl_viewer'));

})();

return {
    page_widgets: page_widgets,
};

});

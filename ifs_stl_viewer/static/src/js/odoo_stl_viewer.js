odoo.define('ifs_stl_viewer.stl_viewer_widget', function(require) {
	"use strict";

	var core = require('web.core');
	
	var relational_fields = require('web.relational_fields');
    var field_registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
	// Form View
	var StlViewerWidget = AbstractField.extend({
		template : 'StlViewer',
		events: _.extend({}, AbstractField.prototype.events, {
	    	'click .o_field_show': '_onShow_3d',
	    }),
	   init:function(){
		   alert('Pippo');
	   },
	    _onShow_3d: function () {
            // Do Nothing
			var self = this;
//			$.get( "/web/content/"+this.value.data.id, function( data ) {
			
			var div = document.getElementById("stl_content");
			if ('myScene' in xeogl.scenes) {
				xeogl.getDefaultScene().destroy();
				delete xeogl.scenes['myScene'];
				while (div.firstChild) {
					div.removeChild(div.firstChild);
				}
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
				    
				    src: "/web/content/"+self.value.data.id,
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
			


			}
        
	});
	field_registry.add('stl_viewer_widget', StlViewerWidget);

});
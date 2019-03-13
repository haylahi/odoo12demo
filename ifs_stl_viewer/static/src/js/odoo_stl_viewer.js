odoo.define('ifs_stl_viewer.stl_viewer_widget', function(require) {
	"use strict";

	var core = require('web.core');
	
	var relational_fields = require('web.relational_fields');
    var field_registry = require('web.field_registry');

	// Form View
	var StlViewerWidget = relational_fields.FieldMany2One.extend({
		template : 'StlViewer',

		_renderReadonly: function () {
            // Do Nothing
			var self = this;
//			$.get( "/web/content/"+this.value.data.id, function( data ) {
			setTimeout(function(){
				var div = document.getElementById("stl_content");
				while (div.firstChild) {
					div.removeChild(div.firstChild);
				}
	            var canvas = document.createElement('canvas');
	            canvas.id = "myCanvas";
	            div.appendChild(canvas);
				var scene = new xeogl.Scene({
						transparent:true,
				        canvas:'myCanvas'
				    });
				xeogl.setDefaultScene(scene);
				var model = new xeogl.STLModel({
				    id: "stl_content",
				    src: "/web/content/"+self.value.data.id,

				    // Some example loading options (see "Options" below)
				   // smoothNormals: true,
				    
				});
				new xeogl.CameraControl();
			    // Initial camera position
			    var scene = xeogl.getDefaultScene();
			    var camera = scene.camera;
			    camera.eye = [37.24, 45.17, -15.02];
			    camera.look = [10.90, 10.90, 8];
			    camera.up = [-0.58, 0.72, 0.35];
			    // Orbit camera
			    scene.on("tick", function () {
			     //   camera.orbitYaw(-0.2);
			    });
			},1000);

//				xeogl.STLModel.parse(model, data, {
//
//					   // Some example parsing options (see "Options" below)
//					    smoothNormals: true,
//					    smoothNormalsAngleThreshold: 45,
//					    combineGeometry: true,
//					    quantizeGeometry: true
//					});
//			});
			
        },
	});
	field_registry.add('stl_viewer_widget', StlViewerWidget);

});
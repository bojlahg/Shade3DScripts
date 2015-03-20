# @title \en Render active faces UV\enden

import math

# 36x24 full frame camera
def focal_to_fov(focal):
	return 2.0 * math.atan(36 / (2.0 * focal))
# 36x24 full frame camera	
def fov_to_focal(fov):
	return (0.5 * 36.0 * (1.0 / math.tan(math.radians(fov) / 2.0)))

# show settings dialog
dlg = xshade.create_dialog()

ppm_idx = dlg.append_int('Scale', 'ppm')
dlg.set_value(ppm_idx, 16)

solidfill_idx = dlg.append_bool('Solid fill')
dlg.set_value(solidfill_idx, False)

antialias_idx = dlg.append_bool('Antialiasing')
dlg.set_value(antialias_idx, False)

show_result_idx = dlg.append_bool('Show result in separate window')
dlg.set_value(show_result_idx, False)

if xshade.scene().active_shape().type == 7: # polygon mesh
	if dlg.ask('Render UV'):
		ppm = dlg.get_value(ppm_idx)
		antialias = dlg.get_value(antialias_idx)
		solidfill = dlg.get_value(solidfill_idx)
		show_result = dlg.get_value(show_result_idx)
		
		scene1 = xshade.scene()
		
		# create new scene
		xshade.new_scene()
		scene2 = xshade.scene()
		
		scene2.begin_creating()
		scene2.begin_polygon_mesh('UV Render')
		
		active_shape = scene1.active_shape()
		newfaces = []
		vertidx = 0
		
		minmaxinit = False
		minx = 0
		miny = 0
		maxx = 0
		maxy = 0
		
		for faceidx in active_shape.active_face_indices:
			curface = active_shape.face(faceidx)
			newfacevertinds = []
			for i in range(0, curface.number_of_vertices):
				uv = curface.get_face_uv(0, i)
				newvert = (uv[0] * 1000, -uv[1] * 1000, 0)
				if minmaxinit == True:
					minx = min(minx, newvert[0])
					miny = min(miny, newvert[1])
					maxx = max(maxx, newvert[0])
					maxy = max(maxy, newvert[1])
				else:
					minmaxinit = True
					minx = newvert[0]
					miny = newvert[1]
					maxx = newvert[0]
					maxy = newvert[1]
				
				scene2.append_polygon_mesh_vertex(newvert)
				newfacevertinds.append(vertidx)
				vertidx = vertidx + 1
			newfaces.append(newfacevertinds)
		
		for vertinds in newfaces:
			vertinds.reverse()
			scene2.append_polygon_mesh_face(vertinds)
			
		scene2.end_polygon_mesh()
		scene2.end_creating()
		
		modelwidth = int(math.ceil(abs(maxx - minx)))
		modelheight = int(math.ceil(abs(maxy - miny)))
		
		maxlen = float(max(modelwidth, modelheight))
		camdist = maxlen / 2
		
		imgwidth = int(math.ceil(modelwidth / ppm))
		imgheight = int(math.ceil(modelheight / ppm))
		
		centerx = (maxx - minx) / 2
		centery = (maxy - miny) / 2
		
		# set up rendering camera
		render_camera = scene2.camera
		render_camera.eye = [centerx, -centery, camdist]
		render_camera.target = [centerx, -centery, 0.0]
		render_camera.zoom = 18
		render_camera.distant_camera = True
		
		# set up rendering
		rend = scene2.rendering
		rend.image_size = (imgwidth, imgheight)
		if solidfill == True:
			rend.method = 0
		else:
			rend.method = 825229312
		rend.antialiasing = antialias
		rend.pixel_depth = 32
		rend.pixel_ratio = 1
		# render
		rend.render()
		rend.start()
		xshade.image_window().hide()	
		
		while rend.is_still_rendering:
			xshade.sleep(20)
	
		if show_result == True:
			rend.image.create_window('Render UV result')

	
		rend.image.save(None)		
	
		scene2.close()	
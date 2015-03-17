# @title \en Snap active UV vertexes\enden

active_shape = xshade.scene().active_shape()

for faceidx in active_shape.active_face_indices:
	curface = active_shape.face(faceidx)
	for vtxidx in range(0, curface.number_of_vertices):
		fgidx = active_shape.get_face_group_index(faceidx)
		
		# find texture image
		surf = None
		if fgidx == -1:
			if active_shape.master_surface != None:
				surf = active_shape.master_surface.surface
			elif active_shape.surface != None:
				surf = active_shape.surface
		else:
			surf = active_shape.get_face_group_surface(fgidx).surface
		
		if surf != None:
			img = None
			if surf.has_mapping_layers:
				for i in range(0, surf.number_of_mapping_layers):
					if surf.mapping_layer(i).pattern == 14 and surf.mapping_layer(i).type == 0:
						img = surf.mapping_layer(i).image
			
			if img != None:
				faceuv = curface.get_face_uv(0, vtxidx)
				map_u = faceuv[0]
				map_v = faceuv[1]
				map_u = round(map_u * img.size[0], 0) / img.size[0]
				map_v = round(map_v * img.size[1], 0) / img.size[1]
				curface.set_face_uv(0, vtxidx, [map_u, map_v])

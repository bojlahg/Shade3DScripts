# @title \en Reset Quad UV active faces\enden
for active_shape in xshade.scene().active_shapes:
	for faceind in active_shape.active_face_indices:
		curface = active_shape.face(faceind)
		if curface.number_of_vertices == 4:
			curface.set_face_uv(0, 0, [0,0])
			curface.set_face_uv(0, 1, [0,1])
			curface.set_face_uv(0, 2, [1,1])
			curface.set_face_uv(0, 3, [1,0])
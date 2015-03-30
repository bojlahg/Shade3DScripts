# @title \en Reset Normals Active Faces\enden

for active_shape in xshade.scene().active_shapes:
	for faceind in active_shape.active_face_indices:
		curface = active_shape.face(faceind)
		for vtxidx in range(0, curface.number_of_vertices):
			curface.normals = []
	active_shape.smooth_edges = False
	active_shape.smooth_edges = True
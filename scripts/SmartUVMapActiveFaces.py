# @title \en Smart UVMap active faces\enden

import math

def vec_sub(va, vb):
	return (va[0] - vb[0], va[1] - vb[1], va[2] - vb[2])
	
def vec_mag(vec):
	return math.sqrt(vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2])
	
def vec_mul_n(v, n):
	return (v[0] * n, v[1] * n, v[2] * n)
	
def vec_dot(va, vb):
	return va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2]

def vec_cross(va, vb):
	return (va[1] * vb[2] - va[2] * vb[1], va[2] * vb[0] - va[0] * vb[2], va[0] * vb[1] - va[1] * vb[0])

def vec_proj(va, vb):
	return vec_mul_n(vb, vec_dot(va, vb) / vec_dot(vb, vb))
	
def vec_unit(v):
	v_m = vec_mag(v)
	return (v[0] / v_m, v[1] / v_m, v[2] / v_m)

def vec_angle(va, vb):
	mag2 = (vec_mag(va) * vec_mag(vb))
	if mag2 == 0:
		return 0;
	return vec_dot(va, vb) / mag2
	
# show settings dialog
dlg = xshade.create_dialog()

scale_idx = dlg.append_float('Scale')
dlg.set_value(scale_idx, 1)

fituv_idx = dlg.append_bool('Fit UV')
dlg.set_value(fituv_idx, False)

if dlg.ask('Smart UV map active faces'):
	scale = dlg.get_value(scale_idx)
	fituv = dlg.get_value(fituv_idx)

	active_shape = xshade.scene().active_shape()
	for faceind in active_shape.active_face_indices:
		curface = active_shape.face(faceind)
		
		vcnt = curface.number_of_vertices
		
		verts1 = []
		for i in range(0, vcnt):
			verts1.append(curface.vertex(curface.vertex_indices[i]).position)
		
		mpidx = 0
		for i in range(0, vcnt):
			vt = vec_sub(verts1[(1 + i) % vcnt], verts1[(0 + i) % vcnt])
			angx = vec_angle(vt, (1,0,0))
			angy = vec_angle(vt, (0,1,0))
			angz = vec_angle(vt, (0,0,1))
			if ((angx < 0.1 and angx > -0.1 and angy < 0.1 and angy > -0.1) or
				(angx < 0.1 and angx > -0.1 and angz < 0.1 and angz > -0.1) or
				(angz < 0.1 and angz > -0.1 and angy < 0.1 and angy > -0.1)):
				mpidx = i
		verts2 = []
		for i in range(0, vcnt):
			verts2.append(verts1[(i + mpidx) % vcnt])

		v0 = verts2[0]
		v1 = verts2[1]
		v2 = verts2[vcnt - 1]
		
		vec1 = vec_sub(v1, v0)
		vec2 = vec_sub(v2, v0)
		
		for i in range(2, vcnt):
			v2 = verts2[i]
			vec2 = vec_sub(v2, v0)
			vang = vec_angle(vec1, vec2)
			if vang > -0.99 and vang < 0.99:
				break
		
		av = vec_unit(vec1)
		au = vec_unit(vec_cross(vec1, vec_cross(vec1, vec2)))
		
		uv = []
		for i in range(0, vcnt):
			texvec = vec_sub(verts2[i], verts2[0])
			pu = vec_proj(texvec, au)
			pus = vec_angle(pu, au)
			pv = vec_proj(texvec, av)
			pvs = vec_angle(pv, av)
			uv.append((pus * vec_mag(pu) / 1000 * scale, pvs * vec_mag(pv) / 1000 * scale))
		
		minu = uv[0][0]
		minv = uv[0][1]
		for i in range(1, vcnt):
			minu = min(minu, uv[i][0])
			minv = min(minv, uv[i][1])
			
		for i in range(0, vcnt):
			uv[i] = (uv[i][0] - minu, uv[i][1] - minv)
			
		for i in range(0, vcnt):
			curface.set_face_uv(0, (i + mpidx) % vcnt, uv[i])

	# fit all UV to 0-1
	if fituv == True:
		first_sample = True
		minu = 0
		minv = 0
		maxu = 0
		maxv = 0
		for faceind in active_shape.active_face_indices:
			curface = active_shape.face(faceind)
			vcnt = curface.number_of_vertices
			for i in range(0, vcnt):
				vtxuv = curface.get_face_uv(0, i)
				print vtxuv
				if first_sample == True:
					first_sample = False
					minu = vtxuv[0]
					minv = vtxuv[1]
					maxu = vtxuv[0]
					maxv = vtxuv[1]
				else:
					minu = min(minu, vtxuv[0])
					minv = min(minv, vtxuv[1])
					maxu = max(maxu, vtxuv[0])
					maxv = max(maxv, vtxuv[1])
		
		lenu = maxu - minu
		lenv = maxv - minv
		
		print maxu, minu, maxv, minv
		
		for faceind in active_shape.active_face_indices:
			curface = active_shape.face(faceind)
			vcnt = curface.number_of_vertices
			for i in range(0, vcnt):
				vtxuv = curface.get_face_uv(0, i)
				curface.set_face_uv(0, i, (vtxuv[0] / lenu, vtxuv[1] / lenv))

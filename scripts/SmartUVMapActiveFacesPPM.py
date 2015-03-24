# @title \en Smart UVMap active faces PPM\enden

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

ppm_idx = dlg.append_int('Scale', 'ppm')
dlg.set_value(ppm_idx, 16)

if dlg.ask('Smart UV map active faces density'):
	ppm = dlg.get_value(ppm_idx)

	active_shape = xshade.scene().active_shape()
	for faceidx in active_shape.active_face_indices:
		curface = active_shape.face(faceidx)
		
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
					
					newu = pus * vec_mag(pu)
					newv = pvs * vec_mag(pv)
			
					uv.append((newu / 1000, newv / 1000))
					
				# calculate min, max u and v
				minu = uv[0][0]
				minv = uv[0][1]
				maxu = uv[0][0]
				maxv = uv[0][1]
				for i in range(1, vcnt):
					minu = min(minu, uv[i][0])
					minv = min(minv, uv[i][1])
					maxu = max(maxu, uv[i][0])
					maxv = max(maxv, uv[i][1])
				
				imgu = float(img.size[0])
				imgv = float(img.size[1])

				# uv length
				ulen = maxu - minu
				vlen = maxv - minv
				
				# check rotation
				if abs(ulen) > abs(vlen):
					if imgu < imgv:
						imgu, imgv = imgv, imgu
				else:
					if imgu > imgv:
						imgu, imgv = imgv, imgu
				
				for i in range(0, vcnt):
					uv[i] = (uv[i][0] * float(ppm) / imgu, uv[i][1] * float(ppm) / imgv)

				# calculate min u and v
				minu = uv[0][0]
				minv = uv[0][1]
				for i in range(1, vcnt):
					minu = min(minu, uv[i][0])
					minv = min(minv, uv[i][1])
					
				# move to origin
                for i in range(0, vcnt):
					uv[i] = ( uv[i][0] - minu, uv[i][1] - minv)
				# set uv back
                for i in range(0, vcnt):
					curface.set_face_uv(0, (i + mpidx) % vcnt, uv[i])
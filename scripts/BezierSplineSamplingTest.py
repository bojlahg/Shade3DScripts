# @title \en Bezier spline sampling test\enden

import math

def vec_add(va, vb):
	return (va[0] + vb[0], va[1] + vb[1], va[2] + vb[2])

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

def bezier_pos(cp1, cp2, t):
	_1mt = 1.0 - t
	_1mt2 = _1mt * _1mt
	t2 = t * t
	return vec_add(vec_add(vec_mul_n(cp1.position, _1mt * _1mt2), vec_mul_n(cp1.out_handle, 3 * _1mt2 * t)), vec_add(vec_mul_n(cp2.in_handle, 3 * _1mt * t2), vec_mul_n(cp2.position, t2 * t)))
	
def bezier_tan(cp1, cp2, t):
	if cp1.has_out_handle == False and cp1.has_in_handle == False:
		return vec_sub(cp2.position, cp1.position)
	_1mt = 1.0 - t
	_1mt2 = _1mt * _1mt
	t2 = t * t
	return vec_add(vec_add(vec_mul_n(cp1.position, -3 * _1mt2), vec_mul_n(cp1.out_handle, -6 * _1mt * t + 3 * _1mt2)), vec_add(vec_mul_n(cp2.in_handle, 6 * _1mt * t - 3 * t2), vec_mul_n(cp2.position, 3 * t2)))

def bezier_norm(cp1, cp2, t):
	
	return vec_add(vec_mul_n(vec_add(vec_sub(cp2.in_handle, vec_mul_n(cp1.out_handle, 2)), cp1.position), 6 * (1 - t)), vec_mul_n(vec_add(vec_sub(cp2.position, vec_mul_n(cp2.in_handle, 2)), cp1.out_handle), 6 * t))
	
for shp in xshade.scene().active_shapes:

	xshade.scene().begin_creating()
	lineshp = xshade.scene().begin_line('Test Bezier Line', False)

	fromidx = 0
	if shp.closed == True:
		toidx = shp.total_number_of_control_points
	else:
		toidx = shp.total_number_of_control_points - 1
	
	for cptidx1 in range(fromidx, toidx):
		cptidx2 = cptidx1 + 1
		if shp.closed == True and cptidx2 == toidx:
			cptidx2 = 0
		
		cpt1 = shp.control_point(cptidx1)
		cpt2 = shp.control_point(cptidx2)


		xshade.scene().append_point(bezier_pos(cpt1, cpt2, 0.5), None, None, None, None)
		
		#xshade.scene().append_point(vec_add(bezier_pos(cpt1, cpt2, 0.5), bezier_tan(cpt1, cpt2, 0.5)), None, None, None, None)
		#xshade.scene().append_point(bezier_pos(cpt1, cpt2, 0.5), None, None, None, None)
		#xshade.scene().append_point(vec_add(bezier_pos(cpt1, cpt2, 0.5), bezier_norm(cpt1, cpt2, 0.5)), None, None, None, None)
		
		#xshade.scene().append_point(bezier_pos(cpt1, cpt2, 0.25), None, None, None, None)
		#xshade.scene().append_point(bezier_pos(cpt1, cpt2, 0.5), None, None, None, None)
		#xshade.scene().append_point(bezier_pos(cpt1, cpt2, 0.75), None, None, None, None)
	
	lineshp.closed = shp.closed
	xshade.scene().end_line()
	xshade.scene().end_creating()


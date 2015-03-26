# @title \en Snap active vertexes\enden

# show settings dialog
dlg = xshade.create_dialog()

# X
snapx_idx = dlg.append_bool('Snap X')
dlg.set_value(snapx_idx, True)

stepx_idx = dlg.append_int('X step')
dlg.set_value(stepx_idx, 100)
# Y
snapy_idx = dlg.append_bool('Snap Y')
dlg.set_value(snapy_idx, True)
stepy_idx = dlg.append_int('Y step')
dlg.set_value(stepy_idx, 100)
# Z
snapz_idx = dlg.append_bool('Snap Z')
dlg.set_value(snapz_idx, True)
stepz_idx = dlg.append_int('Z step')
dlg.set_value(stepz_idx, 100)

preset_idx = dlg.append_radio_button('presets/custom/250/500/1000')

if dlg.ask('Snap active vertexes'):
	snapx = dlg.get_value(snapx_idx)
	stepx = dlg.get_value(stepx_idx)
	
	snapy = dlg.get_value(snapy_idx)
	stepy = dlg.get_value(stepy_idx)
	
	snapz = dlg.get_value(snapz_idx)
	stepz = dlg.get_value(stepz_idx)
	
	preset = dlg.get_value(preset_idx)
	
	if preset == 1:
		stepx = 250
		stepy = 250
		stepz = 250
	elif preset == 2:
		stepx = 500
		stepy = 500
		stepz = 500
	elif preset == 3:
		stepx = 1000
		stepy = 1000
		stepz = 1000

	active_shape = xshade.scene().active_shape()
	for vtxidx in active_shape.active_vertex_indices:
		posx = active_shape.vertex(vtxidx).position[0]
		posy = active_shape.vertex(vtxidx).position[1]
		posz = active_shape.vertex(vtxidx).position[2]

		if snapx:
			posx = round(posx / stepx, 0) * stepx
		if snapy:
			posy = round(posy / stepy, 0) * stepy
		if snapz:
			posz = round(posz / stepz, 0) * stepz

		active_shape.vertex(vtxidx).position = [posx, posy, posz]

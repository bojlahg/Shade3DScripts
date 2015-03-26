# @title \en Load image to surface\enden

import os

openfiledialog = xshade.create_dialog()
path = openfiledialog.ask_path(True, "png(.png)|png")

if path != None:
	msname = os.path.splitext(os.path.basename(path))[0]
	img = xshade.create_image_from_file(path)
	if img != None:
		xshade.scene().begin_creating()
		mimg = xshade.scene().create_master_image(os.path.basename(path))
		mimg.image = img
		xshade.scene().end_creating()
		
		xshade.scene().begin_creating()
		msurf = xshade.scene().create_master_surface(msname)
		msurf.surface.append_mapping_layer()
		maplayer = msurf.surface.mapping_layer(0)
		maplayer.type = 0
		maplayer.pattern = 14
		maplayer.image = img
		xshade.scene().end_creating()
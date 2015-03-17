# @title \en Build Texture Atlas\enden

import sys


class Rect:
    def __init__(self, key, x, y, width, height):
        self.key = key
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self):
        return "#%d: %d, %d, %d, %d" % (self.key, self.x, self.y, self.width, self.height)

def is_contained_in(rectA, rectB):
    return rectA.x >= rectB.x and rectA.y >= rectB.y and rectA.x + rectA.width <= rectB.x + rectB.width and rectA.y + rectA.height <= rectB.y + rectB.height

def common_interval_length(i1start, i1end, i2start, i2end):
    if i1end < i2start or i2end < i1start:
        return 0
    return min(i1end, i2end) - max(i1start, i2start)

class Packer:
    def __init__(self, width, height, rotations):
        self.binWidth = width
        self.binHeight = height
        self.allowRotations = rotations
        self.usedRectangles = []
        self.freeRectangles = []
        self.freeRectangles.append(Rect(-1, 0, 0, width, height));

    def insert(self, width, height, method):
        newNode = Rect(-1, 0, 0, 0, 0)
        score1 = 0;
        score2 = 0;
        if method == 0:
            newNode = self.find_position_for_new_node_best_short_side_fit(width, height, score1, score2)
        elif method == 1:
            newNode = self.find_position_for_new_node_best_long_side_fit(width, height, score2, score1)
        elif method == 2:
            newNode = self.find_position_for_new_node_best_area_fit(width, height, score1, score2)
        elif method == 3:
            newNode = self.find_position_for_new_node_bottom_left(width, height, score1, score2)
        elif method == 4:
            newNode = self.find_position_for_new_node_contact_point(width, height, score1)

        if newNode.height == 0:
            return newNode

        numRectanglesToProcess = len(self.freeRectangles)
        i = 0
        while i < numRectanglesToProcess:
            if self.split_free_node(self.freeRectangles[i], newNode):
                self.freeRectangles.pop(i)
                i -= 1
                numRectanglesToProcess -= 1
            i += 1

        self.prune_free_list()

        self.usedRectangles.append(newNode);
        return newNode

    def insert_multi(self, rects, method):
        dst = []

        while len(rects) > 0:
            bestScore1 = sys.maxint
            bestScore2 = sys.maxint
            bestRectIndex = -1
            bestNode = Rect(-1, 0, 0, 0, 0)

            for i in range(0, len(rects)):
                score1 = 0
                score2 = 0
                newNode = self.score_rect(rects[i].width, rects[i].height, method, score1, score2)

                if score1 < bestScore1 or (score1 == bestScore1 and score2 < bestScore2):
                    bestScore1 = score1
                    bestScore2 = score2
                    bestNode = newNode
                    bestNode.key = rects[i].key
                    bestRectIndex = i

            if bestRectIndex == -1:
                return

            if bestNode.x == 0 and bestNode.y == 0 and bestNode.width == 0 and bestNode.height == 0:
                return dst

            self.place_rect(dst, bestNode)
            rects.pop(bestRectIndex)
        return dst

    def place_rect(self, dst, node):
        numRectanglesToProcess = len(self.freeRectangles)
        i = 0;
        while i < numRectanglesToProcess:
            if self.split_free_node(self.freeRectangles[i], node):
                self.freeRectangles.pop(i)
                i -= 1
                numRectanglesToProcess -= 1
            i += 1

        self.prune_free_list()

        self.usedRectangles.append(node)
        dst.append(node)

    def score_rect(self, width, height, method, score1, score2):
        newNode = Rect(-1, 0, 0, 0, 0)
        score1 = sys.maxint
        score2 = sys.maxint
        if method == 0:
            newNode = self.find_position_for_new_node_best_short_side_fit(width, height, score1, score2)
        elif method == 1:
            newNode = self.find_position_for_new_node_best_long_side_fit(width, height, score2, score1)
        elif method == 2:
            newNode = self.find_position_for_new_node_best_area_fit(width, height, score1, score2)
        elif method == 3:
            newNode = self.find_position_for_new_node_bottom_left(width, height, score1, score2)
        elif method == 4:
            newNode = self.find_position_for_new_node_contact_point(width, height, score1)
            score1 = -score1

        if newNode.height == 0:
            score1 = sys.maxint
            score2 = sys.maxint

        return newNode;

    def occupancy(self):
        usedSurfaceArea = 0
        for i in range(0, len(self.usedRectangles)):
            usedSurfaceArea += self.usedRectangles[i].width * self.usedRectangles[i].height
        return float(usedSurfaceArea) / float(self.binWidth * self.binHeight)

    def find_position_for_new_node_bottom_left(self, width, height, bestY, bestX):
        bestNode = Rect(-1, 0, 0, 0, 0)

        bestY = sys.maxint

        for i in range(0, len(self.freeRectangles)):
            if self.freeRectangles[i].width >= width and self.freeRectangles[i].height >= height:
                topSideY = self.freeRectangles[i].y + height
                if topSideY < bestY or (topSideY == bestY and self.freeRectangles[i].x < bestX):
                    bestNode.x = self.freeRectangles[i].x
                    bestNode.y = self.freeRectangles[i].y
                    bestNode.width = width
                    bestNode.height = height
                    bestY = topSideY
                    bestX = self.freeRectangles[i].x
            if self.allowRotations and self.freeRectangles[i].width >= height and self.freeRectangles[
                i].height >= width:
                topSideY = self.freeRectangles[i].y + width;
                if topSideY < bestY or (topSideY == bestY and self.freeRectangles[i].x < bestX):
                    bestNode.x = self.freeRectangles[i].x
                    bestNode.y = self.freeRectangles[i].y
                    bestNode.width = height
                    bestNode.height = width
                    bestY = topSideY
                    bestX = self.freeRectangles[i].x
        return bestNode;

    def find_position_for_new_node_best_short_side_fit(self, width, height, bestShortSideFit, bestLongSideFit):
        bestNode = Rect(-1, 0, 0, 0, 0)

        bestShortSideFit = sys.maxint

        for i in range(0, len(self.freeRectangles)):
            if self.freeRectangles[i].width >= width and self.freeRectangles[i].height >= height:
                leftoverHoriz = abs(self.freeRectangles[i].width - width)
                leftoverVert = abs(self.freeRectangles[i].height - height)
                shortSideFit = min(leftoverHoriz, leftoverVert)
                longSideFit = max(leftoverHoriz, leftoverVert)

                if shortSideFit < bestShortSideFit or (
                        shortSideFit == bestShortSideFit and longSideFit < bestLongSideFit):
                    bestNode.x = self.freeRectangles[i].x
                    bestNode.y = self.freeRectangles[i].y
                    bestNode.width = width
                    bestNode.height = height
                    bestShortSideFit = shortSideFit
                    bestLongSideFit = longSideFit

            if self.allowRotations and self.freeRectangles[i].width >= height and self.freeRectangles[
                i].height >= width:
                flippedLeftoverHoriz = abs(self.freeRectangles[i].width - height)
                flippedLeftoverVert = abs(self.freeRectangles[i].height - width)
                flippedShortSideFit = min(flippedLeftoverHoriz, flippedLeftoverVert)
                flippedLongSideFit = max(flippedLeftoverHoriz, flippedLeftoverVert)

                if flippedShortSideFit < bestShortSideFit or (
                        flippedShortSideFit == bestShortSideFit and flippedLongSideFit < bestLongSideFit):
                    bestNode.x = self.freeRectangles[i].x
                    bestNode.y = self.freeRectangles[i].y
                    bestNode.width = height
                    bestNode.height = width
                    bestShortSideFit = flippedShortSideFit
                    bestLongSideFit = flippedLongSideFit
        return bestNode

    def find_position_for_new_node_best_long_side_fit(self, width, height, bestShortSideFit, bestLongSideFit):
        bestNode = Rect(-1, 0, 0, 0, 0)

        bestLongSideFit = sys.maxint

        for i in range(0, len(self.freeRectangles)):
            if self.freeRectangles[i].width >= width and self.freeRectangles[i].height >= height:
                leftoverHoriz = abs(self.freeRectangles[i].width - width)
                leftoverVert = abs(self.freeRectangles[i].height - height)
                shortSideFit = min(leftoverHoriz, leftoverVert)
                longSideFit = max(leftoverHoriz, leftoverVert)

                if longSideFit < bestLongSideFit or (
                        longSideFit == bestLongSideFit and shortSideFit < bestShortSideFit):
                    bestNode.x = self.freeRectangles[i].x
                    bestNode.y = self.freeRectangles[i].y
                    bestNode.width = width
                    bestNode.height = height
                    bestShortSideFit = shortSideFit
                    bestLongSideFit = longSideFit

            if self.allowRotations and self.freeRectangles[i].width >= height and self.freeRectangles[
                i].height >= width:
                leftoverHoriz = abs(self.freeRectangles[i].width - height)
                leftoverVert = abs(self.freeRectangles[i].height - width)
                shortSideFit = min(leftoverHoriz, leftoverVert)
                longSideFit = max(leftoverHoriz, leftoverVert)

                if longSideFit < bestLongSideFit or (
                        longSideFit == bestLongSideFit and shortSideFit < bestShortSideFit):
                    bestNode.x = self.freeRectangles[i].x
                    bestNode.y = self.freeRectangles[i].y
                    bestNode.width = height
                    bestNode.height = width
                    bestShortSideFit = shortSideFit
                    bestLongSideFit = longSideFit
        return bestNode

    def find_position_for_new_node_best_area_fit(self, width, height, bestAreaFit, bestShortSideFit):
        bestNode = Rect(-1, 0, 0, 0, 0)

        bestAreaFit = sys.maxint

        for i in range(0, len(self.freeRectangles)):
            areaFit = self.freeRectangles[i].width * self.freeRectangles[i].height - width * height

            if self.freeRectangles[i].width >= width and self.freeRectangles[i].height >= height:
                leftoverHoriz = abs(self.freeRectangles[i].width - width)
                leftoverVert = abs(self.freeRectangles[i].height - height)
                shortSideFit = min(leftoverHoriz, leftoverVert)

                if areaFit < bestAreaFit or (areaFit == bestAreaFit and shortSideFit < bestShortSideFit):
                    bestNode.x = self.freeRectangles[i].x;
                    bestNode.y = self.freeRectangles[i].y;
                    bestNode.width = width;
                    bestNode.height = height;
                    bestShortSideFit = shortSideFit;
                    bestAreaFit = areaFit;

            if self.allowRotations and self.freeRectangles[i].width >= height and self.freeRectangles[
                i].height >= width:
                leftoverHoriz = abs(self.freeRectangles[i].width - height)
                leftoverVert = abs(self.freeRectangles[i].height - width)
                shortSideFit = min(leftoverHoriz, leftoverVert)

                if areaFit < bestAreaFit or (areaFit == bestAreaFit and shortSideFit < bestShortSideFit):
                    bestNode.x = self.freeRectangles[i].x
                    bestNode.y = self.freeRectangles[i].y
                    bestNode.width = height
                    bestNode.height = width
                    bestShortSideFit = shortSideFit
                    bestAreaFit = areaFit
        return bestNode

    def contact_point_score_node(self, x, y, width, height):
        score = 0

        if x == 0 or x + width == self.binWidth:
            score += height
        if y == 0 or y + height == self.binHeight:
            score += width

        for i in range(0, len(self.usedRectangles)):
            if self.usedRectangles[i].x == x + width or self.usedRectangles[i].x + self.usedRectangles[i].width == x:
                score += common_interval_length(self.usedRectangles[i].y,
                                                self.usedRectangles[i].y + self.usedRectangles[i].height, y, y + height)
            if self.usedRectangles[i].y == y + height or self.usedRectangles[i].y + self.usedRectangles[i].height == y:
                score += common_interval_length(self.usedRectangles[i].x,
                                                self.usedRectangles[i].x + self.usedRectangles[i].width, x, x + width)
        return score

    def find_position_for_new_node_contact_point(self, width, height, bestContactScore):
        bestNode = Rect(-1, 0, 0, 0, 0)
        bestContactScore = -1
        for i in range(0, len(self.freeRectangles)):
            if self.freeRectangles[i].width >= width and self.freeRectangles[i].height >= height:
                score = self.contact_point_score_node(self.freeRectangles[i].x, self.freeRectangles[i].y, width, height)
                if score > bestContactScore:
                    bestNode.x = self.freeRectangles[i].x
                    bestNode.y = self.freeRectangles[i].y
                    bestNode.width = width
                    bestNode.height = height
                    bestContactScore = score

            if self.allowRotations and self.freeRectangles[i].width >= height and self.freeRectangles[
                i].height >= width:
                score = self.contact_point_score_node(self.freeRectangles[i].x, self.freeRectangles[i].y, height, width)
                if score > bestContactScore:
                    bestNode.x = self.freeRectangles[i].x
                    bestNode.y = self.freeRectangles[i].y
                    bestNode.width = height
                    bestNode.height = width
                    bestContactScore = score
        return bestNode

    def split_free_node(self, freeNode, usedNode):
        if usedNode.x >= freeNode.x + freeNode.width or usedNode.x + usedNode.width <= freeNode.x or usedNode.y >= freeNode.y + freeNode.height or usedNode.y + usedNode.height <= freeNode.y:
            return False

        if usedNode.x < freeNode.x + freeNode.width and usedNode.x + usedNode.width > freeNode.x:
            if usedNode.y > freeNode.y and usedNode.y < freeNode.y + freeNode.height:
                newNode = Rect(freeNode.key, freeNode.x, freeNode.y, freeNode.width, freeNode.height)
                newNode.height = usedNode.y - newNode.y
                self.freeRectangles.append(newNode)

            if usedNode.y + usedNode.height < freeNode.y + freeNode.height:
                newNode = Rect(freeNode.key, freeNode.x, freeNode.y, freeNode.width, freeNode.height)
                newNode.y = usedNode.y + usedNode.height
                newNode.height = freeNode.y + freeNode.height - (usedNode.y + usedNode.height)
                self.freeRectangles.append(newNode)

        if usedNode.y < freeNode.y + freeNode.height and usedNode.y + usedNode.height > freeNode.y:
            if usedNode.x > freeNode.x and usedNode.x < freeNode.x + freeNode.width:
                newNode = Rect(freeNode.key, freeNode.x, freeNode.y, freeNode.width, freeNode.height)
                newNode.width = usedNode.x - newNode.x
                self.freeRectangles.append(newNode)

            if usedNode.x + usedNode.width < freeNode.x + freeNode.width:
                newNode = Rect(freeNode.key, freeNode.x, freeNode.y, freeNode.width, freeNode.height)
                newNode.x = usedNode.x + usedNode.width
                newNode.width = freeNode.x + freeNode.width - (usedNode.x + usedNode.width)
                self.freeRectangles.append(newNode)
        return True

    def prune_free_list(self):
        i = 0
        while i < len(self.freeRectangles):
            j = i + 1
            while j < len(self.freeRectangles):
                if is_contained_in(self.freeRectangles[i], self.freeRectangles[j]):
                    self.freeRectangles.pop(i);
                    i -= 1
                    break;
                if is_contained_in(self.freeRectangles[j], self.freeRectangles[i]):
                    self.freeRectangles.pop(j);
                    j -= 1
                j += 1
            i += 1

class AtlasData:
    def __init__(self, img_diffuse, img_normal, bao, mesh):
        self.image_diffuse = img_diffuse
        self.image_normal = img_normal
        self.meshes = []
        self.meshes.append(mesh)
        self.rect_src = Rect(-1, 0, 0, img_diffuse.size[0] + bao.padding * 2, img_diffuse.size[1] + bao.padding * 2)
        self.rect_dst = Rect(-1, 0, 0, 0, 0)

def get_textures(shp, bao):
    tl = []
    get_textures_recursive(shp, tl, bao)
    return tl

def get_textures_recursive(shp, tl, bao):
    if shp.type == 7:
        if shp.get_number_of_face_groups() > 0:
            for i in range(0, shp.get_number_of_face_groups()):
                msurf = shp.get_face_group_surface(i)
                if msurf.surface.has_mapping_layers:
                    add_texture(tl, msurf.surface, bao, shp)
        else:
            if shp.master_surface != None:
                msurf = shp.master_surface
                if msurf.surface.has_mapping_layers:
                    add_texture(tl, msurf.surface, bao, shp)
            elif shp.surface != None:
                if shp.surface.has_mapping_layers:
                    add_texture(tl, shp.surface, bao, shp)
    if shp.has_son:
        get_textures_recursive(shp.son, tl, bao)
    if shp.has_dad:
        if shp.has_bro:
            get_textures_recursive(shp.bro, tl, bao)

def add_texture(tl, surf, bao, shp):
    img_diffuse = None
    img_normal = None
    for i in range(0, surf.number_of_mapping_layers):
        maplayer = surf.mapping_layer(i)
        if maplayer.pattern == 14: # Image
            if maplayer.type == 0: # Diffuse
                img_diffuse = maplayer.image
            elif maplayer.type == 21: # Normal
                img_normal = maplayer.image
    for i in range(0, len(tl)):
        tad = tl[i]
        if tad.image_diffuse.path == img_diffuse.path:
            tad.meshes.append(shp)
            return
    if img_diffuse != None:
        tad = AtlasData(img_diffuse, img_normal, bao, shp)
        tl.append(tad)

def copy_texture_to_atlas(mi_diffuse, mi_normal, tad, bao):
    atlasimgdiffuse = mi_diffuse.image
    if bao.include_normalmap == True:
        atlasimgnormal = mi_normal.image
    w = tad.rect_dst.width
    h = tad.rect_dst.height
    # check if rect is rotated
    if tad.rect_src.width != tad.rect_dst.width:
        # rotated
        y = 0
        while y < h:
            x = 0
            while x < w:
                atlasimgdiffuse.set_pixel_rgba(tad.rect_dst.x + x, tad.rect_dst.y + y, get_pixel_clamped_rgba(tad.image_diffuse, h - y - bao.padding - 1, x - bao.padding))
                if bao.include_normalmap == True and tad.image_normal != None:
                    atlasimgnormal.set_pixel_rgba(tad.rect_dst.x + x, tad.rect_dst.y + y, get_pixel_clamped_rgba(tad.image_normal, h - y - bao.padding - 1, x - bao.padding))
                x += 1
            y += 1
    else:
        # without rotation
        y = 0
        while y < h:
            x = 0
            while x < w:
                atlasimgdiffuse.set_pixel_rgba(tad.rect_dst.x + x, tad.rect_dst.y + y, get_pixel_clamped_rgba(tad.image_diffuse, x - bao.padding, y - bao.padding))
                if bao.include_normalmap == True and tad.image_normal != None:
                   atlasimgnormal.set_pixel_rgba(tad.rect_dst.x + x, tad.rect_dst.y + y, get_pixel_clamped_rgba(tad.image_normal, x - bao.padding, y - bao.padding))
                x += 1
            y += 1

def get_pixel_clamped_rgba(img, x, y):
    nx = x
    ny = y
    if nx < 0:
        nx = 0
    if ny < 0:
        ny = 0
    if nx >= img.size[0]:
        nx = img.size[0] - 1
    if ny >= img.size[1]:
        ny = img.size[1] - 1
    return img.get_pixel_rgba(nx, ny)

def fill_normalmap(img):
    for y in range(0, img.size[1]):
        for x in range(0, img.size[0]):
            img.set_pixel_rgba(x, y, (0.5, 0.5, 1, 1))

class BuildAtlasOptions:
    def __init__(self):
        self.pack_method = 2
        self.atlas_width = 512
        self.atlas_height = 512
        self.padding = 2
        self.include_normalmap = True
        self.allow_rotation = True
        self.show_result = False


# clear messages
xshade.message_view().clear_message()
# show atlas settings dialog
dlg = xshade.create_dialog()
pack_method_idx = dlg.append_selection('Pack method/Best short side fit/Best long side fit/Best area fit/Bottom left rule/Contact point rule')
dlg.set_value(pack_method_idx, 2)
atlas_width_idx = dlg.append_int('Atlas width', 'px')
dlg.set_value(atlas_width_idx, 512)
atlas_height_idx = dlg.append_int('Atlas height', 'px')
dlg.set_value(atlas_height_idx, 512)
padding_idx = dlg.append_int('Padding', 'px')
dlg.set_value(padding_idx, 2)
allow_rotation_idx = dlg.append_bool('Allow rotation')
dlg.set_value(allow_rotation_idx, True)
include_normalmap_idx = dlg.append_bool('Include normal map')
dlg.set_value(include_normalmap_idx, True)
show_result_idx = dlg.append_bool('Show result in separate window')
dlg.set_value(show_result_idx, False)


if dlg.ask('Build texture atlas'):
    bao = BuildAtlasOptions()
    scene1 = xshade.scene()
    bao.pack_method = dlg.get_value(pack_method_idx)
    bao.atlas_width = dlg.get_value(atlas_width_idx)
    bao.atlas_height = dlg.get_value(atlas_height_idx)
    bao.padding = dlg.get_value(padding_idx)
    bao.include_normalmap = dlg.get_value(include_normalmap_idx)
    bao.allow_rotation = dlg.get_value(allow_rotation_idx)
    bao.show_result = dlg.get_value(show_result_idx)
    #
    rootshape = scene1.shape
    texlist = get_textures(rootshape, bao)

    #
    packer = Packer(bao.atlas_width, bao.atlas_height, bao.allow_rotation)
    inputrects = []
    for i in range(0, len(texlist)):
        texlist[i].rect_src.key = i
        inputrects.append(texlist[i].rect_src)

    rectcount = len(inputrects)
    inputrects = sorted(inputrects, key=lambda rect: (rect.width * rect.height), reverse=True)
    outputrects = packer.insert_multi(inputrects, bao.pack_method)

    if rectcount == len(outputrects):
        # copy output data
        for i in range(0, len(texlist)):
            for j in range(0, len(outputrects)):
                if texlist[i].rect_src.key == outputrects[j].key:
                    texlist[i].rect_dst = outputrects[j]
                    break;

        # create new scene
        xshade.new_scene()
        scene2 = xshade.scene()

        atlas_master_image_diffuse = scene2.create_master_image('TextureAtlas.png')
        atlas_master_image_diffuse.image = xshade.create_image((bao.atlas_width, bao.atlas_height), 32)

        if bao.include_normalmap == True:
            atlas_master_image_normal = scene2.create_master_image('TextureAtlas_Normal.png')
            atlas_master_image_normal.image = xshade.create_image((bao.atlas_width, bao.atlas_height), 32)
            fill_normalmap(atlas_master_image_normal.image)
        else:
            atlas_master_image_normal = None

        atlas_master_surface = scene2.create_master_surface('TextureAtlas')

        atlas_master_surface.surface.append_mapping_layer()
        difuse_layer = atlas_master_surface.surface.mapping_layer(0)
        difuse_layer.pattern = 14
        difuse_layer.type = 0
        difuse_layer.image = atlas_master_image_diffuse.image

        if bao.include_normalmap == True:
            atlas_master_surface.surface.append_mapping_layer()
            normal_layer = atlas_master_surface.surface.mapping_layer(1)
            normal_layer.pattern = 14
            normal_layer.type = 21
            normal_layer.image = atlas_master_image_normal.image

        for i in range(0, len(texlist)):
            copy_texture_to_atlas(atlas_master_image_diffuse, atlas_master_image_normal, texlist[i], bao)

        # make list with unique meshes
        meshes = []
        for i in range(0, len(texlist)):
            for j in range(0, len(texlist[i].meshes)):
                found = False
                for k in range(len(meshes)):
                    if meshes[k] is texlist[i].meshes[j]:
                        found = True
                        break
                if found == False:
                    meshes.append(texlist[i].meshes[j])

        for i in range(0, len(meshes)):
            #copy mesh to new scene
            mesh1 = meshes[i]
            scene1.active_shapes = [mesh1]
            scene1.cursor_position = (0, 0, 0)
            scene1.copy()

            scene2.cursor_position = (0, 0, 0)
            scene2.paste()
            mesh2 = scene2.active_shapes[0]
            mesh2.master_surface = atlas_master_surface

            for j in range(0, mesh1.number_of_faces):
                face1 = mesh1.face(j)
                fgidx = mesh1.get_face_group_index(j)
                face2 = mesh2.face(j)

                # find texture image
                if fgidx == -1:
                    if mesh1.master_surface != None:
                        surf = mesh1.master_surface.surface
                    elif mesh1.surface != None:
                        surf = mesh1.surface
                else:
                    surf = mesh1.get_face_group_surface(fgidx).surface

                teximg = None
                if surf.has_mapping_layers:
                    for k in range(0, surf.number_of_mapping_layers):
                        if surf.mapping_layer(k).pattern == 14 and surf.mapping_layer(k).type == 0:
                            teximg = surf.mapping_layer(k).image

                tad = None
                if teximg != None:
                    for k in range(0, len(texlist)):
                        if texlist[k].image_diffuse.path == teximg.path:
                            tad = texlist[k]
                            break

                if tad != None:
                    tx = float(tad.rect_dst.x) / float(bao.atlas_width)
                    ty = float(tad.rect_dst.y) / float(bao.atlas_height)
                    tw = float(tad.rect_dst.width) / float(bao.atlas_width)
                    th = float(tad.rect_dst.height) / float(bao.atlas_width)

                    # check if rect is rotated
                    if tad.rect_src.width != tad.rect_dst.width:
                        # rotated
                        for k in range(0, face2.number_of_vertices):
                            uv = face2.get_face_uv(0, k)
                            uv = (tx + uv[1] * tw, ty + (1 - uv[0]) * th)
                            face2.set_face_uv(0, k, uv)
                    else:
                        # without rotation
                        for k in range(0, face2.number_of_vertices):
                            uv = face2.get_face_uv(0, k)
                            uv = (tx + uv[0] * tw, ty + uv[1] * th)
                            face2.set_face_uv(0, k, uv)


            mesh2.clear_face_group()

        if bao.show_result == True:
            atlas_master_image_diffuse.image.create_window('Build texture atlas: Diffuse')
            if bao.include_normalmap == True:
                atlas_master_image_normal.image.create_window('Build texture atlas: Normal')

        #xshade.show_message_box('Success\nAtlas filled %f %%' % (packer.occupancy() * 100), False)
            print 'Success\nAtlas filled %f %%' % (packer.occupancy() * 100)
    else:
        #xshade.show_message_box('Failed\nNot enough space to fit all textures into atlas', False)
        print 'Not enough space to fit all textures into atlas!'
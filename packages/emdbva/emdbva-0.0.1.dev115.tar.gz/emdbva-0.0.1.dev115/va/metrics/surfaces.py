from va.utils.misc import *
from va.utils.ChimeraxViews import ChimeraxViews


def surfaces(workdir, mapname, cl, hmodd=None, hmeven=None, models=None, input_json=None):
    """
        Surface views of primary map, raw map, model with primary map and mask with primary map
    """
    # create viewer
    chimerax = chimerax_envcheck()
    viewer = ChimeraxViews(chimerax, None, workdir)

    # Primary map surface view
    primary_input_map = f'{workdir}{mapname}'
    primary_input_contour = cl
    viewer.new_surface_view_chimerax(primary_input_map, primary_input_contour)

    # Raw map surface view
    if hmodd is not None and hmeven is not None:
        rawmap_name = self.findrawmap()
        rawmap_cl = self.rawmapcl()
        viewer.new_surface_view_chimerax(rawmap_name, rawmap_cl, 'surface', 'raw')

    # Primary map and model
    if self.models:
        for model in self.models:
            viewer.new_surface_view_chimerax(primary_input_map, primary_input_contour, 'surface', '',
                                             None, None, model.filename)

    # Mask surface view
    for mask_name in self.allmasks:
        # Use all 1.0 for mask contour level till it is given by author in the header
        mask_cl = 1.0
        viewer.new_surface_view_chimerax(primary_input_map, primary_input_contour, 'mask', '',
                                         mask_name, mask_cl)




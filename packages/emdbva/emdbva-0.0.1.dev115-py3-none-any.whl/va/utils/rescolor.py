# Fast coloring of residues that avoids slow atom spec parsing.  Atom spec must have form /{chain_id}:{resnumber}.
#
#     rescolor /A:123 blue
#
# or interleaved residues and colors on a line (colors must be in format #rrggbb)
#
#     rescolors /A0:14 #3737ff /A0:15 #3535ff /A0:16 #3232ff


def rescolor(session, res_spec, color):
    parts = res_spec.split(':')
    chain_id = parts[0][1:]
    res_number = int(parts[1])
    from chimerax.atomic import AtomicStructure
    for s in session.models.list(type = AtomicStructure):
        if not hasattr(s, 'res_table'):
            s.res_table = {(r.chain_id, r.number):r for r in s.residues}
        r = s.res_table[(chain_id, res_number)]
        r.color = color
        r.atoms.colors = color
        # color ribbon
        r.ribbon_color = color


def rescolors(session, res_color_string):
    res_color_list = res_color_string.split()
    for res_spec, color in zip(res_color_list[::2], res_color_list[1::2]):
        rgba = tuple(int(color[i:i+2], 16) for i in range(1, 7, 2)) + (255,)
        rescolor(session, res_spec, rgba)


def register_command(session):
    from chimerax.core.commands import CmdDesc, register, StringArg, Color8Arg, RestOfLine
    desc = CmdDesc(required=[('res_spec', StringArg),
                              ('color', Color8Arg)],
                   synopsis='Color a residue fast')
    register('rescolor', desc, rescolor, logger=session.logger)
    desc = CmdDesc(required=[('res_color_string', RestOfLine),],
                   synopsis='Color residues fast')
    register('rescolors', desc, rescolors, logger=session.logger)

register_command(session)
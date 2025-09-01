# table generator

import jpylib as y
import functools
from .table_templates import *


_default_params = dict(
    corner=["", "", "", ""],
    border=["", "", "", ""],
    hsep=["", ""],
    vsep=["", ""],
    tb_cross=["", ""],
    lb_cross=["", ""],
    rb_cross=["", ""],
    bb_cross=["", ""],
    hl_cross=["", ""],
    nl_cross=["", ""],
    data=None,
)

class Table:

    def __init__(self, *, corner=None, border=None, hsep=None, vsep=None,
                 tb_cross=None, lb_cross=None, rb_cross=None, bb_cross=None,
                 hl_cross=None, nl_cross=None, cell_pad=[1, 1], pad_char=" ",
                 template=None, align=None, data=None, rstrip=True, indent=""):
        """Initialise a Table formatting parameter set.
        
        Arguments:
        * corner[4]:     top left, top right, bottom left, bottom right corners
        * border[4]:     top, left, right, bottom border sans crossing or corner
        * hsep[2]:       horizontal separator, after first column and others
        * vsep[2]:       vertical separator, after first row and others
        * tb_cross[2]:   top border crossing, first and others
        * lb_cross[2]:   left border crossing, first and others
        * rb_cross[2]:   right border crossing, first and others
        * bb_cross[2]:   bottom border crossing, first and others
        * hl_cross[2]:   header separator line crossing, first and others
        * nl_cross[2]:   normal separator line crossing, first and others
        * cell_pad[2]:   minimum cell padding, left and right (integers)
        * pad_char:      padding character
        * template:      a template 7 x 7 drawing describing the table
        * align:         alignment descriptor string, 1 char per column, l/r/c;
                         may be sequence of 2 for first and following rows;
                         asterisk at the end means default for following columns
                         is the character in front of the asterisk
        * data:          the data to format, as a sequence of rows, which are
                         sequences of columns (the data items)
        * rstrip:        strip trailing blanks off output lines
        * intend:        a string to lead each output line

        Parameters are first taken from the template, if any, and
        can then tweaked by the other constructor arguments.

        """
        # (1) set default values
        self.__dict__.update(_default_params)
        # (2) override them from the template
        if template:
            self.__dict__.update(template_params(template))
        # (3) override with the constructor parameters
        self.__dict__.update({ k: v for k, v in locals().items()
                               if v is not None })

        # Some need special checking and handling:
        # (1) cell_padding may be specified as list/tuple of 1 or 2, or as int
        if cell_pad is None:
            self.cell_pad = [0, 0]
        elif y.is_sequence(cell_pad):
            if not all(map(y.is_int, cell_pad)):
                raise ValueError("cell_pad is not a sequence of int, but {}"
                                 .format(repr(cell_pad)))
            if len(cell_pad) == 1:
                self.cell_pad = cell_pad * 2
            elif len(cell_pad) != 2:
                raise ValueError("cell_pad is not a sequence len 1 or 2, but {}"
                                 .format(len(cell_pad)))
        elif y.is_int(cell_pad):
            self.cell_pad = [cell_pad, cell_pad]
        else:
            raise ValueError("cell_pad is not None or int or seq of 2 ints: {}"
                             .format(repr(cell_pad)))

        # (2) Always have a separate alignment for the first and the following
        # lines. They need not be different, though. May be a list of 1 or 2
        # or a simple string or None.
        self.defaultalign = [None, None]
        if align is None:
            self.align = ["", ""]
        elif type(align) == str:
            split_align = align.split(",")
            if len(split_align) == 1:
                self.align = [align, align]
            elif len(split_align) == 2:
                self.align = split_align
            else:
                raise ValueError("more than 2 comma-separated align strings: {}"
                                 .format(repr(align)))                
        else:
            raise ValueError("align must be a string of one or two "
                             + "comma-separated fields, "
                             + "but is {}".format(repr(align)))
        # Set default alignment if align ends with "*"
        for i in (0, 1):
            if self.align[i]:
                if self.align[i].endswith("*") and len(self.align[i]) > 1:
                    self.defaultalign[i] = self.align[i][-2]
                    self.align[i] = self.align[i][:-1]
        # Now incorporate the data, if specified here.
        if data:
            self._fill_table(data)


    def _fill_table(self, data):
        """Assess and store the table data."""
        self.data = data
        self.cols = 0                   # maximum column number
        self.rows = 0                   # maximum row number
        self.col_width = []             # maximum item width per columns

        for row, data_line in enumerate(data):
            self.rows = row + 1
            for col, data_item in enumerate(data_line):
                col_width = self.col_width
                if col >= self.cols:
                    self.cols = col + 1
                    self.col_width.append(0)
                self.col_width[col] = \
                    max(self.col_width[col], len(str(data_item)))
        return self

    def _padded_item(self, item, width, alignment):
        """Return a string of the item with left and right padding."""
        padding = width - len(item)
        if alignment in (None, "n"):
            if y.is_num(item):
                alignment = "r"
            else:
                alignment = "l"                
        if alignment == "l":
            lpad = 0
            rpad = padding
        elif alignment == "r":
            lpad = padding
            rpad = 0
        elif alignment == "c":
            lpad = int(padding / 2)
            rpad = padding - lpad
        else:
            raise ValueError("invalid char in alignment: {}"
                             .format(repr(alignment)))
        return (self.pad_char * (lpad + self.cell_pad[0])
                + str(item)
                + self.pad_char * (self.cell_pad[1] + rpad))

    def _vert_sep(self, left_border, right_border, line, cross1, cross2):
        """Return a vertical separator (border or internal)."""
        r = []
        if line:
            r.append(left_border)
            had_first_col = False
            cross = cross1
            for col in range(self.cols):
                if had_first_col:
                    r.append(cross)
                    cross = cross2
                had_first_col = True
                r.append(line * (self.col_width[col] + sum(self.cell_pad)))
            r.append(right_border)
        result = "".join(r)
        return result
            

    def _alignment(self, row, column):
        """Return the alignment of the (row, column) cell."""
        index = 0 if row == 0 else 1
        align = self.align[index]
        if column >= len(align or ""):
            return self.defaultalign[index]
        return align[column]


    def format(self, data=None):
        """Return the formatted Table as a string.

        Table data must be specified here or earlier in the constructor.
        """
        if data:
            self._fill_table(data)
        assert self.data, "Table has no data, so cannot be formatted."
        
        # Start result with the top border line.
        result = []
        tb = self._vert_sep(self.corner[0], self.corner[1], self.border[0],
                            self.tb_cross[0], self.tb_cross[1])
        if tb:
            result.append(self.indent + tb)
        had_first_row = False
        left_cross, int_cross1, int_cross2, right_cross = (
            self.lb_cross[0], self.hl_cross[0],
            self.hl_cross[1], self.rb_cross[0]
        )
        vsep = self.vsep[0]
        for row, data_line in enumerate(self.data):
            # Vertical separator line, if necessary
            if had_first_row:
                sepline = self._vert_sep(left_cross, right_cross,
                                         vsep, int_cross1, int_cross2)
                if sepline:
                    result.append(self.indent + sepline)

                left_cross, int_cross1, int_cross2, right_cross = (
                    self.lb_cross[1], self.nl_cross[0],
                    self.nl_cross[1], self.rb_cross[1]
                )
                vsep = self.vsep[1]
            had_first_row = True

            # actual data line
            rline = []
            had_first_col = False
            hsep = self.hsep[0]
            rline.append(self.border[1])
            for col, data_item in enumerate(data_line):
                if had_first_col:
                    rline.append(hsep)
                    hsep = self.hsep[1]
                had_first_col = True
                rline.append(self._padded_item(str(data_item),
                                               self.col_width[col],
                                               self._alignment(row, col)))
            rline.append(self.border[2])
            result.append(self.indent + "".join(rline))
    
        # bottom border
        bb = self._vert_sep(self.corner[2], self.corner[3],
                            self.border[3], *self.bb_cross)
        if bb:
            result.append(self.indent + bb)
        for lino, line in enumerate(result):
            if self.rstrip:
                line = line.rstrip()
                result[lino] = line
        return "\n".join(result)

def format_table(data=None, template_name=None, template=None, **kwargs):
    """Format a table from the specified data and (optional) template.

    The template can be given by name, selecting one of the pre-defined
    templates, or explicitly. In absence of a specified template, the
    default parameters will be used, which is equivalent to the "minimal"
    template.

    All parameters can be tweaked through the kwargs, which are passed
    to the Table constructor (see there).

    """
    if data is None:
        data = example_data
    if template is None:
        template = get_template(template_name)
    table = Table(template=template, data=data, **kwargs)
    return table.format()


# EOF

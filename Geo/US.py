# Copyright (C) 2008 Laurence Tratt http://tratt.net/laurie/
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


import re
from .import Results


_RE_US_ZIP_PLUS4 = re.compile("[0-9]{4}")


def postcode_match(ft, i):
    for match, new_i in _sub_pc_match(ft, i):
        yield match, new_i

    if i > 0 and _RE_US_ZIP_PLUS4.match(ft.split[i]):
        for match, new_i in _sub_pc_match(ft, i - 1):
            yield match, new_i


def _sub_pc_match(ft, i):
    us_id = ft.queryier.get_country_id_from_iso2(ft, "US")

    c = ft.db.cursor()

    c.execute("SELECT postcode_id, osm_id, country_id, main, "
              + ft.location_printer("location") + " as location "
                                                  "FROM postcode "
                                                  "WHERE lower(main)=%(main)s "
                                                  "AND country_id=%(us_id)s",
              dict(main=ft.split[i], us_id=us_id))

    cols_map = ft.queryier.mk_cols_map(c)
    for cnd in c.fetchall():
        postcode_id = cnd[cols_map["postcode_id"]]
        country_id = cnd[cols_map["country_id"]]
        pp = pp_place_id(ft, cnd[cols_map["main"]], postcode_id)

        if us_id != ft.host_country_id:
            pp = "{0}, {1}".format(pp, ft.queryier.country_name_id(ft, country_id))

        match = Results.RPost_Code(postcode_id, cnd[cols_map["osm_id"]], country_id, cnd[cols_map["location"]], pp)
        yield match, i - 1


def pp_place_id(ft, pp, postcode_id):

    c = ft.db.cursor()

    c.execute("SELECT parent_id FROM postcode WHERE postcode_id=%(id)s", dict(id=postcode_id))
    parent_id = c.fetchone()[0]

    if parent_id is not None:
        pp = "{0}, {1}".format(pp, ft.queryier.pp_place_id(ft, parent_id))

    return pp

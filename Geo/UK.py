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


_RE_UK_PARTIAL_POSTCODE = re.compile(
    "^((?:[a-z][0-9])|(?:[a-z][0-9][0-9])|(?:[a-z][0-9][a-z])|(?:[a-z][a-z][0-9])|(?:[a-z][a-z][0-9][0-9])|(?:[a-z][a-z][0-9][a-z]))$",
    re.I)

_RE_UK_FULL_POSTCODE = re.compile(
    "^((?:[a-z][0-9])|(?:[a-z][0-9][0-9])|(?:[a-z][0-9][a-z])|(?:[a-z][a-z][0-9])|(?:[a-z][a-z][0-9][0-9])|(?:[a-z][a-z][0-9][a-z])) *([0-9][a-z][a-z])?$",
    re.I)

# Not all UK postcodes belong to GB (Isle of Man for example)
_UK_CODES = ["GB", "IM", "GY", "JE", "AI", "IO", "FK", "GI", "PN", "GS", "SH", "TC"]


def postcode_match(ft, i):
    assert i > -1
    ids = [ft.queryier.get_country_id_from_iso2(ft, code) for code in _UK_CODES]

    m = _RE_UK_PARTIAL_POSTCODE.match(ft.split[i])
    if m is not None:
        # We got something that looks as if it might plausibly be the solitary first half of a
        # postcode (e.g. AA9A), so try matching it on its own.

        c = ft.db.cursor()
        c.execute(("SELECT postcode_id, osm_id, country_id, main, "
                   + ft.location_printer("location") + " as location "
                                                       "FROM postcode "
                                                       "WHERE country_id IN %(ids)s "
                                                       "AND lower(main)=%(main)s "
                                                       "AND sup IS NULL"
                      ),
                  dict(ids=tuple(ids), main=ft.split[i]))

        if c.rowcount == 0:
            # Since we couldn't find AA9A on its own, see if there are any postcodes with an
            # arbitrary supplementary (e.g. AA9A 2AA). This is likely to return multiple matches
            # if AA9A is a valid postcode.
            c.execute("SELECT postcode_id, osm_id, country_id, main, "
                      + ft.location_printer("location") + " as location "
                                                          "FROM postcode "
                                                          "WHERE country_id IN %(ids)s "
                                                          "AND lower(main)=%(main)s",
                      dict(ids=tuple(ids), main=ft.split[i]))

        if c.rowcount > 0:
            # We might have got multiple matches, in which case we arbitrarily pick the first one.
            cols_map = ft.queryier.mk_cols_map(c)
            fst = c.fetchone()
            pp = pp_place_id(ft, fst[cols_map["main"]], fst[cols_map["postcode_id"]])
            match = Results.RPost_Code(fst[cols_map["postcode_id"]], fst[cols_map["osm_id"]],
                                       fst[cols_map["country_id"]], fst[cols_map["location"]],
                                       pp)
            yield match, i - 1

    if i == 0:
        # If we were at the beginning of the split and nothing above matched, then there's no chance
        # of matching anything hereon in.
        return

    # OK, we're now going to try and match a "full postcode" (e.g. of the form SW1 2AA). Before we
    # bother trying to do that, we see if the two contributing elements of the split look like they
    # could be a valid postcode. If they don't, then there's no point in going any further.

    main = ft.split[i - 1]
    sup = ft.split[i]
    m = _RE_UK_FULL_POSTCODE.match("{0:>s} {1:>s}".format(main, sup))

    if m is None:
        return

    # We now try and match a "full postcode" (e.g. of the form SW1 2AA). Because we only have partial
    # UK postcode data, we first of all try matching exactly what is given, gradually backing off if
    # that isn't possible. Since all of these matches are against the same string, as soon as we find
    # a match, we don't try searching any further.
    c = ft.db.cursor()
    c.execute(("SELECT postcode_id, osm_id, country_id, main, sup, "
               + ft.location_printer("location") + " as location "
                                                   "FROM postcode "
                                                   "WHERE country_id IN %(ids)s "
                                                   "AND lower(main)=%(main)s "
                                                   "AND lower(sup)=%(sup)s"
                  ),
              dict(ids=tuple(ids), main=ft.split[i - 1], sup=ft.split[i]))

    assert c.rowcount < 2

    if c.rowcount == 1:
        cols_map = ft.queryier.mk_cols_map(c)
        fst = c.fetchone()
        pp = pp_place_id(ft, "{0:>s} {1:>s}".format(fst[cols_map["main"]], fst[cols_map["sup"]]),
                         fst[cols_map["postcode_id"]])
        match = Results.RPost_Code(fst[cols_map["postcode_id"]], fst[cols_map["osm_id"]], fst[cols_map["country_id"]],
                                   fst[cols_map["location"]], pp)
        yield match, i - 2
        return

    # Try matching the main part of the postcode and the first character of the supplementary
    # part. e.g. for AA9A 9AA try matching AA9A 9.

    c = ft.db.cursor()
    c.execute(("SELECT postcode_id, osm_id, country_id, main, sup, "
               + ft.location_printer("location") + " as location "
                                                   "FROM postcode "
                                                   "WHERE country_id IN %(ids)s "
                                                   "AND lower(main)=%(main)s "
                                                   "AND lower(sup)=%(sup0)s"
                  ),
              dict(ids=tuple(ids), main=ft.split[i - 1], sup0=ft.split[i][0]))

    assert c.rowcount < 2

    if c.rowcount == 1:
        cols_map = ft.queryier.mk_cols_map(c)
        fst = c.fetchone()
        pp = pp_place_id(ft, "{0:>s} {1:>s}".format(fst[cols_map["main"]], fst[cols_map["sup"]][0]),
                         fst[cols_map["postcode_id"]])
        match = Results.RPost_Code(fst[cols_map["postcode_id"]], fst[cols_map["osm_id"]], fst[cols_map["country_id"]],
                                   fst[cols_map["location"]], pp)
        yield match, i - 2
        return

    # Now we're struggling - try matching the main part of the postcode and ignore the supplementary
    # part. This will probably return multiple matches.

    c = ft.db.cursor()
    c.execute("SELECT postcode_id, osm_id, country_id, main, "
              + ft.location_printer("location") + " as location "
                                                  "FROM postcode "
                                                  "WHERE country_id IN %(ids)s "
                                                  "AND lower(main)=%(main)s",
              dict(ids=tuple(ids), main=ft.split[i - 1]))

    if c.rowcount != 0:
        cols_map = ft.queryier.mk_cols_map(c)
        fst = c.fetchone() # Arbitrarily pick the first result.
        postcode_id = fst[cols_map["postcode_id"]]
        country_id = fst[cols_map["country_id"]]
        pp = pp_place_id(ft, fst[cols_map["main"]], postcode_id)
        match = Results.RPost_Code(postcode_id, fst[cols_map["osm_id"]], country_id,
                                   fst[cols_map["location"]], pp)
        yield match, i - 2


def pp_place_id(ft, pp, postcode_id):
    c = ft.db.cursor()

    c.execute("SELECT parent_id FROM postcode WHERE postcode_id=%(id)s", dict(id=postcode_id))
    parent_id = c.fetchone()[0]

    if parent_id is not None:
        pp = "{0:>s}, {1:>s}".format(pp, ft.queryier.pp_place_id(ft, parent_id))

    return pp
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


from .import Free_Text, Temp_Cache

# Here we set a custom set of parents to be added to the pretty print.
# http://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative might help choosing which levels we need for
# each country.
_ADMIN_LEVELS = {"LU": (2, 6, 8), "GB": (2, 4, 6, 8)}
_DEFAULT_LEVEL = (2, 4, 6, 8)


class Queryier:
    def __init__(self):
        self.flush_caches()


    def flush_caches(self):
        self.country_id_iso2_cache = {} # These are both too small
        self.country_iso2_id_cache = {} # to bother with a cached dict.
        self.country_name_cache = {}
        self.place_cache = Temp_Cache.Cached_Dict(Temp_Cache.LARGE_CACHE_SIZE)
        self.place_name_cache = Temp_Cache.Cached_Dict(Temp_Cache.LARGE_CACHE_SIZE)
        self.place_pp_cache = Temp_Cache.Cached_Dict(Temp_Cache.LARGE_CACHE_SIZE)
        self.parent_cache = Temp_Cache.Cached_Dict(Temp_Cache.LARGE_CACHE_SIZE)
        self.results_cache = Temp_Cache.Cached_Dict(Temp_Cache.SMALL_CACHE_SIZE)


    def name_to_lat_long(self, db, lang_ids, find_all, allow_dangling, show_area, qs, host_country_id):
        return Free_Text.Free_Text().name_to_lat_long(self, db, lang_ids, find_all, allow_dangling, show_area,
                                                      qs, host_country_id)


    #
    # Convenience methods
    #

    def mk_cols_map(self, c):
        map = {}
        i = 0
        for col in c.description:
            assert col[0] not in map
            map[col[0]] = i
            i += 1

        return map


    def get_country_id_from_iso2(self, ft, iso2):
        if not iso2:
            return None

        if iso2 not in self.country_id_iso2_cache:
            c = ft.db.cursor()
            c.execute("SELECT country_id FROM country WHERE iso3166_2=%(iso2)s", dict(iso2=iso2))
            assert c.rowcount == 1
            self.country_id_iso2_cache[iso2] = c.fetchone()[0]

        return self.country_id_iso2_cache[iso2]


    def get_country_iso2_from_id(self, ft, country_id):
        if not country_id:
            return None

        if country_id not in self.country_iso2_id_cache:
            c = ft.db.cursor()
            c.execute("SELECT iso3166_2 FROM country WHERE country_id=%(id)s", dict(id=country_id))
            assert c.rowcount == 1
            self.country_iso2_id_cache[country_id] = c.fetchone()[0]

        return self.country_iso2_id_cache[country_id]


    def country_name_id(self, ft, country_id):
        if not country_id:
            return None

        cache_key = (ft.lang_ids[0], country_id)
        if cache_key in self.country_name_cache:
            return self.country_name_cache[cache_key]

        c = ft.db.cursor()

        c.execute(("SELECT place_name.name "
                   "FROM place_name, place "
                   "WHERE place.place_id=place_name.place_id "
                   "AND place.country_id=%(country_id)s "
                   "AND place_name.lang_id IN %(lang_id)s "
                   "AND place.type_id=%(type_id)s"
                      ),
                  dict(country_id=country_id, lang_id=tuple(ft.lang_ids), type_id=self.get_type_id(ft.db, "country")))

        if c.rowcount < 1:
            c.execute("SELECT name FROM country WHERE country_id=%(country_id)s", dict(country_id=country_id))

        name = c.fetchone()[0]

        self.country_name_cache[cache_key] = name

        return name

    def get_type_id(self, db, type):
        c = db.cursor()
        c.execute("SELECT type_id FROM type WHERE name=%(type)s", dict(type=type))
        if c.rowcount == 1:
            return c.fetchone()[0]
        return None


    def name_place_id(self, ft, place_id):
        cache_key = (tuple(ft.lang_ids), ft.host_country_id, place_id)
        if self.place_name_cache.has_key(cache_key):
            return self.place_name_cache[cache_key]

        c = ft.db.cursor()

        c.execute("SELECT name FROM place_name WHERE place_id=%(place_id)s AND lang_id IN %(lang_id)s",
                  dict(place_id=place_id, lang_id=tuple(ft.lang_ids)))

        if c.rowcount > 0:
            name = c.fetchone()[0]
            self.place_name_cache[cache_key] = name
            return name

        # We couldn't find anything in the required languages.

        c.execute("SELECT name FROM place_name WHERE place_id=%(place_id)s", dict(place_id=place_id))

        name = c.fetchone()[0]
        self.place_name_cache[cache_key] = name

        return name


    def pp_place_id(self, ft, place_id):
        cache_key = (tuple(ft.lang_ids), ft.host_country_id, place_id)
        if self.place_pp_cache.has_key(cache_key):
            return self.place_pp_cache[cache_key]

        c = ft.db.cursor()

        pp = self.name_place_id(ft, place_id)

        c.execute("SELECT parent_id, country_id, admin_level from place WHERE place_id=%(id)s", dict(id=place_id))
        assert c.rowcount == 1

        parent_id, country_id, admin_level = c.fetchone()

        iso2 = self.get_country_iso2_from_id(ft, country_id)
        if iso2 in _ADMIN_LEVELS:
            format = _ADMIN_LEVELS[iso2]
        else:
            format = _DEFAULT_LEVEL

        while parent_id is not None:
            c.execute("SELECT parent_id, admin_level from place WHERE place_id=%(id)s", dict(id=parent_id))
            new_parent_id, admin_level = c.fetchone()
            assert(new_parent_id != parent_id)

            if admin_level in format:
                pp = "{0}, {1}".format(pp, self.name_place_id(ft, parent_id))

            parent_id = new_parent_id

        self.place_pp_cache[cache_key] = pp

        return pp
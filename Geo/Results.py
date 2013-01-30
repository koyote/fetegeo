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


class Result:
    def __init__(self, ri, dangling):
        self.ri = ri
        self.dangling = dangling


    def to_xml(self):
        return ("<result>\n"
                "{0}\n"
                "<dangling>{1}</dangling>\n"
                "</result>"
            ).format(self.ri.to_xml(), self.dangling)


class RCountry:
    def __init__(self, id, name, pp):
        self.id = id
        self.name = name
        self.pp = pp


    def to_xml(self):
        return ("<country>\n"
                "<id>{0}</id>\n"
                "<name>{1}</name>\n"
                "<pp>{2}</pp>\n"
                "</country>"
            ).format(self.id, self.name, self.pp)


class RPlace:
    def __init__(self, id, name, location, country_id, parent_id, population, pp):
        self.id = id
        self.name = name
        self.location = location
        self.country_id = country_id
        self.parent_id = parent_id
        self.population = population
        self.pp = pp

    def to_xml(self):
        #if self.location is not None:
        #    location_txt = "\n<lat>%s</lat>" % str(self.location)
        #else:
        location_txt = "\n<location>{0:>s}</location>".format(str(self.location))

        if self.parent_id is not None:
            parent_id_txt = "\n<parent_id>{0:>s}</parent_id>".format(str(self.parent_id))
        else:
            parent_id_txt = ""

        if self.population is not None:
            population_txt = "\n<population>{0:>s}</population>".format(str(self.population))
        else:
            population_txt = ""

        return ("<place>\n"
                "<id>{0}</id>\n"
                "<name>{1}</name>{2}\n"
                "<country_id>{3}</country_id>{4}{5}\n"
                "<pp>{6}</pp>\n"
                "</place>"
            ).format(self.id, self.name, location_txt, self.country_id, parent_id_txt, population_txt, self.pp)


class RPost_Code:
    def __init__(self, id, country_id, location, pp):
        self.id = id
        self.country_id = country_id
        self.location = location
        self.pp = pp
        self.dangling = ""


    def to_xml(self):
        return ("<postcode>\n"
                "<id>{0}</id>\n"
                "<country_id>{1}</country_id>\n"
                "<location>{2}</location>\n"
                "<pp>{3}</pp>\n"
                "</postcode>"
            ).format(self.id, str(self.country_id), str(self.location), self.pp)
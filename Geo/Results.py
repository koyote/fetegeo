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
        return u"""<result>
%s
<dangling>%s</dangling>
</result>""" % (self.ri.to_xml(), self.dangling)


class RCountry:
    def __init__(self, id, name, pp):
        self.id = id
        self.name = name
        self.pp = pp


    def to_xml(self):
        return u"""<country>
<id>%s</id>
<name>%s</name>
<pp>%s</pp>
</country>""" % (self.id, self.name, self.pp)


class RPlace:
    def __init__(self, id, name, location, country_id, parent_id, population, pp):
        self.id = id
        self.name = name
        self.location = location
        self.country_id = country_id
        self.parent_id = parent_id
        self.population = population
        self.pp = pp

    #TODO: FIX LOCATION TO BE DISPLAYED PROPERLY

    def to_xml(self):
        #if self.location is not None:
        #    location_txt = "\n<lat>%s</lat>" % str(self.location)
        #else:
        location_txt = ""

        if self.parent_id is not None:
            parent_id_txt = "\n<parent_id>%s</parent_id>" % str(self.parent_id)
        else:
            parent_id_txt = ""

        if self.population is not None:
            population_txt = "\n<population>%s</population>" % str(self.population)
        else:
            population_txt = ""

        return u"""<place>
<id>%d</id>
<name>%s</name>%s
<country_id>%s</country_id>%s%s
<pp>%s</pp>
</place>""" % (self.id, self.name, location_txt, self.country_id,
               parent_id_txt, population_txt, self.pp)


class RPost_Code:
    def __init__(self, id, country_id, location, pp):
        self.id = id
        self.country_id = country_id
        self.location = location
        self.pp = pp
        self.dangling = ""


    def to_xml(self):
        return u"""<postcode>
<id>%d</id>
<country_id>%s</country_id>
<location>%s</location>
<pp>%s</pp>
</postcode>""" % (self.id, str(self.country_id), str(self.location), self.pp)
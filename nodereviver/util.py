'''
    This file is part of nodereviver

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    @author: Vincent Petry <PVince81@yahoo.fr>
'''
def unitVector(vector):
    if vector[0] != 0:
        return (vector[0] / abs(vector[0]), 0)
    elif vector[1] != 0:
        return (0, vector[1] / abs(vector[1]))
    return (0, 0)

def vectorAdd(vector1, vector2):
    return (vector1[0] + vector2[0], vector1[1] + vector2[1])

def vectorDiff(vector1, vector2):
    return (vector1[0] - vector2[0], vector1[1] - vector2[1])

def vectorMult(vector1, vector2):
    return (vector1[0] * vector2[0], vector1[1] * vector2[1])

def vectorFactor(vector1, factor):
    return (vector1[0] * factor, vector1[1] * factor)

def vectorSwap(vector1):
    return (vector1[1], vector1[0])

def between(value, rangeStart, rangeEnd):
    if rangeStart > rangeEnd:
        aux = rangeEnd
        rangeEnd = rangeStart
        rangeStart = aux
    return rangeStart < value and value < rangeEnd

def makeTimeString(elapsed):
    s = ""
    minutes = elapsed / 60
    seconds = elapsed % 60
    hours = minutes / 60
    minutes = minutes % 60
    if hours > 0:
        s = "%i hour" % hours
        if hours > 1:
            s += "s"
        s += " "
    if minutes > 0:
        s += "%i minute" % minutes
        if minutes > 1:
            s += "s"
        s += " "
    s += "%i second" % seconds
    if seconds > 0:
        s += "s"
    return s

"""
Utility for calculating distance
"""
import math

class DistanceCalc(object):
    @staticmethod
    def distance(v1, v2):
        return math.sqrt(DistanceCalc.length_squared(v1, v2))
    @staticmethod
    def length_squared(v1, v2):
        return (v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2
    @staticmethod
    def diff(v1, v2):
        return [v1[0] - v2[0], v1[1] - v2[1]]
    @staticmethod
    def add(v1, v2):
        return [v1[0] + v2[0], v1[1] + v2[1]]
    @staticmethod
    def dot(v1, v2):
        return v1[0] * v2[0] + v1[1] * v2[1]
    @staticmethod
    def times(num, v):
        return map(lambda x: x * num, v)

    @staticmethod
    def minimum_distance(v, w, p):
        line_length = DistanceCalc.distance(v, w)
        p_len = DistanceCalc.dot(DistanceCalc.diff(p, v), DistanceCalc.diff(w, v)) / line_length
        if (p_len < 0):
            return DistanceCalc.distance(p, v)
        elif (p_len > line_length):
            return DistanceCalc.distance(p, w)
        else:
            projection = DistanceCalc.add(v, DistanceCalc.times(p_len / line_length, DistanceCalc.diff(w, v)))
            return DistanceCalc.distance(projection, p)

    @staticmethod
    def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

# Generated from OliviaPKParser.g4 by ANTLR 4.13.0
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,72,684,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,1,0,3,0,62,8,0,1,0,1,0,1,0,1,0,1,0,
        1,0,1,0,1,0,5,0,72,8,0,10,0,12,0,75,9,0,1,0,1,0,1,1,1,1,5,1,81,8,
        1,10,1,12,1,84,9,1,1,1,1,1,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,
        2,1,2,1,2,3,2,100,8,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,
        2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,
        2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,4,2,138,8,2,11,2,12,2,139,
        1,2,1,2,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,1,3,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,
        1,4,1,4,3,4,176,8,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,
        1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,
        1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,
        1,4,1,4,4,4,223,8,4,11,4,12,4,224,1,4,1,4,1,5,1,5,1,5,1,5,1,5,1,
        5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,
        5,1,5,1,5,1,5,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,3,
        6,266,8,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,
        6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,
        6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,
        6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,4,6,322,8,6,11,6,12,6,323,1,6,
        1,6,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,
        1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,8,
        1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,
        1,8,1,8,1,8,3,8,378,8,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,
        1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,
        1,8,1,8,4,8,408,8,8,11,8,12,8,409,1,8,1,8,1,9,1,9,1,9,1,9,1,9,1,
        9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,10,1,
        10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,
        10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,3,10,458,8,10,1,
        10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,
        10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,
        10,1,10,1,10,1,10,1,10,1,10,1,10,4,10,493,8,10,11,10,12,10,494,1,
        10,1,10,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,
        11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,11,1,
        11,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,
        12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,
        12,1,12,1,12,3,12,552,8,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,
        12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,
        12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,
        12,1,12,1,12,1,12,1,12,4,12,592,8,12,11,12,12,12,593,1,12,1,12,1,
        13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,
        13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,
        13,1,13,1,13,1,13,1,14,1,14,1,14,1,15,1,15,1,15,1,16,1,16,1,16,1,
        17,1,17,1,17,1,18,1,18,1,18,1,18,1,19,1,19,1,19,1,19,1,20,1,20,1,
        20,1,20,1,21,1,21,1,21,1,21,1,22,1,22,1,22,1,22,1,22,1,23,1,23,1,
        23,1,23,1,23,1,24,1,24,1,24,1,24,1,24,1,25,1,25,1,25,1,25,1,25,1,
        26,1,26,1,27,1,27,1,28,1,28,1,29,1,29,1,29,0,0,30,0,2,4,6,8,10,12,
        14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,
        58,0,6,1,1,72,72,1,0,28,30,2,0,6,6,15,15,1,0,6,7,1,0,7,9,1,0,13,
        15,687,0,61,1,0,0,0,2,78,1,0,0,0,4,87,1,0,0,0,6,143,1,0,0,0,8,163,
        1,0,0,0,10,228,1,0,0,0,12,253,1,0,0,0,14,327,1,0,0,0,16,357,1,0,
        0,0,18,413,1,0,0,0,20,433,1,0,0,0,22,498,1,0,0,0,24,523,1,0,0,0,
        26,597,1,0,0,0,28,627,1,0,0,0,30,630,1,0,0,0,32,633,1,0,0,0,34,636,
        1,0,0,0,36,639,1,0,0,0,38,643,1,0,0,0,40,647,1,0,0,0,42,651,1,0,
        0,0,44,655,1,0,0,0,46,660,1,0,0,0,48,665,1,0,0,0,50,670,1,0,0,0,
        52,675,1,0,0,0,54,677,1,0,0,0,56,679,1,0,0,0,58,681,1,0,0,0,60,62,
        5,17,0,0,61,60,1,0,0,0,61,62,1,0,0,0,62,73,1,0,0,0,63,72,3,2,1,0,
        64,72,3,4,2,0,65,72,3,8,4,0,66,72,3,12,6,0,67,72,3,16,8,0,68,72,
        3,20,10,0,69,72,3,24,12,0,70,72,5,17,0,0,71,63,1,0,0,0,71,64,1,0,
        0,0,71,65,1,0,0,0,71,66,1,0,0,0,71,67,1,0,0,0,71,68,1,0,0,0,71,69,
        1,0,0,0,71,70,1,0,0,0,72,75,1,0,0,0,73,71,1,0,0,0,73,74,1,0,0,0,
        74,76,1,0,0,0,75,73,1,0,0,0,76,77,5,0,0,1,77,1,1,0,0,0,78,82,5,10,
        0,0,79,81,5,70,0,0,80,79,1,0,0,0,81,84,1,0,0,0,82,80,1,0,0,0,82,
        83,1,0,0,0,83,85,1,0,0,0,84,82,1,0,0,0,85,86,7,0,0,0,86,3,1,0,0,
        0,87,88,5,1,0,0,88,89,5,20,0,0,89,90,5,27,0,0,90,91,5,2,0,0,91,92,
        7,1,0,0,92,93,5,32,0,0,93,94,5,3,0,0,94,99,5,33,0,0,95,100,3,28,
        14,0,96,100,3,30,15,0,97,100,3,32,16,0,98,100,3,34,17,0,99,95,1,
        0,0,0,99,96,1,0,0,0,99,97,1,0,0,0,99,98,1,0,0,0,100,101,1,0,0,0,
        101,102,5,42,0,0,102,103,5,43,0,0,103,104,5,44,0,0,104,105,5,45,
        0,0,105,106,5,49,0,0,106,107,5,53,0,0,107,108,5,57,0,0,108,109,5,
        46,0,0,109,110,5,50,0,0,110,111,5,54,0,0,111,112,5,58,0,0,112,113,
        5,61,0,0,113,114,5,62,0,0,114,115,5,63,0,0,115,116,5,64,0,0,116,
        117,5,66,0,0,117,118,5,67,0,0,118,119,5,67,0,0,119,120,5,67,0,0,
        120,121,5,67,0,0,121,122,5,67,0,0,122,123,5,67,0,0,123,124,5,67,
        0,0,124,125,5,67,0,0,125,126,5,67,0,0,126,127,5,67,0,0,127,128,5,
        67,0,0,128,129,5,67,0,0,129,130,5,67,0,0,130,131,5,67,0,0,131,132,
        5,67,0,0,132,133,5,67,0,0,133,134,5,67,0,0,134,135,5,67,0,0,135,
        137,5,69,0,0,136,138,3,6,3,0,137,136,1,0,0,0,138,139,1,0,0,0,139,
        137,1,0,0,0,139,140,1,0,0,0,140,141,1,0,0,0,141,142,5,4,0,0,142,
        5,1,0,0,0,143,144,5,7,0,0,144,145,3,56,28,0,145,146,3,56,28,0,146,
        147,3,56,28,0,147,148,3,56,28,0,148,149,3,56,28,0,149,150,3,52,26,
        0,150,151,3,52,26,0,151,152,3,54,27,0,152,153,3,52,26,0,153,154,
        3,52,26,0,154,155,3,52,26,0,155,156,3,54,27,0,156,157,3,52,26,0,
        157,158,5,7,0,0,158,159,5,7,0,0,159,160,3,58,29,0,160,161,5,7,0,
        0,161,162,5,17,0,0,162,7,1,0,0,0,163,164,5,1,0,0,164,165,5,21,0,
        0,165,166,5,27,0,0,166,167,5,2,0,0,167,168,7,1,0,0,168,169,5,32,
        0,0,169,170,5,3,0,0,170,175,5,33,0,0,171,176,3,36,18,0,172,176,3,
        38,19,0,173,176,3,40,20,0,174,176,3,42,21,0,175,171,1,0,0,0,175,
        172,1,0,0,0,175,173,1,0,0,0,175,174,1,0,0,0,176,177,1,0,0,0,177,
        178,5,42,0,0,178,179,5,43,0,0,179,180,5,44,0,0,180,181,5,45,0,0,
        181,182,5,49,0,0,182,183,5,53,0,0,183,184,5,57,0,0,184,185,5,46,
        0,0,185,186,5,50,0,0,186,187,5,54,0,0,187,188,5,58,0,0,188,189,5,
        47,0,0,189,190,5,51,0,0,190,191,5,55,0,0,191,192,5,59,0,0,192,193,
        5,61,0,0,193,194,5,62,0,0,194,195,5,63,0,0,195,196,5,64,0,0,196,
        197,5,66,0,0,197,198,5,67,0,0,198,199,5,67,0,0,199,200,5,67,0,0,
        200,201,5,67,0,0,201,202,5,67,0,0,202,203,5,67,0,0,203,204,5,67,
        0,0,204,205,5,67,0,0,205,206,5,67,0,0,206,207,5,67,0,0,207,208,5,
        67,0,0,208,209,5,67,0,0,209,210,5,67,0,0,210,211,5,67,0,0,211,212,
        5,67,0,0,212,213,5,67,0,0,213,214,5,67,0,0,214,215,5,67,0,0,215,
        216,5,67,0,0,216,217,5,67,0,0,217,218,5,67,0,0,218,219,5,67,0,0,
        219,220,5,67,0,0,220,222,5,69,0,0,221,223,3,10,5,0,222,221,1,0,0,
        0,223,224,1,0,0,0,224,222,1,0,0,0,224,225,1,0,0,0,225,226,1,0,0,
        0,226,227,5,4,0,0,227,9,1,0,0,0,228,229,5,7,0,0,229,230,3,56,28,
        0,230,231,3,56,28,0,231,232,3,56,28,0,232,233,3,56,28,0,233,234,
        3,56,28,0,234,235,3,56,28,0,235,236,3,52,26,0,236,237,3,52,26,0,
        237,238,3,54,27,0,238,239,3,52,26,0,239,240,3,52,26,0,240,241,3,
        52,26,0,241,242,3,54,27,0,242,243,3,52,26,0,243,244,3,52,26,0,244,
        245,3,52,26,0,245,246,3,54,27,0,246,247,3,52,26,0,247,248,5,7,0,
        0,248,249,5,7,0,0,249,250,3,58,29,0,250,251,5,7,0,0,251,252,5,17,
        0,0,252,11,1,0,0,0,253,254,5,1,0,0,254,255,5,22,0,0,255,256,5,27,
        0,0,256,257,5,2,0,0,257,258,7,1,0,0,258,259,5,32,0,0,259,260,5,3,
        0,0,260,265,5,33,0,0,261,266,3,44,22,0,262,266,3,46,23,0,263,266,
        3,48,24,0,264,266,3,50,25,0,265,261,1,0,0,0,265,262,1,0,0,0,265,
        263,1,0,0,0,265,264,1,0,0,0,266,267,1,0,0,0,267,268,5,42,0,0,268,
        269,5,43,0,0,269,270,5,44,0,0,270,271,5,45,0,0,271,272,5,49,0,0,
        272,273,5,53,0,0,273,274,5,57,0,0,274,275,5,46,0,0,275,276,5,50,
        0,0,276,277,5,54,0,0,277,278,5,58,0,0,278,279,5,47,0,0,279,280,5,
        51,0,0,280,281,5,55,0,0,281,282,5,59,0,0,282,283,5,48,0,0,283,284,
        5,52,0,0,284,285,5,56,0,0,285,286,5,60,0,0,286,287,5,61,0,0,287,
        288,5,62,0,0,288,289,5,63,0,0,289,290,5,64,0,0,290,291,5,66,0,0,
        291,292,5,67,0,0,292,293,5,67,0,0,293,294,5,67,0,0,294,295,5,67,
        0,0,295,296,5,67,0,0,296,297,5,67,0,0,297,298,5,67,0,0,298,299,5,
        67,0,0,299,300,5,67,0,0,300,301,5,67,0,0,301,302,5,67,0,0,302,303,
        5,67,0,0,303,304,5,67,0,0,304,305,5,67,0,0,305,306,5,67,0,0,306,
        307,5,67,0,0,307,308,5,67,0,0,308,309,5,67,0,0,309,310,5,67,0,0,
        310,311,5,67,0,0,311,312,5,67,0,0,312,313,5,67,0,0,313,314,5,67,
        0,0,314,315,5,67,0,0,315,316,5,67,0,0,316,317,5,67,0,0,317,318,5,
        67,0,0,318,319,5,67,0,0,319,321,5,69,0,0,320,322,3,14,7,0,321,320,
        1,0,0,0,322,323,1,0,0,0,323,321,1,0,0,0,323,324,1,0,0,0,324,325,
        1,0,0,0,325,326,5,4,0,0,326,13,1,0,0,0,327,328,5,7,0,0,328,329,3,
        56,28,0,329,330,3,56,28,0,330,331,3,56,28,0,331,332,3,56,28,0,332,
        333,3,56,28,0,333,334,3,56,28,0,334,335,3,56,28,0,335,336,3,52,26,
        0,336,337,3,52,26,0,337,338,3,54,27,0,338,339,3,52,26,0,339,340,
        3,52,26,0,340,341,3,52,26,0,341,342,3,54,27,0,342,343,3,52,26,0,
        343,344,3,52,26,0,344,345,3,52,26,0,345,346,3,54,27,0,346,347,3,
        52,26,0,347,348,3,52,26,0,348,349,3,52,26,0,349,350,3,54,27,0,350,
        351,3,52,26,0,351,352,5,7,0,0,352,353,5,7,0,0,353,354,3,58,29,0,
        354,355,5,7,0,0,355,356,5,17,0,0,356,15,1,0,0,0,357,358,5,1,0,0,
        358,359,5,23,0,0,359,360,5,27,0,0,360,361,5,2,0,0,361,362,7,1,0,
        0,362,363,5,32,0,0,363,364,5,3,0,0,364,365,5,45,0,0,365,366,5,49,
        0,0,366,367,5,53,0,0,367,368,5,57,0,0,368,369,5,46,0,0,369,370,5,
        50,0,0,370,371,5,54,0,0,371,372,5,58,0,0,372,377,5,33,0,0,373,378,
        3,28,14,0,374,378,3,30,15,0,375,378,3,32,16,0,376,378,3,34,17,0,
        377,373,1,0,0,0,377,374,1,0,0,0,377,375,1,0,0,0,377,376,1,0,0,0,
        378,379,1,0,0,0,379,380,5,42,0,0,380,381,5,43,0,0,381,382,5,44,0,
        0,382,383,5,61,0,0,383,384,5,62,0,0,384,385,5,63,0,0,385,386,5,64,
        0,0,386,387,5,66,0,0,387,388,5,67,0,0,388,389,5,67,0,0,389,390,5,
        67,0,0,390,391,5,67,0,0,391,392,5,67,0,0,392,393,5,67,0,0,393,394,
        5,67,0,0,394,395,5,67,0,0,395,396,5,67,0,0,396,397,5,67,0,0,397,
        398,5,67,0,0,398,399,5,67,0,0,399,400,5,67,0,0,400,401,5,67,0,0,
        401,402,5,67,0,0,402,403,5,67,0,0,403,404,5,67,0,0,404,405,5,67,
        0,0,405,407,5,69,0,0,406,408,3,18,9,0,407,406,1,0,0,0,408,409,1,
        0,0,0,409,407,1,0,0,0,409,410,1,0,0,0,410,411,1,0,0,0,411,412,5,
        4,0,0,412,17,1,0,0,0,413,414,3,52,26,0,414,415,3,52,26,0,415,416,
        3,54,27,0,416,417,3,52,26,0,417,418,3,52,26,0,418,419,3,52,26,0,
        419,420,3,54,27,0,420,421,3,52,26,0,421,422,5,7,0,0,422,423,3,56,
        28,0,423,424,3,56,28,0,424,425,3,56,28,0,425,426,3,56,28,0,426,427,
        3,56,28,0,427,428,5,7,0,0,428,429,5,7,0,0,429,430,3,58,29,0,430,
        431,5,7,0,0,431,432,5,17,0,0,432,19,1,0,0,0,433,434,5,1,0,0,434,
        435,5,24,0,0,435,436,5,27,0,0,436,437,5,2,0,0,437,438,7,1,0,0,438,
        439,5,32,0,0,439,440,5,3,0,0,440,441,5,45,0,0,441,442,5,49,0,0,442,
        443,5,53,0,0,443,444,5,57,0,0,444,445,5,46,0,0,445,446,5,50,0,0,
        446,447,5,54,0,0,447,448,5,58,0,0,448,449,5,47,0,0,449,450,5,51,
        0,0,450,451,5,55,0,0,451,452,5,59,0,0,452,457,5,33,0,0,453,458,3,
        36,18,0,454,458,3,38,19,0,455,458,3,40,20,0,456,458,3,42,21,0,457,
        453,1,0,0,0,457,454,1,0,0,0,457,455,1,0,0,0,457,456,1,0,0,0,458,
        459,1,0,0,0,459,460,5,42,0,0,460,461,5,43,0,0,461,462,5,44,0,0,462,
        463,5,61,0,0,463,464,5,62,0,0,464,465,5,63,0,0,465,466,5,64,0,0,
        466,467,5,66,0,0,467,468,5,67,0,0,468,469,5,67,0,0,469,470,5,67,
        0,0,470,471,5,67,0,0,471,472,5,67,0,0,472,473,5,67,0,0,473,474,5,
        67,0,0,474,475,5,67,0,0,475,476,5,67,0,0,476,477,5,67,0,0,477,478,
        5,67,0,0,478,479,5,67,0,0,479,480,5,67,0,0,480,481,5,67,0,0,481,
        482,5,67,0,0,482,483,5,67,0,0,483,484,5,67,0,0,484,485,5,67,0,0,
        485,486,5,67,0,0,486,487,5,67,0,0,487,488,5,67,0,0,488,489,5,67,
        0,0,489,490,5,67,0,0,490,492,5,69,0,0,491,493,3,22,11,0,492,491,
        1,0,0,0,493,494,1,0,0,0,494,492,1,0,0,0,494,495,1,0,0,0,495,496,
        1,0,0,0,496,497,5,4,0,0,497,21,1,0,0,0,498,499,3,52,26,0,499,500,
        3,52,26,0,500,501,3,54,27,0,501,502,3,52,26,0,502,503,3,52,26,0,
        503,504,3,52,26,0,504,505,3,54,27,0,505,506,3,52,26,0,506,507,3,
        52,26,0,507,508,3,52,26,0,508,509,3,54,27,0,509,510,3,52,26,0,510,
        511,5,7,0,0,511,512,3,56,28,0,512,513,3,56,28,0,513,514,3,56,28,
        0,514,515,3,56,28,0,515,516,3,56,28,0,516,517,3,56,28,0,517,518,
        5,7,0,0,518,519,5,7,0,0,519,520,3,58,29,0,520,521,5,7,0,0,521,522,
        5,17,0,0,522,23,1,0,0,0,523,524,5,1,0,0,524,525,5,25,0,0,525,526,
        5,27,0,0,526,527,5,2,0,0,527,528,7,1,0,0,528,529,5,32,0,0,529,530,
        5,3,0,0,530,531,5,45,0,0,531,532,5,49,0,0,532,533,5,53,0,0,533,534,
        5,57,0,0,534,535,5,46,0,0,535,536,5,50,0,0,536,537,5,54,0,0,537,
        538,5,58,0,0,538,539,5,47,0,0,539,540,5,51,0,0,540,541,5,55,0,0,
        541,542,5,59,0,0,542,543,5,48,0,0,543,544,5,52,0,0,544,545,5,56,
        0,0,545,546,5,60,0,0,546,551,5,33,0,0,547,552,3,44,22,0,548,552,
        3,46,23,0,549,552,3,48,24,0,550,552,3,50,25,0,551,547,1,0,0,0,551,
        548,1,0,0,0,551,549,1,0,0,0,551,550,1,0,0,0,552,553,1,0,0,0,553,
        554,5,42,0,0,554,555,5,43,0,0,555,556,5,44,0,0,556,557,5,61,0,0,
        557,558,5,62,0,0,558,559,5,63,0,0,559,560,5,64,0,0,560,561,5,66,
        0,0,561,562,5,67,0,0,562,563,5,67,0,0,563,564,5,67,0,0,564,565,5,
        67,0,0,565,566,5,67,0,0,566,567,5,67,0,0,567,568,5,67,0,0,568,569,
        5,67,0,0,569,570,5,67,0,0,570,571,5,67,0,0,571,572,5,67,0,0,572,
        573,5,67,0,0,573,574,5,67,0,0,574,575,5,67,0,0,575,576,5,67,0,0,
        576,577,5,67,0,0,577,578,5,67,0,0,578,579,5,67,0,0,579,580,5,67,
        0,0,580,581,5,67,0,0,581,582,5,67,0,0,582,583,5,67,0,0,583,584,5,
        67,0,0,584,585,5,67,0,0,585,586,5,67,0,0,586,587,5,67,0,0,587,588,
        5,67,0,0,588,589,5,67,0,0,589,591,5,69,0,0,590,592,3,26,13,0,591,
        590,1,0,0,0,592,593,1,0,0,0,593,591,1,0,0,0,593,594,1,0,0,0,594,
        595,1,0,0,0,595,596,5,4,0,0,596,25,1,0,0,0,597,598,3,52,26,0,598,
        599,3,52,26,0,599,600,3,54,27,0,600,601,3,52,26,0,601,602,3,52,26,
        0,602,603,3,52,26,0,603,604,3,54,27,0,604,605,3,52,26,0,605,606,
        3,52,26,0,606,607,3,52,26,0,607,608,3,54,27,0,608,609,3,52,26,0,
        609,610,3,52,26,0,610,611,3,52,26,0,611,612,3,54,27,0,612,613,3,
        52,26,0,613,614,5,7,0,0,614,615,3,56,28,0,615,616,3,56,28,0,616,
        617,3,56,28,0,617,618,3,56,28,0,618,619,3,56,28,0,619,620,3,56,28,
        0,620,621,3,56,28,0,621,622,5,7,0,0,622,623,5,7,0,0,623,624,3,58,
        29,0,624,625,5,7,0,0,625,626,5,17,0,0,626,27,1,0,0,0,627,628,5,34,
        0,0,628,629,5,35,0,0,629,29,1,0,0,0,630,631,5,35,0,0,631,632,5,34,
        0,0,632,31,1,0,0,0,633,634,5,38,0,0,634,635,5,39,0,0,635,33,1,0,
        0,0,636,637,5,39,0,0,637,638,5,38,0,0,638,35,1,0,0,0,639,640,5,34,
        0,0,640,641,5,35,0,0,641,642,5,36,0,0,642,37,1,0,0,0,643,644,5,36,
        0,0,644,645,5,35,0,0,645,646,5,34,0,0,646,39,1,0,0,0,647,648,5,38,
        0,0,648,649,5,39,0,0,649,650,5,40,0,0,650,41,1,0,0,0,651,652,5,40,
        0,0,652,653,5,39,0,0,653,654,5,38,0,0,654,43,1,0,0,0,655,656,5,34,
        0,0,656,657,5,35,0,0,657,658,5,36,0,0,658,659,5,37,0,0,659,45,1,
        0,0,0,660,661,5,37,0,0,661,662,5,36,0,0,662,663,5,35,0,0,663,664,
        5,34,0,0,664,47,1,0,0,0,665,666,5,38,0,0,666,667,5,39,0,0,667,668,
        5,40,0,0,668,669,5,41,0,0,669,49,1,0,0,0,670,671,5,41,0,0,671,672,
        5,40,0,0,672,673,5,39,0,0,673,674,5,38,0,0,674,51,1,0,0,0,675,676,
        7,2,0,0,676,53,1,0,0,0,677,678,7,3,0,0,678,55,1,0,0,0,679,680,7,
        4,0,0,680,57,1,0,0,0,681,682,7,5,0,0,682,59,1,0,0,0,16,61,71,73,
        82,99,139,175,224,265,323,377,409,457,494,551,593
    ]

class OliviaPKParser ( Parser ):

    grammarFileName = "OliviaPKParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'TYPEDEF'", "'SEPARATOR'", "'FORMAT\\n'", 
                     "'UNFORMAT'", "'EOF'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'REMARK'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "'IDX_TBL_2D'", 
                     "'IDX_TBL_3D'", "'IDX_TBL_4D'", "'ASS_TBL_2D'", "'ASS_TBL_3D'", 
                     "'ASS_TBL_4D'", "<INVALID>", "<INVALID>", "'TAB'", 
                     "'COMMA'", "'SPACE'", "<INVALID>", "<INVALID>", "'INDEX'", 
                     "'X_PPM'", "'Y_PPM'", "'Z_PPM'", "'A_PPM'", "'X_HZ'", 
                     "'Y_HZ'", "'Z_HZ'", "'A_HZ'", "'AMPLITUDE'", "'VOLUME'", 
                     "'VOL_ERR'", "'X_CHAIN'", "'Y_CHAIN'", "'Z_CHAIN'", 
                     "'A_CHAIN'", "'X_RESNAME'", "'Y_RESNAME'", "'Z_RESNAME'", 
                     "'A_RESNAME'", "'X_SEQNUM'", "'Y_SEQNUM'", "'Z_SEQNUM'", 
                     "'A_SEQNUM'", "'X_ASSIGN'", "'Y_ASSIGN'", "'Z_ASSIGN'", 
                     "'A_ASSIGN'", "'EVAL'", "'STATUS'", "'USER_MEMO'", 
                     "'UPDATE_TIME'" ]

    symbolicNames = [ "<INVALID>", "Typedef", "Separator", "Format", "Unformat", 
                      "Eof", "Null_string", "Integer", "Float", "Real", 
                      "COMMENT", "SHARP_COMMENT", "EXCLM_COMMENT", "Double_quote_string", 
                      "Single_quote_string", "Simple_name", "SPACE", "RETURN", 
                      "SECTION_COMMENT", "LINE_COMMENT", "Idx_tbl_2d", "Idx_tbl_3d", 
                      "Idx_tbl_4d", "Ass_tbl_2d", "Ass_tbl_3d", "Ass_tbl_4d", 
                      "SPACE_TD", "RETURN_TD", "Tab", "Comma", "Space", 
                      "SPACE_SE", "RETURN_SE", "Index", "X_ppm", "Y_ppm", 
                      "Z_ppm", "A_ppm", "X_hz", "Y_hz", "Z_hz", "A_hz", 
                      "Amplitude", "Volume", "Vol_err", "X_chain", "Y_chain", 
                      "Z_chain", "A_chain", "X_resname", "Y_resname", "Z_resname", 
                      "A_resname", "X_seqnum", "Y_seqnum", "Z_seqnum", "A_seqnum", 
                      "X_assign", "Y_assign", "Z_assign", "A_assign", "Eval", 
                      "Status", "User_memo", "Update_time", "SPACE_FO", 
                      "RETURN_FO", "Printf_string", "SPACE_PF", "RETURN_PF", 
                      "Any_name", "SPACE_CM", "RETURN_CM" ]

    RULE_olivia_pk = 0
    RULE_comment = 1
    RULE_idx_peak_list_2d = 2
    RULE_idx_peak_2d = 3
    RULE_idx_peak_list_3d = 4
    RULE_idx_peak_3d = 5
    RULE_idx_peak_list_4d = 6
    RULE_idx_peak_4d = 7
    RULE_ass_peak_list_2d = 8
    RULE_ass_peak_2d = 9
    RULE_ass_peak_list_3d = 10
    RULE_ass_peak_3d = 11
    RULE_ass_peak_list_4d = 12
    RULE_ass_peak_4d = 13
    RULE_def_2d_axis_order_ppm = 14
    RULE_tp_2d_axis_order_ppm = 15
    RULE_def_2d_axis_order_hz = 16
    RULE_tp_2d_axis_order_hz = 17
    RULE_def_3d_axis_order_ppm = 18
    RULE_tp_3d_axis_order_ppm = 19
    RULE_def_3d_axis_order_hz = 20
    RULE_tp_3d_axis_order_hz = 21
    RULE_def_4d_axis_order_ppm = 22
    RULE_tp_4d_axis_order_ppm = 23
    RULE_def_4d_axis_order_hz = 24
    RULE_tp_4d_axis_order_hz = 25
    RULE_string = 26
    RULE_integer = 27
    RULE_number = 28
    RULE_memo = 29

    ruleNames =  [ "olivia_pk", "comment", "idx_peak_list_2d", "idx_peak_2d", 
                   "idx_peak_list_3d", "idx_peak_3d", "idx_peak_list_4d", 
                   "idx_peak_4d", "ass_peak_list_2d", "ass_peak_2d", "ass_peak_list_3d", 
                   "ass_peak_3d", "ass_peak_list_4d", "ass_peak_4d", "def_2d_axis_order_ppm", 
                   "tp_2d_axis_order_ppm", "def_2d_axis_order_hz", "tp_2d_axis_order_hz", 
                   "def_3d_axis_order_ppm", "tp_3d_axis_order_ppm", "def_3d_axis_order_hz", 
                   "tp_3d_axis_order_hz", "def_4d_axis_order_ppm", "tp_4d_axis_order_ppm", 
                   "def_4d_axis_order_hz", "tp_4d_axis_order_hz", "string", 
                   "integer", "number", "memo" ]

    EOF = Token.EOF
    Typedef=1
    Separator=2
    Format=3
    Unformat=4
    Eof=5
    Null_string=6
    Integer=7
    Float=8
    Real=9
    COMMENT=10
    SHARP_COMMENT=11
    EXCLM_COMMENT=12
    Double_quote_string=13
    Single_quote_string=14
    Simple_name=15
    SPACE=16
    RETURN=17
    SECTION_COMMENT=18
    LINE_COMMENT=19
    Idx_tbl_2d=20
    Idx_tbl_3d=21
    Idx_tbl_4d=22
    Ass_tbl_2d=23
    Ass_tbl_3d=24
    Ass_tbl_4d=25
    SPACE_TD=26
    RETURN_TD=27
    Tab=28
    Comma=29
    Space=30
    SPACE_SE=31
    RETURN_SE=32
    Index=33
    X_ppm=34
    Y_ppm=35
    Z_ppm=36
    A_ppm=37
    X_hz=38
    Y_hz=39
    Z_hz=40
    A_hz=41
    Amplitude=42
    Volume=43
    Vol_err=44
    X_chain=45
    Y_chain=46
    Z_chain=47
    A_chain=48
    X_resname=49
    Y_resname=50
    Z_resname=51
    A_resname=52
    X_seqnum=53
    Y_seqnum=54
    Z_seqnum=55
    A_seqnum=56
    X_assign=57
    Y_assign=58
    Z_assign=59
    A_assign=60
    Eval=61
    Status=62
    User_memo=63
    Update_time=64
    SPACE_FO=65
    RETURN_FO=66
    Printf_string=67
    SPACE_PF=68
    RETURN_PF=69
    Any_name=70
    SPACE_CM=71
    RETURN_CM=72

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Olivia_pkContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(OliviaPKParser.EOF, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.RETURN)
            else:
                return self.getToken(OliviaPKParser.RETURN, i)

        def comment(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.CommentContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.CommentContext,i)


        def idx_peak_list_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.Idx_peak_list_2dContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.Idx_peak_list_2dContext,i)


        def idx_peak_list_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.Idx_peak_list_3dContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.Idx_peak_list_3dContext,i)


        def idx_peak_list_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.Idx_peak_list_4dContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.Idx_peak_list_4dContext,i)


        def ass_peak_list_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.Ass_peak_list_2dContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.Ass_peak_list_2dContext,i)


        def ass_peak_list_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.Ass_peak_list_3dContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.Ass_peak_list_3dContext,i)


        def ass_peak_list_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.Ass_peak_list_4dContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.Ass_peak_list_4dContext,i)


        def getRuleIndex(self):
            return OliviaPKParser.RULE_olivia_pk

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOlivia_pk" ):
                listener.enterOlivia_pk(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOlivia_pk" ):
                listener.exitOlivia_pk(self)




    def olivia_pk(self):

        localctx = OliviaPKParser.Olivia_pkContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_olivia_pk)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 61
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.state = 60
                self.match(OliviaPKParser.RETURN)


            self.state = 73
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 132098) != 0):
                self.state = 71
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
                if la_ == 1:
                    self.state = 63
                    self.comment()
                    pass

                elif la_ == 2:
                    self.state = 64
                    self.idx_peak_list_2d()
                    pass

                elif la_ == 3:
                    self.state = 65
                    self.idx_peak_list_3d()
                    pass

                elif la_ == 4:
                    self.state = 66
                    self.idx_peak_list_4d()
                    pass

                elif la_ == 5:
                    self.state = 67
                    self.ass_peak_list_2d()
                    pass

                elif la_ == 6:
                    self.state = 68
                    self.ass_peak_list_3d()
                    pass

                elif la_ == 7:
                    self.state = 69
                    self.ass_peak_list_4d()
                    pass

                elif la_ == 8:
                    self.state = 70
                    self.match(OliviaPKParser.RETURN)
                    pass


                self.state = 75
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 76
            self.match(OliviaPKParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CommentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COMMENT(self):
            return self.getToken(OliviaPKParser.COMMENT, 0)

        def RETURN_CM(self):
            return self.getToken(OliviaPKParser.RETURN_CM, 0)

        def EOF(self):
            return self.getToken(OliviaPKParser.EOF, 0)

        def Any_name(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.Any_name)
            else:
                return self.getToken(OliviaPKParser.Any_name, i)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_comment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComment" ):
                listener.enterComment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComment" ):
                listener.exitComment(self)




    def comment(self):

        localctx = OliviaPKParser.CommentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_comment)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 78
            self.match(OliviaPKParser.COMMENT)
            self.state = 82
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==70:
                self.state = 79
                self.match(OliviaPKParser.Any_name)
                self.state = 84
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 85
            _la = self._input.LA(1)
            if not(_la==-1 or _la==72):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Idx_peak_list_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Typedef(self):
            return self.getToken(OliviaPKParser.Typedef, 0)

        def Idx_tbl_2d(self):
            return self.getToken(OliviaPKParser.Idx_tbl_2d, 0)

        def RETURN_TD(self):
            return self.getToken(OliviaPKParser.RETURN_TD, 0)

        def Separator(self):
            return self.getToken(OliviaPKParser.Separator, 0)

        def RETURN_SE(self):
            return self.getToken(OliviaPKParser.RETURN_SE, 0)

        def Format(self):
            return self.getToken(OliviaPKParser.Format, 0)

        def Index(self):
            return self.getToken(OliviaPKParser.Index, 0)

        def Amplitude(self):
            return self.getToken(OliviaPKParser.Amplitude, 0)

        def Volume(self):
            return self.getToken(OliviaPKParser.Volume, 0)

        def Vol_err(self):
            return self.getToken(OliviaPKParser.Vol_err, 0)

        def X_chain(self):
            return self.getToken(OliviaPKParser.X_chain, 0)

        def X_resname(self):
            return self.getToken(OliviaPKParser.X_resname, 0)

        def X_seqnum(self):
            return self.getToken(OliviaPKParser.X_seqnum, 0)

        def X_assign(self):
            return self.getToken(OliviaPKParser.X_assign, 0)

        def Y_chain(self):
            return self.getToken(OliviaPKParser.Y_chain, 0)

        def Y_resname(self):
            return self.getToken(OliviaPKParser.Y_resname, 0)

        def Y_seqnum(self):
            return self.getToken(OliviaPKParser.Y_seqnum, 0)

        def Y_assign(self):
            return self.getToken(OliviaPKParser.Y_assign, 0)

        def Eval(self):
            return self.getToken(OliviaPKParser.Eval, 0)

        def Status(self):
            return self.getToken(OliviaPKParser.Status, 0)

        def User_memo(self):
            return self.getToken(OliviaPKParser.User_memo, 0)

        def Update_time(self):
            return self.getToken(OliviaPKParser.Update_time, 0)

        def RETURN_FO(self):
            return self.getToken(OliviaPKParser.RETURN_FO, 0)

        def Printf_string(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.Printf_string)
            else:
                return self.getToken(OliviaPKParser.Printf_string, i)

        def RETURN_PF(self):
            return self.getToken(OliviaPKParser.RETURN_PF, 0)

        def Unformat(self):
            return self.getToken(OliviaPKParser.Unformat, 0)

        def Tab(self):
            return self.getToken(OliviaPKParser.Tab, 0)

        def Comma(self):
            return self.getToken(OliviaPKParser.Comma, 0)

        def Space(self):
            return self.getToken(OliviaPKParser.Space, 0)

        def def_2d_axis_order_ppm(self):
            return self.getTypedRuleContext(OliviaPKParser.Def_2d_axis_order_ppmContext,0)


        def tp_2d_axis_order_ppm(self):
            return self.getTypedRuleContext(OliviaPKParser.Tp_2d_axis_order_ppmContext,0)


        def def_2d_axis_order_hz(self):
            return self.getTypedRuleContext(OliviaPKParser.Def_2d_axis_order_hzContext,0)


        def tp_2d_axis_order_hz(self):
            return self.getTypedRuleContext(OliviaPKParser.Tp_2d_axis_order_hzContext,0)


        def idx_peak_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.Idx_peak_2dContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.Idx_peak_2dContext,i)


        def getRuleIndex(self):
            return OliviaPKParser.RULE_idx_peak_list_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdx_peak_list_2d" ):
                listener.enterIdx_peak_list_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdx_peak_list_2d" ):
                listener.exitIdx_peak_list_2d(self)




    def idx_peak_list_2d(self):

        localctx = OliviaPKParser.Idx_peak_list_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_idx_peak_list_2d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 87
            self.match(OliviaPKParser.Typedef)
            self.state = 88
            self.match(OliviaPKParser.Idx_tbl_2d)
            self.state = 89
            self.match(OliviaPKParser.RETURN_TD)
            self.state = 90
            self.match(OliviaPKParser.Separator)
            self.state = 91
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1879048192) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 92
            self.match(OliviaPKParser.RETURN_SE)
            self.state = 93
            self.match(OliviaPKParser.Format)
            self.state = 94
            self.match(OliviaPKParser.Index)
            self.state = 99
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [34]:
                self.state = 95
                self.def_2d_axis_order_ppm()
                pass
            elif token in [35]:
                self.state = 96
                self.tp_2d_axis_order_ppm()
                pass
            elif token in [38]:
                self.state = 97
                self.def_2d_axis_order_hz()
                pass
            elif token in [39]:
                self.state = 98
                self.tp_2d_axis_order_hz()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 101
            self.match(OliviaPKParser.Amplitude)
            self.state = 102
            self.match(OliviaPKParser.Volume)
            self.state = 103
            self.match(OliviaPKParser.Vol_err)
            self.state = 104
            self.match(OliviaPKParser.X_chain)
            self.state = 105
            self.match(OliviaPKParser.X_resname)
            self.state = 106
            self.match(OliviaPKParser.X_seqnum)
            self.state = 107
            self.match(OliviaPKParser.X_assign)
            self.state = 108
            self.match(OliviaPKParser.Y_chain)
            self.state = 109
            self.match(OliviaPKParser.Y_resname)
            self.state = 110
            self.match(OliviaPKParser.Y_seqnum)
            self.state = 111
            self.match(OliviaPKParser.Y_assign)
            self.state = 112
            self.match(OliviaPKParser.Eval)
            self.state = 113
            self.match(OliviaPKParser.Status)
            self.state = 114
            self.match(OliviaPKParser.User_memo)
            self.state = 115
            self.match(OliviaPKParser.Update_time)
            self.state = 116
            self.match(OliviaPKParser.RETURN_FO)
            self.state = 117
            self.match(OliviaPKParser.Printf_string)
            self.state = 118
            self.match(OliviaPKParser.Printf_string)
            self.state = 119
            self.match(OliviaPKParser.Printf_string)
            self.state = 120
            self.match(OliviaPKParser.Printf_string)
            self.state = 121
            self.match(OliviaPKParser.Printf_string)
            self.state = 122
            self.match(OliviaPKParser.Printf_string)
            self.state = 123
            self.match(OliviaPKParser.Printf_string)
            self.state = 124
            self.match(OliviaPKParser.Printf_string)
            self.state = 125
            self.match(OliviaPKParser.Printf_string)
            self.state = 126
            self.match(OliviaPKParser.Printf_string)
            self.state = 127
            self.match(OliviaPKParser.Printf_string)
            self.state = 128
            self.match(OliviaPKParser.Printf_string)
            self.state = 129
            self.match(OliviaPKParser.Printf_string)
            self.state = 130
            self.match(OliviaPKParser.Printf_string)
            self.state = 131
            self.match(OliviaPKParser.Printf_string)
            self.state = 132
            self.match(OliviaPKParser.Printf_string)
            self.state = 133
            self.match(OliviaPKParser.Printf_string)
            self.state = 134
            self.match(OliviaPKParser.Printf_string)
            self.state = 135
            self.match(OliviaPKParser.RETURN_PF)
            self.state = 137 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 136
                self.idx_peak_2d()
                self.state = 139 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==7):
                    break

            self.state = 141
            self.match(OliviaPKParser.Unformat)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Idx_peak_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.Integer)
            else:
                return self.getToken(OliviaPKParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.NumberContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.NumberContext,i)


        def string(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.StringContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.StringContext,i)


        def integer(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.IntegerContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.IntegerContext,i)


        def memo(self):
            return self.getTypedRuleContext(OliviaPKParser.MemoContext,0)


        def RETURN(self):
            return self.getToken(OliviaPKParser.RETURN, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_idx_peak_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdx_peak_2d" ):
                listener.enterIdx_peak_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdx_peak_2d" ):
                listener.exitIdx_peak_2d(self)




    def idx_peak_2d(self):

        localctx = OliviaPKParser.Idx_peak_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_idx_peak_2d)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 143
            self.match(OliviaPKParser.Integer)
            self.state = 144
            self.number()
            self.state = 145
            self.number()
            self.state = 146
            self.number()
            self.state = 147
            self.number()
            self.state = 148
            self.number()
            self.state = 149
            self.string()
            self.state = 150
            self.string()
            self.state = 151
            self.integer()
            self.state = 152
            self.string()
            self.state = 153
            self.string()
            self.state = 154
            self.string()
            self.state = 155
            self.integer()
            self.state = 156
            self.string()
            self.state = 157
            self.match(OliviaPKParser.Integer)
            self.state = 158
            self.match(OliviaPKParser.Integer)
            self.state = 159
            self.memo()
            self.state = 160
            self.match(OliviaPKParser.Integer)
            self.state = 161
            self.match(OliviaPKParser.RETURN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Idx_peak_list_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Typedef(self):
            return self.getToken(OliviaPKParser.Typedef, 0)

        def Idx_tbl_3d(self):
            return self.getToken(OliviaPKParser.Idx_tbl_3d, 0)

        def RETURN_TD(self):
            return self.getToken(OliviaPKParser.RETURN_TD, 0)

        def Separator(self):
            return self.getToken(OliviaPKParser.Separator, 0)

        def RETURN_SE(self):
            return self.getToken(OliviaPKParser.RETURN_SE, 0)

        def Format(self):
            return self.getToken(OliviaPKParser.Format, 0)

        def Index(self):
            return self.getToken(OliviaPKParser.Index, 0)

        def Amplitude(self):
            return self.getToken(OliviaPKParser.Amplitude, 0)

        def Volume(self):
            return self.getToken(OliviaPKParser.Volume, 0)

        def Vol_err(self):
            return self.getToken(OliviaPKParser.Vol_err, 0)

        def X_chain(self):
            return self.getToken(OliviaPKParser.X_chain, 0)

        def X_resname(self):
            return self.getToken(OliviaPKParser.X_resname, 0)

        def X_seqnum(self):
            return self.getToken(OliviaPKParser.X_seqnum, 0)

        def X_assign(self):
            return self.getToken(OliviaPKParser.X_assign, 0)

        def Y_chain(self):
            return self.getToken(OliviaPKParser.Y_chain, 0)

        def Y_resname(self):
            return self.getToken(OliviaPKParser.Y_resname, 0)

        def Y_seqnum(self):
            return self.getToken(OliviaPKParser.Y_seqnum, 0)

        def Y_assign(self):
            return self.getToken(OliviaPKParser.Y_assign, 0)

        def Z_chain(self):
            return self.getToken(OliviaPKParser.Z_chain, 0)

        def Z_resname(self):
            return self.getToken(OliviaPKParser.Z_resname, 0)

        def Z_seqnum(self):
            return self.getToken(OliviaPKParser.Z_seqnum, 0)

        def Z_assign(self):
            return self.getToken(OliviaPKParser.Z_assign, 0)

        def Eval(self):
            return self.getToken(OliviaPKParser.Eval, 0)

        def Status(self):
            return self.getToken(OliviaPKParser.Status, 0)

        def User_memo(self):
            return self.getToken(OliviaPKParser.User_memo, 0)

        def Update_time(self):
            return self.getToken(OliviaPKParser.Update_time, 0)

        def RETURN_FO(self):
            return self.getToken(OliviaPKParser.RETURN_FO, 0)

        def Printf_string(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.Printf_string)
            else:
                return self.getToken(OliviaPKParser.Printf_string, i)

        def RETURN_PF(self):
            return self.getToken(OliviaPKParser.RETURN_PF, 0)

        def Unformat(self):
            return self.getToken(OliviaPKParser.Unformat, 0)

        def Tab(self):
            return self.getToken(OliviaPKParser.Tab, 0)

        def Comma(self):
            return self.getToken(OliviaPKParser.Comma, 0)

        def Space(self):
            return self.getToken(OliviaPKParser.Space, 0)

        def def_3d_axis_order_ppm(self):
            return self.getTypedRuleContext(OliviaPKParser.Def_3d_axis_order_ppmContext,0)


        def tp_3d_axis_order_ppm(self):
            return self.getTypedRuleContext(OliviaPKParser.Tp_3d_axis_order_ppmContext,0)


        def def_3d_axis_order_hz(self):
            return self.getTypedRuleContext(OliviaPKParser.Def_3d_axis_order_hzContext,0)


        def tp_3d_axis_order_hz(self):
            return self.getTypedRuleContext(OliviaPKParser.Tp_3d_axis_order_hzContext,0)


        def idx_peak_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.Idx_peak_3dContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.Idx_peak_3dContext,i)


        def getRuleIndex(self):
            return OliviaPKParser.RULE_idx_peak_list_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdx_peak_list_3d" ):
                listener.enterIdx_peak_list_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdx_peak_list_3d" ):
                listener.exitIdx_peak_list_3d(self)




    def idx_peak_list_3d(self):

        localctx = OliviaPKParser.Idx_peak_list_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_idx_peak_list_3d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 163
            self.match(OliviaPKParser.Typedef)
            self.state = 164
            self.match(OliviaPKParser.Idx_tbl_3d)
            self.state = 165
            self.match(OliviaPKParser.RETURN_TD)
            self.state = 166
            self.match(OliviaPKParser.Separator)
            self.state = 167
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1879048192) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 168
            self.match(OliviaPKParser.RETURN_SE)
            self.state = 169
            self.match(OliviaPKParser.Format)
            self.state = 170
            self.match(OliviaPKParser.Index)
            self.state = 175
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [34]:
                self.state = 171
                self.def_3d_axis_order_ppm()
                pass
            elif token in [36]:
                self.state = 172
                self.tp_3d_axis_order_ppm()
                pass
            elif token in [38]:
                self.state = 173
                self.def_3d_axis_order_hz()
                pass
            elif token in [40]:
                self.state = 174
                self.tp_3d_axis_order_hz()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 177
            self.match(OliviaPKParser.Amplitude)
            self.state = 178
            self.match(OliviaPKParser.Volume)
            self.state = 179
            self.match(OliviaPKParser.Vol_err)
            self.state = 180
            self.match(OliviaPKParser.X_chain)
            self.state = 181
            self.match(OliviaPKParser.X_resname)
            self.state = 182
            self.match(OliviaPKParser.X_seqnum)
            self.state = 183
            self.match(OliviaPKParser.X_assign)
            self.state = 184
            self.match(OliviaPKParser.Y_chain)
            self.state = 185
            self.match(OliviaPKParser.Y_resname)
            self.state = 186
            self.match(OliviaPKParser.Y_seqnum)
            self.state = 187
            self.match(OliviaPKParser.Y_assign)
            self.state = 188
            self.match(OliviaPKParser.Z_chain)
            self.state = 189
            self.match(OliviaPKParser.Z_resname)
            self.state = 190
            self.match(OliviaPKParser.Z_seqnum)
            self.state = 191
            self.match(OliviaPKParser.Z_assign)
            self.state = 192
            self.match(OliviaPKParser.Eval)
            self.state = 193
            self.match(OliviaPKParser.Status)
            self.state = 194
            self.match(OliviaPKParser.User_memo)
            self.state = 195
            self.match(OliviaPKParser.Update_time)
            self.state = 196
            self.match(OliviaPKParser.RETURN_FO)
            self.state = 197
            self.match(OliviaPKParser.Printf_string)
            self.state = 198
            self.match(OliviaPKParser.Printf_string)
            self.state = 199
            self.match(OliviaPKParser.Printf_string)
            self.state = 200
            self.match(OliviaPKParser.Printf_string)
            self.state = 201
            self.match(OliviaPKParser.Printf_string)
            self.state = 202
            self.match(OliviaPKParser.Printf_string)
            self.state = 203
            self.match(OliviaPKParser.Printf_string)
            self.state = 204
            self.match(OliviaPKParser.Printf_string)
            self.state = 205
            self.match(OliviaPKParser.Printf_string)
            self.state = 206
            self.match(OliviaPKParser.Printf_string)
            self.state = 207
            self.match(OliviaPKParser.Printf_string)
            self.state = 208
            self.match(OliviaPKParser.Printf_string)
            self.state = 209
            self.match(OliviaPKParser.Printf_string)
            self.state = 210
            self.match(OliviaPKParser.Printf_string)
            self.state = 211
            self.match(OliviaPKParser.Printf_string)
            self.state = 212
            self.match(OliviaPKParser.Printf_string)
            self.state = 213
            self.match(OliviaPKParser.Printf_string)
            self.state = 214
            self.match(OliviaPKParser.Printf_string)
            self.state = 215
            self.match(OliviaPKParser.Printf_string)
            self.state = 216
            self.match(OliviaPKParser.Printf_string)
            self.state = 217
            self.match(OliviaPKParser.Printf_string)
            self.state = 218
            self.match(OliviaPKParser.Printf_string)
            self.state = 219
            self.match(OliviaPKParser.Printf_string)
            self.state = 220
            self.match(OliviaPKParser.RETURN_PF)
            self.state = 222 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 221
                self.idx_peak_3d()
                self.state = 224 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==7):
                    break

            self.state = 226
            self.match(OliviaPKParser.Unformat)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Idx_peak_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.Integer)
            else:
                return self.getToken(OliviaPKParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.NumberContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.NumberContext,i)


        def string(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.StringContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.StringContext,i)


        def integer(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.IntegerContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.IntegerContext,i)


        def memo(self):
            return self.getTypedRuleContext(OliviaPKParser.MemoContext,0)


        def RETURN(self):
            return self.getToken(OliviaPKParser.RETURN, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_idx_peak_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdx_peak_3d" ):
                listener.enterIdx_peak_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdx_peak_3d" ):
                listener.exitIdx_peak_3d(self)




    def idx_peak_3d(self):

        localctx = OliviaPKParser.Idx_peak_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_idx_peak_3d)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 228
            self.match(OliviaPKParser.Integer)
            self.state = 229
            self.number()
            self.state = 230
            self.number()
            self.state = 231
            self.number()
            self.state = 232
            self.number()
            self.state = 233
            self.number()
            self.state = 234
            self.number()
            self.state = 235
            self.string()
            self.state = 236
            self.string()
            self.state = 237
            self.integer()
            self.state = 238
            self.string()
            self.state = 239
            self.string()
            self.state = 240
            self.string()
            self.state = 241
            self.integer()
            self.state = 242
            self.string()
            self.state = 243
            self.string()
            self.state = 244
            self.string()
            self.state = 245
            self.integer()
            self.state = 246
            self.string()
            self.state = 247
            self.match(OliviaPKParser.Integer)
            self.state = 248
            self.match(OliviaPKParser.Integer)
            self.state = 249
            self.memo()
            self.state = 250
            self.match(OliviaPKParser.Integer)
            self.state = 251
            self.match(OliviaPKParser.RETURN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Idx_peak_list_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Typedef(self):
            return self.getToken(OliviaPKParser.Typedef, 0)

        def Idx_tbl_4d(self):
            return self.getToken(OliviaPKParser.Idx_tbl_4d, 0)

        def RETURN_TD(self):
            return self.getToken(OliviaPKParser.RETURN_TD, 0)

        def Separator(self):
            return self.getToken(OliviaPKParser.Separator, 0)

        def RETURN_SE(self):
            return self.getToken(OliviaPKParser.RETURN_SE, 0)

        def Format(self):
            return self.getToken(OliviaPKParser.Format, 0)

        def Index(self):
            return self.getToken(OliviaPKParser.Index, 0)

        def Amplitude(self):
            return self.getToken(OliviaPKParser.Amplitude, 0)

        def Volume(self):
            return self.getToken(OliviaPKParser.Volume, 0)

        def Vol_err(self):
            return self.getToken(OliviaPKParser.Vol_err, 0)

        def X_chain(self):
            return self.getToken(OliviaPKParser.X_chain, 0)

        def X_resname(self):
            return self.getToken(OliviaPKParser.X_resname, 0)

        def X_seqnum(self):
            return self.getToken(OliviaPKParser.X_seqnum, 0)

        def X_assign(self):
            return self.getToken(OliviaPKParser.X_assign, 0)

        def Y_chain(self):
            return self.getToken(OliviaPKParser.Y_chain, 0)

        def Y_resname(self):
            return self.getToken(OliviaPKParser.Y_resname, 0)

        def Y_seqnum(self):
            return self.getToken(OliviaPKParser.Y_seqnum, 0)

        def Y_assign(self):
            return self.getToken(OliviaPKParser.Y_assign, 0)

        def Z_chain(self):
            return self.getToken(OliviaPKParser.Z_chain, 0)

        def Z_resname(self):
            return self.getToken(OliviaPKParser.Z_resname, 0)

        def Z_seqnum(self):
            return self.getToken(OliviaPKParser.Z_seqnum, 0)

        def Z_assign(self):
            return self.getToken(OliviaPKParser.Z_assign, 0)

        def A_chain(self):
            return self.getToken(OliviaPKParser.A_chain, 0)

        def A_resname(self):
            return self.getToken(OliviaPKParser.A_resname, 0)

        def A_seqnum(self):
            return self.getToken(OliviaPKParser.A_seqnum, 0)

        def A_assign(self):
            return self.getToken(OliviaPKParser.A_assign, 0)

        def Eval(self):
            return self.getToken(OliviaPKParser.Eval, 0)

        def Status(self):
            return self.getToken(OliviaPKParser.Status, 0)

        def User_memo(self):
            return self.getToken(OliviaPKParser.User_memo, 0)

        def Update_time(self):
            return self.getToken(OliviaPKParser.Update_time, 0)

        def RETURN_FO(self):
            return self.getToken(OliviaPKParser.RETURN_FO, 0)

        def Printf_string(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.Printf_string)
            else:
                return self.getToken(OliviaPKParser.Printf_string, i)

        def RETURN_PF(self):
            return self.getToken(OliviaPKParser.RETURN_PF, 0)

        def Unformat(self):
            return self.getToken(OliviaPKParser.Unformat, 0)

        def Tab(self):
            return self.getToken(OliviaPKParser.Tab, 0)

        def Comma(self):
            return self.getToken(OliviaPKParser.Comma, 0)

        def Space(self):
            return self.getToken(OliviaPKParser.Space, 0)

        def def_4d_axis_order_ppm(self):
            return self.getTypedRuleContext(OliviaPKParser.Def_4d_axis_order_ppmContext,0)


        def tp_4d_axis_order_ppm(self):
            return self.getTypedRuleContext(OliviaPKParser.Tp_4d_axis_order_ppmContext,0)


        def def_4d_axis_order_hz(self):
            return self.getTypedRuleContext(OliviaPKParser.Def_4d_axis_order_hzContext,0)


        def tp_4d_axis_order_hz(self):
            return self.getTypedRuleContext(OliviaPKParser.Tp_4d_axis_order_hzContext,0)


        def idx_peak_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.Idx_peak_4dContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.Idx_peak_4dContext,i)


        def getRuleIndex(self):
            return OliviaPKParser.RULE_idx_peak_list_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdx_peak_list_4d" ):
                listener.enterIdx_peak_list_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdx_peak_list_4d" ):
                listener.exitIdx_peak_list_4d(self)




    def idx_peak_list_4d(self):

        localctx = OliviaPKParser.Idx_peak_list_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_idx_peak_list_4d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 253
            self.match(OliviaPKParser.Typedef)
            self.state = 254
            self.match(OliviaPKParser.Idx_tbl_4d)
            self.state = 255
            self.match(OliviaPKParser.RETURN_TD)
            self.state = 256
            self.match(OliviaPKParser.Separator)
            self.state = 257
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1879048192) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 258
            self.match(OliviaPKParser.RETURN_SE)
            self.state = 259
            self.match(OliviaPKParser.Format)
            self.state = 260
            self.match(OliviaPKParser.Index)
            self.state = 265
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [34]:
                self.state = 261
                self.def_4d_axis_order_ppm()
                pass
            elif token in [37]:
                self.state = 262
                self.tp_4d_axis_order_ppm()
                pass
            elif token in [38]:
                self.state = 263
                self.def_4d_axis_order_hz()
                pass
            elif token in [41]:
                self.state = 264
                self.tp_4d_axis_order_hz()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 267
            self.match(OliviaPKParser.Amplitude)
            self.state = 268
            self.match(OliviaPKParser.Volume)
            self.state = 269
            self.match(OliviaPKParser.Vol_err)
            self.state = 270
            self.match(OliviaPKParser.X_chain)
            self.state = 271
            self.match(OliviaPKParser.X_resname)
            self.state = 272
            self.match(OliviaPKParser.X_seqnum)
            self.state = 273
            self.match(OliviaPKParser.X_assign)
            self.state = 274
            self.match(OliviaPKParser.Y_chain)
            self.state = 275
            self.match(OliviaPKParser.Y_resname)
            self.state = 276
            self.match(OliviaPKParser.Y_seqnum)
            self.state = 277
            self.match(OliviaPKParser.Y_assign)
            self.state = 278
            self.match(OliviaPKParser.Z_chain)
            self.state = 279
            self.match(OliviaPKParser.Z_resname)
            self.state = 280
            self.match(OliviaPKParser.Z_seqnum)
            self.state = 281
            self.match(OliviaPKParser.Z_assign)
            self.state = 282
            self.match(OliviaPKParser.A_chain)
            self.state = 283
            self.match(OliviaPKParser.A_resname)
            self.state = 284
            self.match(OliviaPKParser.A_seqnum)
            self.state = 285
            self.match(OliviaPKParser.A_assign)
            self.state = 286
            self.match(OliviaPKParser.Eval)
            self.state = 287
            self.match(OliviaPKParser.Status)
            self.state = 288
            self.match(OliviaPKParser.User_memo)
            self.state = 289
            self.match(OliviaPKParser.Update_time)
            self.state = 290
            self.match(OliviaPKParser.RETURN_FO)
            self.state = 291
            self.match(OliviaPKParser.Printf_string)
            self.state = 292
            self.match(OliviaPKParser.Printf_string)
            self.state = 293
            self.match(OliviaPKParser.Printf_string)
            self.state = 294
            self.match(OliviaPKParser.Printf_string)
            self.state = 295
            self.match(OliviaPKParser.Printf_string)
            self.state = 296
            self.match(OliviaPKParser.Printf_string)
            self.state = 297
            self.match(OliviaPKParser.Printf_string)
            self.state = 298
            self.match(OliviaPKParser.Printf_string)
            self.state = 299
            self.match(OliviaPKParser.Printf_string)
            self.state = 300
            self.match(OliviaPKParser.Printf_string)
            self.state = 301
            self.match(OliviaPKParser.Printf_string)
            self.state = 302
            self.match(OliviaPKParser.Printf_string)
            self.state = 303
            self.match(OliviaPKParser.Printf_string)
            self.state = 304
            self.match(OliviaPKParser.Printf_string)
            self.state = 305
            self.match(OliviaPKParser.Printf_string)
            self.state = 306
            self.match(OliviaPKParser.Printf_string)
            self.state = 307
            self.match(OliviaPKParser.Printf_string)
            self.state = 308
            self.match(OliviaPKParser.Printf_string)
            self.state = 309
            self.match(OliviaPKParser.Printf_string)
            self.state = 310
            self.match(OliviaPKParser.Printf_string)
            self.state = 311
            self.match(OliviaPKParser.Printf_string)
            self.state = 312
            self.match(OliviaPKParser.Printf_string)
            self.state = 313
            self.match(OliviaPKParser.Printf_string)
            self.state = 314
            self.match(OliviaPKParser.Printf_string)
            self.state = 315
            self.match(OliviaPKParser.Printf_string)
            self.state = 316
            self.match(OliviaPKParser.Printf_string)
            self.state = 317
            self.match(OliviaPKParser.Printf_string)
            self.state = 318
            self.match(OliviaPKParser.Printf_string)
            self.state = 319
            self.match(OliviaPKParser.RETURN_PF)
            self.state = 321 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 320
                self.idx_peak_4d()
                self.state = 323 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==7):
                    break

            self.state = 325
            self.match(OliviaPKParser.Unformat)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Idx_peak_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.Integer)
            else:
                return self.getToken(OliviaPKParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.NumberContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.NumberContext,i)


        def string(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.StringContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.StringContext,i)


        def integer(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.IntegerContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.IntegerContext,i)


        def memo(self):
            return self.getTypedRuleContext(OliviaPKParser.MemoContext,0)


        def RETURN(self):
            return self.getToken(OliviaPKParser.RETURN, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_idx_peak_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdx_peak_4d" ):
                listener.enterIdx_peak_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdx_peak_4d" ):
                listener.exitIdx_peak_4d(self)




    def idx_peak_4d(self):

        localctx = OliviaPKParser.Idx_peak_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_idx_peak_4d)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 327
            self.match(OliviaPKParser.Integer)
            self.state = 328
            self.number()
            self.state = 329
            self.number()
            self.state = 330
            self.number()
            self.state = 331
            self.number()
            self.state = 332
            self.number()
            self.state = 333
            self.number()
            self.state = 334
            self.number()
            self.state = 335
            self.string()
            self.state = 336
            self.string()
            self.state = 337
            self.integer()
            self.state = 338
            self.string()
            self.state = 339
            self.string()
            self.state = 340
            self.string()
            self.state = 341
            self.integer()
            self.state = 342
            self.string()
            self.state = 343
            self.string()
            self.state = 344
            self.string()
            self.state = 345
            self.integer()
            self.state = 346
            self.string()
            self.state = 347
            self.string()
            self.state = 348
            self.string()
            self.state = 349
            self.integer()
            self.state = 350
            self.string()
            self.state = 351
            self.match(OliviaPKParser.Integer)
            self.state = 352
            self.match(OliviaPKParser.Integer)
            self.state = 353
            self.memo()
            self.state = 354
            self.match(OliviaPKParser.Integer)
            self.state = 355
            self.match(OliviaPKParser.RETURN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Ass_peak_list_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Typedef(self):
            return self.getToken(OliviaPKParser.Typedef, 0)

        def Ass_tbl_2d(self):
            return self.getToken(OliviaPKParser.Ass_tbl_2d, 0)

        def RETURN_TD(self):
            return self.getToken(OliviaPKParser.RETURN_TD, 0)

        def Separator(self):
            return self.getToken(OliviaPKParser.Separator, 0)

        def RETURN_SE(self):
            return self.getToken(OliviaPKParser.RETURN_SE, 0)

        def Format(self):
            return self.getToken(OliviaPKParser.Format, 0)

        def X_chain(self):
            return self.getToken(OliviaPKParser.X_chain, 0)

        def X_resname(self):
            return self.getToken(OliviaPKParser.X_resname, 0)

        def X_seqnum(self):
            return self.getToken(OliviaPKParser.X_seqnum, 0)

        def X_assign(self):
            return self.getToken(OliviaPKParser.X_assign, 0)

        def Y_chain(self):
            return self.getToken(OliviaPKParser.Y_chain, 0)

        def Y_resname(self):
            return self.getToken(OliviaPKParser.Y_resname, 0)

        def Y_seqnum(self):
            return self.getToken(OliviaPKParser.Y_seqnum, 0)

        def Y_assign(self):
            return self.getToken(OliviaPKParser.Y_assign, 0)

        def Index(self):
            return self.getToken(OliviaPKParser.Index, 0)

        def Amplitude(self):
            return self.getToken(OliviaPKParser.Amplitude, 0)

        def Volume(self):
            return self.getToken(OliviaPKParser.Volume, 0)

        def Vol_err(self):
            return self.getToken(OliviaPKParser.Vol_err, 0)

        def Eval(self):
            return self.getToken(OliviaPKParser.Eval, 0)

        def Status(self):
            return self.getToken(OliviaPKParser.Status, 0)

        def User_memo(self):
            return self.getToken(OliviaPKParser.User_memo, 0)

        def Update_time(self):
            return self.getToken(OliviaPKParser.Update_time, 0)

        def RETURN_FO(self):
            return self.getToken(OliviaPKParser.RETURN_FO, 0)

        def Printf_string(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.Printf_string)
            else:
                return self.getToken(OliviaPKParser.Printf_string, i)

        def RETURN_PF(self):
            return self.getToken(OliviaPKParser.RETURN_PF, 0)

        def Unformat(self):
            return self.getToken(OliviaPKParser.Unformat, 0)

        def Tab(self):
            return self.getToken(OliviaPKParser.Tab, 0)

        def Comma(self):
            return self.getToken(OliviaPKParser.Comma, 0)

        def Space(self):
            return self.getToken(OliviaPKParser.Space, 0)

        def def_2d_axis_order_ppm(self):
            return self.getTypedRuleContext(OliviaPKParser.Def_2d_axis_order_ppmContext,0)


        def tp_2d_axis_order_ppm(self):
            return self.getTypedRuleContext(OliviaPKParser.Tp_2d_axis_order_ppmContext,0)


        def def_2d_axis_order_hz(self):
            return self.getTypedRuleContext(OliviaPKParser.Def_2d_axis_order_hzContext,0)


        def tp_2d_axis_order_hz(self):
            return self.getTypedRuleContext(OliviaPKParser.Tp_2d_axis_order_hzContext,0)


        def ass_peak_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.Ass_peak_2dContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.Ass_peak_2dContext,i)


        def getRuleIndex(self):
            return OliviaPKParser.RULE_ass_peak_list_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAss_peak_list_2d" ):
                listener.enterAss_peak_list_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAss_peak_list_2d" ):
                listener.exitAss_peak_list_2d(self)




    def ass_peak_list_2d(self):

        localctx = OliviaPKParser.Ass_peak_list_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_ass_peak_list_2d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 357
            self.match(OliviaPKParser.Typedef)
            self.state = 358
            self.match(OliviaPKParser.Ass_tbl_2d)
            self.state = 359
            self.match(OliviaPKParser.RETURN_TD)
            self.state = 360
            self.match(OliviaPKParser.Separator)
            self.state = 361
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1879048192) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 362
            self.match(OliviaPKParser.RETURN_SE)
            self.state = 363
            self.match(OliviaPKParser.Format)
            self.state = 364
            self.match(OliviaPKParser.X_chain)
            self.state = 365
            self.match(OliviaPKParser.X_resname)
            self.state = 366
            self.match(OliviaPKParser.X_seqnum)
            self.state = 367
            self.match(OliviaPKParser.X_assign)
            self.state = 368
            self.match(OliviaPKParser.Y_chain)
            self.state = 369
            self.match(OliviaPKParser.Y_resname)
            self.state = 370
            self.match(OliviaPKParser.Y_seqnum)
            self.state = 371
            self.match(OliviaPKParser.Y_assign)
            self.state = 372
            self.match(OliviaPKParser.Index)
            self.state = 377
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [34]:
                self.state = 373
                self.def_2d_axis_order_ppm()
                pass
            elif token in [35]:
                self.state = 374
                self.tp_2d_axis_order_ppm()
                pass
            elif token in [38]:
                self.state = 375
                self.def_2d_axis_order_hz()
                pass
            elif token in [39]:
                self.state = 376
                self.tp_2d_axis_order_hz()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 379
            self.match(OliviaPKParser.Amplitude)
            self.state = 380
            self.match(OliviaPKParser.Volume)
            self.state = 381
            self.match(OliviaPKParser.Vol_err)
            self.state = 382
            self.match(OliviaPKParser.Eval)
            self.state = 383
            self.match(OliviaPKParser.Status)
            self.state = 384
            self.match(OliviaPKParser.User_memo)
            self.state = 385
            self.match(OliviaPKParser.Update_time)
            self.state = 386
            self.match(OliviaPKParser.RETURN_FO)
            self.state = 387
            self.match(OliviaPKParser.Printf_string)
            self.state = 388
            self.match(OliviaPKParser.Printf_string)
            self.state = 389
            self.match(OliviaPKParser.Printf_string)
            self.state = 390
            self.match(OliviaPKParser.Printf_string)
            self.state = 391
            self.match(OliviaPKParser.Printf_string)
            self.state = 392
            self.match(OliviaPKParser.Printf_string)
            self.state = 393
            self.match(OliviaPKParser.Printf_string)
            self.state = 394
            self.match(OliviaPKParser.Printf_string)
            self.state = 395
            self.match(OliviaPKParser.Printf_string)
            self.state = 396
            self.match(OliviaPKParser.Printf_string)
            self.state = 397
            self.match(OliviaPKParser.Printf_string)
            self.state = 398
            self.match(OliviaPKParser.Printf_string)
            self.state = 399
            self.match(OliviaPKParser.Printf_string)
            self.state = 400
            self.match(OliviaPKParser.Printf_string)
            self.state = 401
            self.match(OliviaPKParser.Printf_string)
            self.state = 402
            self.match(OliviaPKParser.Printf_string)
            self.state = 403
            self.match(OliviaPKParser.Printf_string)
            self.state = 404
            self.match(OliviaPKParser.Printf_string)
            self.state = 405
            self.match(OliviaPKParser.RETURN_PF)
            self.state = 407 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 406
                self.ass_peak_2d()
                self.state = 409 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==6 or _la==15):
                    break

            self.state = 411
            self.match(OliviaPKParser.Unformat)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Ass_peak_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def string(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.StringContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.StringContext,i)


        def integer(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.IntegerContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.IntegerContext,i)


        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.Integer)
            else:
                return self.getToken(OliviaPKParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.NumberContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.NumberContext,i)


        def memo(self):
            return self.getTypedRuleContext(OliviaPKParser.MemoContext,0)


        def RETURN(self):
            return self.getToken(OliviaPKParser.RETURN, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_ass_peak_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAss_peak_2d" ):
                listener.enterAss_peak_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAss_peak_2d" ):
                listener.exitAss_peak_2d(self)




    def ass_peak_2d(self):

        localctx = OliviaPKParser.Ass_peak_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_ass_peak_2d)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 413
            self.string()
            self.state = 414
            self.string()
            self.state = 415
            self.integer()
            self.state = 416
            self.string()
            self.state = 417
            self.string()
            self.state = 418
            self.string()
            self.state = 419
            self.integer()
            self.state = 420
            self.string()
            self.state = 421
            self.match(OliviaPKParser.Integer)
            self.state = 422
            self.number()
            self.state = 423
            self.number()
            self.state = 424
            self.number()
            self.state = 425
            self.number()
            self.state = 426
            self.number()
            self.state = 427
            self.match(OliviaPKParser.Integer)
            self.state = 428
            self.match(OliviaPKParser.Integer)
            self.state = 429
            self.memo()
            self.state = 430
            self.match(OliviaPKParser.Integer)
            self.state = 431
            self.match(OliviaPKParser.RETURN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Ass_peak_list_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Typedef(self):
            return self.getToken(OliviaPKParser.Typedef, 0)

        def Ass_tbl_3d(self):
            return self.getToken(OliviaPKParser.Ass_tbl_3d, 0)

        def RETURN_TD(self):
            return self.getToken(OliviaPKParser.RETURN_TD, 0)

        def Separator(self):
            return self.getToken(OliviaPKParser.Separator, 0)

        def RETURN_SE(self):
            return self.getToken(OliviaPKParser.RETURN_SE, 0)

        def Format(self):
            return self.getToken(OliviaPKParser.Format, 0)

        def X_chain(self):
            return self.getToken(OliviaPKParser.X_chain, 0)

        def X_resname(self):
            return self.getToken(OliviaPKParser.X_resname, 0)

        def X_seqnum(self):
            return self.getToken(OliviaPKParser.X_seqnum, 0)

        def X_assign(self):
            return self.getToken(OliviaPKParser.X_assign, 0)

        def Y_chain(self):
            return self.getToken(OliviaPKParser.Y_chain, 0)

        def Y_resname(self):
            return self.getToken(OliviaPKParser.Y_resname, 0)

        def Y_seqnum(self):
            return self.getToken(OliviaPKParser.Y_seqnum, 0)

        def Y_assign(self):
            return self.getToken(OliviaPKParser.Y_assign, 0)

        def Z_chain(self):
            return self.getToken(OliviaPKParser.Z_chain, 0)

        def Z_resname(self):
            return self.getToken(OliviaPKParser.Z_resname, 0)

        def Z_seqnum(self):
            return self.getToken(OliviaPKParser.Z_seqnum, 0)

        def Z_assign(self):
            return self.getToken(OliviaPKParser.Z_assign, 0)

        def Index(self):
            return self.getToken(OliviaPKParser.Index, 0)

        def Amplitude(self):
            return self.getToken(OliviaPKParser.Amplitude, 0)

        def Volume(self):
            return self.getToken(OliviaPKParser.Volume, 0)

        def Vol_err(self):
            return self.getToken(OliviaPKParser.Vol_err, 0)

        def Eval(self):
            return self.getToken(OliviaPKParser.Eval, 0)

        def Status(self):
            return self.getToken(OliviaPKParser.Status, 0)

        def User_memo(self):
            return self.getToken(OliviaPKParser.User_memo, 0)

        def Update_time(self):
            return self.getToken(OliviaPKParser.Update_time, 0)

        def RETURN_FO(self):
            return self.getToken(OliviaPKParser.RETURN_FO, 0)

        def Printf_string(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.Printf_string)
            else:
                return self.getToken(OliviaPKParser.Printf_string, i)

        def RETURN_PF(self):
            return self.getToken(OliviaPKParser.RETURN_PF, 0)

        def Unformat(self):
            return self.getToken(OliviaPKParser.Unformat, 0)

        def Tab(self):
            return self.getToken(OliviaPKParser.Tab, 0)

        def Comma(self):
            return self.getToken(OliviaPKParser.Comma, 0)

        def Space(self):
            return self.getToken(OliviaPKParser.Space, 0)

        def def_3d_axis_order_ppm(self):
            return self.getTypedRuleContext(OliviaPKParser.Def_3d_axis_order_ppmContext,0)


        def tp_3d_axis_order_ppm(self):
            return self.getTypedRuleContext(OliviaPKParser.Tp_3d_axis_order_ppmContext,0)


        def def_3d_axis_order_hz(self):
            return self.getTypedRuleContext(OliviaPKParser.Def_3d_axis_order_hzContext,0)


        def tp_3d_axis_order_hz(self):
            return self.getTypedRuleContext(OliviaPKParser.Tp_3d_axis_order_hzContext,0)


        def ass_peak_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.Ass_peak_3dContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.Ass_peak_3dContext,i)


        def getRuleIndex(self):
            return OliviaPKParser.RULE_ass_peak_list_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAss_peak_list_3d" ):
                listener.enterAss_peak_list_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAss_peak_list_3d" ):
                listener.exitAss_peak_list_3d(self)




    def ass_peak_list_3d(self):

        localctx = OliviaPKParser.Ass_peak_list_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_ass_peak_list_3d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 433
            self.match(OliviaPKParser.Typedef)
            self.state = 434
            self.match(OliviaPKParser.Ass_tbl_3d)
            self.state = 435
            self.match(OliviaPKParser.RETURN_TD)
            self.state = 436
            self.match(OliviaPKParser.Separator)
            self.state = 437
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1879048192) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 438
            self.match(OliviaPKParser.RETURN_SE)
            self.state = 439
            self.match(OliviaPKParser.Format)
            self.state = 440
            self.match(OliviaPKParser.X_chain)
            self.state = 441
            self.match(OliviaPKParser.X_resname)
            self.state = 442
            self.match(OliviaPKParser.X_seqnum)
            self.state = 443
            self.match(OliviaPKParser.X_assign)
            self.state = 444
            self.match(OliviaPKParser.Y_chain)
            self.state = 445
            self.match(OliviaPKParser.Y_resname)
            self.state = 446
            self.match(OliviaPKParser.Y_seqnum)
            self.state = 447
            self.match(OliviaPKParser.Y_assign)
            self.state = 448
            self.match(OliviaPKParser.Z_chain)
            self.state = 449
            self.match(OliviaPKParser.Z_resname)
            self.state = 450
            self.match(OliviaPKParser.Z_seqnum)
            self.state = 451
            self.match(OliviaPKParser.Z_assign)
            self.state = 452
            self.match(OliviaPKParser.Index)
            self.state = 457
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [34]:
                self.state = 453
                self.def_3d_axis_order_ppm()
                pass
            elif token in [36]:
                self.state = 454
                self.tp_3d_axis_order_ppm()
                pass
            elif token in [38]:
                self.state = 455
                self.def_3d_axis_order_hz()
                pass
            elif token in [40]:
                self.state = 456
                self.tp_3d_axis_order_hz()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 459
            self.match(OliviaPKParser.Amplitude)
            self.state = 460
            self.match(OliviaPKParser.Volume)
            self.state = 461
            self.match(OliviaPKParser.Vol_err)
            self.state = 462
            self.match(OliviaPKParser.Eval)
            self.state = 463
            self.match(OliviaPKParser.Status)
            self.state = 464
            self.match(OliviaPKParser.User_memo)
            self.state = 465
            self.match(OliviaPKParser.Update_time)
            self.state = 466
            self.match(OliviaPKParser.RETURN_FO)
            self.state = 467
            self.match(OliviaPKParser.Printf_string)
            self.state = 468
            self.match(OliviaPKParser.Printf_string)
            self.state = 469
            self.match(OliviaPKParser.Printf_string)
            self.state = 470
            self.match(OliviaPKParser.Printf_string)
            self.state = 471
            self.match(OliviaPKParser.Printf_string)
            self.state = 472
            self.match(OliviaPKParser.Printf_string)
            self.state = 473
            self.match(OliviaPKParser.Printf_string)
            self.state = 474
            self.match(OliviaPKParser.Printf_string)
            self.state = 475
            self.match(OliviaPKParser.Printf_string)
            self.state = 476
            self.match(OliviaPKParser.Printf_string)
            self.state = 477
            self.match(OliviaPKParser.Printf_string)
            self.state = 478
            self.match(OliviaPKParser.Printf_string)
            self.state = 479
            self.match(OliviaPKParser.Printf_string)
            self.state = 480
            self.match(OliviaPKParser.Printf_string)
            self.state = 481
            self.match(OliviaPKParser.Printf_string)
            self.state = 482
            self.match(OliviaPKParser.Printf_string)
            self.state = 483
            self.match(OliviaPKParser.Printf_string)
            self.state = 484
            self.match(OliviaPKParser.Printf_string)
            self.state = 485
            self.match(OliviaPKParser.Printf_string)
            self.state = 486
            self.match(OliviaPKParser.Printf_string)
            self.state = 487
            self.match(OliviaPKParser.Printf_string)
            self.state = 488
            self.match(OliviaPKParser.Printf_string)
            self.state = 489
            self.match(OliviaPKParser.Printf_string)
            self.state = 490
            self.match(OliviaPKParser.RETURN_PF)
            self.state = 492 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 491
                self.ass_peak_3d()
                self.state = 494 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==6 or _la==15):
                    break

            self.state = 496
            self.match(OliviaPKParser.Unformat)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Ass_peak_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def string(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.StringContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.StringContext,i)


        def integer(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.IntegerContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.IntegerContext,i)


        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.Integer)
            else:
                return self.getToken(OliviaPKParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.NumberContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.NumberContext,i)


        def memo(self):
            return self.getTypedRuleContext(OliviaPKParser.MemoContext,0)


        def RETURN(self):
            return self.getToken(OliviaPKParser.RETURN, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_ass_peak_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAss_peak_3d" ):
                listener.enterAss_peak_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAss_peak_3d" ):
                listener.exitAss_peak_3d(self)




    def ass_peak_3d(self):

        localctx = OliviaPKParser.Ass_peak_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_ass_peak_3d)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 498
            self.string()
            self.state = 499
            self.string()
            self.state = 500
            self.integer()
            self.state = 501
            self.string()
            self.state = 502
            self.string()
            self.state = 503
            self.string()
            self.state = 504
            self.integer()
            self.state = 505
            self.string()
            self.state = 506
            self.string()
            self.state = 507
            self.string()
            self.state = 508
            self.integer()
            self.state = 509
            self.string()
            self.state = 510
            self.match(OliviaPKParser.Integer)
            self.state = 511
            self.number()
            self.state = 512
            self.number()
            self.state = 513
            self.number()
            self.state = 514
            self.number()
            self.state = 515
            self.number()
            self.state = 516
            self.number()
            self.state = 517
            self.match(OliviaPKParser.Integer)
            self.state = 518
            self.match(OliviaPKParser.Integer)
            self.state = 519
            self.memo()
            self.state = 520
            self.match(OliviaPKParser.Integer)
            self.state = 521
            self.match(OliviaPKParser.RETURN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Ass_peak_list_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Typedef(self):
            return self.getToken(OliviaPKParser.Typedef, 0)

        def Ass_tbl_4d(self):
            return self.getToken(OliviaPKParser.Ass_tbl_4d, 0)

        def RETURN_TD(self):
            return self.getToken(OliviaPKParser.RETURN_TD, 0)

        def Separator(self):
            return self.getToken(OliviaPKParser.Separator, 0)

        def RETURN_SE(self):
            return self.getToken(OliviaPKParser.RETURN_SE, 0)

        def Format(self):
            return self.getToken(OliviaPKParser.Format, 0)

        def X_chain(self):
            return self.getToken(OliviaPKParser.X_chain, 0)

        def X_resname(self):
            return self.getToken(OliviaPKParser.X_resname, 0)

        def X_seqnum(self):
            return self.getToken(OliviaPKParser.X_seqnum, 0)

        def X_assign(self):
            return self.getToken(OliviaPKParser.X_assign, 0)

        def Y_chain(self):
            return self.getToken(OliviaPKParser.Y_chain, 0)

        def Y_resname(self):
            return self.getToken(OliviaPKParser.Y_resname, 0)

        def Y_seqnum(self):
            return self.getToken(OliviaPKParser.Y_seqnum, 0)

        def Y_assign(self):
            return self.getToken(OliviaPKParser.Y_assign, 0)

        def Z_chain(self):
            return self.getToken(OliviaPKParser.Z_chain, 0)

        def Z_resname(self):
            return self.getToken(OliviaPKParser.Z_resname, 0)

        def Z_seqnum(self):
            return self.getToken(OliviaPKParser.Z_seqnum, 0)

        def Z_assign(self):
            return self.getToken(OliviaPKParser.Z_assign, 0)

        def A_chain(self):
            return self.getToken(OliviaPKParser.A_chain, 0)

        def A_resname(self):
            return self.getToken(OliviaPKParser.A_resname, 0)

        def A_seqnum(self):
            return self.getToken(OliviaPKParser.A_seqnum, 0)

        def A_assign(self):
            return self.getToken(OliviaPKParser.A_assign, 0)

        def Index(self):
            return self.getToken(OliviaPKParser.Index, 0)

        def Amplitude(self):
            return self.getToken(OliviaPKParser.Amplitude, 0)

        def Volume(self):
            return self.getToken(OliviaPKParser.Volume, 0)

        def Vol_err(self):
            return self.getToken(OliviaPKParser.Vol_err, 0)

        def Eval(self):
            return self.getToken(OliviaPKParser.Eval, 0)

        def Status(self):
            return self.getToken(OliviaPKParser.Status, 0)

        def User_memo(self):
            return self.getToken(OliviaPKParser.User_memo, 0)

        def Update_time(self):
            return self.getToken(OliviaPKParser.Update_time, 0)

        def RETURN_FO(self):
            return self.getToken(OliviaPKParser.RETURN_FO, 0)

        def Printf_string(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.Printf_string)
            else:
                return self.getToken(OliviaPKParser.Printf_string, i)

        def RETURN_PF(self):
            return self.getToken(OliviaPKParser.RETURN_PF, 0)

        def Unformat(self):
            return self.getToken(OliviaPKParser.Unformat, 0)

        def Tab(self):
            return self.getToken(OliviaPKParser.Tab, 0)

        def Comma(self):
            return self.getToken(OliviaPKParser.Comma, 0)

        def Space(self):
            return self.getToken(OliviaPKParser.Space, 0)

        def def_4d_axis_order_ppm(self):
            return self.getTypedRuleContext(OliviaPKParser.Def_4d_axis_order_ppmContext,0)


        def tp_4d_axis_order_ppm(self):
            return self.getTypedRuleContext(OliviaPKParser.Tp_4d_axis_order_ppmContext,0)


        def def_4d_axis_order_hz(self):
            return self.getTypedRuleContext(OliviaPKParser.Def_4d_axis_order_hzContext,0)


        def tp_4d_axis_order_hz(self):
            return self.getTypedRuleContext(OliviaPKParser.Tp_4d_axis_order_hzContext,0)


        def ass_peak_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.Ass_peak_4dContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.Ass_peak_4dContext,i)


        def getRuleIndex(self):
            return OliviaPKParser.RULE_ass_peak_list_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAss_peak_list_4d" ):
                listener.enterAss_peak_list_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAss_peak_list_4d" ):
                listener.exitAss_peak_list_4d(self)




    def ass_peak_list_4d(self):

        localctx = OliviaPKParser.Ass_peak_list_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_ass_peak_list_4d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 523
            self.match(OliviaPKParser.Typedef)
            self.state = 524
            self.match(OliviaPKParser.Ass_tbl_4d)
            self.state = 525
            self.match(OliviaPKParser.RETURN_TD)
            self.state = 526
            self.match(OliviaPKParser.Separator)
            self.state = 527
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1879048192) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 528
            self.match(OliviaPKParser.RETURN_SE)
            self.state = 529
            self.match(OliviaPKParser.Format)
            self.state = 530
            self.match(OliviaPKParser.X_chain)
            self.state = 531
            self.match(OliviaPKParser.X_resname)
            self.state = 532
            self.match(OliviaPKParser.X_seqnum)
            self.state = 533
            self.match(OliviaPKParser.X_assign)
            self.state = 534
            self.match(OliviaPKParser.Y_chain)
            self.state = 535
            self.match(OliviaPKParser.Y_resname)
            self.state = 536
            self.match(OliviaPKParser.Y_seqnum)
            self.state = 537
            self.match(OliviaPKParser.Y_assign)
            self.state = 538
            self.match(OliviaPKParser.Z_chain)
            self.state = 539
            self.match(OliviaPKParser.Z_resname)
            self.state = 540
            self.match(OliviaPKParser.Z_seqnum)
            self.state = 541
            self.match(OliviaPKParser.Z_assign)
            self.state = 542
            self.match(OliviaPKParser.A_chain)
            self.state = 543
            self.match(OliviaPKParser.A_resname)
            self.state = 544
            self.match(OliviaPKParser.A_seqnum)
            self.state = 545
            self.match(OliviaPKParser.A_assign)
            self.state = 546
            self.match(OliviaPKParser.Index)
            self.state = 551
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [34]:
                self.state = 547
                self.def_4d_axis_order_ppm()
                pass
            elif token in [37]:
                self.state = 548
                self.tp_4d_axis_order_ppm()
                pass
            elif token in [38]:
                self.state = 549
                self.def_4d_axis_order_hz()
                pass
            elif token in [41]:
                self.state = 550
                self.tp_4d_axis_order_hz()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 553
            self.match(OliviaPKParser.Amplitude)
            self.state = 554
            self.match(OliviaPKParser.Volume)
            self.state = 555
            self.match(OliviaPKParser.Vol_err)
            self.state = 556
            self.match(OliviaPKParser.Eval)
            self.state = 557
            self.match(OliviaPKParser.Status)
            self.state = 558
            self.match(OliviaPKParser.User_memo)
            self.state = 559
            self.match(OliviaPKParser.Update_time)
            self.state = 560
            self.match(OliviaPKParser.RETURN_FO)
            self.state = 561
            self.match(OliviaPKParser.Printf_string)
            self.state = 562
            self.match(OliviaPKParser.Printf_string)
            self.state = 563
            self.match(OliviaPKParser.Printf_string)
            self.state = 564
            self.match(OliviaPKParser.Printf_string)
            self.state = 565
            self.match(OliviaPKParser.Printf_string)
            self.state = 566
            self.match(OliviaPKParser.Printf_string)
            self.state = 567
            self.match(OliviaPKParser.Printf_string)
            self.state = 568
            self.match(OliviaPKParser.Printf_string)
            self.state = 569
            self.match(OliviaPKParser.Printf_string)
            self.state = 570
            self.match(OliviaPKParser.Printf_string)
            self.state = 571
            self.match(OliviaPKParser.Printf_string)
            self.state = 572
            self.match(OliviaPKParser.Printf_string)
            self.state = 573
            self.match(OliviaPKParser.Printf_string)
            self.state = 574
            self.match(OliviaPKParser.Printf_string)
            self.state = 575
            self.match(OliviaPKParser.Printf_string)
            self.state = 576
            self.match(OliviaPKParser.Printf_string)
            self.state = 577
            self.match(OliviaPKParser.Printf_string)
            self.state = 578
            self.match(OliviaPKParser.Printf_string)
            self.state = 579
            self.match(OliviaPKParser.Printf_string)
            self.state = 580
            self.match(OliviaPKParser.Printf_string)
            self.state = 581
            self.match(OliviaPKParser.Printf_string)
            self.state = 582
            self.match(OliviaPKParser.Printf_string)
            self.state = 583
            self.match(OliviaPKParser.Printf_string)
            self.state = 584
            self.match(OliviaPKParser.Printf_string)
            self.state = 585
            self.match(OliviaPKParser.Printf_string)
            self.state = 586
            self.match(OliviaPKParser.Printf_string)
            self.state = 587
            self.match(OliviaPKParser.Printf_string)
            self.state = 588
            self.match(OliviaPKParser.Printf_string)
            self.state = 589
            self.match(OliviaPKParser.RETURN_PF)
            self.state = 591 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 590
                self.ass_peak_4d()
                self.state = 593 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==6 or _la==15):
                    break

            self.state = 595
            self.match(OliviaPKParser.Unformat)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Ass_peak_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def string(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.StringContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.StringContext,i)


        def integer(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.IntegerContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.IntegerContext,i)


        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(OliviaPKParser.Integer)
            else:
                return self.getToken(OliviaPKParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(OliviaPKParser.NumberContext)
            else:
                return self.getTypedRuleContext(OliviaPKParser.NumberContext,i)


        def memo(self):
            return self.getTypedRuleContext(OliviaPKParser.MemoContext,0)


        def RETURN(self):
            return self.getToken(OliviaPKParser.RETURN, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_ass_peak_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAss_peak_4d" ):
                listener.enterAss_peak_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAss_peak_4d" ):
                listener.exitAss_peak_4d(self)




    def ass_peak_4d(self):

        localctx = OliviaPKParser.Ass_peak_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_ass_peak_4d)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 597
            self.string()
            self.state = 598
            self.string()
            self.state = 599
            self.integer()
            self.state = 600
            self.string()
            self.state = 601
            self.string()
            self.state = 602
            self.string()
            self.state = 603
            self.integer()
            self.state = 604
            self.string()
            self.state = 605
            self.string()
            self.state = 606
            self.string()
            self.state = 607
            self.integer()
            self.state = 608
            self.string()
            self.state = 609
            self.string()
            self.state = 610
            self.string()
            self.state = 611
            self.integer()
            self.state = 612
            self.string()
            self.state = 613
            self.match(OliviaPKParser.Integer)
            self.state = 614
            self.number()
            self.state = 615
            self.number()
            self.state = 616
            self.number()
            self.state = 617
            self.number()
            self.state = 618
            self.number()
            self.state = 619
            self.number()
            self.state = 620
            self.number()
            self.state = 621
            self.match(OliviaPKParser.Integer)
            self.state = 622
            self.match(OliviaPKParser.Integer)
            self.state = 623
            self.memo()
            self.state = 624
            self.match(OliviaPKParser.Integer)
            self.state = 625
            self.match(OliviaPKParser.RETURN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Def_2d_axis_order_ppmContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def X_ppm(self):
            return self.getToken(OliviaPKParser.X_ppm, 0)

        def Y_ppm(self):
            return self.getToken(OliviaPKParser.Y_ppm, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_def_2d_axis_order_ppm

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDef_2d_axis_order_ppm" ):
                listener.enterDef_2d_axis_order_ppm(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDef_2d_axis_order_ppm" ):
                listener.exitDef_2d_axis_order_ppm(self)




    def def_2d_axis_order_ppm(self):

        localctx = OliviaPKParser.Def_2d_axis_order_ppmContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_def_2d_axis_order_ppm)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 627
            self.match(OliviaPKParser.X_ppm)
            self.state = 628
            self.match(OliviaPKParser.Y_ppm)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tp_2d_axis_order_ppmContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Y_ppm(self):
            return self.getToken(OliviaPKParser.Y_ppm, 0)

        def X_ppm(self):
            return self.getToken(OliviaPKParser.X_ppm, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_tp_2d_axis_order_ppm

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTp_2d_axis_order_ppm" ):
                listener.enterTp_2d_axis_order_ppm(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTp_2d_axis_order_ppm" ):
                listener.exitTp_2d_axis_order_ppm(self)




    def tp_2d_axis_order_ppm(self):

        localctx = OliviaPKParser.Tp_2d_axis_order_ppmContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_tp_2d_axis_order_ppm)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 630
            self.match(OliviaPKParser.Y_ppm)
            self.state = 631
            self.match(OliviaPKParser.X_ppm)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Def_2d_axis_order_hzContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def X_hz(self):
            return self.getToken(OliviaPKParser.X_hz, 0)

        def Y_hz(self):
            return self.getToken(OliviaPKParser.Y_hz, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_def_2d_axis_order_hz

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDef_2d_axis_order_hz" ):
                listener.enterDef_2d_axis_order_hz(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDef_2d_axis_order_hz" ):
                listener.exitDef_2d_axis_order_hz(self)




    def def_2d_axis_order_hz(self):

        localctx = OliviaPKParser.Def_2d_axis_order_hzContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_def_2d_axis_order_hz)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 633
            self.match(OliviaPKParser.X_hz)
            self.state = 634
            self.match(OliviaPKParser.Y_hz)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tp_2d_axis_order_hzContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Y_hz(self):
            return self.getToken(OliviaPKParser.Y_hz, 0)

        def X_hz(self):
            return self.getToken(OliviaPKParser.X_hz, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_tp_2d_axis_order_hz

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTp_2d_axis_order_hz" ):
                listener.enterTp_2d_axis_order_hz(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTp_2d_axis_order_hz" ):
                listener.exitTp_2d_axis_order_hz(self)




    def tp_2d_axis_order_hz(self):

        localctx = OliviaPKParser.Tp_2d_axis_order_hzContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_tp_2d_axis_order_hz)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 636
            self.match(OliviaPKParser.Y_hz)
            self.state = 637
            self.match(OliviaPKParser.X_hz)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Def_3d_axis_order_ppmContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def X_ppm(self):
            return self.getToken(OliviaPKParser.X_ppm, 0)

        def Y_ppm(self):
            return self.getToken(OliviaPKParser.Y_ppm, 0)

        def Z_ppm(self):
            return self.getToken(OliviaPKParser.Z_ppm, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_def_3d_axis_order_ppm

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDef_3d_axis_order_ppm" ):
                listener.enterDef_3d_axis_order_ppm(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDef_3d_axis_order_ppm" ):
                listener.exitDef_3d_axis_order_ppm(self)




    def def_3d_axis_order_ppm(self):

        localctx = OliviaPKParser.Def_3d_axis_order_ppmContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_def_3d_axis_order_ppm)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 639
            self.match(OliviaPKParser.X_ppm)
            self.state = 640
            self.match(OliviaPKParser.Y_ppm)
            self.state = 641
            self.match(OliviaPKParser.Z_ppm)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tp_3d_axis_order_ppmContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Z_ppm(self):
            return self.getToken(OliviaPKParser.Z_ppm, 0)

        def Y_ppm(self):
            return self.getToken(OliviaPKParser.Y_ppm, 0)

        def X_ppm(self):
            return self.getToken(OliviaPKParser.X_ppm, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_tp_3d_axis_order_ppm

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTp_3d_axis_order_ppm" ):
                listener.enterTp_3d_axis_order_ppm(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTp_3d_axis_order_ppm" ):
                listener.exitTp_3d_axis_order_ppm(self)




    def tp_3d_axis_order_ppm(self):

        localctx = OliviaPKParser.Tp_3d_axis_order_ppmContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_tp_3d_axis_order_ppm)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 643
            self.match(OliviaPKParser.Z_ppm)
            self.state = 644
            self.match(OliviaPKParser.Y_ppm)
            self.state = 645
            self.match(OliviaPKParser.X_ppm)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Def_3d_axis_order_hzContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def X_hz(self):
            return self.getToken(OliviaPKParser.X_hz, 0)

        def Y_hz(self):
            return self.getToken(OliviaPKParser.Y_hz, 0)

        def Z_hz(self):
            return self.getToken(OliviaPKParser.Z_hz, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_def_3d_axis_order_hz

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDef_3d_axis_order_hz" ):
                listener.enterDef_3d_axis_order_hz(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDef_3d_axis_order_hz" ):
                listener.exitDef_3d_axis_order_hz(self)




    def def_3d_axis_order_hz(self):

        localctx = OliviaPKParser.Def_3d_axis_order_hzContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_def_3d_axis_order_hz)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 647
            self.match(OliviaPKParser.X_hz)
            self.state = 648
            self.match(OliviaPKParser.Y_hz)
            self.state = 649
            self.match(OliviaPKParser.Z_hz)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tp_3d_axis_order_hzContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Z_hz(self):
            return self.getToken(OliviaPKParser.Z_hz, 0)

        def Y_hz(self):
            return self.getToken(OliviaPKParser.Y_hz, 0)

        def X_hz(self):
            return self.getToken(OliviaPKParser.X_hz, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_tp_3d_axis_order_hz

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTp_3d_axis_order_hz" ):
                listener.enterTp_3d_axis_order_hz(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTp_3d_axis_order_hz" ):
                listener.exitTp_3d_axis_order_hz(self)




    def tp_3d_axis_order_hz(self):

        localctx = OliviaPKParser.Tp_3d_axis_order_hzContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_tp_3d_axis_order_hz)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 651
            self.match(OliviaPKParser.Z_hz)
            self.state = 652
            self.match(OliviaPKParser.Y_hz)
            self.state = 653
            self.match(OliviaPKParser.X_hz)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Def_4d_axis_order_ppmContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def X_ppm(self):
            return self.getToken(OliviaPKParser.X_ppm, 0)

        def Y_ppm(self):
            return self.getToken(OliviaPKParser.Y_ppm, 0)

        def Z_ppm(self):
            return self.getToken(OliviaPKParser.Z_ppm, 0)

        def A_ppm(self):
            return self.getToken(OliviaPKParser.A_ppm, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_def_4d_axis_order_ppm

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDef_4d_axis_order_ppm" ):
                listener.enterDef_4d_axis_order_ppm(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDef_4d_axis_order_ppm" ):
                listener.exitDef_4d_axis_order_ppm(self)




    def def_4d_axis_order_ppm(self):

        localctx = OliviaPKParser.Def_4d_axis_order_ppmContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_def_4d_axis_order_ppm)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 655
            self.match(OliviaPKParser.X_ppm)
            self.state = 656
            self.match(OliviaPKParser.Y_ppm)
            self.state = 657
            self.match(OliviaPKParser.Z_ppm)
            self.state = 658
            self.match(OliviaPKParser.A_ppm)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tp_4d_axis_order_ppmContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def A_ppm(self):
            return self.getToken(OliviaPKParser.A_ppm, 0)

        def Z_ppm(self):
            return self.getToken(OliviaPKParser.Z_ppm, 0)

        def Y_ppm(self):
            return self.getToken(OliviaPKParser.Y_ppm, 0)

        def X_ppm(self):
            return self.getToken(OliviaPKParser.X_ppm, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_tp_4d_axis_order_ppm

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTp_4d_axis_order_ppm" ):
                listener.enterTp_4d_axis_order_ppm(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTp_4d_axis_order_ppm" ):
                listener.exitTp_4d_axis_order_ppm(self)




    def tp_4d_axis_order_ppm(self):

        localctx = OliviaPKParser.Tp_4d_axis_order_ppmContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_tp_4d_axis_order_ppm)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 660
            self.match(OliviaPKParser.A_ppm)
            self.state = 661
            self.match(OliviaPKParser.Z_ppm)
            self.state = 662
            self.match(OliviaPKParser.Y_ppm)
            self.state = 663
            self.match(OliviaPKParser.X_ppm)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Def_4d_axis_order_hzContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def X_hz(self):
            return self.getToken(OliviaPKParser.X_hz, 0)

        def Y_hz(self):
            return self.getToken(OliviaPKParser.Y_hz, 0)

        def Z_hz(self):
            return self.getToken(OliviaPKParser.Z_hz, 0)

        def A_hz(self):
            return self.getToken(OliviaPKParser.A_hz, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_def_4d_axis_order_hz

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDef_4d_axis_order_hz" ):
                listener.enterDef_4d_axis_order_hz(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDef_4d_axis_order_hz" ):
                listener.exitDef_4d_axis_order_hz(self)




    def def_4d_axis_order_hz(self):

        localctx = OliviaPKParser.Def_4d_axis_order_hzContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_def_4d_axis_order_hz)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 665
            self.match(OliviaPKParser.X_hz)
            self.state = 666
            self.match(OliviaPKParser.Y_hz)
            self.state = 667
            self.match(OliviaPKParser.Z_hz)
            self.state = 668
            self.match(OliviaPKParser.A_hz)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tp_4d_axis_order_hzContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def A_hz(self):
            return self.getToken(OliviaPKParser.A_hz, 0)

        def Z_hz(self):
            return self.getToken(OliviaPKParser.Z_hz, 0)

        def Y_hz(self):
            return self.getToken(OliviaPKParser.Y_hz, 0)

        def X_hz(self):
            return self.getToken(OliviaPKParser.X_hz, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_tp_4d_axis_order_hz

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTp_4d_axis_order_hz" ):
                listener.enterTp_4d_axis_order_hz(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTp_4d_axis_order_hz" ):
                listener.exitTp_4d_axis_order_hz(self)




    def tp_4d_axis_order_hz(self):

        localctx = OliviaPKParser.Tp_4d_axis_order_hzContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_tp_4d_axis_order_hz)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 670
            self.match(OliviaPKParser.A_hz)
            self.state = 671
            self.match(OliviaPKParser.Z_hz)
            self.state = 672
            self.match(OliviaPKParser.Y_hz)
            self.state = 673
            self.match(OliviaPKParser.X_hz)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StringContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Simple_name(self):
            return self.getToken(OliviaPKParser.Simple_name, 0)

        def Null_string(self):
            return self.getToken(OliviaPKParser.Null_string, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_string

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterString" ):
                listener.enterString(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitString" ):
                listener.exitString(self)




    def string(self):

        localctx = OliviaPKParser.StringContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_string)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 675
            _la = self._input.LA(1)
            if not(_la==6 or _la==15):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IntegerContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self):
            return self.getToken(OliviaPKParser.Integer, 0)

        def Null_string(self):
            return self.getToken(OliviaPKParser.Null_string, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_integer

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInteger" ):
                listener.enterInteger(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInteger" ):
                listener.exitInteger(self)




    def integer(self):

        localctx = OliviaPKParser.IntegerContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_integer)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 677
            _la = self._input.LA(1)
            if not(_la==6 or _la==7):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NumberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self):
            return self.getToken(OliviaPKParser.Integer, 0)

        def Float(self):
            return self.getToken(OliviaPKParser.Float, 0)

        def Real(self):
            return self.getToken(OliviaPKParser.Real, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)




    def number(self):

        localctx = OliviaPKParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 679
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 896) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MemoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Double_quote_string(self):
            return self.getToken(OliviaPKParser.Double_quote_string, 0)

        def Single_quote_string(self):
            return self.getToken(OliviaPKParser.Single_quote_string, 0)

        def Simple_name(self):
            return self.getToken(OliviaPKParser.Simple_name, 0)

        def getRuleIndex(self):
            return OliviaPKParser.RULE_memo

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMemo" ):
                listener.enterMemo(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMemo" ):
                listener.exitMemo(self)




    def memo(self):

        localctx = OliviaPKParser.MemoContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_memo)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 681
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 57344) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx






# Generated from SparkySPKParser.g4 by ANTLR 4.13.0
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
        4,1,151,611,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,
        7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,
        13,2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,1,
        0,1,0,1,0,1,0,1,0,4,0,46,8,0,11,0,12,0,47,1,0,1,0,1,1,1,1,5,1,54,
        8,1,10,1,12,1,57,9,1,1,1,1,1,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,
        1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,
        1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,2,99,8,2,1,
        2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,2,110,8,2,1,3,1,3,5,3,114,8,
        3,10,3,12,3,117,9,3,1,3,1,3,1,4,1,4,1,4,5,4,124,8,4,10,4,12,4,127,
        9,4,1,4,1,4,1,4,5,4,132,8,4,10,4,12,4,135,9,4,1,4,1,4,1,4,1,4,1,
        4,1,4,4,4,143,8,4,11,4,12,4,144,1,4,1,4,1,4,4,4,150,8,4,11,4,12,
        4,151,1,4,1,4,1,4,4,4,157,8,4,11,4,12,4,158,1,4,1,4,1,4,1,4,1,4,
        1,4,1,4,1,4,1,4,4,4,170,8,4,11,4,12,4,171,1,4,1,4,1,4,1,4,1,4,1,
        4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,
        4,1,4,5,4,197,8,4,10,4,12,4,200,9,4,1,4,1,4,1,4,4,4,205,8,4,11,4,
        12,4,206,1,4,1,4,1,4,4,4,212,8,4,11,4,12,4,213,1,4,1,4,1,4,1,4,1,
        4,1,4,1,4,1,4,1,4,4,4,225,8,4,11,4,12,4,226,1,4,1,4,1,4,4,4,232,
        8,4,11,4,12,4,233,1,4,1,4,1,4,4,4,239,8,4,11,4,12,4,240,1,4,1,4,
        1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,
        1,4,1,4,1,4,4,4,264,8,4,11,4,12,4,265,1,4,1,4,1,4,1,4,4,4,272,8,
        4,11,4,12,4,273,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,
        1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,
        1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,3,4,316,8,4,1,5,
        1,5,1,6,1,6,5,6,322,8,6,10,6,12,6,325,9,6,1,6,1,6,1,7,1,7,1,8,1,
        8,5,8,333,8,8,10,8,12,8,336,9,8,1,8,1,8,1,9,1,9,1,9,5,9,343,8,9,
        10,9,12,9,346,9,9,1,9,1,9,1,9,1,9,1,9,1,9,4,9,354,8,9,11,9,12,9,
        355,1,9,1,9,1,9,1,9,1,9,1,9,1,9,5,9,365,8,9,10,9,12,9,368,9,9,1,
        9,1,9,1,9,1,9,1,9,1,9,5,9,376,8,9,10,9,12,9,379,9,9,1,9,1,9,1,9,
        1,9,1,9,1,9,1,9,4,9,388,8,9,11,9,12,9,389,1,9,1,9,1,9,1,9,1,9,1,
        9,1,9,1,9,4,9,400,8,9,11,9,12,9,401,1,9,1,9,1,9,1,9,1,9,3,9,409,
        8,9,1,10,1,10,1,11,1,11,1,12,1,12,5,12,417,8,12,10,12,12,12,420,
        9,12,1,12,1,12,1,13,1,13,1,13,4,13,427,8,13,11,13,12,13,428,1,13,
        1,13,1,13,4,13,434,8,13,11,13,12,13,435,1,13,1,13,1,13,4,13,441,
        8,13,11,13,12,13,442,1,13,1,13,1,13,4,13,448,8,13,11,13,12,13,449,
        1,13,1,13,1,13,4,13,455,8,13,11,13,12,13,456,1,13,1,13,1,13,1,13,
        1,13,1,13,1,13,3,13,466,8,13,1,14,1,14,5,14,470,8,14,10,14,12,14,
        473,9,14,1,14,1,14,1,15,1,15,1,15,1,15,1,15,1,15,1,15,1,15,1,15,
        4,15,486,8,15,11,15,12,15,487,1,15,4,15,491,8,15,11,15,12,15,492,
        1,15,1,15,1,15,4,15,498,8,15,11,15,12,15,499,1,15,1,15,1,15,1,15,
        1,15,1,15,4,15,508,8,15,11,15,12,15,509,1,15,1,15,1,15,1,15,4,15,
        516,8,15,11,15,12,15,517,1,15,1,15,1,15,4,15,523,8,15,11,15,12,15,
        524,1,15,3,15,528,8,15,1,15,1,15,1,15,1,15,3,15,534,8,15,1,15,1,
        15,1,15,1,15,1,15,1,15,4,15,542,8,15,11,15,12,15,543,1,15,1,15,1,
        15,1,15,3,15,550,8,15,1,16,1,16,1,17,1,17,5,17,556,8,17,10,17,12,
        17,559,9,17,1,17,1,17,1,18,1,18,1,18,1,18,1,18,1,18,4,18,569,8,18,
        11,18,12,18,570,1,18,4,18,574,8,18,11,18,12,18,575,1,18,1,18,1,18,
        4,18,581,8,18,11,18,12,18,582,1,18,1,18,1,18,1,18,1,18,1,18,4,18,
        591,8,18,11,18,12,18,592,1,18,1,18,1,18,1,18,1,18,1,18,1,18,4,18,
        602,8,18,11,18,12,18,603,1,18,3,18,607,8,18,1,19,1,19,1,19,0,0,20,
        0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,0,7,2,0,20,
        20,26,26,1,0,75,78,1,0,95,98,1,0,95,97,1,0,129,130,1,0,143,145,1,
        0,147,148,727,0,45,1,0,0,0,2,51,1,0,0,0,4,109,1,0,0,0,6,111,1,0,
        0,0,8,315,1,0,0,0,10,317,1,0,0,0,12,319,1,0,0,0,14,328,1,0,0,0,16,
        330,1,0,0,0,18,408,1,0,0,0,20,410,1,0,0,0,22,412,1,0,0,0,24,414,
        1,0,0,0,26,465,1,0,0,0,28,467,1,0,0,0,30,549,1,0,0,0,32,551,1,0,
        0,0,34,553,1,0,0,0,36,606,1,0,0,0,38,608,1,0,0,0,40,41,5,1,0,0,41,
        42,5,2,0,0,42,43,3,2,1,0,43,44,3,6,3,0,44,46,1,0,0,0,45,40,1,0,0,
        0,46,47,1,0,0,0,47,45,1,0,0,0,47,48,1,0,0,0,48,49,1,0,0,0,49,50,
        5,0,0,1,50,1,1,0,0,0,51,55,5,3,0,0,52,54,3,4,2,0,53,52,1,0,0,0,54,
        57,1,0,0,0,55,53,1,0,0,0,55,56,1,0,0,0,56,58,1,0,0,0,57,55,1,0,0,
        0,58,59,5,10,0,0,59,3,1,0,0,0,60,110,5,28,0,0,61,62,5,11,0,0,62,
        63,5,12,0,0,63,64,5,24,0,0,64,110,5,28,0,0,65,66,5,11,0,0,66,67,
        5,13,0,0,67,68,5,24,0,0,68,110,5,28,0,0,69,70,5,11,0,0,70,71,5,14,
        0,0,71,72,5,24,0,0,72,110,5,28,0,0,73,74,5,11,0,0,74,75,5,15,0,0,
        75,76,5,24,0,0,76,110,5,28,0,0,77,78,5,11,0,0,78,79,5,16,0,0,79,
        80,5,24,0,0,80,110,5,28,0,0,81,82,5,11,0,0,82,83,5,17,0,0,83,84,
        5,24,0,0,84,110,5,28,0,0,85,86,5,11,0,0,86,87,5,18,0,0,87,88,5,24,
        0,0,88,110,5,28,0,0,89,90,5,19,0,0,90,91,5,20,0,0,91,92,5,21,0,0,
        92,93,7,0,0,0,93,110,5,28,0,0,94,95,5,19,0,0,95,96,5,20,0,0,96,98,
        5,22,0,0,97,99,5,26,0,0,98,97,1,0,0,0,98,99,1,0,0,0,99,100,1,0,0,
        0,100,110,5,28,0,0,101,102,5,19,0,0,102,103,5,20,0,0,103,104,5,23,
        0,0,104,105,5,24,0,0,105,106,5,24,0,0,106,107,5,25,0,0,107,108,5,
        25,0,0,108,110,5,28,0,0,109,60,1,0,0,0,109,61,1,0,0,0,109,65,1,0,
        0,0,109,69,1,0,0,0,109,73,1,0,0,0,109,77,1,0,0,0,109,81,1,0,0,0,
        109,85,1,0,0,0,109,89,1,0,0,0,109,94,1,0,0,0,109,101,1,0,0,0,110,
        5,1,0,0,0,111,115,5,4,0,0,112,114,3,8,4,0,113,112,1,0,0,0,114,117,
        1,0,0,0,115,113,1,0,0,0,115,116,1,0,0,0,116,118,1,0,0,0,117,115,
        1,0,0,0,118,119,5,32,0,0,119,7,1,0,0,0,120,316,5,80,0,0,121,125,
        5,33,0,0,122,124,3,10,5,0,123,122,1,0,0,0,124,127,1,0,0,0,125,123,
        1,0,0,0,125,126,1,0,0,0,126,128,1,0,0,0,127,125,1,0,0,0,128,316,
        5,80,0,0,129,133,5,34,0,0,130,132,3,10,5,0,131,130,1,0,0,0,132,135,
        1,0,0,0,133,131,1,0,0,0,133,134,1,0,0,0,134,136,1,0,0,0,135,133,
        1,0,0,0,136,316,5,80,0,0,137,138,5,35,0,0,138,139,5,75,0,0,139,316,
        5,80,0,0,140,142,5,36,0,0,141,143,5,76,0,0,142,141,1,0,0,0,143,144,
        1,0,0,0,144,142,1,0,0,0,144,145,1,0,0,0,145,146,1,0,0,0,146,316,
        5,80,0,0,147,149,5,37,0,0,148,150,5,75,0,0,149,148,1,0,0,0,150,151,
        1,0,0,0,151,149,1,0,0,0,151,152,1,0,0,0,152,153,1,0,0,0,153,316,
        5,80,0,0,154,156,5,38,0,0,155,157,5,75,0,0,156,155,1,0,0,0,157,158,
        1,0,0,0,158,156,1,0,0,0,158,159,1,0,0,0,159,160,1,0,0,0,160,316,
        5,80,0,0,161,162,5,39,0,0,162,163,5,75,0,0,163,316,5,80,0,0,164,
        165,5,40,0,0,165,166,5,76,0,0,166,316,5,80,0,0,167,169,5,41,0,0,
        168,170,5,75,0,0,169,168,1,0,0,0,170,171,1,0,0,0,171,169,1,0,0,0,
        171,172,1,0,0,0,172,173,1,0,0,0,173,316,5,80,0,0,174,175,5,42,0,
        0,175,176,5,75,0,0,176,177,5,76,0,0,177,316,5,80,0,0,178,179,5,43,
        0,0,179,180,5,74,0,0,180,316,5,80,0,0,181,182,5,44,0,0,182,183,5,
        45,0,0,183,184,5,77,0,0,184,316,5,80,0,0,185,186,5,44,0,0,186,187,
        5,46,0,0,187,188,5,77,0,0,188,316,5,80,0,0,189,190,5,44,0,0,190,
        191,5,47,0,0,191,192,5,77,0,0,192,316,5,80,0,0,193,194,5,44,0,0,
        194,198,5,48,0,0,195,197,5,77,0,0,196,195,1,0,0,0,197,200,1,0,0,
        0,198,196,1,0,0,0,198,199,1,0,0,0,199,201,1,0,0,0,200,198,1,0,0,
        0,201,316,5,80,0,0,202,204,5,49,0,0,203,205,5,76,0,0,204,203,1,0,
        0,0,205,206,1,0,0,0,206,204,1,0,0,0,206,207,1,0,0,0,207,208,1,0,
        0,0,208,316,5,80,0,0,209,211,5,50,0,0,210,212,5,75,0,0,211,210,1,
        0,0,0,212,213,1,0,0,0,213,211,1,0,0,0,213,214,1,0,0,0,214,215,1,
        0,0,0,215,316,5,80,0,0,216,217,5,51,0,0,217,218,5,75,0,0,218,316,
        5,80,0,0,219,220,5,52,0,0,220,221,5,75,0,0,221,316,5,80,0,0,222,
        224,5,53,0,0,223,225,5,76,0,0,224,223,1,0,0,0,225,226,1,0,0,0,226,
        224,1,0,0,0,226,227,1,0,0,0,227,228,1,0,0,0,228,316,5,80,0,0,229,
        231,5,54,0,0,230,232,5,76,0,0,231,230,1,0,0,0,232,233,1,0,0,0,233,
        231,1,0,0,0,233,234,1,0,0,0,234,235,1,0,0,0,235,316,5,80,0,0,236,
        238,5,55,0,0,237,239,5,76,0,0,238,237,1,0,0,0,239,240,1,0,0,0,240,
        238,1,0,0,0,240,241,1,0,0,0,241,242,1,0,0,0,242,316,5,80,0,0,243,
        244,5,56,0,0,244,245,5,75,0,0,245,316,5,80,0,0,246,247,5,57,0,0,
        247,248,5,75,0,0,248,316,5,80,0,0,249,250,5,58,0,0,250,251,5,75,
        0,0,251,316,5,80,0,0,252,253,5,59,0,0,253,254,5,75,0,0,254,316,5,
        80,0,0,255,256,5,60,0,0,256,257,5,75,0,0,257,316,5,80,0,0,258,259,
        5,61,0,0,259,260,5,76,0,0,260,316,5,80,0,0,261,263,5,62,0,0,262,
        264,5,76,0,0,263,262,1,0,0,0,264,265,1,0,0,0,265,263,1,0,0,0,265,
        266,1,0,0,0,266,267,1,0,0,0,267,268,5,75,0,0,268,316,5,80,0,0,269,
        271,5,63,0,0,270,272,5,76,0,0,271,270,1,0,0,0,272,273,1,0,0,0,273,
        271,1,0,0,0,273,274,1,0,0,0,274,275,1,0,0,0,275,316,5,80,0,0,276,
        277,5,64,0,0,277,278,5,76,0,0,278,316,5,80,0,0,279,280,5,65,0,0,
        280,281,5,76,0,0,281,316,5,80,0,0,282,283,5,66,0,0,283,284,5,76,
        0,0,284,316,5,80,0,0,285,286,5,67,0,0,286,287,5,76,0,0,287,316,5,
        80,0,0,288,289,5,68,0,0,289,290,5,76,0,0,290,316,5,80,0,0,291,292,
        5,69,0,0,292,293,5,76,0,0,293,316,5,80,0,0,294,295,5,70,0,0,295,
        296,5,76,0,0,296,316,5,80,0,0,297,298,5,71,0,0,298,299,5,76,0,0,
        299,316,5,80,0,0,300,301,5,72,0,0,301,302,5,76,0,0,302,316,5,80,
        0,0,303,304,5,73,0,0,304,305,5,76,0,0,305,316,5,80,0,0,306,307,3,
        12,6,0,307,308,5,80,0,0,308,316,1,0,0,0,309,310,3,16,8,0,310,311,
        5,80,0,0,311,316,1,0,0,0,312,313,3,28,14,0,313,314,5,80,0,0,314,
        316,1,0,0,0,315,120,1,0,0,0,315,121,1,0,0,0,315,129,1,0,0,0,315,
        137,1,0,0,0,315,140,1,0,0,0,315,147,1,0,0,0,315,154,1,0,0,0,315,
        161,1,0,0,0,315,164,1,0,0,0,315,167,1,0,0,0,315,174,1,0,0,0,315,
        178,1,0,0,0,315,181,1,0,0,0,315,185,1,0,0,0,315,189,1,0,0,0,315,
        193,1,0,0,0,315,202,1,0,0,0,315,209,1,0,0,0,315,216,1,0,0,0,315,
        219,1,0,0,0,315,222,1,0,0,0,315,229,1,0,0,0,315,236,1,0,0,0,315,
        243,1,0,0,0,315,246,1,0,0,0,315,249,1,0,0,0,315,252,1,0,0,0,315,
        255,1,0,0,0,315,258,1,0,0,0,315,261,1,0,0,0,315,269,1,0,0,0,315,
        276,1,0,0,0,315,279,1,0,0,0,315,282,1,0,0,0,315,285,1,0,0,0,315,
        288,1,0,0,0,315,291,1,0,0,0,315,294,1,0,0,0,315,297,1,0,0,0,315,
        300,1,0,0,0,315,303,1,0,0,0,315,306,1,0,0,0,315,309,1,0,0,0,315,
        312,1,0,0,0,316,9,1,0,0,0,317,318,7,1,0,0,318,11,1,0,0,0,319,323,
        5,29,0,0,320,322,3,14,7,0,321,320,1,0,0,0,322,325,1,0,0,0,323,321,
        1,0,0,0,323,324,1,0,0,0,324,326,1,0,0,0,325,323,1,0,0,0,326,327,
        5,81,0,0,327,13,1,0,0,0,328,329,5,82,0,0,329,15,1,0,0,0,330,334,
        5,30,0,0,331,333,3,18,9,0,332,331,1,0,0,0,333,336,1,0,0,0,334,332,
        1,0,0,0,334,335,1,0,0,0,335,337,1,0,0,0,336,334,1,0,0,0,337,338,
        5,85,0,0,338,17,1,0,0,0,339,409,5,100,0,0,340,344,5,86,0,0,341,343,
        3,20,10,0,342,341,1,0,0,0,343,346,1,0,0,0,344,342,1,0,0,0,344,345,
        1,0,0,0,345,347,1,0,0,0,346,344,1,0,0,0,347,409,5,100,0,0,348,349,
        5,87,0,0,349,350,5,95,0,0,350,409,5,100,0,0,351,353,5,88,0,0,352,
        354,5,95,0,0,353,352,1,0,0,0,354,355,1,0,0,0,355,353,1,0,0,0,355,
        356,1,0,0,0,356,357,1,0,0,0,357,409,5,100,0,0,358,359,5,89,0,0,359,
        360,5,95,0,0,360,409,5,100,0,0,361,362,5,90,0,0,362,366,5,95,0,0,
        363,365,5,98,0,0,364,363,1,0,0,0,365,368,1,0,0,0,366,364,1,0,0,0,
        366,367,1,0,0,0,367,369,1,0,0,0,368,366,1,0,0,0,369,409,5,100,0,
        0,370,371,5,91,0,0,371,372,5,95,0,0,372,409,5,100,0,0,373,377,5,
        92,0,0,374,376,5,98,0,0,375,374,1,0,0,0,376,379,1,0,0,0,377,375,
        1,0,0,0,377,378,1,0,0,0,378,380,1,0,0,0,379,377,1,0,0,0,380,409,
        5,100,0,0,381,382,5,93,0,0,382,383,5,95,0,0,383,384,3,22,11,0,384,
        385,5,96,0,0,385,387,5,96,0,0,386,388,5,98,0,0,387,386,1,0,0,0,388,
        389,1,0,0,0,389,387,1,0,0,0,389,390,1,0,0,0,390,391,1,0,0,0,391,
        392,5,100,0,0,392,409,1,0,0,0,393,394,5,94,0,0,394,395,5,95,0,0,
        395,396,3,22,11,0,396,397,5,96,0,0,397,399,5,96,0,0,398,400,5,98,
        0,0,399,398,1,0,0,0,400,401,1,0,0,0,401,399,1,0,0,0,401,402,1,0,
        0,0,402,403,1,0,0,0,403,404,5,100,0,0,404,409,1,0,0,0,405,406,3,
        24,12,0,406,407,5,100,0,0,407,409,1,0,0,0,408,339,1,0,0,0,408,340,
        1,0,0,0,408,348,1,0,0,0,408,351,1,0,0,0,408,358,1,0,0,0,408,361,
        1,0,0,0,408,370,1,0,0,0,408,373,1,0,0,0,408,381,1,0,0,0,408,393,
        1,0,0,0,408,405,1,0,0,0,409,19,1,0,0,0,410,411,7,2,0,0,411,21,1,
        0,0,0,412,413,7,3,0,0,413,23,1,0,0,0,414,418,5,84,0,0,415,417,3,
        26,13,0,416,415,1,0,0,0,417,420,1,0,0,0,418,416,1,0,0,0,418,419,
        1,0,0,0,419,421,1,0,0,0,420,418,1,0,0,0,421,422,5,101,0,0,422,25,
        1,0,0,0,423,466,5,113,0,0,424,426,5,102,0,0,425,427,5,109,0,0,426,
        425,1,0,0,0,427,428,1,0,0,0,428,426,1,0,0,0,428,429,1,0,0,0,429,
        430,1,0,0,0,430,466,5,113,0,0,431,433,5,103,0,0,432,434,5,109,0,
        0,433,432,1,0,0,0,434,435,1,0,0,0,435,433,1,0,0,0,435,436,1,0,0,
        0,436,437,1,0,0,0,437,466,5,113,0,0,438,440,5,104,0,0,439,441,5,
        109,0,0,440,439,1,0,0,0,441,442,1,0,0,0,442,440,1,0,0,0,442,443,
        1,0,0,0,443,444,1,0,0,0,444,466,5,113,0,0,445,447,5,105,0,0,446,
        448,5,110,0,0,447,446,1,0,0,0,448,449,1,0,0,0,449,447,1,0,0,0,449,
        450,1,0,0,0,450,451,1,0,0,0,451,466,5,113,0,0,452,454,5,106,0,0,
        453,455,5,110,0,0,454,453,1,0,0,0,455,456,1,0,0,0,456,454,1,0,0,
        0,456,457,1,0,0,0,457,458,1,0,0,0,458,466,5,113,0,0,459,460,5,107,
        0,0,460,461,5,110,0,0,461,466,5,113,0,0,462,463,5,108,0,0,463,464,
        5,109,0,0,464,466,5,113,0,0,465,423,1,0,0,0,465,424,1,0,0,0,465,
        431,1,0,0,0,465,438,1,0,0,0,465,445,1,0,0,0,465,452,1,0,0,0,465,
        459,1,0,0,0,465,462,1,0,0,0,466,27,1,0,0,0,467,471,5,31,0,0,468,
        470,3,30,15,0,469,468,1,0,0,0,470,473,1,0,0,0,471,469,1,0,0,0,471,
        472,1,0,0,0,472,474,1,0,0,0,473,471,1,0,0,0,474,475,5,115,0,0,475,
        29,1,0,0,0,476,550,5,134,0,0,477,478,5,116,0,0,478,479,5,117,0,0,
        479,550,5,134,0,0,480,481,5,116,0,0,481,482,5,118,0,0,482,550,5,
        134,0,0,483,485,5,119,0,0,484,486,5,129,0,0,485,484,1,0,0,0,486,
        487,1,0,0,0,487,485,1,0,0,0,487,488,1,0,0,0,488,490,1,0,0,0,489,
        491,5,132,0,0,490,489,1,0,0,0,491,492,1,0,0,0,492,490,1,0,0,0,492,
        493,1,0,0,0,493,494,1,0,0,0,494,550,5,134,0,0,495,497,5,120,0,0,
        496,498,5,129,0,0,497,496,1,0,0,0,498,499,1,0,0,0,499,497,1,0,0,
        0,499,500,1,0,0,0,500,501,1,0,0,0,501,550,5,134,0,0,502,503,5,121,
        0,0,503,504,5,129,0,0,504,550,5,134,0,0,505,507,5,122,0,0,506,508,
        3,32,16,0,507,506,1,0,0,0,508,509,1,0,0,0,509,507,1,0,0,0,509,510,
        1,0,0,0,510,511,1,0,0,0,511,512,5,134,0,0,512,550,1,0,0,0,513,515,
        5,123,0,0,514,516,5,130,0,0,515,514,1,0,0,0,516,517,1,0,0,0,517,
        515,1,0,0,0,517,518,1,0,0,0,518,519,1,0,0,0,519,550,5,134,0,0,520,
        522,5,124,0,0,521,523,5,130,0,0,522,521,1,0,0,0,523,524,1,0,0,0,
        524,522,1,0,0,0,524,525,1,0,0,0,525,527,1,0,0,0,526,528,5,132,0,
        0,527,526,1,0,0,0,527,528,1,0,0,0,528,529,1,0,0,0,529,550,5,134,
        0,0,530,531,5,125,0,0,531,533,5,131,0,0,532,534,5,132,0,0,533,532,
        1,0,0,0,533,534,1,0,0,0,534,535,1,0,0,0,535,550,5,134,0,0,536,537,
        5,126,0,0,537,538,5,130,0,0,538,550,5,134,0,0,539,541,5,127,0,0,
        540,542,5,128,0,0,541,540,1,0,0,0,542,543,1,0,0,0,543,541,1,0,0,
        0,543,544,1,0,0,0,544,545,1,0,0,0,545,550,5,134,0,0,546,547,3,34,
        17,0,547,548,5,134,0,0,548,550,1,0,0,0,549,476,1,0,0,0,549,477,1,
        0,0,0,549,480,1,0,0,0,549,483,1,0,0,0,549,495,1,0,0,0,549,502,1,
        0,0,0,549,505,1,0,0,0,549,513,1,0,0,0,549,520,1,0,0,0,549,530,1,
        0,0,0,549,536,1,0,0,0,549,539,1,0,0,0,549,546,1,0,0,0,550,31,1,0,
        0,0,551,552,7,4,0,0,552,33,1,0,0,0,553,557,5,114,0,0,554,556,3,36,
        18,0,555,554,1,0,0,0,556,559,1,0,0,0,557,555,1,0,0,0,557,558,1,0,
        0,0,558,560,1,0,0,0,559,557,1,0,0,0,560,561,5,135,0,0,561,35,1,0,
        0,0,562,607,5,151,0,0,563,564,5,136,0,0,564,565,5,137,0,0,565,607,
        5,151,0,0,566,568,5,138,0,0,567,569,5,147,0,0,568,567,1,0,0,0,569,
        570,1,0,0,0,570,568,1,0,0,0,570,571,1,0,0,0,571,573,1,0,0,0,572,
        574,5,149,0,0,573,572,1,0,0,0,574,575,1,0,0,0,575,573,1,0,0,0,575,
        576,1,0,0,0,576,577,1,0,0,0,577,607,5,151,0,0,578,580,5,139,0,0,
        579,581,5,147,0,0,580,579,1,0,0,0,581,582,1,0,0,0,582,580,1,0,0,
        0,582,583,1,0,0,0,583,584,1,0,0,0,584,607,5,151,0,0,585,586,5,140,
        0,0,586,587,5,147,0,0,587,607,5,151,0,0,588,590,5,141,0,0,589,591,
        3,38,19,0,590,589,1,0,0,0,591,592,1,0,0,0,592,590,1,0,0,0,592,593,
        1,0,0,0,593,594,1,0,0,0,594,595,5,151,0,0,595,607,1,0,0,0,596,597,
        5,137,0,0,597,598,7,5,0,0,598,607,5,151,0,0,599,601,5,142,0,0,600,
        602,5,146,0,0,601,600,1,0,0,0,602,603,1,0,0,0,603,601,1,0,0,0,603,
        604,1,0,0,0,604,605,1,0,0,0,605,607,5,151,0,0,606,562,1,0,0,0,606,
        563,1,0,0,0,606,566,1,0,0,0,606,578,1,0,0,0,606,585,1,0,0,0,606,
        588,1,0,0,0,606,596,1,0,0,0,606,599,1,0,0,0,607,37,1,0,0,0,608,609,
        7,6,0,0,609,39,1,0,0,0,54,47,55,98,109,115,125,133,144,151,158,171,
        198,206,213,226,233,240,265,273,315,323,334,344,355,366,377,389,
        401,408,418,428,435,442,449,456,465,471,487,492,499,509,517,524,
        527,533,543,549,557,570,575,582,592,603,606
    ]

class SparkySPKParser ( Parser ):

    grammarFileName = "SparkySPKParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'<sparky save file>'", "<INVALID>", "'<user>'", 
                     "'<spectrum>'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'<end user>'", "'set'", 
                     "<INVALID>", "'saveprompt'", "'saveinterval'", "'resizeViews'", 
                     "'keytimeout'", "'cachesize'", "'contourgraying'", 
                     "'default'", "'print'", "'command'", "'file'", "'options'", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'<attached data>'", "'<view>'", "'<ornament>'", 
                     "'<end spectrum>'", "<INVALID>", "'pathname'", "'dimension'", 
                     "'shift'", "'points'", "'extraPeakPlanes'", "'assignMultiAxisGuess'", 
                     "'assignGuessThreshold'", "'assignRelation'", "'assignRange'", 
                     "'assignFormat'", "'listTool'", "'sortBy'", "'nameType'", 
                     "'sortAxis'", "'showFlags'", "'integrate.overlapped_sep'", 
                     "'integrate.methods'", "'integrate.allow_motion'", 
                     "'integrate.adjust_linewidths'", "'integrate.motion_range'", 
                     "'integrate.min_linewidth'", "'integrate.max_linewidth'", 
                     "'integrate.fit_baseline'", "'integrate.subtract_peaks'", 
                     "'integrate.contoured_data'", "'integrate.rectangle_data'", 
                     "'integrate.maxiterations'", "'integrate.tolerance'", 
                     "'peak.pick'", "'peak.pick-minimum-linewidth'", "'peak.pick-minimum-dropoff'", 
                     "'noise.sigma'", "'ornament.label.size'", "'ornament.line.size'", 
                     "'ornament.peak.size'", "'ornament.grid.size'", "'ornament.peakgroup.size'", 
                     "'ornament.selectsize'", "'ornament.pointersize'", 
                     "'ornament.lineendsize'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'<end attached data>'", "<INVALID>", 
                     "<INVALID>", "'<params>'", "'<end view>'", "<INVALID>", 
                     "'precision'", "'precision_by_units'", "'viewmode'", 
                     "'show'", "'axistype'", "<INVALID>", "'contour.pos'", 
                     "'contour.neg'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "'<end params>'", 
                     "'orientation'", "'location'", "'size'", "'offset'", 
                     "'scale'", "'zoom'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "'['", "'<end ornament>'", 
                     "<INVALID>", "'peak'", "'grid'", "<INVALID>", "<INVALID>", 
                     "'id'", "<INVALID>", "'height'", "'linewidth'", "'integral'", 
                     "'fr'", "'rs'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "']'", "<INVALID>", "'label'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'xy'" ]

    symbolicNames = [ "<INVALID>", "Sparky_save_file", "Version", "User", 
                      "Spectrum", "Integer", "Float", "Real", "Simple_name", 
                      "SPACE", "End_user", "Set", "Mode_US", "Save_prompt", 
                      "Save_interval", "Resize_views", "Key_timeout", "Cache_size", 
                      "Contour_graying", "Default", "Print", "Command", 
                      "File", "Options", "Integer_US", "Float_US", "Simple_name_US", 
                      "SPACE_US", "RETURN_US", "Attached_data", "View", 
                      "Ornament", "End_spectrum", "Name_SP", "Path_name", 
                      "Dimension", "Shift", "Points", "Extra_peak_planes", 
                      "Assign_multi_axis_guess", "Assign_guess_threshhold", 
                      "Assign_relation", "Assign_range", "Assign_format", 
                      "List_tool", "Sort_by", "Name_type", "Sort_axis", 
                      "Show_flags", "Integrate_overlapped_sep", "Integrate_methods", 
                      "Integrate_allow_motion", "Integrate_adjust_linewidths", 
                      "Integrate_motion_range", "Integrate_min_linewidth", 
                      "Integrate_max_linewidth", "Integrate_fit_baseline", 
                      "Integrate_subtract_peaks", "Integrate_contoured_data", 
                      "Integrate_rectangle_data", "Integrate_max_iterations", 
                      "Integrate_tolerance", "Peak_pick", "Peak_pick_minimum_linewidth", 
                      "Peak_pick_minimum_dropoff", "Noise_sigma", "Ornament_labe_size", 
                      "Ornament_line_size", "Ornament_peak_size", "Ornament_grid_size", 
                      "Ornament_peak_group_size", "Ornament_select_size", 
                      "Ornament_pointer_size", "Ornament_line_end_size", 
                      "Format_ex", "Integer_SP", "Float_SP", "Simple_name_SP", 
                      "Any_name_SP", "SPACE_SP", "RETURN_SP", "End_attached_data", 
                      "Any_name_AD", "SPACE_AD", "Params", "End_view", "Name_VI", 
                      "Precision", "Precision_by_units", "View_mode", "Show", 
                      "Axis_type", "Flags_VI", "Contour_pos", "Contour_neg", 
                      "Integer_VI", "Float_VI", "Real_VI", "Simple_name_VI", 
                      "SPACE_VI", "RETURN_VI", "End_params", "Orientation", 
                      "Location", "Size", "Offset", "Scale", "Zoom", "Flags_PA", 
                      "Integer_PA", "Float_PA", "Simple_name_PA", "SPACE_PA", 
                      "RETURN_PA", "L_brakt", "End_ornament", "Type_OR", 
                      "Peak", "Grid", "Color_OR", "Flags_OR", "Id", "Pos_OR", 
                      "Height", "Line_width", "Integral", "Fr", "Rs", "Rs_ex", 
                      "Integer_OR", "Float_OR", "Real_OR", "Simple_name_OR", 
                      "SPACE_OR", "RETURN_OR", "R_brakt", "Type_LA", "Label", 
                      "Color_LA", "Flags_LA", "Mode_LA", "Pos_LA", "Xy", 
                      "Assignment_2d_ex", "Assignment_3d_ex", "Assignment_4d_ex", 
                      "Xy_pos", "Integer_LA", "Float_LA", "Simple_name_LA", 
                      "SPACE_LA", "RETURN_LA" ]

    RULE_sparky_spk = 0
    RULE_user_block = 1
    RULE_user_statement = 2
    RULE_spectrum_block = 3
    RULE_spectrum_statement = 4
    RULE_spectrum_name = 5
    RULE_attached_data = 6
    RULE_attached_data_statement = 7
    RULE_view = 8
    RULE_view_statement = 9
    RULE_view_name = 10
    RULE_view_number = 11
    RULE_params = 12
    RULE_params_statement = 13
    RULE_ornament = 14
    RULE_ornament_statement = 15
    RULE_ornament_position = 16
    RULE_label = 17
    RULE_label_statement = 18
    RULE_label_position = 19

    ruleNames =  [ "sparky_spk", "user_block", "user_statement", "spectrum_block", 
                   "spectrum_statement", "spectrum_name", "attached_data", 
                   "attached_data_statement", "view", "view_statement", 
                   "view_name", "view_number", "params", "params_statement", 
                   "ornament", "ornament_statement", "ornament_position", 
                   "label", "label_statement", "label_position" ]

    EOF = Token.EOF
    Sparky_save_file=1
    Version=2
    User=3
    Spectrum=4
    Integer=5
    Float=6
    Real=7
    Simple_name=8
    SPACE=9
    End_user=10
    Set=11
    Mode_US=12
    Save_prompt=13
    Save_interval=14
    Resize_views=15
    Key_timeout=16
    Cache_size=17
    Contour_graying=18
    Default=19
    Print=20
    Command=21
    File=22
    Options=23
    Integer_US=24
    Float_US=25
    Simple_name_US=26
    SPACE_US=27
    RETURN_US=28
    Attached_data=29
    View=30
    Ornament=31
    End_spectrum=32
    Name_SP=33
    Path_name=34
    Dimension=35
    Shift=36
    Points=37
    Extra_peak_planes=38
    Assign_multi_axis_guess=39
    Assign_guess_threshhold=40
    Assign_relation=41
    Assign_range=42
    Assign_format=43
    List_tool=44
    Sort_by=45
    Name_type=46
    Sort_axis=47
    Show_flags=48
    Integrate_overlapped_sep=49
    Integrate_methods=50
    Integrate_allow_motion=51
    Integrate_adjust_linewidths=52
    Integrate_motion_range=53
    Integrate_min_linewidth=54
    Integrate_max_linewidth=55
    Integrate_fit_baseline=56
    Integrate_subtract_peaks=57
    Integrate_contoured_data=58
    Integrate_rectangle_data=59
    Integrate_max_iterations=60
    Integrate_tolerance=61
    Peak_pick=62
    Peak_pick_minimum_linewidth=63
    Peak_pick_minimum_dropoff=64
    Noise_sigma=65
    Ornament_labe_size=66
    Ornament_line_size=67
    Ornament_peak_size=68
    Ornament_grid_size=69
    Ornament_peak_group_size=70
    Ornament_select_size=71
    Ornament_pointer_size=72
    Ornament_line_end_size=73
    Format_ex=74
    Integer_SP=75
    Float_SP=76
    Simple_name_SP=77
    Any_name_SP=78
    SPACE_SP=79
    RETURN_SP=80
    End_attached_data=81
    Any_name_AD=82
    SPACE_AD=83
    Params=84
    End_view=85
    Name_VI=86
    Precision=87
    Precision_by_units=88
    View_mode=89
    Show=90
    Axis_type=91
    Flags_VI=92
    Contour_pos=93
    Contour_neg=94
    Integer_VI=95
    Float_VI=96
    Real_VI=97
    Simple_name_VI=98
    SPACE_VI=99
    RETURN_VI=100
    End_params=101
    Orientation=102
    Location=103
    Size=104
    Offset=105
    Scale=106
    Zoom=107
    Flags_PA=108
    Integer_PA=109
    Float_PA=110
    Simple_name_PA=111
    SPACE_PA=112
    RETURN_PA=113
    L_brakt=114
    End_ornament=115
    Type_OR=116
    Peak=117
    Grid=118
    Color_OR=119
    Flags_OR=120
    Id=121
    Pos_OR=122
    Height=123
    Line_width=124
    Integral=125
    Fr=126
    Rs=127
    Rs_ex=128
    Integer_OR=129
    Float_OR=130
    Real_OR=131
    Simple_name_OR=132
    SPACE_OR=133
    RETURN_OR=134
    R_brakt=135
    Type_LA=136
    Label=137
    Color_LA=138
    Flags_LA=139
    Mode_LA=140
    Pos_LA=141
    Xy=142
    Assignment_2d_ex=143
    Assignment_3d_ex=144
    Assignment_4d_ex=145
    Xy_pos=146
    Integer_LA=147
    Float_LA=148
    Simple_name_LA=149
    SPACE_LA=150
    RETURN_LA=151

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Sparky_spkContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(SparkySPKParser.EOF, 0)

        def Sparky_save_file(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Sparky_save_file)
            else:
                return self.getToken(SparkySPKParser.Sparky_save_file, i)

        def Version(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Version)
            else:
                return self.getToken(SparkySPKParser.Version, i)

        def user_block(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SparkySPKParser.User_blockContext)
            else:
                return self.getTypedRuleContext(SparkySPKParser.User_blockContext,i)


        def spectrum_block(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SparkySPKParser.Spectrum_blockContext)
            else:
                return self.getTypedRuleContext(SparkySPKParser.Spectrum_blockContext,i)


        def getRuleIndex(self):
            return SparkySPKParser.RULE_sparky_spk

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSparky_spk" ):
                listener.enterSparky_spk(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSparky_spk" ):
                listener.exitSparky_spk(self)




    def sparky_spk(self):

        localctx = SparkySPKParser.Sparky_spkContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_sparky_spk)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 45 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 40
                self.match(SparkySPKParser.Sparky_save_file)
                self.state = 41
                self.match(SparkySPKParser.Version)
                self.state = 42
                self.user_block()
                self.state = 43
                self.spectrum_block()
                self.state = 47 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==1):
                    break

            self.state = 49
            self.match(SparkySPKParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class User_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def User(self):
            return self.getToken(SparkySPKParser.User, 0)

        def End_user(self):
            return self.getToken(SparkySPKParser.End_user, 0)

        def user_statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SparkySPKParser.User_statementContext)
            else:
                return self.getTypedRuleContext(SparkySPKParser.User_statementContext,i)


        def getRuleIndex(self):
            return SparkySPKParser.RULE_user_block

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUser_block" ):
                listener.enterUser_block(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUser_block" ):
                listener.exitUser_block(self)




    def user_block(self):

        localctx = SparkySPKParser.User_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_user_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 51
            self.match(SparkySPKParser.User)
            self.state = 55
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 268961792) != 0):
                self.state = 52
                self.user_statement()
                self.state = 57
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 58
            self.match(SparkySPKParser.End_user)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class User_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN_US(self):
            return self.getToken(SparkySPKParser.RETURN_US, 0)

        def Set(self):
            return self.getToken(SparkySPKParser.Set, 0)

        def Mode_US(self):
            return self.getToken(SparkySPKParser.Mode_US, 0)

        def Integer_US(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Integer_US)
            else:
                return self.getToken(SparkySPKParser.Integer_US, i)

        def Save_prompt(self):
            return self.getToken(SparkySPKParser.Save_prompt, 0)

        def Save_interval(self):
            return self.getToken(SparkySPKParser.Save_interval, 0)

        def Resize_views(self):
            return self.getToken(SparkySPKParser.Resize_views, 0)

        def Key_timeout(self):
            return self.getToken(SparkySPKParser.Key_timeout, 0)

        def Cache_size(self):
            return self.getToken(SparkySPKParser.Cache_size, 0)

        def Contour_graying(self):
            return self.getToken(SparkySPKParser.Contour_graying, 0)

        def Default(self):
            return self.getToken(SparkySPKParser.Default, 0)

        def Print(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Print)
            else:
                return self.getToken(SparkySPKParser.Print, i)

        def Command(self):
            return self.getToken(SparkySPKParser.Command, 0)

        def Simple_name_US(self):
            return self.getToken(SparkySPKParser.Simple_name_US, 0)

        def File(self):
            return self.getToken(SparkySPKParser.File, 0)

        def Options(self):
            return self.getToken(SparkySPKParser.Options, 0)

        def Float_US(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Float_US)
            else:
                return self.getToken(SparkySPKParser.Float_US, i)

        def getRuleIndex(self):
            return SparkySPKParser.RULE_user_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUser_statement" ):
                listener.enterUser_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUser_statement" ):
                listener.exitUser_statement(self)




    def user_statement(self):

        localctx = SparkySPKParser.User_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_user_statement)
        self._la = 0 # Token type
        try:
            self.state = 109
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 60
                self.match(SparkySPKParser.RETURN_US)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 61
                self.match(SparkySPKParser.Set)
                self.state = 62
                self.match(SparkySPKParser.Mode_US)
                self.state = 63
                self.match(SparkySPKParser.Integer_US)
                self.state = 64
                self.match(SparkySPKParser.RETURN_US)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 65
                self.match(SparkySPKParser.Set)
                self.state = 66
                self.match(SparkySPKParser.Save_prompt)
                self.state = 67
                self.match(SparkySPKParser.Integer_US)
                self.state = 68
                self.match(SparkySPKParser.RETURN_US)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 69
                self.match(SparkySPKParser.Set)
                self.state = 70
                self.match(SparkySPKParser.Save_interval)
                self.state = 71
                self.match(SparkySPKParser.Integer_US)
                self.state = 72
                self.match(SparkySPKParser.RETURN_US)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 73
                self.match(SparkySPKParser.Set)
                self.state = 74
                self.match(SparkySPKParser.Resize_views)
                self.state = 75
                self.match(SparkySPKParser.Integer_US)
                self.state = 76
                self.match(SparkySPKParser.RETURN_US)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 77
                self.match(SparkySPKParser.Set)
                self.state = 78
                self.match(SparkySPKParser.Key_timeout)
                self.state = 79
                self.match(SparkySPKParser.Integer_US)
                self.state = 80
                self.match(SparkySPKParser.RETURN_US)
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 81
                self.match(SparkySPKParser.Set)
                self.state = 82
                self.match(SparkySPKParser.Cache_size)
                self.state = 83
                self.match(SparkySPKParser.Integer_US)
                self.state = 84
                self.match(SparkySPKParser.RETURN_US)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 85
                self.match(SparkySPKParser.Set)
                self.state = 86
                self.match(SparkySPKParser.Contour_graying)
                self.state = 87
                self.match(SparkySPKParser.Integer_US)
                self.state = 88
                self.match(SparkySPKParser.RETURN_US)
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 89
                self.match(SparkySPKParser.Default)
                self.state = 90
                self.match(SparkySPKParser.Print)
                self.state = 91
                self.match(SparkySPKParser.Command)
                self.state = 92
                _la = self._input.LA(1)
                if not(_la==20 or _la==26):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 93
                self.match(SparkySPKParser.RETURN_US)
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 94
                self.match(SparkySPKParser.Default)
                self.state = 95
                self.match(SparkySPKParser.Print)
                self.state = 96
                self.match(SparkySPKParser.File)
                self.state = 98
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==26:
                    self.state = 97
                    self.match(SparkySPKParser.Simple_name_US)


                self.state = 100
                self.match(SparkySPKParser.RETURN_US)
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 101
                self.match(SparkySPKParser.Default)
                self.state = 102
                self.match(SparkySPKParser.Print)
                self.state = 103
                self.match(SparkySPKParser.Options)
                self.state = 104
                self.match(SparkySPKParser.Integer_US)
                self.state = 105
                self.match(SparkySPKParser.Integer_US)
                self.state = 106
                self.match(SparkySPKParser.Float_US)
                self.state = 107
                self.match(SparkySPKParser.Float_US)
                self.state = 108
                self.match(SparkySPKParser.RETURN_US)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Spectrum_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Spectrum(self):
            return self.getToken(SparkySPKParser.Spectrum, 0)

        def End_spectrum(self):
            return self.getToken(SparkySPKParser.End_spectrum, 0)

        def spectrum_statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SparkySPKParser.Spectrum_statementContext)
            else:
                return self.getTypedRuleContext(SparkySPKParser.Spectrum_statementContext,i)


        def getRuleIndex(self):
            return SparkySPKParser.RULE_spectrum_block

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSpectrum_block" ):
                listener.enterSpectrum_block(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSpectrum_block" ):
                listener.exitSpectrum_block(self)




    def spectrum_block(self):

        localctx = SparkySPKParser.Spectrum_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_spectrum_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 111
            self.match(SparkySPKParser.Spectrum)
            self.state = 115
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 29)) & ~0x3f) == 0 and ((1 << (_la - 29)) & 2286984184791031) != 0):
                self.state = 112
                self.spectrum_statement()
                self.state = 117
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 118
            self.match(SparkySPKParser.End_spectrum)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Spectrum_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN_SP(self):
            return self.getToken(SparkySPKParser.RETURN_SP, 0)

        def Name_SP(self):
            return self.getToken(SparkySPKParser.Name_SP, 0)

        def spectrum_name(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SparkySPKParser.Spectrum_nameContext)
            else:
                return self.getTypedRuleContext(SparkySPKParser.Spectrum_nameContext,i)


        def Path_name(self):
            return self.getToken(SparkySPKParser.Path_name, 0)

        def Dimension(self):
            return self.getToken(SparkySPKParser.Dimension, 0)

        def Integer_SP(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Integer_SP)
            else:
                return self.getToken(SparkySPKParser.Integer_SP, i)

        def Shift(self):
            return self.getToken(SparkySPKParser.Shift, 0)

        def Float_SP(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Float_SP)
            else:
                return self.getToken(SparkySPKParser.Float_SP, i)

        def Points(self):
            return self.getToken(SparkySPKParser.Points, 0)

        def Extra_peak_planes(self):
            return self.getToken(SparkySPKParser.Extra_peak_planes, 0)

        def Assign_multi_axis_guess(self):
            return self.getToken(SparkySPKParser.Assign_multi_axis_guess, 0)

        def Assign_guess_threshhold(self):
            return self.getToken(SparkySPKParser.Assign_guess_threshhold, 0)

        def Assign_relation(self):
            return self.getToken(SparkySPKParser.Assign_relation, 0)

        def Assign_range(self):
            return self.getToken(SparkySPKParser.Assign_range, 0)

        def Assign_format(self):
            return self.getToken(SparkySPKParser.Assign_format, 0)

        def Format_ex(self):
            return self.getToken(SparkySPKParser.Format_ex, 0)

        def List_tool(self):
            return self.getToken(SparkySPKParser.List_tool, 0)

        def Sort_by(self):
            return self.getToken(SparkySPKParser.Sort_by, 0)

        def Simple_name_SP(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Simple_name_SP)
            else:
                return self.getToken(SparkySPKParser.Simple_name_SP, i)

        def Name_type(self):
            return self.getToken(SparkySPKParser.Name_type, 0)

        def Sort_axis(self):
            return self.getToken(SparkySPKParser.Sort_axis, 0)

        def Show_flags(self):
            return self.getToken(SparkySPKParser.Show_flags, 0)

        def Integrate_overlapped_sep(self):
            return self.getToken(SparkySPKParser.Integrate_overlapped_sep, 0)

        def Integrate_methods(self):
            return self.getToken(SparkySPKParser.Integrate_methods, 0)

        def Integrate_allow_motion(self):
            return self.getToken(SparkySPKParser.Integrate_allow_motion, 0)

        def Integrate_adjust_linewidths(self):
            return self.getToken(SparkySPKParser.Integrate_adjust_linewidths, 0)

        def Integrate_motion_range(self):
            return self.getToken(SparkySPKParser.Integrate_motion_range, 0)

        def Integrate_min_linewidth(self):
            return self.getToken(SparkySPKParser.Integrate_min_linewidth, 0)

        def Integrate_max_linewidth(self):
            return self.getToken(SparkySPKParser.Integrate_max_linewidth, 0)

        def Integrate_fit_baseline(self):
            return self.getToken(SparkySPKParser.Integrate_fit_baseline, 0)

        def Integrate_subtract_peaks(self):
            return self.getToken(SparkySPKParser.Integrate_subtract_peaks, 0)

        def Integrate_contoured_data(self):
            return self.getToken(SparkySPKParser.Integrate_contoured_data, 0)

        def Integrate_rectangle_data(self):
            return self.getToken(SparkySPKParser.Integrate_rectangle_data, 0)

        def Integrate_max_iterations(self):
            return self.getToken(SparkySPKParser.Integrate_max_iterations, 0)

        def Integrate_tolerance(self):
            return self.getToken(SparkySPKParser.Integrate_tolerance, 0)

        def Peak_pick(self):
            return self.getToken(SparkySPKParser.Peak_pick, 0)

        def Peak_pick_minimum_linewidth(self):
            return self.getToken(SparkySPKParser.Peak_pick_minimum_linewidth, 0)

        def Peak_pick_minimum_dropoff(self):
            return self.getToken(SparkySPKParser.Peak_pick_minimum_dropoff, 0)

        def Noise_sigma(self):
            return self.getToken(SparkySPKParser.Noise_sigma, 0)

        def Ornament_labe_size(self):
            return self.getToken(SparkySPKParser.Ornament_labe_size, 0)

        def Ornament_line_size(self):
            return self.getToken(SparkySPKParser.Ornament_line_size, 0)

        def Ornament_peak_size(self):
            return self.getToken(SparkySPKParser.Ornament_peak_size, 0)

        def Ornament_grid_size(self):
            return self.getToken(SparkySPKParser.Ornament_grid_size, 0)

        def Ornament_peak_group_size(self):
            return self.getToken(SparkySPKParser.Ornament_peak_group_size, 0)

        def Ornament_select_size(self):
            return self.getToken(SparkySPKParser.Ornament_select_size, 0)

        def Ornament_pointer_size(self):
            return self.getToken(SparkySPKParser.Ornament_pointer_size, 0)

        def Ornament_line_end_size(self):
            return self.getToken(SparkySPKParser.Ornament_line_end_size, 0)

        def attached_data(self):
            return self.getTypedRuleContext(SparkySPKParser.Attached_dataContext,0)


        def view(self):
            return self.getTypedRuleContext(SparkySPKParser.ViewContext,0)


        def ornament(self):
            return self.getTypedRuleContext(SparkySPKParser.OrnamentContext,0)


        def getRuleIndex(self):
            return SparkySPKParser.RULE_spectrum_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSpectrum_statement" ):
                listener.enterSpectrum_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSpectrum_statement" ):
                listener.exitSpectrum_statement(self)




    def spectrum_statement(self):

        localctx = SparkySPKParser.Spectrum_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_spectrum_statement)
        self._la = 0 # Token type
        try:
            self.state = 315
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,19,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 120
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 121
                self.match(SparkySPKParser.Name_SP)
                self.state = 125
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while ((((_la - 75)) & ~0x3f) == 0 and ((1 << (_la - 75)) & 15) != 0):
                    self.state = 122
                    self.spectrum_name()
                    self.state = 127
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 128
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 129
                self.match(SparkySPKParser.Path_name)
                self.state = 133
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while ((((_la - 75)) & ~0x3f) == 0 and ((1 << (_la - 75)) & 15) != 0):
                    self.state = 130
                    self.spectrum_name()
                    self.state = 135
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 136
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 137
                self.match(SparkySPKParser.Dimension)
                self.state = 138
                self.match(SparkySPKParser.Integer_SP)
                self.state = 139
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 140
                self.match(SparkySPKParser.Shift)
                self.state = 142 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 141
                    self.match(SparkySPKParser.Float_SP)
                    self.state = 144 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==76):
                        break

                self.state = 146
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 147
                self.match(SparkySPKParser.Points)
                self.state = 149 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 148
                    self.match(SparkySPKParser.Integer_SP)
                    self.state = 151 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==75):
                        break

                self.state = 153
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 154
                self.match(SparkySPKParser.Extra_peak_planes)
                self.state = 156 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 155
                    self.match(SparkySPKParser.Integer_SP)
                    self.state = 158 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==75):
                        break

                self.state = 160
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 161
                self.match(SparkySPKParser.Assign_multi_axis_guess)
                self.state = 162
                self.match(SparkySPKParser.Integer_SP)
                self.state = 163
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 164
                self.match(SparkySPKParser.Assign_guess_threshhold)
                self.state = 165
                self.match(SparkySPKParser.Float_SP)
                self.state = 166
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 167
                self.match(SparkySPKParser.Assign_relation)
                self.state = 169 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 168
                    self.match(SparkySPKParser.Integer_SP)
                    self.state = 171 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==75):
                        break

                self.state = 173
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 174
                self.match(SparkySPKParser.Assign_range)
                self.state = 175
                self.match(SparkySPKParser.Integer_SP)
                self.state = 176
                self.match(SparkySPKParser.Float_SP)
                self.state = 177
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 178
                self.match(SparkySPKParser.Assign_format)
                self.state = 179
                self.match(SparkySPKParser.Format_ex)
                self.state = 180
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 13:
                self.enterOuterAlt(localctx, 13)
                self.state = 181
                self.match(SparkySPKParser.List_tool)
                self.state = 182
                self.match(SparkySPKParser.Sort_by)
                self.state = 183
                self.match(SparkySPKParser.Simple_name_SP)
                self.state = 184
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 14:
                self.enterOuterAlt(localctx, 14)
                self.state = 185
                self.match(SparkySPKParser.List_tool)
                self.state = 186
                self.match(SparkySPKParser.Name_type)
                self.state = 187
                self.match(SparkySPKParser.Simple_name_SP)
                self.state = 188
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 15:
                self.enterOuterAlt(localctx, 15)
                self.state = 189
                self.match(SparkySPKParser.List_tool)
                self.state = 190
                self.match(SparkySPKParser.Sort_axis)
                self.state = 191
                self.match(SparkySPKParser.Simple_name_SP)
                self.state = 192
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 16:
                self.enterOuterAlt(localctx, 16)
                self.state = 193
                self.match(SparkySPKParser.List_tool)
                self.state = 194
                self.match(SparkySPKParser.Show_flags)
                self.state = 198
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==77:
                    self.state = 195
                    self.match(SparkySPKParser.Simple_name_SP)
                    self.state = 200
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 201
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 17:
                self.enterOuterAlt(localctx, 17)
                self.state = 202
                self.match(SparkySPKParser.Integrate_overlapped_sep)
                self.state = 204 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 203
                    self.match(SparkySPKParser.Float_SP)
                    self.state = 206 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==76):
                        break

                self.state = 208
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 18:
                self.enterOuterAlt(localctx, 18)
                self.state = 209
                self.match(SparkySPKParser.Integrate_methods)
                self.state = 211 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 210
                    self.match(SparkySPKParser.Integer_SP)
                    self.state = 213 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==75):
                        break

                self.state = 215
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 19:
                self.enterOuterAlt(localctx, 19)
                self.state = 216
                self.match(SparkySPKParser.Integrate_allow_motion)
                self.state = 217
                self.match(SparkySPKParser.Integer_SP)
                self.state = 218
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 20:
                self.enterOuterAlt(localctx, 20)
                self.state = 219
                self.match(SparkySPKParser.Integrate_adjust_linewidths)
                self.state = 220
                self.match(SparkySPKParser.Integer_SP)
                self.state = 221
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 21:
                self.enterOuterAlt(localctx, 21)
                self.state = 222
                self.match(SparkySPKParser.Integrate_motion_range)
                self.state = 224 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 223
                    self.match(SparkySPKParser.Float_SP)
                    self.state = 226 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==76):
                        break

                self.state = 228
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 22:
                self.enterOuterAlt(localctx, 22)
                self.state = 229
                self.match(SparkySPKParser.Integrate_min_linewidth)
                self.state = 231 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 230
                    self.match(SparkySPKParser.Float_SP)
                    self.state = 233 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==76):
                        break

                self.state = 235
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 23:
                self.enterOuterAlt(localctx, 23)
                self.state = 236
                self.match(SparkySPKParser.Integrate_max_linewidth)
                self.state = 238 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 237
                    self.match(SparkySPKParser.Float_SP)
                    self.state = 240 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==76):
                        break

                self.state = 242
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 24:
                self.enterOuterAlt(localctx, 24)
                self.state = 243
                self.match(SparkySPKParser.Integrate_fit_baseline)
                self.state = 244
                self.match(SparkySPKParser.Integer_SP)
                self.state = 245
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 25:
                self.enterOuterAlt(localctx, 25)
                self.state = 246
                self.match(SparkySPKParser.Integrate_subtract_peaks)
                self.state = 247
                self.match(SparkySPKParser.Integer_SP)
                self.state = 248
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 26:
                self.enterOuterAlt(localctx, 26)
                self.state = 249
                self.match(SparkySPKParser.Integrate_contoured_data)
                self.state = 250
                self.match(SparkySPKParser.Integer_SP)
                self.state = 251
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 27:
                self.enterOuterAlt(localctx, 27)
                self.state = 252
                self.match(SparkySPKParser.Integrate_rectangle_data)
                self.state = 253
                self.match(SparkySPKParser.Integer_SP)
                self.state = 254
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 28:
                self.enterOuterAlt(localctx, 28)
                self.state = 255
                self.match(SparkySPKParser.Integrate_max_iterations)
                self.state = 256
                self.match(SparkySPKParser.Integer_SP)
                self.state = 257
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 29:
                self.enterOuterAlt(localctx, 29)
                self.state = 258
                self.match(SparkySPKParser.Integrate_tolerance)
                self.state = 259
                self.match(SparkySPKParser.Float_SP)
                self.state = 260
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 30:
                self.enterOuterAlt(localctx, 30)
                self.state = 261
                self.match(SparkySPKParser.Peak_pick)
                self.state = 263 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 262
                    self.match(SparkySPKParser.Float_SP)
                    self.state = 265 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==76):
                        break

                self.state = 267
                self.match(SparkySPKParser.Integer_SP)
                self.state = 268
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 31:
                self.enterOuterAlt(localctx, 31)
                self.state = 269
                self.match(SparkySPKParser.Peak_pick_minimum_linewidth)
                self.state = 271 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 270
                    self.match(SparkySPKParser.Float_SP)
                    self.state = 273 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==76):
                        break

                self.state = 275
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 32:
                self.enterOuterAlt(localctx, 32)
                self.state = 276
                self.match(SparkySPKParser.Peak_pick_minimum_dropoff)
                self.state = 277
                self.match(SparkySPKParser.Float_SP)
                self.state = 278
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 33:
                self.enterOuterAlt(localctx, 33)
                self.state = 279
                self.match(SparkySPKParser.Noise_sigma)
                self.state = 280
                self.match(SparkySPKParser.Float_SP)
                self.state = 281
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 34:
                self.enterOuterAlt(localctx, 34)
                self.state = 282
                self.match(SparkySPKParser.Ornament_labe_size)
                self.state = 283
                self.match(SparkySPKParser.Float_SP)
                self.state = 284
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 35:
                self.enterOuterAlt(localctx, 35)
                self.state = 285
                self.match(SparkySPKParser.Ornament_line_size)
                self.state = 286
                self.match(SparkySPKParser.Float_SP)
                self.state = 287
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 36:
                self.enterOuterAlt(localctx, 36)
                self.state = 288
                self.match(SparkySPKParser.Ornament_peak_size)
                self.state = 289
                self.match(SparkySPKParser.Float_SP)
                self.state = 290
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 37:
                self.enterOuterAlt(localctx, 37)
                self.state = 291
                self.match(SparkySPKParser.Ornament_grid_size)
                self.state = 292
                self.match(SparkySPKParser.Float_SP)
                self.state = 293
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 38:
                self.enterOuterAlt(localctx, 38)
                self.state = 294
                self.match(SparkySPKParser.Ornament_peak_group_size)
                self.state = 295
                self.match(SparkySPKParser.Float_SP)
                self.state = 296
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 39:
                self.enterOuterAlt(localctx, 39)
                self.state = 297
                self.match(SparkySPKParser.Ornament_select_size)
                self.state = 298
                self.match(SparkySPKParser.Float_SP)
                self.state = 299
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 40:
                self.enterOuterAlt(localctx, 40)
                self.state = 300
                self.match(SparkySPKParser.Ornament_pointer_size)
                self.state = 301
                self.match(SparkySPKParser.Float_SP)
                self.state = 302
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 41:
                self.enterOuterAlt(localctx, 41)
                self.state = 303
                self.match(SparkySPKParser.Ornament_line_end_size)
                self.state = 304
                self.match(SparkySPKParser.Float_SP)
                self.state = 305
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 42:
                self.enterOuterAlt(localctx, 42)
                self.state = 306
                self.attached_data()
                self.state = 307
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 43:
                self.enterOuterAlt(localctx, 43)
                self.state = 309
                self.view()
                self.state = 310
                self.match(SparkySPKParser.RETURN_SP)
                pass

            elif la_ == 44:
                self.enterOuterAlt(localctx, 44)
                self.state = 312
                self.ornament()
                self.state = 313
                self.match(SparkySPKParser.RETURN_SP)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Spectrum_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer_SP(self):
            return self.getToken(SparkySPKParser.Integer_SP, 0)

        def Float_SP(self):
            return self.getToken(SparkySPKParser.Float_SP, 0)

        def Simple_name_SP(self):
            return self.getToken(SparkySPKParser.Simple_name_SP, 0)

        def Any_name_SP(self):
            return self.getToken(SparkySPKParser.Any_name_SP, 0)

        def getRuleIndex(self):
            return SparkySPKParser.RULE_spectrum_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSpectrum_name" ):
                listener.enterSpectrum_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSpectrum_name" ):
                listener.exitSpectrum_name(self)




    def spectrum_name(self):

        localctx = SparkySPKParser.Spectrum_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_spectrum_name)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 317
            _la = self._input.LA(1)
            if not(((((_la - 75)) & ~0x3f) == 0 and ((1 << (_la - 75)) & 15) != 0)):
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


    class Attached_dataContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Attached_data(self):
            return self.getToken(SparkySPKParser.Attached_data, 0)

        def End_attached_data(self):
            return self.getToken(SparkySPKParser.End_attached_data, 0)

        def attached_data_statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SparkySPKParser.Attached_data_statementContext)
            else:
                return self.getTypedRuleContext(SparkySPKParser.Attached_data_statementContext,i)


        def getRuleIndex(self):
            return SparkySPKParser.RULE_attached_data

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttached_data" ):
                listener.enterAttached_data(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttached_data" ):
                listener.exitAttached_data(self)




    def attached_data(self):

        localctx = SparkySPKParser.Attached_dataContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_attached_data)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 319
            self.match(SparkySPKParser.Attached_data)
            self.state = 323
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==82:
                self.state = 320
                self.attached_data_statement()
                self.state = 325
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 326
            self.match(SparkySPKParser.End_attached_data)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Attached_data_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Any_name_AD(self):
            return self.getToken(SparkySPKParser.Any_name_AD, 0)

        def getRuleIndex(self):
            return SparkySPKParser.RULE_attached_data_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttached_data_statement" ):
                listener.enterAttached_data_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttached_data_statement" ):
                listener.exitAttached_data_statement(self)




    def attached_data_statement(self):

        localctx = SparkySPKParser.Attached_data_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_attached_data_statement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 328
            self.match(SparkySPKParser.Any_name_AD)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ViewContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def View(self):
            return self.getToken(SparkySPKParser.View, 0)

        def End_view(self):
            return self.getToken(SparkySPKParser.End_view, 0)

        def view_statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SparkySPKParser.View_statementContext)
            else:
                return self.getTypedRuleContext(SparkySPKParser.View_statementContext,i)


        def getRuleIndex(self):
            return SparkySPKParser.RULE_view

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterView" ):
                listener.enterView(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitView" ):
                listener.exitView(self)




    def view(self):

        localctx = SparkySPKParser.ViewContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_view)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 330
            self.match(SparkySPKParser.View)
            self.state = 334
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 84)) & ~0x3f) == 0 and ((1 << (_la - 84)) & 67581) != 0):
                self.state = 331
                self.view_statement()
                self.state = 336
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 337
            self.match(SparkySPKParser.End_view)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class View_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN_VI(self):
            return self.getToken(SparkySPKParser.RETURN_VI, 0)

        def Name_VI(self):
            return self.getToken(SparkySPKParser.Name_VI, 0)

        def view_name(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SparkySPKParser.View_nameContext)
            else:
                return self.getTypedRuleContext(SparkySPKParser.View_nameContext,i)


        def Precision(self):
            return self.getToken(SparkySPKParser.Precision, 0)

        def Integer_VI(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Integer_VI)
            else:
                return self.getToken(SparkySPKParser.Integer_VI, i)

        def Precision_by_units(self):
            return self.getToken(SparkySPKParser.Precision_by_units, 0)

        def View_mode(self):
            return self.getToken(SparkySPKParser.View_mode, 0)

        def Show(self):
            return self.getToken(SparkySPKParser.Show, 0)

        def Simple_name_VI(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Simple_name_VI)
            else:
                return self.getToken(SparkySPKParser.Simple_name_VI, i)

        def Axis_type(self):
            return self.getToken(SparkySPKParser.Axis_type, 0)

        def Flags_VI(self):
            return self.getToken(SparkySPKParser.Flags_VI, 0)

        def Contour_pos(self):
            return self.getToken(SparkySPKParser.Contour_pos, 0)

        def view_number(self):
            return self.getTypedRuleContext(SparkySPKParser.View_numberContext,0)


        def Float_VI(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Float_VI)
            else:
                return self.getToken(SparkySPKParser.Float_VI, i)

        def Contour_neg(self):
            return self.getToken(SparkySPKParser.Contour_neg, 0)

        def params(self):
            return self.getTypedRuleContext(SparkySPKParser.ParamsContext,0)


        def getRuleIndex(self):
            return SparkySPKParser.RULE_view_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterView_statement" ):
                listener.enterView_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitView_statement" ):
                listener.exitView_statement(self)




    def view_statement(self):

        localctx = SparkySPKParser.View_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_view_statement)
        self._la = 0 # Token type
        try:
            self.state = 408
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [100]:
                self.enterOuterAlt(localctx, 1)
                self.state = 339
                self.match(SparkySPKParser.RETURN_VI)
                pass
            elif token in [86]:
                self.enterOuterAlt(localctx, 2)
                self.state = 340
                self.match(SparkySPKParser.Name_VI)
                self.state = 344
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while ((((_la - 95)) & ~0x3f) == 0 and ((1 << (_la - 95)) & 15) != 0):
                    self.state = 341
                    self.view_name()
                    self.state = 346
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 347
                self.match(SparkySPKParser.RETURN_VI)
                pass
            elif token in [87]:
                self.enterOuterAlt(localctx, 3)
                self.state = 348
                self.match(SparkySPKParser.Precision)
                self.state = 349
                self.match(SparkySPKParser.Integer_VI)
                self.state = 350
                self.match(SparkySPKParser.RETURN_VI)
                pass
            elif token in [88]:
                self.enterOuterAlt(localctx, 4)
                self.state = 351
                self.match(SparkySPKParser.Precision_by_units)
                self.state = 353 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 352
                    self.match(SparkySPKParser.Integer_VI)
                    self.state = 355 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==95):
                        break

                self.state = 357
                self.match(SparkySPKParser.RETURN_VI)
                pass
            elif token in [89]:
                self.enterOuterAlt(localctx, 5)
                self.state = 358
                self.match(SparkySPKParser.View_mode)
                self.state = 359
                self.match(SparkySPKParser.Integer_VI)
                self.state = 360
                self.match(SparkySPKParser.RETURN_VI)
                pass
            elif token in [90]:
                self.enterOuterAlt(localctx, 6)
                self.state = 361
                self.match(SparkySPKParser.Show)
                self.state = 362
                self.match(SparkySPKParser.Integer_VI)
                self.state = 366
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==98:
                    self.state = 363
                    self.match(SparkySPKParser.Simple_name_VI)
                    self.state = 368
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 369
                self.match(SparkySPKParser.RETURN_VI)
                pass
            elif token in [91]:
                self.enterOuterAlt(localctx, 7)
                self.state = 370
                self.match(SparkySPKParser.Axis_type)
                self.state = 371
                self.match(SparkySPKParser.Integer_VI)
                self.state = 372
                self.match(SparkySPKParser.RETURN_VI)
                pass
            elif token in [92]:
                self.enterOuterAlt(localctx, 8)
                self.state = 373
                self.match(SparkySPKParser.Flags_VI)
                self.state = 377
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==98:
                    self.state = 374
                    self.match(SparkySPKParser.Simple_name_VI)
                    self.state = 379
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 380
                self.match(SparkySPKParser.RETURN_VI)
                pass
            elif token in [93]:
                self.enterOuterAlt(localctx, 9)
                self.state = 381
                self.match(SparkySPKParser.Contour_pos)
                self.state = 382
                self.match(SparkySPKParser.Integer_VI)
                self.state = 383
                self.view_number()
                self.state = 384
                self.match(SparkySPKParser.Float_VI)
                self.state = 385
                self.match(SparkySPKParser.Float_VI)
                self.state = 387 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 386
                    self.match(SparkySPKParser.Simple_name_VI)
                    self.state = 389 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==98):
                        break

                self.state = 391
                self.match(SparkySPKParser.RETURN_VI)
                pass
            elif token in [94]:
                self.enterOuterAlt(localctx, 10)
                self.state = 393
                self.match(SparkySPKParser.Contour_neg)
                self.state = 394
                self.match(SparkySPKParser.Integer_VI)
                self.state = 395
                self.view_number()
                self.state = 396
                self.match(SparkySPKParser.Float_VI)
                self.state = 397
                self.match(SparkySPKParser.Float_VI)
                self.state = 399 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 398
                    self.match(SparkySPKParser.Simple_name_VI)
                    self.state = 401 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==98):
                        break

                self.state = 403
                self.match(SparkySPKParser.RETURN_VI)
                pass
            elif token in [84]:
                self.enterOuterAlt(localctx, 11)
                self.state = 405
                self.params()
                self.state = 406
                self.match(SparkySPKParser.RETURN_VI)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class View_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer_VI(self):
            return self.getToken(SparkySPKParser.Integer_VI, 0)

        def Float_VI(self):
            return self.getToken(SparkySPKParser.Float_VI, 0)

        def Real_VI(self):
            return self.getToken(SparkySPKParser.Real_VI, 0)

        def Simple_name_VI(self):
            return self.getToken(SparkySPKParser.Simple_name_VI, 0)

        def getRuleIndex(self):
            return SparkySPKParser.RULE_view_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterView_name" ):
                listener.enterView_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitView_name" ):
                listener.exitView_name(self)




    def view_name(self):

        localctx = SparkySPKParser.View_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_view_name)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 410
            _la = self._input.LA(1)
            if not(((((_la - 95)) & ~0x3f) == 0 and ((1 << (_la - 95)) & 15) != 0)):
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


    class View_numberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer_VI(self):
            return self.getToken(SparkySPKParser.Integer_VI, 0)

        def Float_VI(self):
            return self.getToken(SparkySPKParser.Float_VI, 0)

        def Real_VI(self):
            return self.getToken(SparkySPKParser.Real_VI, 0)

        def getRuleIndex(self):
            return SparkySPKParser.RULE_view_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterView_number" ):
                listener.enterView_number(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitView_number" ):
                listener.exitView_number(self)




    def view_number(self):

        localctx = SparkySPKParser.View_numberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_view_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 412
            _la = self._input.LA(1)
            if not(((((_la - 95)) & ~0x3f) == 0 and ((1 << (_la - 95)) & 7) != 0)):
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


    class ParamsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Params(self):
            return self.getToken(SparkySPKParser.Params, 0)

        def End_params(self):
            return self.getToken(SparkySPKParser.End_params, 0)

        def params_statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SparkySPKParser.Params_statementContext)
            else:
                return self.getTypedRuleContext(SparkySPKParser.Params_statementContext,i)


        def getRuleIndex(self):
            return SparkySPKParser.RULE_params

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParams" ):
                listener.enterParams(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParams" ):
                listener.exitParams(self)




    def params(self):

        localctx = SparkySPKParser.ParamsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_params)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 414
            self.match(SparkySPKParser.Params)
            self.state = 418
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 102)) & ~0x3f) == 0 and ((1 << (_la - 102)) & 2175) != 0):
                self.state = 415
                self.params_statement()
                self.state = 420
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 421
            self.match(SparkySPKParser.End_params)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Params_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN_PA(self):
            return self.getToken(SparkySPKParser.RETURN_PA, 0)

        def Orientation(self):
            return self.getToken(SparkySPKParser.Orientation, 0)

        def Integer_PA(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Integer_PA)
            else:
                return self.getToken(SparkySPKParser.Integer_PA, i)

        def Location(self):
            return self.getToken(SparkySPKParser.Location, 0)

        def Size(self):
            return self.getToken(SparkySPKParser.Size, 0)

        def Offset(self):
            return self.getToken(SparkySPKParser.Offset, 0)

        def Float_PA(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Float_PA)
            else:
                return self.getToken(SparkySPKParser.Float_PA, i)

        def Scale(self):
            return self.getToken(SparkySPKParser.Scale, 0)

        def Zoom(self):
            return self.getToken(SparkySPKParser.Zoom, 0)

        def Flags_PA(self):
            return self.getToken(SparkySPKParser.Flags_PA, 0)

        def getRuleIndex(self):
            return SparkySPKParser.RULE_params_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParams_statement" ):
                listener.enterParams_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParams_statement" ):
                listener.exitParams_statement(self)




    def params_statement(self):

        localctx = SparkySPKParser.Params_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_params_statement)
        self._la = 0 # Token type
        try:
            self.state = 465
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [113]:
                self.enterOuterAlt(localctx, 1)
                self.state = 423
                self.match(SparkySPKParser.RETURN_PA)
                pass
            elif token in [102]:
                self.enterOuterAlt(localctx, 2)
                self.state = 424
                self.match(SparkySPKParser.Orientation)
                self.state = 426 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 425
                    self.match(SparkySPKParser.Integer_PA)
                    self.state = 428 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==109):
                        break

                self.state = 430
                self.match(SparkySPKParser.RETURN_PA)
                pass
            elif token in [103]:
                self.enterOuterAlt(localctx, 3)
                self.state = 431
                self.match(SparkySPKParser.Location)
                self.state = 433 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 432
                    self.match(SparkySPKParser.Integer_PA)
                    self.state = 435 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==109):
                        break

                self.state = 437
                self.match(SparkySPKParser.RETURN_PA)
                pass
            elif token in [104]:
                self.enterOuterAlt(localctx, 4)
                self.state = 438
                self.match(SparkySPKParser.Size)
                self.state = 440 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 439
                    self.match(SparkySPKParser.Integer_PA)
                    self.state = 442 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==109):
                        break

                self.state = 444
                self.match(SparkySPKParser.RETURN_PA)
                pass
            elif token in [105]:
                self.enterOuterAlt(localctx, 5)
                self.state = 445
                self.match(SparkySPKParser.Offset)
                self.state = 447 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 446
                    self.match(SparkySPKParser.Float_PA)
                    self.state = 449 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==110):
                        break

                self.state = 451
                self.match(SparkySPKParser.RETURN_PA)
                pass
            elif token in [106]:
                self.enterOuterAlt(localctx, 6)
                self.state = 452
                self.match(SparkySPKParser.Scale)
                self.state = 454 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 453
                    self.match(SparkySPKParser.Float_PA)
                    self.state = 456 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==110):
                        break

                self.state = 458
                self.match(SparkySPKParser.RETURN_PA)
                pass
            elif token in [107]:
                self.enterOuterAlt(localctx, 7)
                self.state = 459
                self.match(SparkySPKParser.Zoom)
                self.state = 460
                self.match(SparkySPKParser.Float_PA)
                self.state = 461
                self.match(SparkySPKParser.RETURN_PA)
                pass
            elif token in [108]:
                self.enterOuterAlt(localctx, 8)
                self.state = 462
                self.match(SparkySPKParser.Flags_PA)
                self.state = 463
                self.match(SparkySPKParser.Integer_PA)
                self.state = 464
                self.match(SparkySPKParser.RETURN_PA)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OrnamentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Ornament(self):
            return self.getToken(SparkySPKParser.Ornament, 0)

        def End_ornament(self):
            return self.getToken(SparkySPKParser.End_ornament, 0)

        def ornament_statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SparkySPKParser.Ornament_statementContext)
            else:
                return self.getTypedRuleContext(SparkySPKParser.Ornament_statementContext,i)


        def getRuleIndex(self):
            return SparkySPKParser.RULE_ornament

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrnament" ):
                listener.enterOrnament(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrnament" ):
                listener.exitOrnament(self)




    def ornament(self):

        localctx = SparkySPKParser.OrnamentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_ornament)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 467
            self.match(SparkySPKParser.Ornament)
            self.state = 471
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 114)) & ~0x3f) == 0 and ((1 << (_la - 114)) & 1064933) != 0):
                self.state = 468
                self.ornament_statement()
                self.state = 473
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 474
            self.match(SparkySPKParser.End_ornament)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Ornament_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN_OR(self):
            return self.getToken(SparkySPKParser.RETURN_OR, 0)

        def Type_OR(self):
            return self.getToken(SparkySPKParser.Type_OR, 0)

        def Peak(self):
            return self.getToken(SparkySPKParser.Peak, 0)

        def Grid(self):
            return self.getToken(SparkySPKParser.Grid, 0)

        def Color_OR(self):
            return self.getToken(SparkySPKParser.Color_OR, 0)

        def Integer_OR(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Integer_OR)
            else:
                return self.getToken(SparkySPKParser.Integer_OR, i)

        def Simple_name_OR(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Simple_name_OR)
            else:
                return self.getToken(SparkySPKParser.Simple_name_OR, i)

        def Flags_OR(self):
            return self.getToken(SparkySPKParser.Flags_OR, 0)

        def Id(self):
            return self.getToken(SparkySPKParser.Id, 0)

        def Pos_OR(self):
            return self.getToken(SparkySPKParser.Pos_OR, 0)

        def ornament_position(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SparkySPKParser.Ornament_positionContext)
            else:
                return self.getTypedRuleContext(SparkySPKParser.Ornament_positionContext,i)


        def Height(self):
            return self.getToken(SparkySPKParser.Height, 0)

        def Float_OR(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Float_OR)
            else:
                return self.getToken(SparkySPKParser.Float_OR, i)

        def Line_width(self):
            return self.getToken(SparkySPKParser.Line_width, 0)

        def Integral(self):
            return self.getToken(SparkySPKParser.Integral, 0)

        def Real_OR(self):
            return self.getToken(SparkySPKParser.Real_OR, 0)

        def Fr(self):
            return self.getToken(SparkySPKParser.Fr, 0)

        def Rs(self):
            return self.getToken(SparkySPKParser.Rs, 0)

        def Rs_ex(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Rs_ex)
            else:
                return self.getToken(SparkySPKParser.Rs_ex, i)

        def label(self):
            return self.getTypedRuleContext(SparkySPKParser.LabelContext,0)


        def getRuleIndex(self):
            return SparkySPKParser.RULE_ornament_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrnament_statement" ):
                listener.enterOrnament_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrnament_statement" ):
                listener.exitOrnament_statement(self)




    def ornament_statement(self):

        localctx = SparkySPKParser.Ornament_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_ornament_statement)
        self._la = 0 # Token type
        try:
            self.state = 549
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,46,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 476
                self.match(SparkySPKParser.RETURN_OR)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 477
                self.match(SparkySPKParser.Type_OR)
                self.state = 478
                self.match(SparkySPKParser.Peak)
                self.state = 479
                self.match(SparkySPKParser.RETURN_OR)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 480
                self.match(SparkySPKParser.Type_OR)
                self.state = 481
                self.match(SparkySPKParser.Grid)
                self.state = 482
                self.match(SparkySPKParser.RETURN_OR)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 483
                self.match(SparkySPKParser.Color_OR)
                self.state = 485 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 484
                    self.match(SparkySPKParser.Integer_OR)
                    self.state = 487 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==129):
                        break

                self.state = 490 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 489
                    self.match(SparkySPKParser.Simple_name_OR)
                    self.state = 492 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==132):
                        break

                self.state = 494
                self.match(SparkySPKParser.RETURN_OR)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 495
                self.match(SparkySPKParser.Flags_OR)
                self.state = 497 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 496
                    self.match(SparkySPKParser.Integer_OR)
                    self.state = 499 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==129):
                        break

                self.state = 501
                self.match(SparkySPKParser.RETURN_OR)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 502
                self.match(SparkySPKParser.Id)
                self.state = 503
                self.match(SparkySPKParser.Integer_OR)
                self.state = 504
                self.match(SparkySPKParser.RETURN_OR)
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 505
                self.match(SparkySPKParser.Pos_OR)
                self.state = 507 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 506
                    self.ornament_position()
                    self.state = 509 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==129 or _la==130):
                        break

                self.state = 511
                self.match(SparkySPKParser.RETURN_OR)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 513
                self.match(SparkySPKParser.Height)
                self.state = 515 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 514
                    self.match(SparkySPKParser.Float_OR)
                    self.state = 517 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==130):
                        break

                self.state = 519
                self.match(SparkySPKParser.RETURN_OR)
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 520
                self.match(SparkySPKParser.Line_width)
                self.state = 522 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 521
                    self.match(SparkySPKParser.Float_OR)
                    self.state = 524 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==130):
                        break

                self.state = 527
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==132:
                    self.state = 526
                    self.match(SparkySPKParser.Simple_name_OR)


                self.state = 529
                self.match(SparkySPKParser.RETURN_OR)
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 530
                self.match(SparkySPKParser.Integral)
                self.state = 531
                self.match(SparkySPKParser.Real_OR)
                self.state = 533
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==132:
                    self.state = 532
                    self.match(SparkySPKParser.Simple_name_OR)


                self.state = 535
                self.match(SparkySPKParser.RETURN_OR)
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 536
                self.match(SparkySPKParser.Fr)
                self.state = 537
                self.match(SparkySPKParser.Float_OR)
                self.state = 538
                self.match(SparkySPKParser.RETURN_OR)
                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 539
                self.match(SparkySPKParser.Rs)
                self.state = 541 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 540
                    self.match(SparkySPKParser.Rs_ex)
                    self.state = 543 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==128):
                        break

                self.state = 545
                self.match(SparkySPKParser.RETURN_OR)
                pass

            elif la_ == 13:
                self.enterOuterAlt(localctx, 13)
                self.state = 546
                self.label()
                self.state = 547
                self.match(SparkySPKParser.RETURN_OR)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Ornament_positionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer_OR(self):
            return self.getToken(SparkySPKParser.Integer_OR, 0)

        def Float_OR(self):
            return self.getToken(SparkySPKParser.Float_OR, 0)

        def getRuleIndex(self):
            return SparkySPKParser.RULE_ornament_position

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrnament_position" ):
                listener.enterOrnament_position(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrnament_position" ):
                listener.exitOrnament_position(self)




    def ornament_position(self):

        localctx = SparkySPKParser.Ornament_positionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_ornament_position)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 551
            _la = self._input.LA(1)
            if not(_la==129 or _la==130):
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


    class LabelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def L_brakt(self):
            return self.getToken(SparkySPKParser.L_brakt, 0)

        def R_brakt(self):
            return self.getToken(SparkySPKParser.R_brakt, 0)

        def label_statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SparkySPKParser.Label_statementContext)
            else:
                return self.getTypedRuleContext(SparkySPKParser.Label_statementContext,i)


        def getRuleIndex(self):
            return SparkySPKParser.RULE_label

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLabel" ):
                listener.enterLabel(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLabel" ):
                listener.exitLabel(self)




    def label(self):

        localctx = SparkySPKParser.LabelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_label)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 553
            self.match(SparkySPKParser.L_brakt)
            self.state = 557
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 136)) & ~0x3f) == 0 and ((1 << (_la - 136)) & 32895) != 0):
                self.state = 554
                self.label_statement()
                self.state = 559
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 560
            self.match(SparkySPKParser.R_brakt)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Label_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN_LA(self):
            return self.getToken(SparkySPKParser.RETURN_LA, 0)

        def Type_LA(self):
            return self.getToken(SparkySPKParser.Type_LA, 0)

        def Label(self):
            return self.getToken(SparkySPKParser.Label, 0)

        def Color_LA(self):
            return self.getToken(SparkySPKParser.Color_LA, 0)

        def Integer_LA(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Integer_LA)
            else:
                return self.getToken(SparkySPKParser.Integer_LA, i)

        def Simple_name_LA(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Simple_name_LA)
            else:
                return self.getToken(SparkySPKParser.Simple_name_LA, i)

        def Flags_LA(self):
            return self.getToken(SparkySPKParser.Flags_LA, 0)

        def Mode_LA(self):
            return self.getToken(SparkySPKParser.Mode_LA, 0)

        def Pos_LA(self):
            return self.getToken(SparkySPKParser.Pos_LA, 0)

        def label_position(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SparkySPKParser.Label_positionContext)
            else:
                return self.getTypedRuleContext(SparkySPKParser.Label_positionContext,i)


        def Assignment_2d_ex(self):
            return self.getToken(SparkySPKParser.Assignment_2d_ex, 0)

        def Assignment_3d_ex(self):
            return self.getToken(SparkySPKParser.Assignment_3d_ex, 0)

        def Assignment_4d_ex(self):
            return self.getToken(SparkySPKParser.Assignment_4d_ex, 0)

        def Xy(self):
            return self.getToken(SparkySPKParser.Xy, 0)

        def Xy_pos(self, i:int=None):
            if i is None:
                return self.getTokens(SparkySPKParser.Xy_pos)
            else:
                return self.getToken(SparkySPKParser.Xy_pos, i)

        def getRuleIndex(self):
            return SparkySPKParser.RULE_label_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLabel_statement" ):
                listener.enterLabel_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLabel_statement" ):
                listener.exitLabel_statement(self)




    def label_statement(self):

        localctx = SparkySPKParser.Label_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_label_statement)
        self._la = 0 # Token type
        try:
            self.state = 606
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [151]:
                self.enterOuterAlt(localctx, 1)
                self.state = 562
                self.match(SparkySPKParser.RETURN_LA)
                pass
            elif token in [136]:
                self.enterOuterAlt(localctx, 2)
                self.state = 563
                self.match(SparkySPKParser.Type_LA)
                self.state = 564
                self.match(SparkySPKParser.Label)
                self.state = 565
                self.match(SparkySPKParser.RETURN_LA)
                pass
            elif token in [138]:
                self.enterOuterAlt(localctx, 3)
                self.state = 566
                self.match(SparkySPKParser.Color_LA)
                self.state = 568 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 567
                    self.match(SparkySPKParser.Integer_LA)
                    self.state = 570 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==147):
                        break

                self.state = 573 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 572
                    self.match(SparkySPKParser.Simple_name_LA)
                    self.state = 575 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==149):
                        break

                self.state = 577
                self.match(SparkySPKParser.RETURN_LA)
                pass
            elif token in [139]:
                self.enterOuterAlt(localctx, 4)
                self.state = 578
                self.match(SparkySPKParser.Flags_LA)
                self.state = 580 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 579
                    self.match(SparkySPKParser.Integer_LA)
                    self.state = 582 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==147):
                        break

                self.state = 584
                self.match(SparkySPKParser.RETURN_LA)
                pass
            elif token in [140]:
                self.enterOuterAlt(localctx, 5)
                self.state = 585
                self.match(SparkySPKParser.Mode_LA)
                self.state = 586
                self.match(SparkySPKParser.Integer_LA)
                self.state = 587
                self.match(SparkySPKParser.RETURN_LA)
                pass
            elif token in [141]:
                self.enterOuterAlt(localctx, 6)
                self.state = 588
                self.match(SparkySPKParser.Pos_LA)
                self.state = 590 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 589
                    self.label_position()
                    self.state = 592 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==147 or _la==148):
                        break

                self.state = 594
                self.match(SparkySPKParser.RETURN_LA)
                pass
            elif token in [137]:
                self.enterOuterAlt(localctx, 7)
                self.state = 596
                self.match(SparkySPKParser.Label)
                self.state = 597
                _la = self._input.LA(1)
                if not(((((_la - 143)) & ~0x3f) == 0 and ((1 << (_la - 143)) & 7) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 598
                self.match(SparkySPKParser.RETURN_LA)
                pass
            elif token in [142]:
                self.enterOuterAlt(localctx, 8)
                self.state = 599
                self.match(SparkySPKParser.Xy)
                self.state = 601 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 600
                    self.match(SparkySPKParser.Xy_pos)
                    self.state = 603 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==146):
                        break

                self.state = 605
                self.match(SparkySPKParser.RETURN_LA)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Label_positionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer_LA(self):
            return self.getToken(SparkySPKParser.Integer_LA, 0)

        def Float_LA(self):
            return self.getToken(SparkySPKParser.Float_LA, 0)

        def getRuleIndex(self):
            return SparkySPKParser.RULE_label_position

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLabel_position" ):
                listener.enterLabel_position(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLabel_position" ):
                listener.exitLabel_position(self)




    def label_position(self):

        localctx = SparkySPKParser.Label_positionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_label_position)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 608
            _la = self._input.LA(1)
            if not(_la==147 or _la==148):
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






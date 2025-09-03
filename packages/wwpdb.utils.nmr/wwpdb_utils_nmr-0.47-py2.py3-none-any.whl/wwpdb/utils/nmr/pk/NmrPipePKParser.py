# Generated from NmrPipePKParser.g4 by ANTLR 4.13.0
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
        4,1,100,612,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,
        7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,
        13,2,14,7,14,2,15,7,15,2,16,7,16,1,0,3,0,36,8,0,1,0,1,0,1,0,1,0,
        1,0,1,0,1,0,1,0,1,0,5,0,47,8,0,10,0,12,0,50,9,0,1,0,1,0,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,
        1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,2,
        87,8,2,1,2,1,2,1,2,3,2,92,8,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,
        2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,
        2,3,2,119,8,2,1,2,1,2,1,2,3,2,124,8,2,1,2,1,2,1,2,1,2,3,2,130,8,
        2,1,2,1,2,1,2,3,2,135,8,2,1,2,4,2,138,8,2,11,2,12,2,139,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,3,3,165,8,3,1,3,1,3,1,3,3,3,170,8,3,1,3,1,3,
        1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,
        1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,
        3,4,206,8,4,1,4,1,4,1,4,3,4,211,8,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,
        1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,
        1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,3,4,246,8,4,1,4,1,4,1,4,
        3,4,251,8,4,1,4,1,4,1,4,1,4,3,4,257,8,4,1,4,1,4,1,4,3,4,262,8,4,
        1,4,4,4,265,8,4,11,4,12,4,266,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,
        5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,
        5,1,5,1,5,1,5,1,5,1,5,1,5,3,5,300,8,5,1,5,1,5,1,5,3,5,305,8,5,1,
        5,1,5,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,
        6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,
        6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,3,6,349,8,6,1,6,1,6,1,6,3,
        6,354,8,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,
        6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,
        6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,3,6,397,8,6,1,6,1,
        6,1,6,3,6,402,8,6,1,6,1,6,1,6,1,6,3,6,408,8,6,1,6,1,6,1,6,3,6,413,
        8,6,1,6,4,6,416,8,6,11,6,12,6,417,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,
        7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,
        7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,3,
        7,459,8,7,1,7,1,7,1,7,3,7,464,8,7,1,7,1,7,1,8,1,8,1,8,1,8,1,8,4,
        8,473,8,8,11,8,12,8,474,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,
        1,10,1,10,4,10,489,8,10,11,10,12,10,490,1,10,1,10,1,10,1,10,1,10,
        1,10,1,10,1,10,1,10,3,10,502,8,10,1,10,1,10,4,10,506,8,10,11,10,
        12,10,507,1,11,1,11,1,11,1,11,4,11,514,8,11,11,11,12,11,515,1,11,
        1,11,1,12,1,12,4,12,522,8,12,11,12,12,12,523,1,12,1,12,1,12,1,12,
        3,12,530,8,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,3,12,539,8,12,1,
        12,1,12,4,12,543,8,12,11,12,12,12,544,1,13,1,13,3,13,549,8,13,1,
        13,1,13,1,13,1,13,4,13,555,8,13,11,13,12,13,556,1,13,1,13,1,14,1,
        14,4,14,563,8,14,11,14,12,14,564,1,14,1,14,1,14,1,14,3,14,571,8,
        14,1,14,3,14,574,8,14,1,14,1,14,1,14,1,14,1,14,1,14,1,14,1,14,3,
        14,584,8,14,1,14,1,14,4,14,588,8,14,11,14,12,14,589,1,15,1,15,3,
        15,594,8,15,1,15,3,15,597,8,15,1,15,1,15,1,15,1,15,1,15,4,15,604,
        8,15,11,15,12,15,605,1,15,1,15,1,16,1,16,1,16,0,0,17,0,2,4,6,8,10,
        12,14,16,18,20,22,24,26,28,30,32,0,4,1,0,16,19,1,1,13,13,1,0,22,
        23,2,0,6,8,11,11,653,0,35,1,0,0,0,2,53,1,0,0,0,4,62,1,0,0,0,6,141,
        1,0,0,0,8,173,1,0,0,0,10,268,1,0,0,0,12,308,1,0,0,0,14,419,1,0,0,
        0,16,467,1,0,0,0,18,476,1,0,0,0,20,486,1,0,0,0,22,509,1,0,0,0,24,
        519,1,0,0,0,26,546,1,0,0,0,28,560,1,0,0,0,30,591,1,0,0,0,32,609,
        1,0,0,0,34,36,5,13,0,0,35,34,1,0,0,0,35,36,1,0,0,0,36,48,1,0,0,0,
        37,47,3,2,1,0,38,47,3,4,2,0,39,47,3,8,4,0,40,47,3,12,6,0,41,47,3,
        16,8,0,42,47,3,20,10,0,43,47,3,24,12,0,44,47,3,28,14,0,45,47,5,13,
        0,0,46,37,1,0,0,0,46,38,1,0,0,0,46,39,1,0,0,0,46,40,1,0,0,0,46,41,
        1,0,0,0,46,42,1,0,0,0,46,43,1,0,0,0,46,44,1,0,0,0,46,45,1,0,0,0,
        47,50,1,0,0,0,48,46,1,0,0,0,48,49,1,0,0,0,49,51,1,0,0,0,50,48,1,
        0,0,0,51,52,5,0,0,1,52,1,1,0,0,0,53,54,5,1,0,0,54,55,7,0,0,0,55,
        56,5,27,0,0,56,57,5,24,0,0,57,58,5,24,0,0,58,59,5,20,0,0,59,60,5,
        20,0,0,60,61,5,29,0,0,61,3,1,0,0,0,62,63,5,2,0,0,63,64,5,31,0,0,
        64,65,5,32,0,0,65,66,5,33,0,0,66,67,5,36,0,0,67,68,5,37,0,0,68,69,
        5,40,0,0,69,70,5,41,0,0,70,71,5,44,0,0,71,72,5,45,0,0,72,73,5,48,
        0,0,73,74,5,49,0,0,74,75,5,52,0,0,75,76,5,53,0,0,76,77,5,56,0,0,
        77,78,5,57,0,0,78,79,5,58,0,0,79,80,5,59,0,0,80,81,5,64,0,0,81,82,
        5,65,0,0,82,83,5,66,0,0,83,84,5,67,0,0,84,86,5,68,0,0,85,87,5,69,
        0,0,86,85,1,0,0,0,86,87,1,0,0,0,87,88,1,0,0,0,88,89,5,70,0,0,89,
        91,5,71,0,0,90,92,5,72,0,0,91,90,1,0,0,0,91,92,1,0,0,0,92,93,1,0,
        0,0,93,94,5,89,0,0,94,95,5,3,0,0,95,96,5,91,0,0,96,97,5,91,0,0,97,
        98,5,91,0,0,98,99,5,91,0,0,99,100,5,91,0,0,100,101,5,91,0,0,101,
        102,5,91,0,0,102,103,5,91,0,0,103,104,5,91,0,0,104,105,5,91,0,0,
        105,106,5,91,0,0,106,107,5,91,0,0,107,108,5,91,0,0,108,109,5,91,
        0,0,109,110,5,91,0,0,110,111,5,91,0,0,111,112,5,91,0,0,112,113,5,
        91,0,0,113,114,5,91,0,0,114,115,5,91,0,0,115,116,5,91,0,0,116,118,
        5,91,0,0,117,119,5,91,0,0,118,117,1,0,0,0,118,119,1,0,0,0,119,120,
        1,0,0,0,120,121,5,91,0,0,121,123,5,91,0,0,122,124,5,91,0,0,123,122,
        1,0,0,0,123,124,1,0,0,0,124,125,1,0,0,0,125,129,5,93,0,0,126,127,
        5,4,0,0,127,128,5,95,0,0,128,130,5,97,0,0,129,126,1,0,0,0,129,130,
        1,0,0,0,130,134,1,0,0,0,131,132,5,5,0,0,132,133,5,98,0,0,133,135,
        5,100,0,0,134,131,1,0,0,0,134,135,1,0,0,0,135,137,1,0,0,0,136,138,
        3,6,3,0,137,136,1,0,0,0,138,139,1,0,0,0,139,137,1,0,0,0,139,140,
        1,0,0,0,140,5,1,0,0,0,141,142,5,6,0,0,142,143,3,32,16,0,143,144,
        3,32,16,0,144,145,3,32,16,0,145,146,3,32,16,0,146,147,3,32,16,0,
        147,148,3,32,16,0,148,149,3,32,16,0,149,150,3,32,16,0,150,151,3,
        32,16,0,151,152,3,32,16,0,152,153,3,32,16,0,153,154,3,32,16,0,154,
        155,5,6,0,0,155,156,5,6,0,0,156,157,5,6,0,0,157,158,5,6,0,0,158,
        159,3,32,16,0,159,160,3,32,16,0,160,161,3,32,16,0,161,162,3,32,16,
        0,162,164,5,6,0,0,163,165,5,11,0,0,164,163,1,0,0,0,164,165,1,0,0,
        0,165,166,1,0,0,0,166,167,5,6,0,0,167,169,5,6,0,0,168,170,5,6,0,
        0,169,168,1,0,0,0,169,170,1,0,0,0,170,171,1,0,0,0,171,172,7,1,0,
        0,172,7,1,0,0,0,173,174,5,2,0,0,174,175,5,31,0,0,175,176,5,32,0,
        0,176,177,5,33,0,0,177,178,5,34,0,0,178,179,5,36,0,0,179,180,5,37,
        0,0,180,181,5,38,0,0,181,182,5,40,0,0,182,183,5,41,0,0,183,184,5,
        42,0,0,184,185,5,44,0,0,185,186,5,45,0,0,186,187,5,46,0,0,187,188,
        5,48,0,0,188,189,5,49,0,0,189,190,5,50,0,0,190,191,5,52,0,0,191,
        192,5,53,0,0,192,193,5,54,0,0,193,194,5,56,0,0,194,195,5,57,0,0,
        195,196,5,58,0,0,196,197,5,59,0,0,197,198,5,60,0,0,198,199,5,61,
        0,0,199,200,5,64,0,0,200,201,5,65,0,0,201,202,5,66,0,0,202,203,5,
        67,0,0,203,205,5,68,0,0,204,206,5,69,0,0,205,204,1,0,0,0,205,206,
        1,0,0,0,206,207,1,0,0,0,207,208,5,70,0,0,208,210,5,71,0,0,209,211,
        5,72,0,0,210,209,1,0,0,0,210,211,1,0,0,0,211,212,1,0,0,0,212,213,
        5,89,0,0,213,214,5,3,0,0,214,215,5,91,0,0,215,216,5,91,0,0,216,217,
        5,91,0,0,217,218,5,91,0,0,218,219,5,91,0,0,219,220,5,91,0,0,220,
        221,5,91,0,0,221,222,5,91,0,0,222,223,5,91,0,0,223,224,5,91,0,0,
        224,225,5,91,0,0,225,226,5,91,0,0,226,227,5,91,0,0,227,228,5,91,
        0,0,228,229,5,91,0,0,229,230,5,91,0,0,230,231,5,91,0,0,231,232,5,
        91,0,0,232,233,5,91,0,0,233,234,5,91,0,0,234,235,5,91,0,0,235,236,
        5,91,0,0,236,237,5,91,0,0,237,238,5,91,0,0,238,239,5,91,0,0,239,
        240,5,91,0,0,240,241,5,91,0,0,241,242,5,91,0,0,242,243,5,91,0,0,
        243,245,5,91,0,0,244,246,5,91,0,0,245,244,1,0,0,0,245,246,1,0,0,
        0,246,247,1,0,0,0,247,248,5,91,0,0,248,250,5,91,0,0,249,251,5,91,
        0,0,250,249,1,0,0,0,250,251,1,0,0,0,251,252,1,0,0,0,252,256,5,93,
        0,0,253,254,5,4,0,0,254,255,5,95,0,0,255,257,5,97,0,0,256,253,1,
        0,0,0,256,257,1,0,0,0,257,261,1,0,0,0,258,259,5,5,0,0,259,260,5,
        98,0,0,260,262,5,100,0,0,261,258,1,0,0,0,261,262,1,0,0,0,262,264,
        1,0,0,0,263,265,3,10,5,0,264,263,1,0,0,0,265,266,1,0,0,0,266,264,
        1,0,0,0,266,267,1,0,0,0,267,9,1,0,0,0,268,269,5,6,0,0,269,270,3,
        32,16,0,270,271,3,32,16,0,271,272,3,32,16,0,272,273,3,32,16,0,273,
        274,3,32,16,0,274,275,3,32,16,0,275,276,3,32,16,0,276,277,3,32,16,
        0,277,278,3,32,16,0,278,279,3,32,16,0,279,280,3,32,16,0,280,281,
        3,32,16,0,281,282,3,32,16,0,282,283,3,32,16,0,283,284,3,32,16,0,
        284,285,3,32,16,0,285,286,3,32,16,0,286,287,3,32,16,0,287,288,5,
        6,0,0,288,289,5,6,0,0,289,290,5,6,0,0,290,291,5,6,0,0,291,292,5,
        6,0,0,292,293,5,6,0,0,293,294,3,32,16,0,294,295,3,32,16,0,295,296,
        3,32,16,0,296,297,3,32,16,0,297,299,5,6,0,0,298,300,5,11,0,0,299,
        298,1,0,0,0,299,300,1,0,0,0,300,301,1,0,0,0,301,302,5,6,0,0,302,
        304,5,6,0,0,303,305,5,6,0,0,304,303,1,0,0,0,304,305,1,0,0,0,305,
        306,1,0,0,0,306,307,7,1,0,0,307,11,1,0,0,0,308,309,5,2,0,0,309,310,
        5,31,0,0,310,311,5,32,0,0,311,312,5,33,0,0,312,313,5,34,0,0,313,
        314,5,35,0,0,314,315,5,36,0,0,315,316,5,37,0,0,316,317,5,38,0,0,
        317,318,5,38,0,0,318,319,5,40,0,0,319,320,5,41,0,0,320,321,5,42,
        0,0,321,322,5,43,0,0,322,323,5,44,0,0,323,324,5,45,0,0,324,325,5,
        46,0,0,325,326,5,47,0,0,326,327,5,48,0,0,327,328,5,49,0,0,328,329,
        5,50,0,0,329,330,5,51,0,0,330,331,5,52,0,0,331,332,5,53,0,0,332,
        333,5,54,0,0,333,334,5,55,0,0,334,335,5,56,0,0,335,336,5,57,0,0,
        336,337,5,58,0,0,337,338,5,59,0,0,338,339,5,60,0,0,339,340,5,61,
        0,0,340,341,5,62,0,0,341,342,5,63,0,0,342,343,5,64,0,0,343,344,5,
        65,0,0,344,345,5,66,0,0,345,346,5,67,0,0,346,348,5,68,0,0,347,349,
        5,69,0,0,348,347,1,0,0,0,348,349,1,0,0,0,349,350,1,0,0,0,350,351,
        5,70,0,0,351,353,5,71,0,0,352,354,5,72,0,0,353,352,1,0,0,0,353,354,
        1,0,0,0,354,355,1,0,0,0,355,356,5,89,0,0,356,357,5,3,0,0,357,358,
        5,91,0,0,358,359,5,91,0,0,359,360,5,91,0,0,360,361,5,91,0,0,361,
        362,5,91,0,0,362,363,5,91,0,0,363,364,5,91,0,0,364,365,5,91,0,0,
        365,366,5,91,0,0,366,367,5,91,0,0,367,368,5,91,0,0,368,369,5,91,
        0,0,369,370,5,91,0,0,370,371,5,91,0,0,371,372,5,91,0,0,372,373,5,
        91,0,0,373,374,5,91,0,0,374,375,5,91,0,0,375,376,5,91,0,0,376,377,
        5,91,0,0,377,378,5,91,0,0,378,379,5,91,0,0,379,380,5,91,0,0,380,
        381,5,91,0,0,381,382,5,91,0,0,382,383,5,91,0,0,383,384,5,91,0,0,
        384,385,5,91,0,0,385,386,5,91,0,0,386,387,5,91,0,0,387,388,5,91,
        0,0,388,389,5,91,0,0,389,390,5,91,0,0,390,391,5,91,0,0,391,392,5,
        91,0,0,392,393,5,91,0,0,393,394,5,91,0,0,394,396,5,91,0,0,395,397,
        5,91,0,0,396,395,1,0,0,0,396,397,1,0,0,0,397,398,1,0,0,0,398,399,
        5,91,0,0,399,401,5,91,0,0,400,402,5,91,0,0,401,400,1,0,0,0,401,402,
        1,0,0,0,402,403,1,0,0,0,403,407,5,93,0,0,404,405,5,4,0,0,405,406,
        5,95,0,0,406,408,5,97,0,0,407,404,1,0,0,0,407,408,1,0,0,0,408,412,
        1,0,0,0,409,410,5,5,0,0,410,411,5,98,0,0,411,413,5,100,0,0,412,409,
        1,0,0,0,412,413,1,0,0,0,413,415,1,0,0,0,414,416,3,14,7,0,415,414,
        1,0,0,0,416,417,1,0,0,0,417,415,1,0,0,0,417,418,1,0,0,0,418,13,1,
        0,0,0,419,420,5,6,0,0,420,421,3,32,16,0,421,422,3,32,16,0,422,423,
        3,32,16,0,423,424,3,32,16,0,424,425,3,32,16,0,425,426,3,32,16,0,
        426,427,3,32,16,0,427,428,3,32,16,0,428,429,3,32,16,0,429,430,3,
        32,16,0,430,431,3,32,16,0,431,432,3,32,16,0,432,433,3,32,16,0,433,
        434,3,32,16,0,434,435,3,32,16,0,435,436,3,32,16,0,436,437,3,32,16,
        0,437,438,3,32,16,0,438,439,3,32,16,0,439,440,3,32,16,0,440,441,
        3,32,16,0,441,442,3,32,16,0,442,443,3,32,16,0,443,444,3,32,16,0,
        444,445,5,6,0,0,445,446,5,6,0,0,446,447,5,6,0,0,447,448,5,6,0,0,
        448,449,5,6,0,0,449,450,5,6,0,0,450,451,5,6,0,0,451,452,5,6,0,0,
        452,453,3,32,16,0,453,454,3,32,16,0,454,455,3,32,16,0,455,456,3,
        32,16,0,456,458,5,6,0,0,457,459,5,11,0,0,458,457,1,0,0,0,458,459,
        1,0,0,0,459,460,1,0,0,0,460,461,5,6,0,0,461,463,5,6,0,0,462,464,
        5,6,0,0,463,462,1,0,0,0,463,464,1,0,0,0,464,465,1,0,0,0,465,466,
        7,1,0,0,466,15,1,0,0,0,467,468,5,1,0,0,468,469,5,21,0,0,469,470,
        5,24,0,0,470,472,5,29,0,0,471,473,3,18,9,0,472,471,1,0,0,0,473,474,
        1,0,0,0,474,472,1,0,0,0,474,475,1,0,0,0,475,17,1,0,0,0,476,477,5,
        1,0,0,477,478,7,0,0,0,478,479,5,24,0,0,479,480,5,25,0,0,480,481,
        5,25,0,0,481,482,5,25,0,0,482,483,7,2,0,0,483,484,5,25,0,0,484,485,
        5,29,0,0,485,19,1,0,0,0,486,488,5,3,0,0,487,489,5,91,0,0,488,487,
        1,0,0,0,489,490,1,0,0,0,490,488,1,0,0,0,490,491,1,0,0,0,491,492,
        1,0,0,0,492,493,5,93,0,0,493,494,5,2,0,0,494,495,5,73,0,0,495,496,
        5,76,0,0,496,497,5,77,0,0,497,501,5,80,0,0,498,502,5,81,0,0,499,
        500,5,82,0,0,500,502,5,83,0,0,501,498,1,0,0,0,501,499,1,0,0,0,501,
        502,1,0,0,0,502,503,1,0,0,0,503,505,5,89,0,0,504,506,3,22,11,0,505,
        504,1,0,0,0,506,507,1,0,0,0,507,505,1,0,0,0,507,508,1,0,0,0,508,
        21,1,0,0,0,509,510,5,6,0,0,510,511,3,32,16,0,511,513,3,32,16,0,512,
        514,3,32,16,0,513,512,1,0,0,0,514,515,1,0,0,0,515,513,1,0,0,0,515,
        516,1,0,0,0,516,517,1,0,0,0,517,518,7,1,0,0,518,23,1,0,0,0,519,521,
        5,3,0,0,520,522,5,91,0,0,521,520,1,0,0,0,522,523,1,0,0,0,523,521,
        1,0,0,0,523,524,1,0,0,0,524,525,1,0,0,0,525,526,5,93,0,0,526,527,
        5,2,0,0,527,529,5,73,0,0,528,530,5,74,0,0,529,528,1,0,0,0,529,530,
        1,0,0,0,530,531,1,0,0,0,531,532,5,76,0,0,532,533,5,77,0,0,533,534,
        5,78,0,0,534,538,5,80,0,0,535,539,5,81,0,0,536,537,5,82,0,0,537,
        539,5,83,0,0,538,535,1,0,0,0,538,536,1,0,0,0,538,539,1,0,0,0,539,
        540,1,0,0,0,540,542,5,89,0,0,541,543,3,26,13,0,542,541,1,0,0,0,543,
        544,1,0,0,0,544,542,1,0,0,0,544,545,1,0,0,0,545,25,1,0,0,0,546,548,
        5,6,0,0,547,549,5,6,0,0,548,547,1,0,0,0,548,549,1,0,0,0,549,550,
        1,0,0,0,550,551,3,32,16,0,551,552,3,32,16,0,552,554,3,32,16,0,553,
        555,3,32,16,0,554,553,1,0,0,0,555,556,1,0,0,0,556,554,1,0,0,0,556,
        557,1,0,0,0,557,558,1,0,0,0,558,559,7,1,0,0,559,27,1,0,0,0,560,562,
        5,3,0,0,561,563,5,91,0,0,562,561,1,0,0,0,563,564,1,0,0,0,564,562,
        1,0,0,0,564,565,1,0,0,0,565,566,1,0,0,0,566,567,5,93,0,0,567,568,
        5,2,0,0,568,570,5,73,0,0,569,571,5,75,0,0,570,569,1,0,0,0,570,571,
        1,0,0,0,571,573,1,0,0,0,572,574,5,74,0,0,573,572,1,0,0,0,573,574,
        1,0,0,0,574,575,1,0,0,0,575,576,5,76,0,0,576,577,5,77,0,0,577,578,
        5,78,0,0,578,579,5,79,0,0,579,583,5,80,0,0,580,584,5,81,0,0,581,
        582,5,82,0,0,582,584,5,83,0,0,583,580,1,0,0,0,583,581,1,0,0,0,583,
        584,1,0,0,0,584,585,1,0,0,0,585,587,5,89,0,0,586,588,3,30,15,0,587,
        586,1,0,0,0,588,589,1,0,0,0,589,587,1,0,0,0,589,590,1,0,0,0,590,
        29,1,0,0,0,591,593,5,6,0,0,592,594,5,6,0,0,593,592,1,0,0,0,593,594,
        1,0,0,0,594,596,1,0,0,0,595,597,5,6,0,0,596,595,1,0,0,0,596,597,
        1,0,0,0,597,598,1,0,0,0,598,599,3,32,16,0,599,600,3,32,16,0,600,
        601,3,32,16,0,601,603,3,32,16,0,602,604,3,32,16,0,603,602,1,0,0,
        0,604,605,1,0,0,0,605,603,1,0,0,0,605,606,1,0,0,0,606,607,1,0,0,
        0,607,608,7,1,0,0,608,31,1,0,0,0,609,610,7,3,0,0,610,33,1,0,0,0,
        49,35,46,48,86,91,118,123,129,134,139,164,169,205,210,245,250,256,
        261,266,299,304,348,353,396,401,407,412,417,458,463,474,490,501,
        507,515,523,529,538,544,548,556,564,570,573,583,589,593,596,605
    ]

class NmrPipePKParser ( Parser ):

    grammarFileName = "NmrPipePKParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'DATA'", "'VARS'", "'FORMAT'", "'NULLVALUE'", 
                     "'NULLSTRING'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'DIMCOUNT'", "'PPM'", "'HZ'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'INDEX'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'DX'", "'DY'", "'DZ'", "'DA'", "'X_PPM'", 
                     "'Y_PPM'", "'Z_PPM'", "'A_PPM'", "'X_HZ'", "'Y_HZ'", 
                     "'Z_HZ'", "'A_HZ'", "'XW'", "'YW'", "'ZW'", "'AW'", 
                     "'XW_HZ'", "'YW_HZ'", "'ZW_HZ'", "'AW_HZ'", "'X1'", 
                     "'X3'", "'Y1'", "'Y3'", "'Z1'", "'Z3'", "'A1'", "'A3'", 
                     "'HEIGHT'", "'DHEIGHT'", "'VOL'", "'PCHI2'", "'TYPE'", 
                     "'ASS'", "'CLUSTID'", "'MEMCNT'", "'TROUBLE'", "'PkID'", 
                     "'Sl.Z'", "'Sl.A'", "'X'", "'Y'", "'Z'", "'A'", "'Intensity'", 
                     "'Assign'", "'Assign1'", "'Assign2'" ]

    symbolicNames = [ "<INVALID>", "Data", "Vars", "Format", "Null_value", 
                      "Null_string", "Integer", "Float", "Real", "SHARP_COMMENT", 
                      "EXCLM_COMMENT", "Any_name", "SPACE", "RETURN", "SECTION_COMMENT", 
                      "LINE_COMMENT", "X_axis_DA", "Y_axis_DA", "Z_axis_DA", 
                      "A_axis_DA", "Ppm_value_DA", "Dim_count_DA", "Ppm_DA", 
                      "Hz_DA", "Integer_DA", "Float_DA", "Real_DA", "Simple_name_DA", 
                      "SPACE_DA", "RETURN_DA", "LINE_COMMENT_DA", "Index", 
                      "X_axis", "Y_axis", "Z_axis", "A_axis", "Dx", "Dy", 
                      "Dz", "Da", "X_ppm", "Y_ppm", "Z_ppm", "A_ppm", "X_hz", 
                      "Y_hz", "Z_hz", "A_hz", "Xw", "Yw", "Zw", "Aw", "Xw_hz", 
                      "Yw_hz", "Zw_hz", "Aw_hz", "X1", "X3", "Y1", "Y3", 
                      "Z1", "Z3", "A1", "A3", "Height", "DHeight", "Vol", 
                      "Pchi2", "Type", "Ass", "ClustId", "Memcnt", "Trouble", 
                      "PkID", "Sl_Z", "Sl_A", "X", "Y", "Z", "A", "Intensity", 
                      "Assign", "Assign1", "Assign2", "Integer_VA", "Float_VA", 
                      "Real_VA", "Simple_name_VA", "SPACE_VA", "RETURN_VA", 
                      "LINE_COMMENT_VA", "Format_code", "SPACE_FO", "RETURN_FO", 
                      "LINE_COMMENT_FO", "Any_name_NV", "SPACE_NV", "RETURN_NV", 
                      "Any_name_NS", "SPACE_NS", "RETURN_NS" ]

    RULE_nmrpipe_pk = 0
    RULE_data_label = 1
    RULE_peak_list_2d = 2
    RULE_peak_2d = 3
    RULE_peak_list_3d = 4
    RULE_peak_3d = 5
    RULE_peak_list_4d = 6
    RULE_peak_4d = 7
    RULE_pipp_label = 8
    RULE_pipp_axis = 9
    RULE_pipp_peak_list_2d = 10
    RULE_pipp_peak_2d = 11
    RULE_pipp_peak_list_3d = 12
    RULE_pipp_peak_3d = 13
    RULE_pipp_peak_list_4d = 14
    RULE_pipp_peak_4d = 15
    RULE_number = 16

    ruleNames =  [ "nmrpipe_pk", "data_label", "peak_list_2d", "peak_2d", 
                   "peak_list_3d", "peak_3d", "peak_list_4d", "peak_4d", 
                   "pipp_label", "pipp_axis", "pipp_peak_list_2d", "pipp_peak_2d", 
                   "pipp_peak_list_3d", "pipp_peak_3d", "pipp_peak_list_4d", 
                   "pipp_peak_4d", "number" ]

    EOF = Token.EOF
    Data=1
    Vars=2
    Format=3
    Null_value=4
    Null_string=5
    Integer=6
    Float=7
    Real=8
    SHARP_COMMENT=9
    EXCLM_COMMENT=10
    Any_name=11
    SPACE=12
    RETURN=13
    SECTION_COMMENT=14
    LINE_COMMENT=15
    X_axis_DA=16
    Y_axis_DA=17
    Z_axis_DA=18
    A_axis_DA=19
    Ppm_value_DA=20
    Dim_count_DA=21
    Ppm_DA=22
    Hz_DA=23
    Integer_DA=24
    Float_DA=25
    Real_DA=26
    Simple_name_DA=27
    SPACE_DA=28
    RETURN_DA=29
    LINE_COMMENT_DA=30
    Index=31
    X_axis=32
    Y_axis=33
    Z_axis=34
    A_axis=35
    Dx=36
    Dy=37
    Dz=38
    Da=39
    X_ppm=40
    Y_ppm=41
    Z_ppm=42
    A_ppm=43
    X_hz=44
    Y_hz=45
    Z_hz=46
    A_hz=47
    Xw=48
    Yw=49
    Zw=50
    Aw=51
    Xw_hz=52
    Yw_hz=53
    Zw_hz=54
    Aw_hz=55
    X1=56
    X3=57
    Y1=58
    Y3=59
    Z1=60
    Z3=61
    A1=62
    A3=63
    Height=64
    DHeight=65
    Vol=66
    Pchi2=67
    Type=68
    Ass=69
    ClustId=70
    Memcnt=71
    Trouble=72
    PkID=73
    Sl_Z=74
    Sl_A=75
    X=76
    Y=77
    Z=78
    A=79
    Intensity=80
    Assign=81
    Assign1=82
    Assign2=83
    Integer_VA=84
    Float_VA=85
    Real_VA=86
    Simple_name_VA=87
    SPACE_VA=88
    RETURN_VA=89
    LINE_COMMENT_VA=90
    Format_code=91
    SPACE_FO=92
    RETURN_FO=93
    LINE_COMMENT_FO=94
    Any_name_NV=95
    SPACE_NV=96
    RETURN_NV=97
    Any_name_NS=98
    SPACE_NS=99
    RETURN_NS=100

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Nmrpipe_pkContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(NmrPipePKParser.EOF, 0)

        def RETURN(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.RETURN)
            else:
                return self.getToken(NmrPipePKParser.RETURN, i)

        def data_label(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Data_labelContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Data_labelContext,i)


        def peak_list_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Peak_list_2dContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Peak_list_2dContext,i)


        def peak_list_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Peak_list_3dContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Peak_list_3dContext,i)


        def peak_list_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Peak_list_4dContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Peak_list_4dContext,i)


        def pipp_label(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Pipp_labelContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Pipp_labelContext,i)


        def pipp_peak_list_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Pipp_peak_list_2dContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Pipp_peak_list_2dContext,i)


        def pipp_peak_list_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Pipp_peak_list_3dContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Pipp_peak_list_3dContext,i)


        def pipp_peak_list_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Pipp_peak_list_4dContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Pipp_peak_list_4dContext,i)


        def getRuleIndex(self):
            return NmrPipePKParser.RULE_nmrpipe_pk

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNmrpipe_pk" ):
                listener.enterNmrpipe_pk(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNmrpipe_pk" ):
                listener.exitNmrpipe_pk(self)




    def nmrpipe_pk(self):

        localctx = NmrPipePKParser.Nmrpipe_pkContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_nmrpipe_pk)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 35
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.state = 34
                self.match(NmrPipePKParser.RETURN)


            self.state = 48
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 8206) != 0):
                self.state = 46
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
                if la_ == 1:
                    self.state = 37
                    self.data_label()
                    pass

                elif la_ == 2:
                    self.state = 38
                    self.peak_list_2d()
                    pass

                elif la_ == 3:
                    self.state = 39
                    self.peak_list_3d()
                    pass

                elif la_ == 4:
                    self.state = 40
                    self.peak_list_4d()
                    pass

                elif la_ == 5:
                    self.state = 41
                    self.pipp_label()
                    pass

                elif la_ == 6:
                    self.state = 42
                    self.pipp_peak_list_2d()
                    pass

                elif la_ == 7:
                    self.state = 43
                    self.pipp_peak_list_3d()
                    pass

                elif la_ == 8:
                    self.state = 44
                    self.pipp_peak_list_4d()
                    pass

                elif la_ == 9:
                    self.state = 45
                    self.match(NmrPipePKParser.RETURN)
                    pass


                self.state = 50
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 51
            self.match(NmrPipePKParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Data_labelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Data(self):
            return self.getToken(NmrPipePKParser.Data, 0)

        def Simple_name_DA(self):
            return self.getToken(NmrPipePKParser.Simple_name_DA, 0)

        def Integer_DA(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Integer_DA)
            else:
                return self.getToken(NmrPipePKParser.Integer_DA, i)

        def Ppm_value_DA(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Ppm_value_DA)
            else:
                return self.getToken(NmrPipePKParser.Ppm_value_DA, i)

        def RETURN_DA(self):
            return self.getToken(NmrPipePKParser.RETURN_DA, 0)

        def X_axis_DA(self):
            return self.getToken(NmrPipePKParser.X_axis_DA, 0)

        def Y_axis_DA(self):
            return self.getToken(NmrPipePKParser.Y_axis_DA, 0)

        def Z_axis_DA(self):
            return self.getToken(NmrPipePKParser.Z_axis_DA, 0)

        def A_axis_DA(self):
            return self.getToken(NmrPipePKParser.A_axis_DA, 0)

        def getRuleIndex(self):
            return NmrPipePKParser.RULE_data_label

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterData_label" ):
                listener.enterData_label(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitData_label" ):
                listener.exitData_label(self)




    def data_label(self):

        localctx = NmrPipePKParser.Data_labelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_data_label)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 53
            self.match(NmrPipePKParser.Data)
            self.state = 54
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 983040) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 55
            self.match(NmrPipePKParser.Simple_name_DA)
            self.state = 56
            self.match(NmrPipePKParser.Integer_DA)
            self.state = 57
            self.match(NmrPipePKParser.Integer_DA)
            self.state = 58
            self.match(NmrPipePKParser.Ppm_value_DA)
            self.state = 59
            self.match(NmrPipePKParser.Ppm_value_DA)
            self.state = 60
            self.match(NmrPipePKParser.RETURN_DA)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_list_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Vars(self):
            return self.getToken(NmrPipePKParser.Vars, 0)

        def Index(self):
            return self.getToken(NmrPipePKParser.Index, 0)

        def X_axis(self):
            return self.getToken(NmrPipePKParser.X_axis, 0)

        def Y_axis(self):
            return self.getToken(NmrPipePKParser.Y_axis, 0)

        def Dx(self):
            return self.getToken(NmrPipePKParser.Dx, 0)

        def Dy(self):
            return self.getToken(NmrPipePKParser.Dy, 0)

        def X_ppm(self):
            return self.getToken(NmrPipePKParser.X_ppm, 0)

        def Y_ppm(self):
            return self.getToken(NmrPipePKParser.Y_ppm, 0)

        def X_hz(self):
            return self.getToken(NmrPipePKParser.X_hz, 0)

        def Y_hz(self):
            return self.getToken(NmrPipePKParser.Y_hz, 0)

        def Xw(self):
            return self.getToken(NmrPipePKParser.Xw, 0)

        def Yw(self):
            return self.getToken(NmrPipePKParser.Yw, 0)

        def Xw_hz(self):
            return self.getToken(NmrPipePKParser.Xw_hz, 0)

        def Yw_hz(self):
            return self.getToken(NmrPipePKParser.Yw_hz, 0)

        def X1(self):
            return self.getToken(NmrPipePKParser.X1, 0)

        def X3(self):
            return self.getToken(NmrPipePKParser.X3, 0)

        def Y1(self):
            return self.getToken(NmrPipePKParser.Y1, 0)

        def Y3(self):
            return self.getToken(NmrPipePKParser.Y3, 0)

        def Height(self):
            return self.getToken(NmrPipePKParser.Height, 0)

        def DHeight(self):
            return self.getToken(NmrPipePKParser.DHeight, 0)

        def Vol(self):
            return self.getToken(NmrPipePKParser.Vol, 0)

        def Pchi2(self):
            return self.getToken(NmrPipePKParser.Pchi2, 0)

        def Type(self):
            return self.getToken(NmrPipePKParser.Type, 0)

        def ClustId(self):
            return self.getToken(NmrPipePKParser.ClustId, 0)

        def Memcnt(self):
            return self.getToken(NmrPipePKParser.Memcnt, 0)

        def RETURN_VA(self):
            return self.getToken(NmrPipePKParser.RETURN_VA, 0)

        def Format(self):
            return self.getToken(NmrPipePKParser.Format, 0)

        def Format_code(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Format_code)
            else:
                return self.getToken(NmrPipePKParser.Format_code, i)

        def RETURN_FO(self):
            return self.getToken(NmrPipePKParser.RETURN_FO, 0)

        def Ass(self):
            return self.getToken(NmrPipePKParser.Ass, 0)

        def Trouble(self):
            return self.getToken(NmrPipePKParser.Trouble, 0)

        def Null_value(self):
            return self.getToken(NmrPipePKParser.Null_value, 0)

        def Any_name_NV(self):
            return self.getToken(NmrPipePKParser.Any_name_NV, 0)

        def RETURN_NV(self):
            return self.getToken(NmrPipePKParser.RETURN_NV, 0)

        def Null_string(self):
            return self.getToken(NmrPipePKParser.Null_string, 0)

        def Any_name_NS(self):
            return self.getToken(NmrPipePKParser.Any_name_NS, 0)

        def RETURN_NS(self):
            return self.getToken(NmrPipePKParser.RETURN_NS, 0)

        def peak_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Peak_2dContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Peak_2dContext,i)


        def getRuleIndex(self):
            return NmrPipePKParser.RULE_peak_list_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_list_2d" ):
                listener.enterPeak_list_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_list_2d" ):
                listener.exitPeak_list_2d(self)




    def peak_list_2d(self):

        localctx = NmrPipePKParser.Peak_list_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_peak_list_2d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 62
            self.match(NmrPipePKParser.Vars)
            self.state = 63
            self.match(NmrPipePKParser.Index)
            self.state = 64
            self.match(NmrPipePKParser.X_axis)
            self.state = 65
            self.match(NmrPipePKParser.Y_axis)
            self.state = 66
            self.match(NmrPipePKParser.Dx)
            self.state = 67
            self.match(NmrPipePKParser.Dy)
            self.state = 68
            self.match(NmrPipePKParser.X_ppm)
            self.state = 69
            self.match(NmrPipePKParser.Y_ppm)
            self.state = 70
            self.match(NmrPipePKParser.X_hz)
            self.state = 71
            self.match(NmrPipePKParser.Y_hz)
            self.state = 72
            self.match(NmrPipePKParser.Xw)
            self.state = 73
            self.match(NmrPipePKParser.Yw)
            self.state = 74
            self.match(NmrPipePKParser.Xw_hz)
            self.state = 75
            self.match(NmrPipePKParser.Yw_hz)
            self.state = 76
            self.match(NmrPipePKParser.X1)
            self.state = 77
            self.match(NmrPipePKParser.X3)
            self.state = 78
            self.match(NmrPipePKParser.Y1)
            self.state = 79
            self.match(NmrPipePKParser.Y3)
            self.state = 80
            self.match(NmrPipePKParser.Height)
            self.state = 81
            self.match(NmrPipePKParser.DHeight)
            self.state = 82
            self.match(NmrPipePKParser.Vol)
            self.state = 83
            self.match(NmrPipePKParser.Pchi2)
            self.state = 84
            self.match(NmrPipePKParser.Type)
            self.state = 86
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==69:
                self.state = 85
                self.match(NmrPipePKParser.Ass)


            self.state = 88
            self.match(NmrPipePKParser.ClustId)
            self.state = 89
            self.match(NmrPipePKParser.Memcnt)
            self.state = 91
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==72:
                self.state = 90
                self.match(NmrPipePKParser.Trouble)


            self.state = 93
            self.match(NmrPipePKParser.RETURN_VA)
            self.state = 94
            self.match(NmrPipePKParser.Format)
            self.state = 95
            self.match(NmrPipePKParser.Format_code)
            self.state = 96
            self.match(NmrPipePKParser.Format_code)
            self.state = 97
            self.match(NmrPipePKParser.Format_code)
            self.state = 98
            self.match(NmrPipePKParser.Format_code)
            self.state = 99
            self.match(NmrPipePKParser.Format_code)
            self.state = 100
            self.match(NmrPipePKParser.Format_code)
            self.state = 101
            self.match(NmrPipePKParser.Format_code)
            self.state = 102
            self.match(NmrPipePKParser.Format_code)
            self.state = 103
            self.match(NmrPipePKParser.Format_code)
            self.state = 104
            self.match(NmrPipePKParser.Format_code)
            self.state = 105
            self.match(NmrPipePKParser.Format_code)
            self.state = 106
            self.match(NmrPipePKParser.Format_code)
            self.state = 107
            self.match(NmrPipePKParser.Format_code)
            self.state = 108
            self.match(NmrPipePKParser.Format_code)
            self.state = 109
            self.match(NmrPipePKParser.Format_code)
            self.state = 110
            self.match(NmrPipePKParser.Format_code)
            self.state = 111
            self.match(NmrPipePKParser.Format_code)
            self.state = 112
            self.match(NmrPipePKParser.Format_code)
            self.state = 113
            self.match(NmrPipePKParser.Format_code)
            self.state = 114
            self.match(NmrPipePKParser.Format_code)
            self.state = 115
            self.match(NmrPipePKParser.Format_code)
            self.state = 116
            self.match(NmrPipePKParser.Format_code)
            self.state = 118
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
            if la_ == 1:
                self.state = 117
                self.match(NmrPipePKParser.Format_code)


            self.state = 120
            self.match(NmrPipePKParser.Format_code)
            self.state = 121
            self.match(NmrPipePKParser.Format_code)
            self.state = 123
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==91:
                self.state = 122
                self.match(NmrPipePKParser.Format_code)


            self.state = 125
            self.match(NmrPipePKParser.RETURN_FO)
            self.state = 129
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==4:
                self.state = 126
                self.match(NmrPipePKParser.Null_value)
                self.state = 127
                self.match(NmrPipePKParser.Any_name_NV)
                self.state = 128
                self.match(NmrPipePKParser.RETURN_NV)


            self.state = 134
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==5:
                self.state = 131
                self.match(NmrPipePKParser.Null_string)
                self.state = 132
                self.match(NmrPipePKParser.Any_name_NS)
                self.state = 133
                self.match(NmrPipePKParser.RETURN_NS)


            self.state = 137 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 136
                self.peak_2d()
                self.state = 139 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==6):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Integer)
            else:
                return self.getToken(NmrPipePKParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.NumberContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.NumberContext,i)


        def RETURN(self):
            return self.getToken(NmrPipePKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(NmrPipePKParser.EOF, 0)

        def Any_name(self):
            return self.getToken(NmrPipePKParser.Any_name, 0)

        def getRuleIndex(self):
            return NmrPipePKParser.RULE_peak_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_2d" ):
                listener.enterPeak_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_2d" ):
                listener.exitPeak_2d(self)




    def peak_2d(self):

        localctx = NmrPipePKParser.Peak_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_peak_2d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 141
            self.match(NmrPipePKParser.Integer)
            self.state = 142
            self.number()
            self.state = 143
            self.number()
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
            self.number()
            self.state = 150
            self.number()
            self.state = 151
            self.number()
            self.state = 152
            self.number()
            self.state = 153
            self.number()
            self.state = 154
            self.match(NmrPipePKParser.Integer)
            self.state = 155
            self.match(NmrPipePKParser.Integer)
            self.state = 156
            self.match(NmrPipePKParser.Integer)
            self.state = 157
            self.match(NmrPipePKParser.Integer)
            self.state = 158
            self.number()
            self.state = 159
            self.number()
            self.state = 160
            self.number()
            self.state = 161
            self.number()
            self.state = 162
            self.match(NmrPipePKParser.Integer)
            self.state = 164
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==11:
                self.state = 163
                self.match(NmrPipePKParser.Any_name)


            self.state = 166
            self.match(NmrPipePKParser.Integer)
            self.state = 167
            self.match(NmrPipePKParser.Integer)
            self.state = 169
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==6:
                self.state = 168
                self.match(NmrPipePKParser.Integer)


            self.state = 171
            _la = self._input.LA(1)
            if not(_la==-1 or _la==13):
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


    class Peak_list_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Vars(self):
            return self.getToken(NmrPipePKParser.Vars, 0)

        def Index(self):
            return self.getToken(NmrPipePKParser.Index, 0)

        def X_axis(self):
            return self.getToken(NmrPipePKParser.X_axis, 0)

        def Y_axis(self):
            return self.getToken(NmrPipePKParser.Y_axis, 0)

        def Z_axis(self):
            return self.getToken(NmrPipePKParser.Z_axis, 0)

        def Dx(self):
            return self.getToken(NmrPipePKParser.Dx, 0)

        def Dy(self):
            return self.getToken(NmrPipePKParser.Dy, 0)

        def Dz(self):
            return self.getToken(NmrPipePKParser.Dz, 0)

        def X_ppm(self):
            return self.getToken(NmrPipePKParser.X_ppm, 0)

        def Y_ppm(self):
            return self.getToken(NmrPipePKParser.Y_ppm, 0)

        def Z_ppm(self):
            return self.getToken(NmrPipePKParser.Z_ppm, 0)

        def X_hz(self):
            return self.getToken(NmrPipePKParser.X_hz, 0)

        def Y_hz(self):
            return self.getToken(NmrPipePKParser.Y_hz, 0)

        def Z_hz(self):
            return self.getToken(NmrPipePKParser.Z_hz, 0)

        def Xw(self):
            return self.getToken(NmrPipePKParser.Xw, 0)

        def Yw(self):
            return self.getToken(NmrPipePKParser.Yw, 0)

        def Zw(self):
            return self.getToken(NmrPipePKParser.Zw, 0)

        def Xw_hz(self):
            return self.getToken(NmrPipePKParser.Xw_hz, 0)

        def Yw_hz(self):
            return self.getToken(NmrPipePKParser.Yw_hz, 0)

        def Zw_hz(self):
            return self.getToken(NmrPipePKParser.Zw_hz, 0)

        def X1(self):
            return self.getToken(NmrPipePKParser.X1, 0)

        def X3(self):
            return self.getToken(NmrPipePKParser.X3, 0)

        def Y1(self):
            return self.getToken(NmrPipePKParser.Y1, 0)

        def Y3(self):
            return self.getToken(NmrPipePKParser.Y3, 0)

        def Z1(self):
            return self.getToken(NmrPipePKParser.Z1, 0)

        def Z3(self):
            return self.getToken(NmrPipePKParser.Z3, 0)

        def Height(self):
            return self.getToken(NmrPipePKParser.Height, 0)

        def DHeight(self):
            return self.getToken(NmrPipePKParser.DHeight, 0)

        def Vol(self):
            return self.getToken(NmrPipePKParser.Vol, 0)

        def Pchi2(self):
            return self.getToken(NmrPipePKParser.Pchi2, 0)

        def Type(self):
            return self.getToken(NmrPipePKParser.Type, 0)

        def ClustId(self):
            return self.getToken(NmrPipePKParser.ClustId, 0)

        def Memcnt(self):
            return self.getToken(NmrPipePKParser.Memcnt, 0)

        def RETURN_VA(self):
            return self.getToken(NmrPipePKParser.RETURN_VA, 0)

        def Format(self):
            return self.getToken(NmrPipePKParser.Format, 0)

        def Format_code(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Format_code)
            else:
                return self.getToken(NmrPipePKParser.Format_code, i)

        def RETURN_FO(self):
            return self.getToken(NmrPipePKParser.RETURN_FO, 0)

        def Ass(self):
            return self.getToken(NmrPipePKParser.Ass, 0)

        def Trouble(self):
            return self.getToken(NmrPipePKParser.Trouble, 0)

        def Null_value(self):
            return self.getToken(NmrPipePKParser.Null_value, 0)

        def Any_name_NV(self):
            return self.getToken(NmrPipePKParser.Any_name_NV, 0)

        def RETURN_NV(self):
            return self.getToken(NmrPipePKParser.RETURN_NV, 0)

        def Null_string(self):
            return self.getToken(NmrPipePKParser.Null_string, 0)

        def Any_name_NS(self):
            return self.getToken(NmrPipePKParser.Any_name_NS, 0)

        def RETURN_NS(self):
            return self.getToken(NmrPipePKParser.RETURN_NS, 0)

        def peak_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Peak_3dContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Peak_3dContext,i)


        def getRuleIndex(self):
            return NmrPipePKParser.RULE_peak_list_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_list_3d" ):
                listener.enterPeak_list_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_list_3d" ):
                listener.exitPeak_list_3d(self)




    def peak_list_3d(self):

        localctx = NmrPipePKParser.Peak_list_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_peak_list_3d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 173
            self.match(NmrPipePKParser.Vars)
            self.state = 174
            self.match(NmrPipePKParser.Index)
            self.state = 175
            self.match(NmrPipePKParser.X_axis)
            self.state = 176
            self.match(NmrPipePKParser.Y_axis)
            self.state = 177
            self.match(NmrPipePKParser.Z_axis)
            self.state = 178
            self.match(NmrPipePKParser.Dx)
            self.state = 179
            self.match(NmrPipePKParser.Dy)
            self.state = 180
            self.match(NmrPipePKParser.Dz)
            self.state = 181
            self.match(NmrPipePKParser.X_ppm)
            self.state = 182
            self.match(NmrPipePKParser.Y_ppm)
            self.state = 183
            self.match(NmrPipePKParser.Z_ppm)
            self.state = 184
            self.match(NmrPipePKParser.X_hz)
            self.state = 185
            self.match(NmrPipePKParser.Y_hz)
            self.state = 186
            self.match(NmrPipePKParser.Z_hz)
            self.state = 187
            self.match(NmrPipePKParser.Xw)
            self.state = 188
            self.match(NmrPipePKParser.Yw)
            self.state = 189
            self.match(NmrPipePKParser.Zw)
            self.state = 190
            self.match(NmrPipePKParser.Xw_hz)
            self.state = 191
            self.match(NmrPipePKParser.Yw_hz)
            self.state = 192
            self.match(NmrPipePKParser.Zw_hz)
            self.state = 193
            self.match(NmrPipePKParser.X1)
            self.state = 194
            self.match(NmrPipePKParser.X3)
            self.state = 195
            self.match(NmrPipePKParser.Y1)
            self.state = 196
            self.match(NmrPipePKParser.Y3)
            self.state = 197
            self.match(NmrPipePKParser.Z1)
            self.state = 198
            self.match(NmrPipePKParser.Z3)
            self.state = 199
            self.match(NmrPipePKParser.Height)
            self.state = 200
            self.match(NmrPipePKParser.DHeight)
            self.state = 201
            self.match(NmrPipePKParser.Vol)
            self.state = 202
            self.match(NmrPipePKParser.Pchi2)
            self.state = 203
            self.match(NmrPipePKParser.Type)
            self.state = 205
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==69:
                self.state = 204
                self.match(NmrPipePKParser.Ass)


            self.state = 207
            self.match(NmrPipePKParser.ClustId)
            self.state = 208
            self.match(NmrPipePKParser.Memcnt)
            self.state = 210
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==72:
                self.state = 209
                self.match(NmrPipePKParser.Trouble)


            self.state = 212
            self.match(NmrPipePKParser.RETURN_VA)
            self.state = 213
            self.match(NmrPipePKParser.Format)
            self.state = 214
            self.match(NmrPipePKParser.Format_code)
            self.state = 215
            self.match(NmrPipePKParser.Format_code)
            self.state = 216
            self.match(NmrPipePKParser.Format_code)
            self.state = 217
            self.match(NmrPipePKParser.Format_code)
            self.state = 218
            self.match(NmrPipePKParser.Format_code)
            self.state = 219
            self.match(NmrPipePKParser.Format_code)
            self.state = 220
            self.match(NmrPipePKParser.Format_code)
            self.state = 221
            self.match(NmrPipePKParser.Format_code)
            self.state = 222
            self.match(NmrPipePKParser.Format_code)
            self.state = 223
            self.match(NmrPipePKParser.Format_code)
            self.state = 224
            self.match(NmrPipePKParser.Format_code)
            self.state = 225
            self.match(NmrPipePKParser.Format_code)
            self.state = 226
            self.match(NmrPipePKParser.Format_code)
            self.state = 227
            self.match(NmrPipePKParser.Format_code)
            self.state = 228
            self.match(NmrPipePKParser.Format_code)
            self.state = 229
            self.match(NmrPipePKParser.Format_code)
            self.state = 230
            self.match(NmrPipePKParser.Format_code)
            self.state = 231
            self.match(NmrPipePKParser.Format_code)
            self.state = 232
            self.match(NmrPipePKParser.Format_code)
            self.state = 233
            self.match(NmrPipePKParser.Format_code)
            self.state = 234
            self.match(NmrPipePKParser.Format_code)
            self.state = 235
            self.match(NmrPipePKParser.Format_code)
            self.state = 236
            self.match(NmrPipePKParser.Format_code)
            self.state = 237
            self.match(NmrPipePKParser.Format_code)
            self.state = 238
            self.match(NmrPipePKParser.Format_code)
            self.state = 239
            self.match(NmrPipePKParser.Format_code)
            self.state = 240
            self.match(NmrPipePKParser.Format_code)
            self.state = 241
            self.match(NmrPipePKParser.Format_code)
            self.state = 242
            self.match(NmrPipePKParser.Format_code)
            self.state = 243
            self.match(NmrPipePKParser.Format_code)
            self.state = 245
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,14,self._ctx)
            if la_ == 1:
                self.state = 244
                self.match(NmrPipePKParser.Format_code)


            self.state = 247
            self.match(NmrPipePKParser.Format_code)
            self.state = 248
            self.match(NmrPipePKParser.Format_code)
            self.state = 250
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==91:
                self.state = 249
                self.match(NmrPipePKParser.Format_code)


            self.state = 252
            self.match(NmrPipePKParser.RETURN_FO)
            self.state = 256
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==4:
                self.state = 253
                self.match(NmrPipePKParser.Null_value)
                self.state = 254
                self.match(NmrPipePKParser.Any_name_NV)
                self.state = 255
                self.match(NmrPipePKParser.RETURN_NV)


            self.state = 261
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==5:
                self.state = 258
                self.match(NmrPipePKParser.Null_string)
                self.state = 259
                self.match(NmrPipePKParser.Any_name_NS)
                self.state = 260
                self.match(NmrPipePKParser.RETURN_NS)


            self.state = 264 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 263
                self.peak_3d()
                self.state = 266 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==6):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Integer)
            else:
                return self.getToken(NmrPipePKParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.NumberContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.NumberContext,i)


        def RETURN(self):
            return self.getToken(NmrPipePKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(NmrPipePKParser.EOF, 0)

        def Any_name(self):
            return self.getToken(NmrPipePKParser.Any_name, 0)

        def getRuleIndex(self):
            return NmrPipePKParser.RULE_peak_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_3d" ):
                listener.enterPeak_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_3d" ):
                listener.exitPeak_3d(self)




    def peak_3d(self):

        localctx = NmrPipePKParser.Peak_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_peak_3d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 268
            self.match(NmrPipePKParser.Integer)
            self.state = 269
            self.number()
            self.state = 270
            self.number()
            self.state = 271
            self.number()
            self.state = 272
            self.number()
            self.state = 273
            self.number()
            self.state = 274
            self.number()
            self.state = 275
            self.number()
            self.state = 276
            self.number()
            self.state = 277
            self.number()
            self.state = 278
            self.number()
            self.state = 279
            self.number()
            self.state = 280
            self.number()
            self.state = 281
            self.number()
            self.state = 282
            self.number()
            self.state = 283
            self.number()
            self.state = 284
            self.number()
            self.state = 285
            self.number()
            self.state = 286
            self.number()
            self.state = 287
            self.match(NmrPipePKParser.Integer)
            self.state = 288
            self.match(NmrPipePKParser.Integer)
            self.state = 289
            self.match(NmrPipePKParser.Integer)
            self.state = 290
            self.match(NmrPipePKParser.Integer)
            self.state = 291
            self.match(NmrPipePKParser.Integer)
            self.state = 292
            self.match(NmrPipePKParser.Integer)
            self.state = 293
            self.number()
            self.state = 294
            self.number()
            self.state = 295
            self.number()
            self.state = 296
            self.number()
            self.state = 297
            self.match(NmrPipePKParser.Integer)
            self.state = 299
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==11:
                self.state = 298
                self.match(NmrPipePKParser.Any_name)


            self.state = 301
            self.match(NmrPipePKParser.Integer)
            self.state = 302
            self.match(NmrPipePKParser.Integer)
            self.state = 304
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==6:
                self.state = 303
                self.match(NmrPipePKParser.Integer)


            self.state = 306
            _la = self._input.LA(1)
            if not(_la==-1 or _la==13):
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


    class Peak_list_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Vars(self):
            return self.getToken(NmrPipePKParser.Vars, 0)

        def Index(self):
            return self.getToken(NmrPipePKParser.Index, 0)

        def X_axis(self):
            return self.getToken(NmrPipePKParser.X_axis, 0)

        def Y_axis(self):
            return self.getToken(NmrPipePKParser.Y_axis, 0)

        def Z_axis(self):
            return self.getToken(NmrPipePKParser.Z_axis, 0)

        def A_axis(self):
            return self.getToken(NmrPipePKParser.A_axis, 0)

        def Dx(self):
            return self.getToken(NmrPipePKParser.Dx, 0)

        def Dy(self):
            return self.getToken(NmrPipePKParser.Dy, 0)

        def Dz(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Dz)
            else:
                return self.getToken(NmrPipePKParser.Dz, i)

        def X_ppm(self):
            return self.getToken(NmrPipePKParser.X_ppm, 0)

        def Y_ppm(self):
            return self.getToken(NmrPipePKParser.Y_ppm, 0)

        def Z_ppm(self):
            return self.getToken(NmrPipePKParser.Z_ppm, 0)

        def A_ppm(self):
            return self.getToken(NmrPipePKParser.A_ppm, 0)

        def X_hz(self):
            return self.getToken(NmrPipePKParser.X_hz, 0)

        def Y_hz(self):
            return self.getToken(NmrPipePKParser.Y_hz, 0)

        def Z_hz(self):
            return self.getToken(NmrPipePKParser.Z_hz, 0)

        def A_hz(self):
            return self.getToken(NmrPipePKParser.A_hz, 0)

        def Xw(self):
            return self.getToken(NmrPipePKParser.Xw, 0)

        def Yw(self):
            return self.getToken(NmrPipePKParser.Yw, 0)

        def Zw(self):
            return self.getToken(NmrPipePKParser.Zw, 0)

        def Aw(self):
            return self.getToken(NmrPipePKParser.Aw, 0)

        def Xw_hz(self):
            return self.getToken(NmrPipePKParser.Xw_hz, 0)

        def Yw_hz(self):
            return self.getToken(NmrPipePKParser.Yw_hz, 0)

        def Zw_hz(self):
            return self.getToken(NmrPipePKParser.Zw_hz, 0)

        def Aw_hz(self):
            return self.getToken(NmrPipePKParser.Aw_hz, 0)

        def X1(self):
            return self.getToken(NmrPipePKParser.X1, 0)

        def X3(self):
            return self.getToken(NmrPipePKParser.X3, 0)

        def Y1(self):
            return self.getToken(NmrPipePKParser.Y1, 0)

        def Y3(self):
            return self.getToken(NmrPipePKParser.Y3, 0)

        def Z1(self):
            return self.getToken(NmrPipePKParser.Z1, 0)

        def Z3(self):
            return self.getToken(NmrPipePKParser.Z3, 0)

        def A1(self):
            return self.getToken(NmrPipePKParser.A1, 0)

        def A3(self):
            return self.getToken(NmrPipePKParser.A3, 0)

        def Height(self):
            return self.getToken(NmrPipePKParser.Height, 0)

        def DHeight(self):
            return self.getToken(NmrPipePKParser.DHeight, 0)

        def Vol(self):
            return self.getToken(NmrPipePKParser.Vol, 0)

        def Pchi2(self):
            return self.getToken(NmrPipePKParser.Pchi2, 0)

        def Type(self):
            return self.getToken(NmrPipePKParser.Type, 0)

        def ClustId(self):
            return self.getToken(NmrPipePKParser.ClustId, 0)

        def Memcnt(self):
            return self.getToken(NmrPipePKParser.Memcnt, 0)

        def RETURN_VA(self):
            return self.getToken(NmrPipePKParser.RETURN_VA, 0)

        def Format(self):
            return self.getToken(NmrPipePKParser.Format, 0)

        def Format_code(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Format_code)
            else:
                return self.getToken(NmrPipePKParser.Format_code, i)

        def RETURN_FO(self):
            return self.getToken(NmrPipePKParser.RETURN_FO, 0)

        def Ass(self):
            return self.getToken(NmrPipePKParser.Ass, 0)

        def Trouble(self):
            return self.getToken(NmrPipePKParser.Trouble, 0)

        def Null_value(self):
            return self.getToken(NmrPipePKParser.Null_value, 0)

        def Any_name_NV(self):
            return self.getToken(NmrPipePKParser.Any_name_NV, 0)

        def RETURN_NV(self):
            return self.getToken(NmrPipePKParser.RETURN_NV, 0)

        def Null_string(self):
            return self.getToken(NmrPipePKParser.Null_string, 0)

        def Any_name_NS(self):
            return self.getToken(NmrPipePKParser.Any_name_NS, 0)

        def RETURN_NS(self):
            return self.getToken(NmrPipePKParser.RETURN_NS, 0)

        def peak_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Peak_4dContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Peak_4dContext,i)


        def getRuleIndex(self):
            return NmrPipePKParser.RULE_peak_list_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_list_4d" ):
                listener.enterPeak_list_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_list_4d" ):
                listener.exitPeak_list_4d(self)




    def peak_list_4d(self):

        localctx = NmrPipePKParser.Peak_list_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_peak_list_4d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 308
            self.match(NmrPipePKParser.Vars)
            self.state = 309
            self.match(NmrPipePKParser.Index)
            self.state = 310
            self.match(NmrPipePKParser.X_axis)
            self.state = 311
            self.match(NmrPipePKParser.Y_axis)
            self.state = 312
            self.match(NmrPipePKParser.Z_axis)
            self.state = 313
            self.match(NmrPipePKParser.A_axis)
            self.state = 314
            self.match(NmrPipePKParser.Dx)
            self.state = 315
            self.match(NmrPipePKParser.Dy)
            self.state = 316
            self.match(NmrPipePKParser.Dz)
            self.state = 317
            self.match(NmrPipePKParser.Dz)
            self.state = 318
            self.match(NmrPipePKParser.X_ppm)
            self.state = 319
            self.match(NmrPipePKParser.Y_ppm)
            self.state = 320
            self.match(NmrPipePKParser.Z_ppm)
            self.state = 321
            self.match(NmrPipePKParser.A_ppm)
            self.state = 322
            self.match(NmrPipePKParser.X_hz)
            self.state = 323
            self.match(NmrPipePKParser.Y_hz)
            self.state = 324
            self.match(NmrPipePKParser.Z_hz)
            self.state = 325
            self.match(NmrPipePKParser.A_hz)
            self.state = 326
            self.match(NmrPipePKParser.Xw)
            self.state = 327
            self.match(NmrPipePKParser.Yw)
            self.state = 328
            self.match(NmrPipePKParser.Zw)
            self.state = 329
            self.match(NmrPipePKParser.Aw)
            self.state = 330
            self.match(NmrPipePKParser.Xw_hz)
            self.state = 331
            self.match(NmrPipePKParser.Yw_hz)
            self.state = 332
            self.match(NmrPipePKParser.Zw_hz)
            self.state = 333
            self.match(NmrPipePKParser.Aw_hz)
            self.state = 334
            self.match(NmrPipePKParser.X1)
            self.state = 335
            self.match(NmrPipePKParser.X3)
            self.state = 336
            self.match(NmrPipePKParser.Y1)
            self.state = 337
            self.match(NmrPipePKParser.Y3)
            self.state = 338
            self.match(NmrPipePKParser.Z1)
            self.state = 339
            self.match(NmrPipePKParser.Z3)
            self.state = 340
            self.match(NmrPipePKParser.A1)
            self.state = 341
            self.match(NmrPipePKParser.A3)
            self.state = 342
            self.match(NmrPipePKParser.Height)
            self.state = 343
            self.match(NmrPipePKParser.DHeight)
            self.state = 344
            self.match(NmrPipePKParser.Vol)
            self.state = 345
            self.match(NmrPipePKParser.Pchi2)
            self.state = 346
            self.match(NmrPipePKParser.Type)
            self.state = 348
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==69:
                self.state = 347
                self.match(NmrPipePKParser.Ass)


            self.state = 350
            self.match(NmrPipePKParser.ClustId)
            self.state = 351
            self.match(NmrPipePKParser.Memcnt)
            self.state = 353
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==72:
                self.state = 352
                self.match(NmrPipePKParser.Trouble)


            self.state = 355
            self.match(NmrPipePKParser.RETURN_VA)
            self.state = 356
            self.match(NmrPipePKParser.Format)
            self.state = 357
            self.match(NmrPipePKParser.Format_code)
            self.state = 358
            self.match(NmrPipePKParser.Format_code)
            self.state = 359
            self.match(NmrPipePKParser.Format_code)
            self.state = 360
            self.match(NmrPipePKParser.Format_code)
            self.state = 361
            self.match(NmrPipePKParser.Format_code)
            self.state = 362
            self.match(NmrPipePKParser.Format_code)
            self.state = 363
            self.match(NmrPipePKParser.Format_code)
            self.state = 364
            self.match(NmrPipePKParser.Format_code)
            self.state = 365
            self.match(NmrPipePKParser.Format_code)
            self.state = 366
            self.match(NmrPipePKParser.Format_code)
            self.state = 367
            self.match(NmrPipePKParser.Format_code)
            self.state = 368
            self.match(NmrPipePKParser.Format_code)
            self.state = 369
            self.match(NmrPipePKParser.Format_code)
            self.state = 370
            self.match(NmrPipePKParser.Format_code)
            self.state = 371
            self.match(NmrPipePKParser.Format_code)
            self.state = 372
            self.match(NmrPipePKParser.Format_code)
            self.state = 373
            self.match(NmrPipePKParser.Format_code)
            self.state = 374
            self.match(NmrPipePKParser.Format_code)
            self.state = 375
            self.match(NmrPipePKParser.Format_code)
            self.state = 376
            self.match(NmrPipePKParser.Format_code)
            self.state = 377
            self.match(NmrPipePKParser.Format_code)
            self.state = 378
            self.match(NmrPipePKParser.Format_code)
            self.state = 379
            self.match(NmrPipePKParser.Format_code)
            self.state = 380
            self.match(NmrPipePKParser.Format_code)
            self.state = 381
            self.match(NmrPipePKParser.Format_code)
            self.state = 382
            self.match(NmrPipePKParser.Format_code)
            self.state = 383
            self.match(NmrPipePKParser.Format_code)
            self.state = 384
            self.match(NmrPipePKParser.Format_code)
            self.state = 385
            self.match(NmrPipePKParser.Format_code)
            self.state = 386
            self.match(NmrPipePKParser.Format_code)
            self.state = 387
            self.match(NmrPipePKParser.Format_code)
            self.state = 388
            self.match(NmrPipePKParser.Format_code)
            self.state = 389
            self.match(NmrPipePKParser.Format_code)
            self.state = 390
            self.match(NmrPipePKParser.Format_code)
            self.state = 391
            self.match(NmrPipePKParser.Format_code)
            self.state = 392
            self.match(NmrPipePKParser.Format_code)
            self.state = 393
            self.match(NmrPipePKParser.Format_code)
            self.state = 394
            self.match(NmrPipePKParser.Format_code)
            self.state = 396
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,23,self._ctx)
            if la_ == 1:
                self.state = 395
                self.match(NmrPipePKParser.Format_code)


            self.state = 398
            self.match(NmrPipePKParser.Format_code)
            self.state = 399
            self.match(NmrPipePKParser.Format_code)
            self.state = 401
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==91:
                self.state = 400
                self.match(NmrPipePKParser.Format_code)


            self.state = 403
            self.match(NmrPipePKParser.RETURN_FO)
            self.state = 407
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==4:
                self.state = 404
                self.match(NmrPipePKParser.Null_value)
                self.state = 405
                self.match(NmrPipePKParser.Any_name_NV)
                self.state = 406
                self.match(NmrPipePKParser.RETURN_NV)


            self.state = 412
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==5:
                self.state = 409
                self.match(NmrPipePKParser.Null_string)
                self.state = 410
                self.match(NmrPipePKParser.Any_name_NS)
                self.state = 411
                self.match(NmrPipePKParser.RETURN_NS)


            self.state = 415 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 414
                self.peak_4d()
                self.state = 417 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==6):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Peak_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Integer)
            else:
                return self.getToken(NmrPipePKParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.NumberContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.NumberContext,i)


        def RETURN(self):
            return self.getToken(NmrPipePKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(NmrPipePKParser.EOF, 0)

        def Any_name(self):
            return self.getToken(NmrPipePKParser.Any_name, 0)

        def getRuleIndex(self):
            return NmrPipePKParser.RULE_peak_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPeak_4d" ):
                listener.enterPeak_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPeak_4d" ):
                listener.exitPeak_4d(self)




    def peak_4d(self):

        localctx = NmrPipePKParser.Peak_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_peak_4d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 419
            self.match(NmrPipePKParser.Integer)
            self.state = 420
            self.number()
            self.state = 421
            self.number()
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
            self.number()
            self.state = 428
            self.number()
            self.state = 429
            self.number()
            self.state = 430
            self.number()
            self.state = 431
            self.number()
            self.state = 432
            self.number()
            self.state = 433
            self.number()
            self.state = 434
            self.number()
            self.state = 435
            self.number()
            self.state = 436
            self.number()
            self.state = 437
            self.number()
            self.state = 438
            self.number()
            self.state = 439
            self.number()
            self.state = 440
            self.number()
            self.state = 441
            self.number()
            self.state = 442
            self.number()
            self.state = 443
            self.number()
            self.state = 444
            self.match(NmrPipePKParser.Integer)
            self.state = 445
            self.match(NmrPipePKParser.Integer)
            self.state = 446
            self.match(NmrPipePKParser.Integer)
            self.state = 447
            self.match(NmrPipePKParser.Integer)
            self.state = 448
            self.match(NmrPipePKParser.Integer)
            self.state = 449
            self.match(NmrPipePKParser.Integer)
            self.state = 450
            self.match(NmrPipePKParser.Integer)
            self.state = 451
            self.match(NmrPipePKParser.Integer)
            self.state = 452
            self.number()
            self.state = 453
            self.number()
            self.state = 454
            self.number()
            self.state = 455
            self.number()
            self.state = 456
            self.match(NmrPipePKParser.Integer)
            self.state = 458
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==11:
                self.state = 457
                self.match(NmrPipePKParser.Any_name)


            self.state = 460
            self.match(NmrPipePKParser.Integer)
            self.state = 461
            self.match(NmrPipePKParser.Integer)
            self.state = 463
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==6:
                self.state = 462
                self.match(NmrPipePKParser.Integer)


            self.state = 465
            _la = self._input.LA(1)
            if not(_la==-1 or _la==13):
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


    class Pipp_labelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Data(self):
            return self.getToken(NmrPipePKParser.Data, 0)

        def Dim_count_DA(self):
            return self.getToken(NmrPipePKParser.Dim_count_DA, 0)

        def Integer_DA(self):
            return self.getToken(NmrPipePKParser.Integer_DA, 0)

        def RETURN_DA(self):
            return self.getToken(NmrPipePKParser.RETURN_DA, 0)

        def pipp_axis(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Pipp_axisContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Pipp_axisContext,i)


        def getRuleIndex(self):
            return NmrPipePKParser.RULE_pipp_label

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPipp_label" ):
                listener.enterPipp_label(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPipp_label" ):
                listener.exitPipp_label(self)




    def pipp_label(self):

        localctx = NmrPipePKParser.Pipp_labelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_pipp_label)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 467
            self.match(NmrPipePKParser.Data)
            self.state = 468
            self.match(NmrPipePKParser.Dim_count_DA)
            self.state = 469
            self.match(NmrPipePKParser.Integer_DA)
            self.state = 470
            self.match(NmrPipePKParser.RETURN_DA)
            self.state = 472 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 471
                    self.pipp_axis()

                else:
                    raise NoViableAltException(self)
                self.state = 474 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,30,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Pipp_axisContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Data(self):
            return self.getToken(NmrPipePKParser.Data, 0)

        def Integer_DA(self):
            return self.getToken(NmrPipePKParser.Integer_DA, 0)

        def Float_DA(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Float_DA)
            else:
                return self.getToken(NmrPipePKParser.Float_DA, i)

        def RETURN_DA(self):
            return self.getToken(NmrPipePKParser.RETURN_DA, 0)

        def X_axis_DA(self):
            return self.getToken(NmrPipePKParser.X_axis_DA, 0)

        def Y_axis_DA(self):
            return self.getToken(NmrPipePKParser.Y_axis_DA, 0)

        def Z_axis_DA(self):
            return self.getToken(NmrPipePKParser.Z_axis_DA, 0)

        def A_axis_DA(self):
            return self.getToken(NmrPipePKParser.A_axis_DA, 0)

        def Ppm_DA(self):
            return self.getToken(NmrPipePKParser.Ppm_DA, 0)

        def Hz_DA(self):
            return self.getToken(NmrPipePKParser.Hz_DA, 0)

        def getRuleIndex(self):
            return NmrPipePKParser.RULE_pipp_axis

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPipp_axis" ):
                listener.enterPipp_axis(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPipp_axis" ):
                listener.exitPipp_axis(self)




    def pipp_axis(self):

        localctx = NmrPipePKParser.Pipp_axisContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_pipp_axis)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 476
            self.match(NmrPipePKParser.Data)
            self.state = 477
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 983040) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 478
            self.match(NmrPipePKParser.Integer_DA)
            self.state = 479
            self.match(NmrPipePKParser.Float_DA)
            self.state = 480
            self.match(NmrPipePKParser.Float_DA)
            self.state = 481
            self.match(NmrPipePKParser.Float_DA)
            self.state = 482
            _la = self._input.LA(1)
            if not(_la==22 or _la==23):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 483
            self.match(NmrPipePKParser.Float_DA)
            self.state = 484
            self.match(NmrPipePKParser.RETURN_DA)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Pipp_peak_list_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Format(self):
            return self.getToken(NmrPipePKParser.Format, 0)

        def RETURN_FO(self):
            return self.getToken(NmrPipePKParser.RETURN_FO, 0)

        def Vars(self):
            return self.getToken(NmrPipePKParser.Vars, 0)

        def PkID(self):
            return self.getToken(NmrPipePKParser.PkID, 0)

        def X(self):
            return self.getToken(NmrPipePKParser.X, 0)

        def Y(self):
            return self.getToken(NmrPipePKParser.Y, 0)

        def Intensity(self):
            return self.getToken(NmrPipePKParser.Intensity, 0)

        def RETURN_VA(self):
            return self.getToken(NmrPipePKParser.RETURN_VA, 0)

        def Format_code(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Format_code)
            else:
                return self.getToken(NmrPipePKParser.Format_code, i)

        def Assign(self):
            return self.getToken(NmrPipePKParser.Assign, 0)

        def Assign1(self):
            return self.getToken(NmrPipePKParser.Assign1, 0)

        def Assign2(self):
            return self.getToken(NmrPipePKParser.Assign2, 0)

        def pipp_peak_2d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Pipp_peak_2dContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Pipp_peak_2dContext,i)


        def getRuleIndex(self):
            return NmrPipePKParser.RULE_pipp_peak_list_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPipp_peak_list_2d" ):
                listener.enterPipp_peak_list_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPipp_peak_list_2d" ):
                listener.exitPipp_peak_list_2d(self)




    def pipp_peak_list_2d(self):

        localctx = NmrPipePKParser.Pipp_peak_list_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_pipp_peak_list_2d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 486
            self.match(NmrPipePKParser.Format)
            self.state = 488 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 487
                self.match(NmrPipePKParser.Format_code)
                self.state = 490 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==91):
                    break

            self.state = 492
            self.match(NmrPipePKParser.RETURN_FO)
            self.state = 493
            self.match(NmrPipePKParser.Vars)
            self.state = 494
            self.match(NmrPipePKParser.PkID)
            self.state = 495
            self.match(NmrPipePKParser.X)
            self.state = 496
            self.match(NmrPipePKParser.Y)
            self.state = 497
            self.match(NmrPipePKParser.Intensity)
            self.state = 501
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [81]:
                self.state = 498
                self.match(NmrPipePKParser.Assign)
                pass
            elif token in [82]:
                self.state = 499
                self.match(NmrPipePKParser.Assign1)
                self.state = 500
                self.match(NmrPipePKParser.Assign2)
                pass
            elif token in [89]:
                pass
            else:
                pass
            self.state = 503
            self.match(NmrPipePKParser.RETURN_VA)
            self.state = 505 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 504
                self.pipp_peak_2d()
                self.state = 507 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==6):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Pipp_peak_2dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self):
            return self.getToken(NmrPipePKParser.Integer, 0)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.NumberContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.NumberContext,i)


        def RETURN(self):
            return self.getToken(NmrPipePKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(NmrPipePKParser.EOF, 0)

        def getRuleIndex(self):
            return NmrPipePKParser.RULE_pipp_peak_2d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPipp_peak_2d" ):
                listener.enterPipp_peak_2d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPipp_peak_2d" ):
                listener.exitPipp_peak_2d(self)




    def pipp_peak_2d(self):

        localctx = NmrPipePKParser.Pipp_peak_2dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_pipp_peak_2d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 509
            self.match(NmrPipePKParser.Integer)
            self.state = 510
            self.number()
            self.state = 511
            self.number()
            self.state = 513 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 512
                self.number()
                self.state = 515 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 2496) != 0)):
                    break

            self.state = 517
            _la = self._input.LA(1)
            if not(_la==-1 or _la==13):
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


    class Pipp_peak_list_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Format(self):
            return self.getToken(NmrPipePKParser.Format, 0)

        def RETURN_FO(self):
            return self.getToken(NmrPipePKParser.RETURN_FO, 0)

        def Vars(self):
            return self.getToken(NmrPipePKParser.Vars, 0)

        def PkID(self):
            return self.getToken(NmrPipePKParser.PkID, 0)

        def X(self):
            return self.getToken(NmrPipePKParser.X, 0)

        def Y(self):
            return self.getToken(NmrPipePKParser.Y, 0)

        def Z(self):
            return self.getToken(NmrPipePKParser.Z, 0)

        def Intensity(self):
            return self.getToken(NmrPipePKParser.Intensity, 0)

        def RETURN_VA(self):
            return self.getToken(NmrPipePKParser.RETURN_VA, 0)

        def Format_code(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Format_code)
            else:
                return self.getToken(NmrPipePKParser.Format_code, i)

        def Sl_Z(self):
            return self.getToken(NmrPipePKParser.Sl_Z, 0)

        def Assign(self):
            return self.getToken(NmrPipePKParser.Assign, 0)

        def Assign1(self):
            return self.getToken(NmrPipePKParser.Assign1, 0)

        def Assign2(self):
            return self.getToken(NmrPipePKParser.Assign2, 0)

        def pipp_peak_3d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Pipp_peak_3dContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Pipp_peak_3dContext,i)


        def getRuleIndex(self):
            return NmrPipePKParser.RULE_pipp_peak_list_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPipp_peak_list_3d" ):
                listener.enterPipp_peak_list_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPipp_peak_list_3d" ):
                listener.exitPipp_peak_list_3d(self)




    def pipp_peak_list_3d(self):

        localctx = NmrPipePKParser.Pipp_peak_list_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_pipp_peak_list_3d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 519
            self.match(NmrPipePKParser.Format)
            self.state = 521 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 520
                self.match(NmrPipePKParser.Format_code)
                self.state = 523 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==91):
                    break

            self.state = 525
            self.match(NmrPipePKParser.RETURN_FO)
            self.state = 526
            self.match(NmrPipePKParser.Vars)
            self.state = 527
            self.match(NmrPipePKParser.PkID)
            self.state = 529
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==74:
                self.state = 528
                self.match(NmrPipePKParser.Sl_Z)


            self.state = 531
            self.match(NmrPipePKParser.X)
            self.state = 532
            self.match(NmrPipePKParser.Y)
            self.state = 533
            self.match(NmrPipePKParser.Z)
            self.state = 534
            self.match(NmrPipePKParser.Intensity)
            self.state = 538
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [81]:
                self.state = 535
                self.match(NmrPipePKParser.Assign)
                pass
            elif token in [82]:
                self.state = 536
                self.match(NmrPipePKParser.Assign1)
                self.state = 537
                self.match(NmrPipePKParser.Assign2)
                pass
            elif token in [89]:
                pass
            else:
                pass
            self.state = 540
            self.match(NmrPipePKParser.RETURN_VA)
            self.state = 542 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 541
                self.pipp_peak_3d()
                self.state = 544 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==6):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Pipp_peak_3dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Integer)
            else:
                return self.getToken(NmrPipePKParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.NumberContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.NumberContext,i)


        def RETURN(self):
            return self.getToken(NmrPipePKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(NmrPipePKParser.EOF, 0)

        def getRuleIndex(self):
            return NmrPipePKParser.RULE_pipp_peak_3d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPipp_peak_3d" ):
                listener.enterPipp_peak_3d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPipp_peak_3d" ):
                listener.exitPipp_peak_3d(self)




    def pipp_peak_3d(self):

        localctx = NmrPipePKParser.Pipp_peak_3dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_pipp_peak_3d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 546
            self.match(NmrPipePKParser.Integer)
            self.state = 548
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,39,self._ctx)
            if la_ == 1:
                self.state = 547
                self.match(NmrPipePKParser.Integer)


            self.state = 550
            self.number()
            self.state = 551
            self.number()
            self.state = 552
            self.number()
            self.state = 554 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 553
                self.number()
                self.state = 556 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 2496) != 0)):
                    break

            self.state = 558
            _la = self._input.LA(1)
            if not(_la==-1 or _la==13):
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


    class Pipp_peak_list_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Format(self):
            return self.getToken(NmrPipePKParser.Format, 0)

        def RETURN_FO(self):
            return self.getToken(NmrPipePKParser.RETURN_FO, 0)

        def Vars(self):
            return self.getToken(NmrPipePKParser.Vars, 0)

        def PkID(self):
            return self.getToken(NmrPipePKParser.PkID, 0)

        def X(self):
            return self.getToken(NmrPipePKParser.X, 0)

        def Y(self):
            return self.getToken(NmrPipePKParser.Y, 0)

        def Z(self):
            return self.getToken(NmrPipePKParser.Z, 0)

        def A(self):
            return self.getToken(NmrPipePKParser.A, 0)

        def Intensity(self):
            return self.getToken(NmrPipePKParser.Intensity, 0)

        def RETURN_VA(self):
            return self.getToken(NmrPipePKParser.RETURN_VA, 0)

        def Format_code(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Format_code)
            else:
                return self.getToken(NmrPipePKParser.Format_code, i)

        def Sl_A(self):
            return self.getToken(NmrPipePKParser.Sl_A, 0)

        def Sl_Z(self):
            return self.getToken(NmrPipePKParser.Sl_Z, 0)

        def Assign(self):
            return self.getToken(NmrPipePKParser.Assign, 0)

        def Assign1(self):
            return self.getToken(NmrPipePKParser.Assign1, 0)

        def Assign2(self):
            return self.getToken(NmrPipePKParser.Assign2, 0)

        def pipp_peak_4d(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.Pipp_peak_4dContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.Pipp_peak_4dContext,i)


        def getRuleIndex(self):
            return NmrPipePKParser.RULE_pipp_peak_list_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPipp_peak_list_4d" ):
                listener.enterPipp_peak_list_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPipp_peak_list_4d" ):
                listener.exitPipp_peak_list_4d(self)




    def pipp_peak_list_4d(self):

        localctx = NmrPipePKParser.Pipp_peak_list_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_pipp_peak_list_4d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 560
            self.match(NmrPipePKParser.Format)
            self.state = 562 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 561
                self.match(NmrPipePKParser.Format_code)
                self.state = 564 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==91):
                    break

            self.state = 566
            self.match(NmrPipePKParser.RETURN_FO)
            self.state = 567
            self.match(NmrPipePKParser.Vars)
            self.state = 568
            self.match(NmrPipePKParser.PkID)
            self.state = 570
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==75:
                self.state = 569
                self.match(NmrPipePKParser.Sl_A)


            self.state = 573
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==74:
                self.state = 572
                self.match(NmrPipePKParser.Sl_Z)


            self.state = 575
            self.match(NmrPipePKParser.X)
            self.state = 576
            self.match(NmrPipePKParser.Y)
            self.state = 577
            self.match(NmrPipePKParser.Z)
            self.state = 578
            self.match(NmrPipePKParser.A)
            self.state = 579
            self.match(NmrPipePKParser.Intensity)
            self.state = 583
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [81]:
                self.state = 580
                self.match(NmrPipePKParser.Assign)
                pass
            elif token in [82]:
                self.state = 581
                self.match(NmrPipePKParser.Assign1)
                self.state = 582
                self.match(NmrPipePKParser.Assign2)
                pass
            elif token in [89]:
                pass
            else:
                pass
            self.state = 585
            self.match(NmrPipePKParser.RETURN_VA)
            self.state = 587 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 586
                self.pipp_peak_4d()
                self.state = 589 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==6):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Pipp_peak_4dContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(NmrPipePKParser.Integer)
            else:
                return self.getToken(NmrPipePKParser.Integer, i)

        def number(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NmrPipePKParser.NumberContext)
            else:
                return self.getTypedRuleContext(NmrPipePKParser.NumberContext,i)


        def RETURN(self):
            return self.getToken(NmrPipePKParser.RETURN, 0)

        def EOF(self):
            return self.getToken(NmrPipePKParser.EOF, 0)

        def getRuleIndex(self):
            return NmrPipePKParser.RULE_pipp_peak_4d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPipp_peak_4d" ):
                listener.enterPipp_peak_4d(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPipp_peak_4d" ):
                listener.exitPipp_peak_4d(self)




    def pipp_peak_4d(self):

        localctx = NmrPipePKParser.Pipp_peak_4dContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_pipp_peak_4d)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 591
            self.match(NmrPipePKParser.Integer)
            self.state = 593
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,46,self._ctx)
            if la_ == 1:
                self.state = 592
                self.match(NmrPipePKParser.Integer)


            self.state = 596
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,47,self._ctx)
            if la_ == 1:
                self.state = 595
                self.match(NmrPipePKParser.Integer)


            self.state = 598
            self.number()
            self.state = 599
            self.number()
            self.state = 600
            self.number()
            self.state = 601
            self.number()
            self.state = 603 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 602
                self.number()
                self.state = 605 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 2496) != 0)):
                    break

            self.state = 607
            _la = self._input.LA(1)
            if not(_la==-1 or _la==13):
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
            return self.getToken(NmrPipePKParser.Integer, 0)

        def Float(self):
            return self.getToken(NmrPipePKParser.Float, 0)

        def Real(self):
            return self.getToken(NmrPipePKParser.Real, 0)

        def Any_name(self):
            return self.getToken(NmrPipePKParser.Any_name, 0)

        def getRuleIndex(self):
            return NmrPipePKParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)




    def number(self):

        localctx = NmrPipePKParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 609
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 2496) != 0)):
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






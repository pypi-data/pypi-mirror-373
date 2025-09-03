# fmt: off
# flake8: noqa
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable-all

a=' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
import base64 as V1R45
import logging
import os
import platform as MJ5112
import sys
from getpass import getpass as JL21
from os.path import exists as LMK849

from cryptography.fernet import Fernet as L54SD
from cryptography.fernet import InvalidToken as EL714DO

B=logging.getLogger("regscale")
D=a[14]+a[83]+a[69]+a[67]+a[82]+a[69]+a[84]+a[83]
F=a[14]+a[84]+a[88]+a[84],a[14]+a[89]+a[65]+a[77]+a[76],a[14]+a[74]+a[83]+a[79]+a[78],a[14]+a[67]+a[83]+a[86]
def A7801(a_6451):G6487=V1R45.b64encode(a_6451.encode(a[85]+a[84]+a[70]+a[13]+a[24]));return G6487
def N4512_3s2(B24156):G4891=V1R45.b64decode(B24156);G4891=G4891.decode(a[85]+a[84]+a[70]+a[13]+a[24]);return G4891
def G9873():
	if not LMK849(D):
		os.makedirs(D)
		if MJ5112.system().lower()==a[87]+a[73]+a[78]+a[68]+a[79]+a[87]+a[83]:os.system(a[65]+a[84]+a[84]+a[82]+a[73]+a[66]+a[0]+a[11]+a[72]+a[0]+D)
	if LMK849(a[14]+a[15]+D+a[15]+a[70]+a[73]+a[76]+a[69]+a[75]+a[69]+a[89]+a[14]+a[75]+a[69]+a[89]):
		with open(a[14]+a[15]+D+a[15]+a[70]+a[73]+a[76]+a[69]+a[75]+a[69]+a[89]+a[14]+a[75]+a[69]+a[89],a[82]+a[66])as HJ6584:Y8293=HJ6584.read()
	else:
		Y8293=L54SD.generate_key()
		with open(a[14]+a[15]+D+a[15]+a[70]+a[73]+a[76]+a[69]+a[75]+a[69]+a[89]+a[14]+a[75]+a[69]+a[89],a[87]+a[66])as HJ6584:HJ6584.write(Y8293)
	return Y8293
def AB53621(JT3828):
	a9531=JL21(a[48]+a[76]+a[69]+a[65]+a[83]+a[69]+a[0]+a[67]+a[82]+a[69]+a[65]+a[84]+a[69]+a[0]+a[48]+a[65]+a[83]+a[83]+a[75]+a[69]+a[89]+a[26]+a[0]);TH4874=JL21(a[48]+a[76]+a[69]+a[65]+a[83]+a[69]+a[0]+a[67]+a[79]+a[78]+a[70]+a[73]+a[82]+a[77]+a[0]+a[48]+a[65]+a[83]+a[83]+a[75]+a[69]+a[89]+a[26]+a[0])
	if TH4874!=a9531:B.error(a[52]+a[72]+a[69]+a[0]+a[80]+a[65]+a[83]+a[83]+a[75]+a[69]+a[89]+a[83]+a[0]+a[68]+a[79]+a[0]+a[78]+a[79]+a[84]+a[0]+a[77]+a[65]+a[84]+a[67]+a[72]+a[14]+a[0]+a[48]+a[76]+a[69]+a[65]+a[83]+a[69]+a[0]+a[84]+a[82]+a[89]+a[0]+a[65]+a[71]+a[65]+a[73]+a[78]+a[14]);sys.exit(1)
	else:
		a9531=A7801(a9531)
		with open(a[14]+a[15]+a[14]+a[83]+a[69]+a[67]+a[82]+a[69]+a[84]+a[83]+a[15]+a[80]+a[65]+a[83]+a[83]+a[75]+a[69]+a[89]+a[14]+a[75]+a[69]+a[89],a[87]+a[66])as RASD:RASD.write(JT3828.encrypt(a9531))
		B.info(a[48]+a[65]+a[83]+a[83]+a[75]+a[69]+a[89]+a[83]+a[0]+a[77]+a[65]+a[84]+a[67]+a[72]+a[69]+a[68]+a[0]+a[65]+a[78]+a[68]+a[0]+a[73]+a[84]+a[0]+a[87]+a[73]+a[76]+a[76]+a[0]+a[78]+a[79]+a[87]+a[0]+a[66]+a[69]+a[0]+a[89]+a[79]+a[85]+a[82]+a[0]+a[69]+a[78]+a[67]+a[82]+a[89]+a[80]+a[84]+a[73]+a[79]+a[78]+a[15]+a[68]+a[69]+a[67]+a[82]+a[89]+a[80]+a[84]+a[73]+a[79]+a[78]+a[0]+a[80]+a[65]+a[83]+a[83]+a[75]+a[69]+a[89]+a[1])
	return a9531
def FB1107SX(KB92):
	G_HJ21=G9873();MB_11257=L54SD(G_HJ21)
	if LMK849(a[14]+a[15]+D+a[15]+a[80]+a[65]+a[83]+a[83]+a[75]+a[69]+a[89]+a[14]+a[75]+a[69]+a[89]):
		with open(a[14]+a[15]+D+a[15]+a[80]+a[65]+a[83]+a[83]+a[75]+a[69]+a[89]+a[14]+a[75]+a[69]+a[89],a[82]+a[66])as JG2351:GF0357=JG2351.read();AT487=MB_11257.decrypt(GF0357)
	else:
		AT487=AB53621(MB_11257)
		if KB92==a[85]+a[80]+a[68]+a[65]+a[84]+a[69]:sys.exit()
	return AT487
def JHG2152(GHLSDD):NBA45788=JL21(a[37]+a[78]+a[84]+a[69]+a[82]+a[0]+a[80]+a[65]+a[83]+a[83]+a[75]+a[69]+a[89]+a[26]+a[0]);return NBA45788==N4512_3s2(GHLSDD)
def JH0847(CV3S412):
	UY_45558=FB1107SX(a[69]+a[78]+a[67]+a[82]+a[89]+a[80]+a[84])
	if JHG2152(UY_45558):
		OPSD23=L54SD(G9873())
		if LMK849(CV3S412)and CV3S412.endswith(F):
			with open(CV3S412,a[82]+a[66])as JG398:GJ87e2=JG398.read()
			BR51Ls=OPSD23.encrypt(GJ87e2)
			with open(CV3S412,a[87]+a[66])as BJASD:BJASD.write(BR51Ls)
			B.info(a[5]+a[83]+a[0]+a[72]+a[65]+a[83]+a[0]+a[66]+a[69]+a[69]+a[78]+a[0]+a[69]+a[78]+a[67]+a[82]+a[89]+a[80]+a[84]+a[69]+a[68]+a[0]+a[83]+a[85]+a[67]+a[67]+a[69]+a[83]+a[83]+a[70]+a[85]+a[76]+a[76]+a[89]+a[14],CV3S412)
		else:B.error(CV3S412+a[0]+a[68]+a[79]+a[69]+a[83]+a[78]+a[7]+a[84]+a[0]+a[69]+a[88]+a[73]+a[83]+a[84]+a[12]+a[0]+a[79]+a[82]+a[0]+a[73]+a[83]+a[0]+a[65]+a[78]+a[0]+a[85]+a[78]+a[65]+a[67]+a[67]+a[69]+a[80]+a[84]+a[65]+a[66]+a[76]+a[69]+a[0]+a[70]+a[73]+a[76]+a[69]+a[0]+a[69]+a[88]+a[84]+a[69]+a[78]+a[83]+a[73]+a[79]+a[78]+a[1]);sys.exit(1)
	else:B.error(a[48]+a[65]+a[83]+a[83]+a[75]+a[69]+a[89]+a[83]+a[0]+a[68]+a[79]+a[78]+a[7]+a[84]+a[0]+a[77]+a[65]+a[84]+a[67]+a[72]+a[1]);sys.exit(1)
def IOA21H98(KAB46228):
	PH6239=FB1107SX(a[68]+a[69]+a[67]+a[82]+a[89]+a[80]+a[84])
	if JHG2152(PH6239):
		UOPGG23441=L54SD(G9873())
		if LMK849(KAB46228)and KAB46228.endswith(F):
			with open(KAB46228,a[82]+a[66])as URT9934:JYT32446=URT9934.read()
			try:UIAS9877=UOPGG23441.decrypt(JYT32446)
			except EL714DO:B.error(KAB46228+a[0]+a[73]+a[83]+a[0]+a[78]+a[79]+a[84]+a[0]+a[69]+a[78]+a[67]+a[82]+a[89]+a[80]+a[84]+a[69]+a[68]+a[14]);sys.exit()
			with open(KAB46228,a[87]+a[66])as BAB98455:BAB98455.write(UIAS9877)
			B.info(KAB46228+a[0]+a[72]+a[65]+a[83]+a[0]+a[66]+a[69]+a[69]+a[78]+a[0]+a[68]+a[69]+a[67]+a[82]+a[89]+a[80]+a[84]+a[69]+a[68]+a[0]+a[83]+a[85]+a[67]+a[67]+a[69]+a[83]+a[83]+a[70]+a[85]+a[76]+a[76]+a[89]+a[14])
		else:B.error(KAB46228+a[0]+a[68]+a[79]+a[69]+a[83]+a[78]+a[7]+a[84]+a[0]+a[69]+a[88]+a[73]+a[83]+a[84]+a[12]+a[0]+a[79]+a[82]+a[0]+a[73]+a[83]+a[0]+a[65]+a[78]+a[0]+a[85]+a[78]+a[65]+a[67]+a[67]+a[69]+a[80]+a[84]+a[65]+a[66]+a[76]+a[69]+a[0]+a[70]+a[73]+a[76]+a[69]+a[0]+a[69]+a[88]+a[84]+a[69]+a[78]+a[83]+a[73]+a[79]+a[78]+a[1]);sys.exit(1)
	else:B.error(a[48]+a[65]+a[83]+a[83]+a[75]+a[69]+a[89]+a[83]+a[0]+a[68]+a[79]+a[78]+a[7]+a[84]+a[0]+a[77]+a[65]+a[84]+a[67]+a[72]+a[1]);sys.exit(1)
def YO9322():
	YR6248=FB1107SX(a[85]+a[80]+a[68]+a[65]+a[84]+a[69])
	if JHG2152(YR6248):N_j214=G9873();BNS21=L54SD(N_j214);AB53621(BNS21)
	else:B.error(a[48]+a[65]+a[83]+a[83]+a[75]+a[69]+a[89]+a[83]+a[0]+a[68]+a[79]+a[78]+a[7]+a[84]+a[0]+a[77]+a[65]+a[84]+a[67]+a[72]+a[1])

# fmt: on

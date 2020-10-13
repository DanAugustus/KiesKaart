#!/usr/bin/env python
# coding: utf-8

# # Prototype Voorspellend model PC6 Data

# ### Samenvatting:
# X, oftewel de onafhankelijke variabelen. Dit worden de demografische gegevens van het CBS.
# Er is minimaal één set nodig maar het mogen er meer zijn. Hoe veel data er minimaal nodig is en of één model past bij heel Nederland past zijn open vragen. Het kan altijd nauwkeuriger, is het devies. Een fractie van X wordt gebruikt om de nauwkeurigheid van het model te scoren. Als het model bepaalde groepen beter begrijpt dan anderen is de score erg variabel. 
# De datasets mogen GEEN foutieve waarden bevatten. Gebruik Pandas om te controleren of er outliers of NaN's aanwezig zijn. Missende waarden kunnen het beste worden opgevuld met een mediaan of gemiddelde. Gebruik daarvoor een waarde van een overkoepelende zone of bepaal deze zelf. Het is mogelijk om deze waarde te voorspellen op basis van kolommen die wel helemaal goed ingevuld zijn.
# 
# y, oftewel de afhankelijke variabele. Dat is hier de stemuitslag per ???? of PC6, per partij plus de opkomst. Uiteraard moet bij elk verkiezingsjaar een dataset met het juiste jaartal komen. Het model kan alleen leren van data waarvan vaststaat dat elke Xn hoort bij elke Yn.
# 
# Het model, een lineare regressie in de laatste versie. Met dit model kunnen we nagaan welke kolommen veel invloed hebben op de beslissing die het model neemt. Ook is het mogelijk om per voorspellen een foutmarge te berekenen.
# 
# Ten slotte gebruiken we een X waarvan we nog geen y hebben om de y te voorspellen.
# 
# Opmerkingen:
# Omdat de data van het CBS niet precies op de verkiezingsdag is afgenomen zal de berekening van de opkomst niet tot op de komma nauwkeurig zijn.
# Het maakt voor het model niet uit of getallen komen van een gemiddelde van een kleine buurt of een grote gemeenten.
# Hoe nauwkeuriger en fijnmaziger de data, hoe beter het model verbanden kan ontdekken. Naarmate de zones kleiner worden, moet de data over stemgedrag ook even nauwkeurig uit die zone gehaald worden. Houd er rekening mee dat modellen zelden goed omgaan met uitschieters.
# De gerichte GL campagne beperkt zich tot 20 gemeenten in de lijst in deze map.
# 
# To Do:
# Maak een model voor ELK Schaalniveau. Als je dan gegevens mist van een buurt of straat gebruik je de data of voorspelling van een wijk. Als de data van een wijk mist gebruik je de data van een gemeente, maar dat zal niet precies genoeg zijn voor het beoogde doel.

# ### Databases en links:
# Hoe deelt het CBS data in op basis van postcode?
# https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/gegevens-per-postcode
# Informatie over data uit 2019 in Odata4 (Wijken en buurten)
# https://www.cbs.nl/nl-nl/maatwerk/2019/42/buurt-wijk-en-gemeente-2019-voor-postcode-huisnummer\
# Het campagneteam heeft toegang tot data op PC6 niveau, voor meer info vraag het aan Jasper.
# In de oude github staan de uitslagen uit 2017

# In[1]:


# import database
url2019 = "https://odata4.cbs.nl/CBS/84583NED" # Kerncijfers wijken en buurten 2019
url2017 = "https://odata4.cbs.nl/CBS/83765NED" # Kerncijfers wijken en buurten 2017
# Toelichting: https://www.cbs.nl/nl-nl/maatwerk/2017/31/kerncijfers-wijken-en-buurten-2017


# ### Checklist:
# Welke X gaan we gebruiken? De laatste Europarlementsverkiezingen vonden plaats in mei 2019. De laatste tweedekamerverkiezingen vonden plaats in maart 2017. Ook zijn er nog de Provinciale Statenverkiezingen.
# We hebben toegang tot demografische data op PC6-niveau afkomstig van het CBS. Dat moet wel steeds uit het jaartal zijn dat overeenkomt met de y.
# Welke y gaan we gebruiken? We hebben toegang tot stemuitslagen op PC6-niveau.
# Is er nog foutieve data aanwezig?
# Weten we zeker dat de stemuitslagen worden ingedeeld op basis van dezelfde zones? Zijn de Vonoroy-diagrammen (met correcties) goed genoeg?
# 
# De meeste features in de CBS data zijn absoluut, maar niet allemaal! Alle features moeten genormaliseerd zijn,
# anders kan het model anders kijken naar een groot aantal inwoners zonder te relativeren.

# ## Imports, laden en controleren data

# In[15]:


import numpy as np
import pandas as pd
import re
import time
import CBSparserOData4
from PC4e6_database import *
#importeer van scikit learn alleen de delenfuncties/klassen die nodig zijn.
from sklearn import linear_model, model_selection
from sklearn.multioutput import MultiOutputRegressor


# ### Info over features
# Zie PC4e6_database

# ### Kies features en laad de data

# In[3]:


stemTK, register = laad_uitslagenPC6("adressen_gl_prioriteit/adressen_TK2017.csv")


# In[4]:


demo = laad_CBSdataPC6('CBS_PC6_selectie.csv')


# ## Data filteren en combineren

# In[5]:


dataPC6 = join_PC6(stemTK,demo)
dataPC6.head()


# In[6]:


feature_select = ['MAN','VROUW','UITKMINAOW','WON_MRGEZ']
dataPC6 = normaliseer_PC6(dataPC6,feature_select)
dataPC6.describe()


# ### Lineare regressie

# In[12]:


ycols = ['stemperc']
xcols = feature_select
for col in dataPC6.columns:
    if re.search('percentage$',col):
        ycols.append(col)
    elif re.search('^INW',col):
        xcols.append(col)
print(ycols, '\n', xcols)
# Schud de data en maak het model! Noteer ook hoe je foutmarges weergeeft. Wat is de beste verdeling van train/test?

Xtrain, Xtest, ytrain, ytest = model_selection.train_test_split(dataPC6[xcols], dataPC6[ycols], test_size=0.12, random_state=14)


# In[17]:


prototype = MultiOutputRegressor(linear_model.LinearRegression())
prototype.fit(Xtrain,ytrain)
accuracy = prototype.score(Xtest,ytest)
print(accuracy)


# In[ ]:





# In[ ]:


lijst_gemeenten = open("lijst_gemeenten.txt")
doelen_gemeenten = []
for regel in lijst_gemeenten:
    doelen_gemeenten.append(regel.strip("\n "))
print(doelen_gemeenten)


# In[ ]:





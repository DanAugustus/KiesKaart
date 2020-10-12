#!/usr/bin/env python
# coding: utf-8

# In[57]:


import numpy as np
import pandas as pd
import CBSparserOData4
import re


# In[42]:


def laad_uitslagenPC6(path):
    uitslagen = pd.read_csv(path,sep="|")
    uitslagen['PC6'] = uitslagen['postcode']
    uitslagen['PC4'] = uitslagen['postcode'].str[0:4]
    uitslagen.drop(['postcode','huisnummertoevoeging','letter'], inplace = True, axis=1)
    register = uitslagen[['stad','straatnaam','stembureau','postcode_stembureau','PC6','PC4']]
    
    # Voor het gemak brengen we de data terug naar PC6 niveau, want de CBS data heeft toch niet meer nauwkeurigheid.
    # Later kan worden gecorrigeerd voor verschillen tussen PC6 en de zone rondom een stembureau.
    # Voordat de data gegroepeerd wordt moeten tabellen voor het koppelen van tekstkolommen bewaard worden.
    # Want een groupby wist alle tekstkolommen.
    # verkiezing = demo['verkiezing'].values[0] # Deze waarde is nodig mochten meerdere verkiezingen tegelijk geladen worden.
    
    uitslagen=uitslagen.groupby('PC6').median()
    #uitslagen=uitslagen.groupby(['postcode_stembureau','straatnaam']).median()
    #uitslagen=uitslagen.groupby(['PC6','straatnaam']).median()
    
    return uitslagen, register


# In[43]:


def laad_CBSdataPC6(path):
    demo = pd.read_csv(path, sep=",", index_col=0)
    demo = demo.groupby('PC6').median()
    
    return demo
    


# In[54]:


def join_PC6(uitslagen,demo):
    # Omdat de data per PC6 is gemeten is het logisch om eerst met de PC6 de databases te koppelen.
    
    return uitslagen.join(demo)


# In[45]:


def normaliseer_PC6(df, feature_selectie=None):
    
    pass


# In[40]:


TK2017, register = laad_uitslagenPC6("adressen_gl_prioriteit/adressen_TK2017.csv")
TK2017.head()


# In[35]:


demo = laad_CBSdataPC6('CBS_PC6_selectie.csv')
demo.head()


# In[56]:


dataPC6 = join_PC6(TK2017,demo)
dataPC6.head()


# In[ ]:


features = pd.read_csv("features_verzoek.csv",sep=";", index_col=0)
Data2017 = CBSparserOData4.parserOData4("83765NED","GM",features['Identifier'])
Data2017.head()


# In[65]:


index = pd.read_csv('2019-cbs-pc6huisnr20190801_buurt/pc6hnr20190801_gwb.csv', sep=';')
#deze data vind je hier: https://www.cbs.nl/nl-nl/maatwerk/2019/42/buurt-wijk-en-gemeente-2019-voor-postcode-huisnummer
index.head()


# In[68]:


def prefixer(s, prefix, lengte):
    s = str(s)
    while len(s) < lengte:
        s = '0' + s
    s = prefix + s
    return s

def get_index():
    index = index.groupby('PC6').median()
    index['Buurt2019'] = index['Buurt2019'].astype('int').apply(lambda s: prefixer(s,'BU', 8))
    index['Wijk2019'] = index['Wijk2019'].astype('int').apply(lambda s: prefixer(s, 'WK', 6))
    index['Gemeente2019'] = index['Gemeente2019'].astype('int').apply(lambda s: prefixer(s, 'GM', 4))
    return index 


# In[69]:


# Verwijder kolommen die niet meer nodig zijn.
# Vul NaN aan met 0 waar dat een goede aanname is. Wis de rest van de rijen met missende waarden.


# Slimmer indelen:
# Maak een functie die in de oorspronkelijke tabel informatie uit tekstkolommen ophaalt na het invoeren van een PC6 (van stembureau). Laat deze een kolom aanmaken die aangeeft of er straten (of adressen) zijn binnen dat kader die buiten die PC6 vallen. Bijvoorbeeld met een cijfer dat het aantal combinaties aangeeft.

#!/usr/bin/env python
# coding: utf-8

# In[49]:


import numpy as np
import pandas as pd
import CBSparserOData4
import re


# In[50]:


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


# In[51]:


def laad_CBSdataPC6(path):
    demo = pd.read_csv(path, sep=",", index_col=0)
    demo = demo.groupby('PC6').median()
    
    return demo
    


# Normaliseer met aantal inwoners: MAN, VROUW, INW_xxx, UITKMINAOW,
# Normaliseer met aantal huishoudens: WON_MRGEZ, 
# Laat weg: INWONER, AANTAL_HH, Perc_NW_migracht. Deze laatse kolom bevat veel missende waarden.

# In[53]:


def join_PC6(uitslagen,demo):
    # Omdat de data per PC6 is gemeten is het logisch om eerst met de PC6 de databases te koppelen.
    return uitslagen.join(demo)



def normaliseer_PC6(df, features=None, dropNA=True, drempel = None):
    # verwijder ook NaN's ?
    
    # Lijsten van alle mogelijke features, opgedeeld in hoe ze verwerkt moeten worden
    INW = [] # Wordt gevuld met inwoners in leeftijdsgroep en features in overig_persoon
    perc = ['stemperc'] # Opkomst en percentages stemmen worden altijd toegevoegd.
    huish = ['WON_MRGEZ']
    overig_persoon = ['MAN','VROUW','UITKMINAOW']
    overig_normaal = ['GEM_HH_GR'] # Features die al genormaliseerd zijn.
    zwarte_lijst = ['Perc_NW_migracht'] # Teveel missende waarden in deze kolom
    
    # verwijder kolommen 
    def overbodig(lijst, checklist):
        for c in lijst:
            if c not in checklist:
                lijst.remove(c)
        return lijst
    
    if features:
        huish = overbodig(huish, features)
        overig_persoon = overbodig(overig_persoon, features)
        overig_normaal = overbodig(overig_normaal, features)
        
    if drempel:
        stuk = df[df['INWONER'] >= drempel]
        df = df.loc[ stuk.index ]
        
    for col in df.columns:
        if col in overig_persoon or re.search('^INW_',col):
            df[col] = df[col] / df['INWONER']
            INW.append(col)
        elif col in huish:
            df[col] = df[col] / df['AANTAL_HH']
        elif col in zwarte_lijst:
            df.drop(col, axis=1,inplace=True)
        elif re.search('percentage$',col):
            perc.append(col)
            
    if features:
        cols = INW+overig_normaal+huish+perc
        print(cols)
        df = df[cols]
        
    if dropNA:
        df = df.dropna(axis=0)
    
    return df



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

def get_prioriteit(df):
    if 'prioriteit' in df.columns:
        if 'PC6' in df.columns:
            return(df[['PC6','prioriteit']])
        else:
            return df.prioriteit


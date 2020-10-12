#!/usr/bin/env python
# coding: utf-8

# In[27]:


import numpy as np
import pandas as pd
import re


# In[42]:


def laad_uitslagenPC6(path):
    uitslagen = pd.read_csv(path,sep="|")
    uitslagen['PC6'] = uitslagen['postcode']
    uitslagen['PC4'] = uitslagen['postcode'].str[0:4]
    # Dit moet een numerieke kolom worden.
    
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

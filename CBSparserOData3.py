#!/usr/bin/env python
# coding: utf-8

# # Python functies voor Odata3
# Functies voor ophalen, inspecteren en samenvoegen van data van CBS
# Verschillen met indeling data CBS op OData4:
# 
# file:///C:/Users/DKuipers/AppData/Local/Temp/odata4-overstappen-odata3.pdf
# 
# handleiding voor data CBS op Odata3:
# file:///C:/Users/DKuipers/AppData/Local/Temp/cbs-open-data-services.pdf
# 
# Het voornaamste verschil is dat Odata3 al op de klassieke (tidy) manier observaties opslaat. Verder verschillende de namen van de tabellen in één set, en de namen van de metingen. Er zijn verschillen in welke data wordt gemeten, Odata 4 heeft bijvoorbeeld niet de kolom "meest voorkomende postcode".

# In[30]:


import re
import numpy as np
import pandas as pd
import requests
import time

def get_odata(target_url):
    
    """"
    De functie gebruikt een API genaamd OData om data van het CBS op te halen.
    De data wordt in stukken opgehaald en in een pandas dataframe gezet.
    De URL moet er zo uitzien: "https://opendata.cbs.nl/ODataApi/odata/84583NED"
    De code van de tabel die je zoekt vindt je via Statline.
    Ga naar de data in Statline op de website van het CBS en kijk naar de URL om de code te vinden.
    """
    
    data = pd.DataFrame()
    while target_url:
        r = requests.get(target_url).json()
        data = data.append(pd.DataFrame(r['value']))
        
        if '@odata.nextLink' in r:
            target_url = r['@odata.nextLink']
        else:
            target_url = None
            
    return data


# Functie werkt maar automatisch queries samenvoegen is handiger.

def get_top_observations(table_url, url_filter = "", skip=None):
    
    """Haal de tabel met metingen op. In tegenstelling tot Odata4 hoeft de tabel niet geformatteerd te worden.
    Odata3 beperkt echter hoeveel metingen je op kan halen. Kies uit de bovenste of onderste 9999 rijen.
    Als dat niet genoeg is moeten filters toegepast worden.
    Filteren om minder of specifiekere data op te vragen is mogelijk as volgt:
    url_filter = $filter=WijkenEnBuurten eq 'GM0363' and Measure eq 'T001036'
    Door de filteren op deze kolommen kun je een plaats (land, gemeente, wijk of buurt) kiezen.
    Of gebruik: $filter=Measure in ('M001607', 'M001636')
    Je hoeft niet beide kolommen te gebruiken voor het filter."""
    
    
    if skip:
        side = "?$top=9999&$skip={} &amp;".format(skip)
    else:
        side = "?$top=9999 &amp;"
    
    if url_filter == "":
        target_url = table_url + "/TypedDataSet" + side 
    elif "$filter=" in url_filter:
        target_url = table_url + "/TypedDataSet" + side + url_filter
    else:
        print("WAARSCHUWING! FILTER NIET GOED GEFORMATTEERD. VERGELIJK MET VOORBEELD OF GA NAAR ")
        print("\n https://www.cbs.nl/nl-nl/onze-diensten/open-data/open-data-v4/filters-odata-v4")
        #return None
        return(table_url + url_filter)
    
    #print(target_url)
    data = get_odata(target_url)
    #print(data.head)
    
    #if len(data.index) >= 9999:
    #    print("Waarschuwing: Verzoek om data ingekort door limiet van 9999 rijen.")
    #    print("Query '{}' is te groot voor één request".format(target_url))
    
    return(data)


# In[6]:


def auto_query(url, fil):
    
    repeat = True
    nrow=0
    frames=[]
    
    while repeat:
        result = get_top_observations(url, url_filter=fil,skip=nrow)
        if len(result) != 9999:
            repeat = False
        nrow += 9999
        frames.append(result)
    
    return pd.concat(frames,axis=0)


def splits_cijfer(Identifier):
    if re.search("_\d+$", Identifier):
        cijfer = re.search("\d+$", Identifier).group()
    else:
        cijfer = "0"
    return cijfer
        

def get_observations(database, filtersoort=0, plaatsen = None, custom_filter="", features = None, beta=True):
    
    """
    Haal de tabel met metingen op. In tegenstelling tot Odata4 hoeft de tabel niet geformatteerd te worden.
    De code van de dataset is de combinatie van cijfers en letters achteraan de url:
    https://opendata.cbs.nl/ODataApi/odata/84583NED
    filtersoort geeft aan op welke kolom de plaatsen gefilterd worden.
    0 = alleen ingevoerde filter
    1 = naam gemeente
    2 = Gemeente/Wijk/Buurt
    3 = Code
    Je kan ook zelf een filter genereren dat achter de andere filters geplakt wordt. Zie 
    https://www.odata.org/documentation/odata-version-3-0/odata-version-3-0-core-protocol/
    voor meer uitleg. of ga naar 
    https://help.nintex.com/en-US/insight/OData/HE_CON_ODATAQueryCheatSheet.htm
    voor een beknopte cheatsheet
    """
    table_url = "https://opendata.cbs.nl/ODataApi/odata/{}".format(database) 
    # /TypedDataSet wordt er nog aangeplakt in get_top_observations()
    #print(table_url)
    
    if custom_filter != "":
            custom_filter = " and "+custom_filter
    
    if filtersoort == 1:
        filterkolom = "Gemeentenaam_1"
    elif filtersoort == 2:
        filterkolom = "SoortRegio_2"
    elif filtersoort == 3:
        filterkolom = "Codering_3"
    else:
        df = get_odata(table_url+"$filter="+custom_filter)
        
        return df
    
    frames = []
    if type(plaatsen) == list or type(plaatsen) == pd.Series:
        
        for plaats in plaatsen:
            url_filter = "$filter={} eq '".format(filterkolom)+plaats+"'"+custom_filter
            frames.append( auto_query(table_url,url_filter) )
            time.sleep(0.5)
            
        print("Download geslaagd!")
        observations = pd.concat(frames,axis=0)       
    
        if beta:
            observations[filterkolom] = observations[filterkolom].str.strip()
            frames = []
            for plaats in plaatsen:
                print(observations[filterkolom].head())
                frames.append( observations[observations[filterkolom] == plaats] )
            observations = pd.concat(frames,axis=0)
                
    else:
        observations = get_top_observations(table_url+custom_filter)
        # Resultaten die niet meer in 9999 rijen passen worden weggelaten! Maar dit voorkomt foutmeldingen.
        # Gebruik daarom een filter
    cols = pd.Series(observations.columns)
    Volgorde = cols.apply(lambda s: splits_cijfer(s))
    sorteer = pd.DataFrame({'Identifier':cols, 'Volgorde':Volgorde})
    sorteer['Volgorde'] = sorteer['Volgorde'].astype('int')
    sorteer = sorteer.sort_values('Volgorde').reset_index(drop=True)
    
    if features:
        return observations[features]
    else:
        return(observations[ list(sorteer['Identifier']) ])
    
#https://opendata.cbs.nl/ODataApi/odata/84583NED/TypedDataSet?$top=9999%20&amp;$filter=contains(Codering_3,%27WK%27)


# ## Filteren van query
# Het filteren van de data maakt het downloaden sneller.
# Het filteren van 'Observations' data kan door code van dit format achter de url te plakken:
# 
# **?$filter=Codering_3 eq 'GM0363' and Measure eq 'T001036'**
# 
# **$filter=Measure in ('M001607', 'M001636')**
# 
# De code uit de kolom WijkenEnBuurten kun je vinden met 
# 
# **get_odata(table_url + "/WijkenEnBuurtenCodes")**
# 
# De 'Title' kolom van deze tabel bevat de namen van wijken, zodat je kan zoeken met str.find, <>.str.contains of Regex.
# Zoals wel vaken met tektskolommen moet je dan vertrouwen op de volledigheid en consistentie.
# Achteraf controleren of je wel de juiste weijken hebt s dus wel aangeraden.
# De kolom WijkenenBuurten bevat zowel landen, gemeenten, wijken als buurten.
# Aan het voorvoegsel van twee letters kun je zien met welke soort regio je te maken hebt.
# 
# Zie https://www.odata.org/documentation/odata-version-3-0/odata-version-3-0-core-protocol/ voor meer uitleg.
# of ga naar https://help.nintex.com/en-US/insight/OData/HE_CON_ODATAQueryCheatSheet.htm voor een beknopte cheatsheet

# Een dataset uit ODATA3 (uit 2019) kan gebruikt worden om postcodes aan buurten te koppelen als andere geografische data niet gevonden kan worden.
# Houd rekening met de limiet van 9999 rijen per verzoek.
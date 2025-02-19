import pandas as pd
import numpy as np 
from sklearn.model_selection import train_test_split  
import warnings
warnings.filterwarnings("ignore")

def clean_columns(df):
    df.columns = df.columns.str.replace('1st Flr SF','first_flr_sf')
    df.columns = df.columns.str.replace('2nd Flr SF','second_flr_sf')
    df.columns = df.columns.str.replace(' ','_')
    df.columns = df.columns.str.replace('/','_')
    df.columns = df.columns.str.lower()
    return df 

def features_selection(df):
    to_keep = ['overall_qual', 'neighborhood_int', 'exterior_1st', 'year_remod_add', 'quality_house', 
               'main_score_house', 'options_in_house', 'main_living_area', 'good_garage', 'sale_condition_int']
    return df[to_keep]


def neighbors_and_conditions_dict(X_train):
    neighbors_dict = {}
    for idx, value in enumerate(list(X_train.groupby('neighborhood').mean()['saleprice'].sort_values(ascending=True).index)):
        neighbors_dict[value] = idx 
        
    conditions_dict = {}
    for idx, value in enumerate(list(X_train.groupby('condition_1').mean()['saleprice'].sort_values(ascending=True).index)):
        conditions_dict[value] = idx 
        
    sale_condition_dict = {}
    for idx, value in enumerate(list(X_train.groupby('sale_condition').mean()['saleprice'].sort_values(ascending=True).index)):
        sale_condition_dict[value] = idx 
    
    return neighbors_dict, conditions_dict, sale_condition_dict


def data_preprocessing(df, neighbors_dict, conditions_dict, sale_condition_dict ):

    dict_po_to_ex = { 'Po': 0, 'Fa': 1, 'TA': 2, "Gd": 3, "Ex": 4 }
    dict_na_to_ex = { np.nan : 0, 'Na': 0, 'Po': 1, 'Fa': 2, 'TA': 3, 'Gd': 4, 'Ex': 5 }
    dict_garage_finish = { 'NA': 0, 'Unf': 1, 'RFn': 2, 'Fin': 3 }
    
    df['neighborhood_int'] = 0
    df.neighborhood_int = df.neighborhood.replace(neighbors_dict)     
    
    df['condition_int'] = 0
    df['condition_int'] = df['condition_1'].replace(conditions_dict)
    df['condition_int'] += df['condition_2'].replace(conditions_dict)

    df['sale_condition_int'] = 0
    df['sale_condition_int'] = df['sale_condition'].replace(sale_condition_dict)

    df['garage_qual_int'] = 0 
    df['garage_qual_int'] = df['garage_qual'].replace(dict_na_to_ex) 
    df['garage_qual_int'] = df['garage_qual_int'].fillna(3) # Represente la valeur la plus présente dans le jeu de données
    df['garage_qual_int'] = df['garage_qual_int'].astype(int)
    
    df['fireplace_qual'] = 0 
    df['fireplace_qual'] = df['fireplace_qu'].replace(dict_na_to_ex) 
    
    df['bsmt_qual_int'] = 0 
    df['bsmt_qual_int'] = df['bsmt_qual'].replace(dict_na_to_ex) 
    df['bsmt_qual_int'] = df['bsmt_qual_int'].fillna(0)
    df['bsmt_qual_int'] = df['bsmt_qual_int'].astype(int)


    df['heating_qc'] = df['heating_qc'].replace(dict_po_to_ex)
    df['heating_qc'] = df['heating_qc'].astype(int)

    df['exter_qual_int'] = 0 
    df['exter_qual_int'] = df['exter_qual'].replace(dict_po_to_ex) 
    df['exter_qual_int'] = df['exter_qual_int'].astype(int)

    df['kitchen_qual_int'] = 0 
    df['kitchen_qual_int'] = df['kitchen_qual'].replace(dict_po_to_ex) 
    df['kitchen_qual_int'] = df['kitchen_qual_int'].astype(int)
    
    df['garage_finish_int'] = 0 
    df['garage_finish_int'] = df['garage_finish'].replace(dict_garage_finish) 
    df['garage_finish_int'] = df['garage_finish_int'].fillna(df['garage_finish_int'].mean())
    df['garage_finish_int'] = df['garage_finish_int'].astype(int)
    
    df['central_air'] = np.where(df['central_air'] == "Y", 1, 0)
    df['central_air'] = df['central_air'].astype(int)

    df.utilities[df.utilities == "NoSewr"] = 0 
    df.utilities[df.utilities == "NoSeWa"] = 1
    df.utilities[df.utilities == "AllPub"] = 2 
    df.utilities = df.utilities.astype(int)
    
    df['bsmt_exposure'][df['bsmt_exposure'] == np.nan ] = 0
    df['bsmt_exposure'][df['bsmt_exposure'] == "No"] = 1
    df['bsmt_exposure'][df['bsmt_exposure'] == "Mn"] = 2 
    df['bsmt_exposure'][df['bsmt_exposure'] == "Av"] = 3 
    df['bsmt_exposure'][df['bsmt_exposure'] == "Gd"] = 4
    
    df['paved_drive'][df['paved_drive'] == "N"] = 0 
    df['paved_drive'][df['paved_drive'] == "P"] = 1
    df['paved_drive'][df['paved_drive'] == "Y"] = 2 
    
    df.street[df.street == 'Pave'] = 10
    df.street[df.street == 'Grvl'] = 0
    df.street = df.street.astype(int)

    return df

def data_engineering(df):
    
    # Caractéristique du garage. Plus le score est élevé, plus le garage est grand et/ou de qualité
    df['good_garage'] = 0 
    df['good_garage'] = df['garage_cars'] + (df['garage_finish_int'] *2) + (df['garage_qual_int'] *2 )
    df['good_garage'] = df['good_garage'].fillna(0)
    df['good_garage'][df['garage_area'] >= 575] += 2
    df['good_garage'] = df['good_garage'].astype(int)
    
    # Espace LowQualFinSF == Low quality finished square feet (all floors) est inclus dans le total => gr_liv_area (first_flr_sf + second_flr_sf + LowQualFinSF)
    # Je prend en compte l'espace supplémentaire mais je donne du poid à l'espace habitable sans la partie de faible qualité en ajoutant (first_flr_sf + second_flr_sf)
    df['main_living_area'] = df['gr_liv_area'] + df['total_bsmt_sf'].fillna(0) + df['first_flr_sf'] + df['second_flr_sf'] # + df['garage_area']
    
    # Je suis parti de l'idée d'ajouter tout les scores de qualité. J'ai aussi multiplié le nbr de cheminée par la qualité de la maison.
    # De sorte à augmenter le score des maisons ayant une cheminée ET une belle qualité général, et à pénalisé les maisons de mauvaises qualités avec cheminée.  
    df['quality_house'] = df['bsmt_qual_int'] + df['exter_qual_int'] + df['kitchen_qual_int'] + df['garage_qual_int'] +  ((df['fireplaces'] *  df['overall_qual']) /2) #*  df['overall_qual'] # + df['utilities'] # + df['overall_qual']
    
    # J'ajoute le nombre de salle de bain aux étages + rdc et j'applique un coéfficient sur les salle de bain non complete pour les pénalisés 
    df['total_bath'] = 0 
    df['total_bath'] = df['full_bath'] + (df['half_bath'] /2) + df['bsmt_full_bath'].fillna(0) + (df['bsmt_half_bath'].fillna(0) /1.5 )# / df['overall_qual'] # + df['TotRms AbvGrd'] 

    # Colonne qui encode pour la qualité du mur exterieur ou du jardin, de la rue et la presence de la climatisation, 
    # la route pavé semble couté plus chère qu'une route en gravié pour la colonnne street et la colonne paved_drive
    # bsmt_exposure => Qualité murs trottoire, jaridns.  
    df['qual_walkout_clim'] = df['bsmt_exposure'].fillna(0) + df['paved_drive'] + df['street'] + df['central_air'] 
    df.qual_walkout_clim = df.qual_walkout_clim.astype(float)    
    
    # Score general de la maison, je multiplie certains critère de qualité. Le 0 est possible uniquement dans utilities. 
    # Ce qui permet de mettre un lourd poid negatif quand il n'y a pas de fausse septique pour traiter les eaux usées.
    # A l'inverse plus les qualités seront élevé et plus le score le sera aussi.  
    df['main_score_house'] = 0 
    df['main_score_house'] = df['overall_qual'] * df['neighborhood_int'] * df['quality_house'] * df['total_bath'] * df['utilities'] 
    
    df['options_in_house'] = 0 
    # Là ou belle maison, beau quartier, et espace vivable important
    df['options_in_house'][(df['overall_qual']>=6) & (df['neighborhood_int'] >= 17) & (df['main_living_area'] >= 4000)] +=1
    # Open porch area in square feet (genre de balcon au rdc (typique usa))
    df['options_in_house'][(df['open_porch_sf'] > 0)] += 1
    # Wood deck area in square feet (surface terrasse en bois)
    df['options_in_house'][(df['wood_deck_sf'] > 0)] += 1
    # Là ou on a une piscine 
    df['options_in_house'][(df['pool_area'] > 0 )] += 1
    # Là ou on a de l'espace à l'étage 
    df['options_in_house'][df['gr_liv_area'] >= 1800] += 1
    # Qualité du chauffage 
    df['options_in_house'] += df['heating_qc']
    # Ajoute du poid si route pavé et clim. 
    df['options_in_house'] += df['qual_walkout_clim']
    # Ajoute du poid si axe routier interessant, grosse artère etc.
    df['options_in_house'] += df['condition_int']
    df['options_in_house'] = df.options_in_house.astype(int)
    
    return df 

# Preprocessing and features ingeneering 

df = pd.read_csv("model/data/AmesHousing.csv")
df = clean_columns(df)
X_train, X_test, y_train, y_test = train_test_split(df, df.saleprice, test_size=0.2, random_state=42)
neighbors_dict, conditions_dict, sale_condition_dict = neighbors_and_conditions_dict(X_train)
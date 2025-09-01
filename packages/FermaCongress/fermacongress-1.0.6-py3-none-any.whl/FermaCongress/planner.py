import requests
import pandas as pd
from io import StringIO
from FermaCongress.extractferma import *

def baseplanner(client, CONGRESS_ID: str, PLANNER_ID: str):
    sessions_data = get_all_sessions(client, CONGRESS_ID)
    keywords_data = get_skg(client, CONGRESS_ID)
    df = sessions_data[['internal_id', 'abstract_id', 'session_title', 'session_type', 'abstract_title', 'abstract_link', 'authors', 'institution', 'location', 'start_date', 'end_date', 'classification', 'full_abstract_text']]
    df = df.merge(keywords_data[['internal_id', 'firms', 'diseases', 'primary_drugs', 'secondary_drugs', 'comparator_drugs', 'nct', 'acronym', 'drug_classes', 'indications']], on='internal_id', how='left')
    df['Date'] = df['start_date']
    df['firms'] = df['firms'].str.replace('<0>', '', regex=False).str.strip()
    
    for col in ['firms', 'diseases', 'primary_drugs', 'secondary_drugs', 'comparator_drugs', 'nct', 'acronym', 'drug_classes', 'indications']:
        df[col] = df[col].fillna('').astype(str).str.replace(';;', ', ', regex=False).replace(['nan', 'None'], '')

    if PLANNER_ID != "NA":
        planner_resp = requests.get(f"https://admin-portal.ferma.ai/planners/{PLANNER_ID}/download?download_type=all", headers=client)
        planner_data = pd.read_csv(StringIO(planner_resp.text))
        df = df.merge(planner_data[['internal_id', 'priority_name']], on='internal_id', how='left')
    else:
        df['priority_name'] = None
    
    df = df.rename(columns={"internal_id": "Int ID", "abstract_id": "Abstract ID", "abstract_link": "Abstract Link", "priority_name": "Priority", 
                "session_type": "Session Type", "session_title": "Session Title", "abstract_title": "Abstract Title", "full_abstract_text": "Full Abstract Text",
                "authors": "Authors", "institution": "Institution", "location": "Location", "start_date": "Start Time", "end_date": "End Time", "firms": "Agencies",
                "drug_classes": "Drug Class", "indications": "Indication", "primary_drugs": "Primary Drugs", "secondary_drugs": "Secondary Drugs",
                "comparator_drugs": "Comparator Drugs", "nct": "NCT", "acronym": "Acronym"})
    
    columns = ['Int ID','Abstract ID', 'Abstract Link', 'Session Title', 'Session Type', 'Abstract Title', 'Full Abstract Text', 'Authors', 'Institution',
            'Location', 'Date', 'Start Time', 'End Time', 'Agencies', 'Drug Class', 'Indication', 'Primary Drugs', 'Secondary Drugs', 'Comparator Drugs',
            'NCT', 'Acronym', 'classification']
    
    if PLANNER_ID != "NA":
        columns.insert(3, 'Priority')

    return df[columns]
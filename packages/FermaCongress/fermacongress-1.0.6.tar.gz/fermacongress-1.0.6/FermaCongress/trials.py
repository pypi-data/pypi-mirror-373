import re
import requests
import pandas as pd
from tqdm import tqdm


def extracttrials(df: pd.DataFrame, column: str, delimiter: str = ";;") -> pd.DataFrame:
    headers = {
        "accept": "application/json",
        "user-agent": "ClinicalPhaseExtractor/1.0"
    }

    def extract_nct(trial_id: str) -> tuple:
        url = f"https://clinicaltrials.gov/api/v2/studies/{trial_id}"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                protocol = data.get('protocolSection', {})
                
                # Get Acronym or Study ID
                identification = protocol.get('identificationModule', {})
                study_id = identification.get('acronym') or identification.get('orgStudyIdInfo', {}).get('id', 'Unknown ID')
                
                # Extract Phase Information
                phases = protocol.get('designModule', {}).get('phases', [])
                phase = "" if phases == ['NA'] else "/".join(phases) if phases else ""
                
                # Extract Enrollment Count
                enrollment = protocol.get('designModule', {}).get('enrollmentInfo', {})
                enrollment_count = enrollment.get('count', '')
                
                # Extract Sponsors & Collaborators
                sponsors_data = protocol.get('sponsorCollaboratorsModule', {})
                lead_sponsor = sponsors_data.get('leadSponsor', {}).get('name', 'Unknown Sponsor')
                collaborators = sponsors_data.get('collaborators', [])
                collaborator_names = ";;".join([collab.get('name', 'Unknown Collaborator') for collab in collaborators]) if collaborators else ""
                
                return study_id, phase, enrollment_count, lead_sponsor, collaborator_names
            
        except Exception as e:
            pass
        return "", "", "", "", ""
    
    def extract_ctis(trial_id: str):
        data = {"pagination":{"page":1,"size":20},"sort":{"property":"decisionDate","direction":"DESC"},"searchCriteria":{"containAll":None,"containAny":None,"containNot":None,"title":None,"number":None,"status":None,"medicalCondition":None,"sponsor":None,"endPoint":None,"productName":None,"productRole":None,"populationType":None,"orphanDesignation":None,"msc":None,"ageGroupCode":None,"therapeuticAreaCode":None,"trialPhaseCode":None,"sponsorTypeCode":None,"gender":None,"eeaStartDateFrom":None,"eeaStartDateTo":None,"eeaEndDateFrom":None,"eeaEndDateTo":None,"protocolCode":None,"rareDisease":None,"pip":None,"haveOrphanDesignation":None,"hasStudyResults":None,"hasClinicalStudyReport":None,"isLowIntervention":None,"hasSeriousBreach":None,"hasUnexpectedEvent":None,"hasUrgentSafetyMeasure":None,"isTransitioned":None,"eudraCtCode":None,"trialRegion":None,"vulnerablePopulation":None,"mscStatus":None}}

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
            "cache-control": "no-cache",
            "content-length": "905",
            "content-type": "application/json",
            "cookie": "accepted_cookie=true",
            "origin": "https://euclinicaltrials.eu",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://euclinicaltrials.eu/ctis-public/search?lang=en",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133")',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
        }

        url = "https://euclinicaltrials.eu/ctis-public-api/search"
        
        data['searchCriteria']['number'] = trial_id
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            response_data = response.json()
            if 'data' in response_data and len(response_data['data']) > 0:
                for j in response_data['data']:
                    if j['ctNumber'] == trial_id:
                        acronym = j.get('shortTitle', '')
                        phase = j.get('trialPhase', '')
                        enrollment_count = j.get('totalNumberEnrolled', '')
                        lead_sponsers = j.get('sponsor', '')
                        return acronym, phase, enrollment_count, lead_sponsers, ''
            
        return "", "", "", "", ""

    def extract_eudract(trail_id: str):
        url = f"https://www.clinicaltrialsregister.eu/ctr-search/rest/download/full?query={trail_id}&mode=current_page"
        response = requests.get(url)
        if response.status_code == 200:
            file_content = response.text
            
            acronym_match = re.search(r"A\.\d+(\.\d+)?\s*Name or abbreviated title of the trial where available:\s*(.+)", file_content)
            if acronym_match:
                acronym = acronym_match.group(2).strip()
            else:
                acronym = ''
                
            if re.search(r"Therapeutic exploratory \(Phase II\): Yes", file_content):
                phase = "Phase 2"
            elif re.search(r"Human pharmacology \(Phase I\): Yes", file_content):
                phase = "Phase 1"
            elif re.search(r"Therapeutic confirmatory \(Phase III\): Yes", file_content):
                phase = "Phase 3"
            elif re.search(r"Therapeutic use \(Phase IV\): Yes", file_content):
                phase = "Phase 4"
            else:
                phase = ""
        
            sponsor_match = re.search(r"B\.1\.1 Name of Sponsor:\s*(.+)", file_content)
            if sponsor_match:
                lead_sponsers = sponsor_match.group(1).strip()
            else:
                lead_sponsers = ''
                
            return acronym, phase, '', lead_sponsers, ''
        
        return "", "", "", "", ""
    
    df = df.copy()
    df['INTERNAL_ID_FLAG'] = range(len(df))
    
    # Create long format reference DataFrame
    df_long_ref = df.assign(**{column: df[column].astype(str).str.split(delimiter)}).explode(column, ignore_index=True)
    df_long_ref[column] = df_long_ref[column].str.strip()
    df_long_ref[column] = df_long_ref[column].replace(['nan', 'None', None], '')
    # Get unique trial IDs
    unique_trial_ids = df_long_ref[column].dropna().unique()
    
    # --- Route extraction ---
    def route_extraction(trial_id: str):
        if not trial_id or str(trial_id).strip().lower() in ["", "nan", "none"]:
            return "", "", "", "", ""
        trial_id = trial_id.strip()
        try:
            if trial_id.upper().startswith("NCT"):
                return extract_nct(trial_id)
            elif re.match(r"\b\d{4}-\d{6}-\d{2}-\d{2}\b", trial_id):
                return extract_ctis(trial_id)
            elif re.match(r"\b\d{4}-\d{6}-\d{2}\b", trial_id):
                return extract_eudract(trial_id)
        except:
            return "", "", "", "", ""
        return "", "", "", "", ""
    
    # 4️⃣ Extract data for unique trial IDs
    trial_map = {tid: route_extraction(tid) for tid in tqdm(unique_trial_ids, desc="Extracting trial info")}
    
    # 5️⃣ Map results back to long reference DataFrame
    df_long_ref[['Study ID','Phase','Enrollment','Lead Sponsor','Collaborators']] = \
        df_long_ref[column].apply(lambda x: pd.Series(trial_map.get(x, ("","","","",""))))
    
    # 6️⃣ Generate standard (wide) format by INTERNAL_ID_FLAG
    group_cols = ['Study ID','Phase','Enrollment','Lead Sponsor','Collaborators']
    df_standard = df_long_ref.groupby('INTERNAL_ID_FLAG')[group_cols].agg(
        lambda x: ", ".join([str(i) for i in x if i not in [None, ""]])
    ).reset_index()
    
    # Merge back original columns (except INTERNAL_ID_FLAG)
    original_cols = [c for c in df.columns if c != 'INTERNAL_ID_FLAG']
    df_standard = df.merge(df_standard, left_on='INTERNAL_ID_FLAG', right_on='INTERNAL_ID_FLAG', how='left')
    
    # 7️⃣ Drop INTERNAL_ID_FLAG before returning
    df_standard = df_standard.drop(columns=['INTERNAL_ID_FLAG'])
    df_long = df_long_ref.drop(columns=['INTERNAL_ID_FLAG'])
    
    return df_standard, df_long    
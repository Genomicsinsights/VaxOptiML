import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from Bio.SeqUtils.ProtParamData import kd
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from lightgbm import LGBMRegressor
import joblib
import time
import base64
import smtplib
from email.mime.multipart import  MIMEMultipart
from email.mime.text import  MIMEText
from email.mime.base import MIMEBase
from email import encoders


def clear_catche():
    st.cache_data()

clear_catche()

sender_email = 'genomicsinsights@gmail.com'
password = 'iffemqtvylfoartz'
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')
def create_download_link(data, filename, mime):
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:{mime};base64,{b64}" download="{filename}">Download {filename}</a>'


page = st.sidebar.radio("Choose a page", ["Home", "About", "Help"])
st.title("VaxOptiML")
st.write("An integrated pipeline designed to enhance Cancer epitope prediction and prioritization")
st.image("logo.png", width=200)

text = [
    'For epitope prediction in cancer immunotherapy, our integrated pipeline uses three models. We prioritize targets based on immunogenicity, precisely anticipate epitopes, and customize HLA pairing using sophisticated machine learning approaches and carefully selected datasets.',
    'Thorough assessment demonstrates improved performance compared to current methods, and highlight the effectiveness of our ensemble model in accelerating epitope discovery and vaccine development for cancer immunotherapy.',
    'The input protein will be chunked and peptide features will be generated.',
    'On the basis of 0 and 1 annotations, peptides will be classified as either epitopes or non-epitopes.',
    'For such peptides, antigenic scores are computed and HLA bindings are predicted.',
    'Finally, the machine learning classifier and antigenic score will determine the final probable epitopes, as well as their starting and ending positions.']

text1 = [
    'Our advanced epitope prediction framework leverages three robust models for cancer immunotherapy. By focusing on immunogenicity, we precisely forecast epitopes and align them with HLAs through advanced machine learning techniques and curated datasets.',
    'Extensive evaluation shows our method outperforms existing techniques, emphasizing the ensemble model\'s efficiency in fast-tracking epitope identification and vaccine design for cancer treatment.',
    'The target protein is segmented, and peptide characteristics are extracted.',
    'Based on binary annotations, peptides are categorized as either epitopes or non-epitopes.',
    'For these peptides, antigenicity scores are calculated, and their HLA bindings are predicted.',
    'In conclusion, the machine learning classifier and antigenicity score pinpoint the most likely epitopes, along with their start and end locations.']

text2 = [
    "In our integrated pipeline for epitope prediction in cancer immunotherapy, three distinct models are utilized. We prioritize targets based on immunogenicity, accurately predict epitopes, and tailor HLA binding using sophisticated machine learning algorithms and selected datasets.",
    "Comprehensive assessments show our method's enhanced performance compared to current techniques, highlighting the effectiveness of our ensemble model in speeding up epitope discovery and vaccine development for cancer immunotherapy.",
    "The input protein sequence is divided into segments, and peptide features are generated.",
    "Peptides are classified as either epitopes or non-epitopes based on binary annotations.",
    "For these peptides, antigenic scores are calculated, and their HLA interactions are predicted.",
    "Ultimately, the machine learning classifier and antigenic score determine the final probable epitopes, including their start and end positions."]

def main():
    if page == "Home":
        text_input = st.text_input("Enter Protein Sequence :").upper()
        text_input = text_input.replace(" ", "")  # This line removes spaces from the input sequence
        prediction_option = st.radio("\n 1.Remove the spaces from the amino acid sequences\n"
                                     "\n 2.Remove Headers/Identifier\n"
                                     "\n 3.If the input protein sequence is more than 250 amino acids, we recommend you to use our standalone package through this link: https://drive.google.com/file/d/1Zlc_U9beh5gNmcM1og3erpjDIiQLl1KD/view?usp=sharing ( See Help page for more information )\n"  
                                     "\n 4.Dont close the browser while Analysis is Running\n",
                                     ("MHC-1", "MHC-2", "BOTH"))

        receiver_email=st.text_input("Enter the Email*: ")
        if st.button("Predict") and receiver_email:
            if prediction_option == "MHC-1" and text_input:
                status_text = st.empty()
                for i in range(6):
                    time.sleep(9)
                    status_text.text(f'****⏳Analysis Initiated:***')
                    st.write(f"[{i + 1}] ", text1[i])

                protein_sequence = text_input
                if len(protein_sequence)>=10:
                    def find_epitopes(sequence, window_size=10):
                        epitopes = []
                        start = []
                        end = []
                        for i in range(len(sequence) - window_size + 1):
                            epitope = sequence[i:i + window_size]
                            epitopes.append(epitope)
                            start.append(i)
                            end.append(i + window_size - 1)
                        return (epitopes, start, end)

                elif len(protein_sequence)==9:
                    def find_epitopes(sequence, window_size=9):
                        epitopes = []
                        start = []
                        end = []
                        for i in range(len(sequence) - window_size + 1):
                            epitope = sequence[i:i + window_size]
                            epitopes.append(epitope)
                            start.append(i)
                            end.append(i + window_size - 1)
                        return (epitopes, start, end)
                elif len(protein_sequence)==8:
                    def find_epitopes(sequence, window_size=8):
                        epitopes = []
                        start = []
                        end = []
                        for i in range(len(sequence) - window_size + 1):
                            epitope = sequence[i:i + window_size]
                            epitopes.append(epitope)
                            start.append(i)
                            end.append(i + window_size - 1)
                        return (epitopes, start, end)


                def is_valid_protein_sequence(peptide_sequence):
                    valid_letters = set("ACDEFGHIKLMNPQRSTVWY")
                    return set(peptide_sequence) <= valid_letters

                def calculate_atom_counts(peptide_sequence):
                    atom_counts = {'H': 0, 'C': 0, 'N': 0, 'O': 0, 'S': 0}
                    aa_info = {
                        'A': [5, 3, 1, 1, 0], 'R': [17, 6, 4, 2, 0], 'N': [8, 4, 2, 2, 0], 'D': [7, 4, 1, 3, 0],
                        'C': [7, 3, 1, 1, 1], 'E': [9, 5, 1, 3, 0], 'Q': [10, 5, 2, 2, 0], 'G': [3, 2, 1, 1, 0],
                        'H': [11, 6, 3, 2, 0], 'I': [11, 6, 1, 2, 0], 'L': [11, 6, 1, 2, 0], 'K': [14, 6, 2, 2, 0],
                        'M': [11, 5, 1, 2, 1], 'F': [11, 9, 1, 1, 0], 'P': [9, 5, 1, 1, 0], 'S': [9, 3, 1, 2, 0],
                        'T': [11, 4, 1, 2, 0], 'W': [14, 11, 2, 1, 0], 'Y': [12, 6, 1, 3, 0], 'V': [9, 5, 1, 1, 0]
                    }
                    for aa in peptide_sequence:
                        aa = aa.upper()
                        if aa in aa_info:
                            atom_counts['H'] += aa_info[aa][0]
                            atom_counts['C'] += aa_info[aa][1]
                            atom_counts['N'] += aa_info[aa][2]
                            atom_counts['O'] += aa_info[aa][3]
                            atom_counts['S'] += aa_info[aa][4]

                    return atom_counts

                def calculate_physicochemical_properties(peptide_sequence):
                    if not is_valid_protein_sequence(peptide_sequence):
                        return [None] * 35
                    protein_analyzer = ProteinAnalysis(peptide_sequence)
                    theoretical_pI = protein_analyzer.isoelectric_point()
                    aliphatic_index = sum(kd[aa] for aa in peptide_sequence) / len(peptide_sequence)
                    positive_residues = sum(peptide_sequence.count(aa) for aa in ['R', 'K', 'H'])
                    negative_residues = sum(peptide_sequence.count(aa) for aa in ['D', 'E'])
                    aromatic_count = protein_analyzer.aromaticity() * len(peptide_sequence)
                    polar_amino_acids = set("STNQ")
                    non_polar_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
                    polar_count = sum(peptide_sequence.count(aa) for aa in polar_amino_acids)
                    nonpolar_count = sum(peptide_sequence.count(aa) for aa in non_polar_amino_acids)
                    amino_acid_composition = protein_analyzer.get_amino_acids_percent()
                    molecular_weight = protein_analyzer.molecular_weight()
                    instability_index = protein_analyzer.instability_index()
                    aromaticity = protein_analyzer.aromaticity()
                    helix_fraction = protein_analyzer.secondary_structure_fraction()[0]
                    strand_fraction = protein_analyzer.secondary_structure_fraction()[1]
                    coil_fraction = protein_analyzer.secondary_structure_fraction()[2]
                    charge_at_pH_7 = protein_analyzer.charge_at_pH(7.0)
                    gravy = protein_analyzer.gravy()
                    amphipathicity = calculate_amphipathicity(peptide_sequence)
                    gravy_last_50 = protein_analyzer.gravy()
                    molar_extinction_coefficient = protein_analyzer.molar_extinction_coefficient()

                    return [theoretical_pI, aliphatic_index, positive_residues, negative_residues, aromatic_count,
                            polar_count, nonpolar_count, amino_acid_composition, molecular_weight, instability_index,
                            aromaticity, helix_fraction, strand_fraction, coil_fraction, charge_at_pH_7, gravy,
                            amphipathicity,
                            gravy_last_50, molar_extinction_coefficient]

                def calculate_amphipathicity(peptide_sequence):
                    hydrophobic_moment_scale = kd
                    hydrophobic_moment = sum(hydrophobic_moment_scale[aa] for aa in peptide_sequence)
                    mean_hydrophobicity = hydrophobic_moment / len(peptide_sequence)
                    return hydrophobic_moment - mean_hydrophobicity

                def process_single_protein(peptide_sequence, start, end):
                    atom_counts = calculate_atom_counts(peptide_sequence)
                    physicochemical_properties = calculate_physicochemical_properties(peptide_sequence)
                    total_atoms = sum(atom_counts.values())

                    result_dict = {'epitope': peptide_sequence,
                                   'start': start,
                                   'end': end,
                                   'H_Count': atom_counts['H'],
                                   'C_Count': atom_counts['C'],
                                   'N_Count': atom_counts['N'],
                                   'O_Count': atom_counts['O'],
                                   'S_Count': atom_counts['S'],
                                   'TotalAtoms_Count': total_atoms}

                    result_dict.update({
                        'Theoretical.pI': physicochemical_properties[0],
                        'Aliphatic.Index': physicochemical_properties[1],
                        'Positive.Residues': physicochemical_properties[2],
                        'Negative.Residues': physicochemical_properties[3],
                        'Aromatic.Count': physicochemical_properties[4],
                        'Polar.Count': physicochemical_properties[5],
                        'Nonpolar.Count': physicochemical_properties[6]
                    })

                    amino_acids = ['A', 'R', 'N', 'D', 'C', 'E', 'Q', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T',
                                   'W',
                                   'Y', 'V']
                    for i, aa in enumerate(amino_acids):
                        result_dict[aa + '_Percent'] = physicochemical_properties[7].get(aa, 0)

                    result_dict.update({
                        'Molecular.Weight': physicochemical_properties[8],
                        'Instability.Index': physicochemical_properties[9],
                        'Aromaticity': physicochemical_properties[10],
                        'Helix.Fraction': physicochemical_properties[11],
                        'Strand.Fraction': physicochemical_properties[12],
                        'Coil.Fraction': physicochemical_properties[13],
                        'Charge.at.pH.7.0': physicochemical_properties[14],
                        'Gravy': physicochemical_properties[15],
                        'Amphipathicity': physicochemical_properties[16],
                        'GRAVY.Last.50': physicochemical_properties[17],
                        'Molar.Extinction.Coefficient': physicochemical_properties[18]
                    })

                    return result_dict

                def p_is_valid_protein_sequence(protein_sequence):
                    p_valid_letters = set("ACDEFGHIKLMNPQRSTVWY")
                    return set(protein_sequence) <= p_valid_letters

                def p_calculate_atom_counts(protein_sequence):
                    p_atom_counts = {'H': 0, 'C': 0, 'N': 0, 'O': 0, 'S': 0}
                    p_aa_info = {
                        'A': [5, 3, 1, 1, 0], 'R': [17, 6, 4, 2, 0], 'N': [8, 4, 2, 2, 0], 'D': [7, 4, 1, 3, 0],
                        'C': [7, 3, 1, 1, 1], 'E': [9, 5, 1, 3, 0], 'Q': [10, 5, 2, 2, 0], 'G': [3, 2, 1, 1, 0],
                        'H': [11, 6, 3, 2, 0], 'I': [11, 6, 1, 2, 0], 'L': [11, 6, 1, 2, 0], 'K': [14, 6, 2, 2, 0],
                        'M': [11, 5, 1, 2, 1], 'F': [11, 9, 1, 1, 0], 'P': [9, 5, 1, 1, 0], 'S': [9, 3, 1, 2, 0],
                        'T': [11, 4, 1, 2, 0], 'W': [14, 11, 2, 1, 0], 'Y': [12, 6, 1, 3, 0], 'V': [9, 5, 1, 1, 0]
                    }

                    for aa in protein_sequence:
                        aa = aa.upper()
                        if aa in p_aa_info:
                            p_atom_counts['H'] += p_aa_info[aa][0]
                            p_atom_counts['C'] += p_aa_info[aa][1]
                            p_atom_counts['N'] += p_aa_info[aa][2]
                            p_atom_counts['O'] += p_aa_info[aa][3]
                            p_atom_counts['S'] += p_aa_info[aa][4]

                    return p_atom_counts

                def p_calculate_physicochemical_properties(protein_sequence):
                    if not p_is_valid_protein_sequence(protein_sequence):
                        return [None] * 35

                    p_protein_analyzer = ProteinAnalysis(protein_sequence)

                    p_theoretical_pI = p_protein_analyzer.isoelectric_point()
                    p_aliphatic_index = sum(kd[aa] for aa in protein_sequence) / len(protein_sequence)
                    p_positive_residues = sum(protein_sequence.count(aa) for aa in ['R', 'K', 'H'])
                    p_negative_residues = sum(protein_sequence.count(aa) for aa in ['D', 'E'])
                    p_aromatic_count = p_protein_analyzer.aromaticity() * len(protein_sequence)
                    p_polar_amino_acids = set("STNQ")
                    p_non_polar_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
                    p_polar_count = sum(protein_sequence.count(aa) for aa in p_polar_amino_acids)
                    p_nonpolar_count = sum(protein_sequence.count(aa) for aa in p_non_polar_amino_acids)
                    p_amino_acid_composition = p_protein_analyzer.get_amino_acids_percent()
                    p_molecular_weight = p_protein_analyzer.molecular_weight()
                    p_instability_index = p_protein_analyzer.instability_index()
                    p_aromaticity = p_protein_analyzer.aromaticity()
                    p_helix_fraction = p_protein_analyzer.secondary_structure_fraction()[0]
                    p_strand_fraction = p_protein_analyzer.secondary_structure_fraction()[1]
                    p_coil_fraction = p_protein_analyzer.secondary_structure_fraction()[2]
                    p_charge_at_pH_7 = p_protein_analyzer.charge_at_pH(7.0)
                    p_gravy = p_protein_analyzer.gravy()
                    p_amphipathicity = p_calculate_amphipathicity(protein_sequence)
                    p_gravy_last_50 = p_protein_analyzer.gravy()
                    p_molar_extinction_coefficient = p_protein_analyzer.molar_extinction_coefficient()

                    return [p_theoretical_pI, p_aliphatic_index, p_positive_residues, p_negative_residues,
                            p_aromatic_count,
                            p_polar_count, p_nonpolar_count, p_amino_acid_composition, p_molecular_weight,
                            p_instability_index,
                            p_aromaticity, p_helix_fraction, p_strand_fraction, p_coil_fraction, p_charge_at_pH_7,
                            p_gravy,
                            p_amphipathicity,
                            p_gravy_last_50, p_molar_extinction_coefficient]

                def p_calculate_amphipathicity(protein_sequence):
                    p_hydrophobic_moment_scale = kd
                    p_hydrophobic_moment = sum(p_hydrophobic_moment_scale[aa] for aa in protein_sequence)
                    p_mean_hydrophobicity = p_hydrophobic_moment / len(protein_sequence)
                    return p_hydrophobic_moment - p_mean_hydrophobicity

                def p_process_single_protein(protein_sequence):
                    p_atom_counts = p_calculate_atom_counts(protein_sequence)
                    p_physicochemical_properties = p_calculate_physicochemical_properties(protein_sequence)
                    p_total_atoms = sum(p_atom_counts.values())

                    p_result_dict = {'p_Sequence': protein_sequence,
                                     'p_H_Count': p_atom_counts['H'],
                                     'p_C_Count': p_atom_counts['C'],
                                     'p_N_Count': p_atom_counts['N'],
                                     'p_O_Count': p_atom_counts['O'],
                                     'p_S_Count': p_atom_counts['S'],
                                     'p_TotalAtoms_Count': p_total_atoms}

                    p_result_dict.update({
                        'p_Theoretical.pI': p_physicochemical_properties[0],
                        'p_Aliphatic.Index': p_physicochemical_properties[1],
                        'p_Positive.Residues': p_physicochemical_properties[2],
                        'p_Negative.Residues': p_physicochemical_properties[3],
                        'p_Aromatic.Count': p_physicochemical_properties[4],
                        'p_Polar.Count': p_physicochemical_properties[5],
                        'p_Nonpolar.Count': p_physicochemical_properties[6]
                    })

                    amino_acids = ['A', 'R', 'N', 'D', 'C', 'E', 'Q', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T',
                                   'W', 'Y', 'V']
                    for i, aa in enumerate(amino_acids):
                        p_result_dict['p_' + aa + '_Percent'] = p_physicochemical_properties[7].get(aa, 0)

                    p_result_dict.update({
                        'p_Molecular.Weight': p_physicochemical_properties[8],
                        'p_Instability.Index': p_physicochemical_properties[9],
                        'p_Aromaticity': p_physicochemical_properties[10],
                        'p_Helix.Fraction': p_physicochemical_properties[11],
                        'p_Strand.Fraction': p_physicochemical_properties[12],
                        'p_Coil.Fraction': p_physicochemical_properties[13],
                        'p_Charge.at.pH.7.0': p_physicochemical_properties[14],
                        'p_Gravy': p_physicochemical_properties[15],
                        'p_Amphipathicity': p_physicochemical_properties[16],
                        'p_GRAVY.Last.50': p_physicochemical_properties[17],
                        'p_Molar.Extinction.Coefficient': p_physicochemical_properties[18]
                    })

                    return p_result_dict

                r_result = p_process_single_protein(protein_sequence)
                global epitopes
                if len(protein_sequence) >= 10:
                    epitopes = find_epitopes(protein_sequence, window_size=10)
                elif len(protein_sequence) ==9:
                    epitopes=find_epitopes(protein_sequence,window_size=9)
                elif len(protein_sequence)==8:
                    epitopes=find_epitopes(protein_sequence,window_size=8)
                epi = []
                for i in range(len(epitopes[0])):
                    result = process_single_protein(epitopes[0][i], epitopes[1][i], epitopes[2][i])
                    epi.append(result)

                df = pd.DataFrame(epi)
                file_name = 'epitopes_results.csv'
                df.to_csv(file_name)
                df_d = pd.read_csv(file_name)
                st.header("The epitope information")
                st.dataframe(df_d)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['subject'] = "Thank you for using our tool"
                body = f"The epitope information  for mhc-1 of {protein_sequence}"
                msg.attach(MIMEText(body, 'html'))
                filename = 'epitopes_results.csv'
                attachment = open(filename, 'rb')
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                msg.attach(p)
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.send_message(msg)
                server.quit()
                st.header('Email sent')

                csv_dt = convert_df_to_csv(df_d)
                csv_lnk = create_download_link(csv_dt, "Epitope_information.csv", "text/csv")
                st.markdown(csv_lnk, unsafe_allow_html=True)

                pro = []
                for i in range(len(epi)):
                    r_result = p_process_single_protein(protein_sequence)
                    pro.append(r_result)

                clear_catche()

                df_p = pd.DataFrame(pro)
                file_name = 'p_Sequence.csv'
                df_p.to_csv(file_name)
                df_d1 = pd.read_csv(file_name)
                st.header("The Protein sequence information")
                st.dataframe(df_d1)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['subject'] = "Thank you for using our tool"
                body = f"The protein_sequence information  for mhc-1 of {protein_sequence}"
                msg.attach(MIMEText(body, 'html'))
                filename = 'p_Sequence.csv'
                attachment = open(filename, 'rb')
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                msg.attach(p)
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.send_message(msg)
                server.quit()
                st.header('Email sent')


                csv_dt = convert_df_to_csv(df_d1)
                csv_lnk = create_download_link(csv_dt, "Protein_sequence_information.csv", "text/csv")
                st.markdown(csv_lnk, unsafe_allow_html=True)

                df1 = pd.read_csv('epitopes_results.csv')
                df2 = pd.read_csv('p_Sequence.csv')
                merged_df = pd.merge(df1, df2, how='inner')
                merged_df.to_csv('result.csv', index=False)
                print("Merged CSV file has been created.")
                final_res = pd.read_csv('result.csv')

                inps = ['start', 'end', 'R_Percent', 'D_Percent', 'Q_Percent', 'H_Percent',
                        'I_Percent', 'L_Percent',
                        'K_Percent', 'S_Percent', 'Theoretical.pI',
                        'Aliphatic.Index', 'Helix.Fraction', 'Charge.at.pH.7.0', 'Amphipathicity',
                        'p_Molecular.Weight', 'p_Instability.Index', 'p_Helix.Fraction',
                        'p_Amphipathicity', 'p_Aliphatic.Index',
                        'p_H_Count', 'p_C_Count', 'p_N_Count',
                        'p_O_Count', 'p_S_Count', 'p_TotalAtoms_Count',
                        'p_A_Percent',
                        'p_D_Percent',
                        'p_E_Percent', 'p_G_Percent',
                        'p_I_Percent', 'p_K_Percent',
                        'p_F_Percent', 'p_T_Percent',
                        'p_V_Percent',
                        ]
                columns_to_extract = [final_res[j].values[:len(final_res)] for j in inps]
                columns_data = dict(zip(inps, columns_to_extract))
                columns_df = pd.DataFrame(columns_data)
                columns_df.to_csv('extracted_columns.csv')
                bagging_pred = []
                extra_trees_pred = []
                random_forest_pred = []
                df = pd.read_csv('extracted_columns.csv')
                print(df.columns)

                for i in range(len(df)):
                    print(df.end.values[i])
                    print(
                        '-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f'FOR THE {final_res.epitope[i]} the value if 1-> epitope and o-> non-epitope')
                    print(
                        '------------------------------------------------------------------------------------------------------------')

                    inp = [df.start.values[i], df.end.values[i], df.R_Percent.values[i], df.D_Percent.values[i],
                           df.Q_Percent.values[i], df.H_Percent.values[i],
                           df.I_Percent.values[i], df.L_Percent.values[i], df.K_Percent.values[i],
                           df.S_Percent.values[i], df['Theoretical.pI'].values[i], df['Aliphatic.Index'].values[i],
                           df['Helix.Fraction'].values[i], df['Charge.at.pH.7.0'].values[i],
                           df['Amphipathicity'].values[i],
                           df['p_Molecular.Weight'].values[i], df['p_Instability.Index'].values[i],
                           df['p_Helix.Fraction'].values[i],
                           df['p_Amphipathicity'].values[i], df['p_Aliphatic.Index'].values[i],
                           df['p_H_Count'].values[i],
                           df['p_C_Count'].values[i], df['p_N_Count'].values[i], df['p_O_Count'].values[i],
                           df['p_S_Count'].values[i], df['p_TotalAtoms_Count'].values[i], df['p_A_Percent'].values[i],
                           df['p_D_Percent'].values[i], df['p_E_Percent'].values[i], df['p_G_Percent'].values[i],
                           df['p_I_Percent'].values[i], df['p_K_Percent'].values[i], df['p_F_Percent'].values[i],
                           df['p_T_Percent'].values[i], df['p_V_Percent'].values[i]]

                    bagging = joblib.load('Bagging_tar_mhc1.pkl')
                    pred_bag = bagging.predict([inp])
                    bagging_pred.append(pred_bag[0])
                    print("The prediction using Bagging ", pred_bag)

                    extratree = joblib.load('extratree_tar_mhc1.pkl')
                    predict = extratree.predict([inp])
                    extra_trees_pred.append(predict[0])
                    print("The extra tree prediction ", predict)

                    randomfor = joblib.load('randomforest_tar_mhc1.pkl')
                    random_pred = randomfor.predict([inp])
                    random_forest_pred.append(random_pred[0])
                    print("The random forest ", random_pred)

                df = pd.read_csv('result.csv')
                print(df.columns)
                epitopes = []
                xg_boost = []
                lgbm_score = []
                start_val = []
                end_val = []

                for i in range(len(df)):
                    print('-------------------------------------------')
                    epitopes.append(df.epitope.values[i])
                    start_val.append(df.start.values[i])
                    end_val.append(df.end.values[i])
                    print("---------------------------------------------")
                    print(df.epitope.values[i])

                    print('---------------------------------------------')
                    score_inp = [df.start.values[i], df.end.values[i],
                                 df['A_Percent'].values[i], df['R_Percent'].values[i],
                                 df['N_Percent'].values[i], df['D_Percent'].values[i],
                                 df['C_Percent'].values[i], df['E_Percent'].values[i],
                                 df['Q_Percent'].values[i], df['G_Percent'].values[i], df['H_Percent'].values[i],
                                 df['I_Percent'].values[i], df['L_Percent'].values[i], df['K_Percent'].values[i],
                                 df['M_Percent'].values[i], df['F_Percent'].values[i], df['P_Percent'].values[i],
                                 df['S_Percent'].values[i], df['T_Percent'].values[i], df['W_Percent'].values[i],
                                 df['Y_Percent'].values[i], df['V_Percent'].values[i],
                                 df['H_Count'].values[i], df['C_Count'].values[i], df['N_Count'].values[i],
                                 df['S_Count'].values[i],
                                 df['TotalAtoms_Count'].values[i],
                                 df['Theoretical.pI'].values[i], df['Aliphatic.Index'].values[i],
                                 df['Positive.Residues'].values[i], df['Negative.Residues'].values[i],
                                 df['Aromatic.Count'].values[i], df['Polar.Count'].values[i],
                                 df['Nonpolar.Count'].values[i], df['Molecular.Weight'].values[i],
                                 df['Instability.Index'].values[i], df['Aromaticity'].values[i],
                                 df['Helix.Fraction'].values[i], df['Strand.Fraction'].values[i],
                                 df['Coil.Fraction'].values[i],
                                 df['Charge.at.pH.7.0'].values[i], df['Amphipathicity'].values[i],
                                 df['GRAVY.Last.50'].values[i],
                                 df['p_Instability.Index'].values[i], df['p_Helix.Fraction'].values[i],
                                 df['p_Strand.Fraction'].values[i], df['p_Coil.Fraction'].values[i],
                                 df['p_Charge.at.pH.7.0'].values[i],
                                 df['p_Amphipathicity'].values[i], df['p_Aliphatic.Index'].values[i],
                                 df['p_Aromatic.Count'].values[i], df['p_Nonpolar.Count'].values[i],
                                 df['p_H_Count'].values[i],
                                 df['p_C_Count'].values[i], df['p_O_Count'].values[i],
                                 df['p_TotalAtoms_Count'].values[i],
                                 df['p_R_Percent'].values[i],
                                 df['p_N_Percent'].values[i], df['p_D_Percent'].values[i],
                                 df['p_E_Percent'].values[i],
                                 df['p_L_Percent'].values[i],
                                 df['p_T_Percent'].values[i], df['p_W_Percent'].values[i]]

                    xgb = joblib.load('xgb_score_mhc1.pkl')
                    xgb_pred = xgb.predict([score_inp])
                    print("The xgb_pred ", xgb_pred)
                    xg_boost.append(xgb_pred[0])

                    lgb = joblib.load('lgb_score_mhc1.pkl')
                    lgbm_prediction = lgb.predict([score_inp])
                    lgbm_score.append(lgbm_prediction[0])
                    print('The lgbm prediction ', lgbm_prediction)

                kolaskar_df = pd.DataFrame({
                    "start": start_val,
                    "end": end_val,
                    "Epitope": epitopes,
                    "XGB_predicted_score": xg_boost,
                    "KOLASKAR_SCORE": lgbm_score,
                    "Extra_tree_Target": extra_trees_pred,
                    "bagging_Target": bagging_pred,
                    "Random_forest_Target": random_forest_pred,
                })

                kolaskar_df.to_csv('kolaskar.csv')
                df_kolaskar = pd.read_csv("kolaskar.csv")

                def protein_to_numerical(sequence):
                    if isinstance(sequence, str):
                        aa_hydrophobicity = {
                            'A': 1.8, 'C': 2.5, 'D': -3.5, 'E': -3.5, 'F': 2.8,
                            'G': -0.4, 'H': -3.2, 'I': 4.5, 'K': -3.9, 'L': 3.8,
                            'M': 1.9, 'N': -3.5, 'P': -1.6, 'Q': -3.5, 'R': -4.5,
                            'S': -0.8, 'T': -0.7, 'V': 4.2, 'W': -0.9, 'Y': -1.3
                        }
                        numerical_seq = [aa_hydrophobicity.get(aa, 0.5) for aa in
                                         sequence.upper()]  # Convert to uppercase
                        return sum(numerical_seq) / len(numerical_seq) if len(
                            numerical_seq) > 0 else 0.5  # Handle empty sequences
                    else:
                        raise TypeError("Input must be a string representing a protein sequence.")

                df_res = pd.read_csv('result.csv')
                lgbm_hla = []
                hist_hla = []
                for i in range(len(df_res)):
                    hla_inp = [df_res['A_Percent'].values[i], df_res['R_Percent'].values[i],
                               df_res['N_Percent'].values[i],
                               df_res['D_Percent'].values[i], df_res['Q_Percent'].values[i],
                               df_res['G_Percent'].values[i],
                               df_res['H_Percent'].values[i], df_res['F_Percent'].values[i],
                               df_res['S_Percent'].values[i],
                               df_res['T_Percent'].values[i], df_res['H_Count'].values[i], df_res['C_Count'].values[i],
                               df_res['N_Count'].values[i], df_res['O_Count'].values[i],
                               df_res['TotalAtoms_Count'].values[i],
                               df_res['Theoretical.pI'].values[i], df_res['Positive.Residues'].values[i],
                               df_res['Negative.Residues'].values[i], df_res['Aromatic.Count'].values[i],
                               df_res['Polar.Count'].values[i], df_res['Nonpolar.Count'].values[i],
                               df_res['Molecular.Weight'].values[i],
                               df_res['Helix.Fraction'].values[i], df_res['Strand.Fraction'].values[i],
                               df_res['Charge.at.pH.7.0'].values[i], df_res['p_Aromaticity'].values[i],
                               df_res['p_Strand.Fraction'].values[i],
                               df_res['p_Coil.Fraction'].values[i], df_res['p_Gravy'].values[i],
                               df_res['p_Aliphatic.Index'].values[i], df_res['p_GRAVY.Last.50'].values[i],
                               df_res['p_A_Percent'].values[i], df_res['p_G_Percent'].values[i],
                               df_res['p_H_Percent'].values[i], df_res['p_F_Percent'].values[i],
                               df_res['p_T_Percent'].values[i], df_res['p_W_Percent'].values[i],
                               df_res['p_Y_Percent'].values[i], df_res['p_V_Percent'].values[i], 0,
                               protein_to_numerical(text_input)]

                    lgbm = joblib.load('lgbm_hla.pkl')
                    lgbm_hla.append(lgbm.predict([hla_inp])[0])
                    print("The LGBM prediction ", lgbm.predict([hla_inp])[0])

                    hist = joblib.load('hist_hla.pkl')
                    hist_hla.append(hist.predict([hla_inp])[0])
                    print("The Hist_prediction ", hist.predict([hla_inp])[0])

                score_df = pd.DataFrame({
                    "start": start_val,
                    "end": end_val,
                    "Epitope": epitopes,
                    "XGB_predicted_score": xg_boost,
                    "KOLASKAR_SCORE": lgbm_score,
                    "Extra_tree_Target": extra_trees_pred,
                    "bagging_Target": bagging_pred,
                    "Random_forest_Target": random_forest_pred,
                    "lgbm_hla": lgbm_hla,
                    "hist_hla": hist_hla
                })

                score_df.to_csv("final_output.csv")
                score = pd.read_csv('final_output.csv')
                st.header("The Machine Learning Classifier results")
                clear_catche()
                st.dataframe(score)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['subject'] = "Thank you for using our tool"
                body = f"The Machine Learning Classifier results for mhc-1 of {protein_sequence}"
                msg.attach(MIMEText(body, 'html'))
                filename = 'final_output.csv'
                attachment = open(filename, 'rb')
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                msg.attach(p)
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.send_message(msg)
                server.quit()
                st.header('Email sent')

                csv_dt = convert_df_to_csv(score)
                csv_lnk = create_download_link(csv_dt, "ML_classification_output.csv", "text/csv")
                st.markdown(csv_lnk, unsafe_allow_html=True)

                print(score['Random_forest_Target'].values)
                print(score['Extra_tree_Target'].values)
                count_ones = score[['Extra_tree_Target', 'Random_forest_Target', 'bagging_Target']].sum(axis=1)
                score['Target'] = (count_ones > 2).astype(int)
                score.to_csv('target_final.csv')
                df_final = pd.read_csv('target_final.csv')
                df = df_final['lgbm_hla']

                amino_acid_values = {
                    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5,
                    'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
                    'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15,
                    'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20,
                    'U': 21, 'V': 22, 'W': 23, 'X': 24, 'Y': 25, 'Z': 26
                }

                def calculate_numerical_score(hla):
                    hla = str(hla)
                    alleles = hla.split('/')
                    total_score = 0
                    for allele in alleles:
                        amino_acid_sequence = ''.join(char for char in allele if char.isalpha())
                        numeric_parts = ''.join(char for char in allele if char.isdigit())
                        for amino_acid in amino_acid_sequence:
                            total_score += amino_acid_values.get(amino_acid, 0)
                        if numeric_parts:
                            total_score += float(numeric_parts)
                    return total_score

                def find_nearest_hla(total_score, hla_strings, k=10):
                    nearest_hla_list = []
                    hla_strings_sorted = sorted(hla_strings,
                                                key=lambda hla: abs(calculate_numerical_score(hla) - total_score))
                    for hla in hla_strings_sorted[:k]:
                        nearest_hla_list.append(hla)
                    return nearest_hla_list
                clear_catche()
                data = pd.read_csv('hla.csv')
                hla_output = []
                pred = []
                hla_strings = [str(hla) for hla in data['HLA'].values]
                for i in range(len(df_final)):
                    nearest_hla_list = find_nearest_hla(df_final['lgbm_hla'].values[i], hla_strings, k=5)
                    print("10 Nearest HLA Strings:")
                    for i, hla in enumerate(nearest_hla_list, start=1):
                        print(hla)
                        pred.append(hla)
                        if len(pred) == 5:
                            hla_output.append(set(pred))
                            pred = []

                df_final['hla_values'] = hla_output
                df_final.to_csv("expected.csv")
                df_d3 = pd.read_csv("expected.csv")
                target = df_d3[['Extra_tree_Target', 'Random_forest_Target', 'bagging_Target']].sum(axis=1)
                print('---------------------------------------------')
                print(target)
                df_d3['Target'] = (target >= 2).astype(int)
                print(df_d3.Target)
                print('-------------------------------------------------------')
                df_tar = df_d3[df_d3['Target'] == 1]
                if len(df_tar.Target.values) <= 30:
                    df_tar.to_csv('target.csv')
                    df_tab = pd.read_csv('target.csv')
                    print(df_tab.columns)
                    col = ['start', 'end', 'Epitope', 'hla_values', 'KOLASKAR_SCORE']
                    df_tab[col].to_csv("final_epitopes.csv")
                    st.header("ANALYSIS COMPLETED")
                    st.dataframe(df_tab[col])

                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg['subject'] = "Thank you for using our tool"
                    body = f"FINAL CSV FILE OF FINAL PREDICTED EPITOPES for mhc-1 of {protein_sequence}"
                    msg.attach(MIMEText(body, 'html'))
                    filename = 'final_epitopes.csv'
                    attachment = open(filename, 'rb')
                    p = MIMEBase('application', 'octet-stream')
                    p.set_payload((attachment).read())
                    encoders.encode_base64(p)
                    p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                    msg.attach(p)
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(sender_email, password)
                    text = msg.as_string()
                    server.send_message(msg)
                    server.quit()
                    st.header('Email sent')

                    csv_d = convert_df_to_csv(df_tar)
                    c_lnk = create_download_link(csv_d, "final_epitopes.csv", "text/csv")
                    st.markdown(c_lnk, unsafe_allow_html=True)
                else:
                    values = df_d3['KOLASKAR_SCORE'].sort_values(ascending=False).values
                    val = []
                    for i in range(len(values)):
                        val.append(values[i])
                        if len(val) == 30:
                            break
                    epitope = []
                    hla = []
                    starts = []
                    ends = []
                    score = []
                    for i in val:
                        df_val = df_d3[df_d3['KOLASKAR_SCORE'] == i]
                        epitope.append(df_val.Epitope)
                        hla.append(set(df_val.hla_values))
                        starts.append(df_val.start)
                        ends.append(df_val.end)
                        score.append(df_val.KOLASKAR_SCORE)

                    data_dict = {
                        'Epitope': epitope,
                        'HLA': hla,
                        'Start': starts,
                        'End': ends,
                        'Kolaskar_score': score
                    }
                    df_l = pd.DataFrame(data_dict)
                    df_l = df_l.explode('Epitope').explode('HLA').explode('Start').explode('End').explode(
                        'Kolaskar_score')
                    df_l.reset_index(drop=True, inplace=True)
                    print(df_l)
                    st.header("ANALYSIS COMPLETED")
                    st.dataframe(df_l)

                    df_l.to_csv("final_epi.csv")
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg['subject'] = "Thank your for using our tool"
                    body = f"FINAL CSV FILE OF FINALLY PREDICTED EPITOPES for mhc-1 of {protein_sequence}"
                    msg.attach(MIMEText(body, 'html'))
                    filename = 'final_epi.csv'
                    attachment = open(filename, 'rb')
                    p = MIMEBase('application', 'octet-stream')
                    p.set_payload((attachment).read())
                    encoders.encode_base64(p)
                    p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                    msg.attach(p)
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(sender_email, password)
                    text = msg.as_string()
                    server.send_message(msg)
                    server.quit()
                    st.header('Email sent')
                    csv_d = convert_df_to_csv(df_l)
                    c_lnk = create_download_link(csv_d, "final_epitopes.csv", "text/csv")
                    st.markdown(c_lnk, unsafe_allow_html=True)
                clear_catche()
            elif prediction_option == "MHC-2" and text_input:
                status_text = st.empty()
                for i in range(6):
                    time.sleep(9)
                    status_text.text(f'****⏳Analysis Initiated:***')
                    st.write(f"[{i + 1}] ", text1[i])

                protein_sequence = text_input

                def find_epitopes(sequence, window_size=15):
                    epitopes = []
                    start = []
                    end = []
                    for i in range(len(sequence) - window_size + 1):
                        epitope = sequence[i:i + window_size]
                        epitopes.append(epitope)
                        start.append(i)
                        end.append(i + window_size - 1)
                    return (epitopes, start, end)

                def is_valid_protein_sequence(peptide_sequence):
                    valid_letters = set("ACDEFGHIKLMNPQRSTVWY")
                    return set(peptide_sequence) <= valid_letters

                def calculate_atom_counts(peptide_sequence):
                    atom_counts = {'H': 0, 'C': 0, 'N': 0, 'O': 0, 'S': 0}
                    aa_info = {
                        'A': [5, 3, 1, 1, 0], 'R': [17, 6, 4, 2, 0], 'N': [8, 4, 2, 2, 0], 'D': [7, 4, 1, 3, 0],
                        'C': [7, 3, 1, 1, 1], 'E': [9, 5, 1, 3, 0], 'Q': [10, 5, 2, 2, 0], 'G': [3, 2, 1, 1, 0],
                        'H': [11, 6, 3, 2, 0], 'I': [11, 6, 1, 2, 0], 'L': [11, 6, 1, 2, 0], 'K': [14, 6, 2, 2, 0],
                        'M': [11, 5, 1, 2, 1], 'F': [11, 9, 1, 1, 0], 'P': [9, 5, 1, 1, 0], 'S': [9, 3, 1, 2, 0],
                        'T': [11, 4, 1, 2, 0], 'W': [14, 11, 2, 1, 0], 'Y': [12, 6, 1, 3, 0], 'V': [9, 5, 1, 1, 0]
                    }
                    for aa in peptide_sequence:
                        aa = aa.upper()
                        if aa in aa_info:
                            atom_counts['H'] += aa_info[aa][0]
                            atom_counts['C'] += aa_info[aa][1]
                            atom_counts['N'] += aa_info[aa][2]
                            atom_counts['O'] += aa_info[aa][3]
                            atom_counts['S'] += aa_info[aa][4]

                    return atom_counts

                def calculate_physicochemical_properties(peptide_sequence):
                    if not is_valid_protein_sequence(peptide_sequence):
                        return [None] * 35
                    protein_analyzer = ProteinAnalysis(peptide_sequence)
                    theoretical_pI = protein_analyzer.isoelectric_point()
                    aliphatic_index = sum(kd[aa] for aa in peptide_sequence) / len(peptide_sequence)
                    positive_residues = sum(peptide_sequence.count(aa) for aa in ['R', 'K', 'H'])
                    negative_residues = sum(peptide_sequence.count(aa) for aa in ['D', 'E'])
                    aromatic_count = protein_analyzer.aromaticity() * len(peptide_sequence)
                    polar_amino_acids = set("STNQ")
                    non_polar_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
                    polar_count = sum(peptide_sequence.count(aa) for aa in polar_amino_acids)
                    nonpolar_count = sum(peptide_sequence.count(aa) for aa in non_polar_amino_acids)
                    amino_acid_composition = protein_analyzer.get_amino_acids_percent()
                    molecular_weight = protein_analyzer.molecular_weight()
                    instability_index = protein_analyzer.instability_index()
                    aromaticity = protein_analyzer.aromaticity()
                    helix_fraction = protein_analyzer.secondary_structure_fraction()[0]
                    strand_fraction = protein_analyzer.secondary_structure_fraction()[1]
                    coil_fraction = protein_analyzer.secondary_structure_fraction()[2]
                    charge_at_pH_7 = protein_analyzer.charge_at_pH(7.0)
                    gravy = protein_analyzer.gravy()
                    amphipathicity = calculate_amphipathicity(peptide_sequence)
                    gravy_last_50 = protein_analyzer.gravy()
                    molar_extinction_coefficient = protein_analyzer.molar_extinction_coefficient()

                    return [theoretical_pI, aliphatic_index, positive_residues, negative_residues, aromatic_count,
                            polar_count, nonpolar_count, amino_acid_composition, molecular_weight, instability_index,
                            aromaticity, helix_fraction, strand_fraction, coil_fraction, charge_at_pH_7, gravy,
                            amphipathicity,
                            gravy_last_50, molar_extinction_coefficient]

                def calculate_amphipathicity(peptide_sequence):
                    hydrophobic_moment_scale = kd
                    hydrophobic_moment = sum(hydrophobic_moment_scale[aa] for aa in peptide_sequence)
                    mean_hydrophobicity = hydrophobic_moment / len(peptide_sequence)
                    return hydrophobic_moment - mean_hydrophobicity
                clear_catche()
                def process_single_protein(peptide_sequence, start, end):
                    atom_counts = calculate_atom_counts(peptide_sequence)
                    physicochemical_properties = calculate_physicochemical_properties(peptide_sequence)
                    total_atoms = sum(atom_counts.values())

                    result_dict = {'epitope': peptide_sequence,
                                   'start': start,
                                   'end': end,
                                   'H_Count': atom_counts['H'],
                                   'C_Count': atom_counts['C'],
                                   'N_Count': atom_counts['N'],
                                   'O_Count': atom_counts['O'],
                                   'S_Count': atom_counts['S'],
                                   'TotalAtoms_Count': total_atoms}

                    result_dict.update({
                        'Theoretical.pI': physicochemical_properties[0],
                        'Aliphatic.Index': physicochemical_properties[1],
                        'Positive.Residues': physicochemical_properties[2],
                        'Negative.Residues': physicochemical_properties[3],
                        'Aromatic.Count': physicochemical_properties[4],
                        'Polar.Count': physicochemical_properties[5],
                        'Nonpolar.Count': physicochemical_properties[6]
                    })

                    amino_acids = ['A', 'R', 'N', 'D', 'C', 'E', 'Q', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T',
                                   'W',
                                   'Y', 'V']
                    for i, aa in enumerate(amino_acids):
                        result_dict[aa + '_Percent'] = physicochemical_properties[7].get(aa, 0)

                    result_dict.update({
                        'Molecular.Weight': physicochemical_properties[8],
                        'Instability.Index': physicochemical_properties[9],
                        'Aromaticity': physicochemical_properties[10],
                        'Helix.Fraction': physicochemical_properties[11],
                        'Strand.Fraction': physicochemical_properties[12],
                        'Coil.Fraction': physicochemical_properties[13],
                        'Charge.at.pH.7.0': physicochemical_properties[14],
                        'Gravy': physicochemical_properties[15],
                        'Amphipathicity': physicochemical_properties[16],
                        'GRAVY.Last.50': physicochemical_properties[17],
                        'Molar.Extinction.Coefficient': physicochemical_properties[18]
                    })

                    return result_dict

                def p_is_valid_protein_sequence(protein_sequence):
                    p_valid_letters = set("ACDEFGHIKLMNPQRSTVWY")
                    return set(protein_sequence) <= p_valid_letters

                def p_calculate_atom_counts(protein_sequence):
                    p_atom_counts = {'H': 0, 'C': 0, 'N': 0, 'O': 0, 'S': 0}
                    p_aa_info = {
                        'A': [5, 3, 1, 1, 0], 'R': [17, 6, 4, 2, 0], 'N': [8, 4, 2, 2, 0], 'D': [7, 4, 1, 3, 0],
                        'C': [7, 3, 1, 1, 1], 'E': [9, 5, 1, 3, 0], 'Q': [10, 5, 2, 2, 0], 'G': [3, 2, 1, 1, 0],
                        'H': [11, 6, 3, 2, 0], 'I': [11, 6, 1, 2, 0], 'L': [11, 6, 1, 2, 0], 'K': [14, 6, 2, 2, 0],
                        'M': [11, 5, 1, 2, 1], 'F': [11, 9, 1, 1, 0], 'P': [9, 5, 1, 1, 0], 'S': [9, 3, 1, 2, 0],
                        'T': [11, 4, 1, 2, 0], 'W': [14, 11, 2, 1, 0], 'Y': [12, 6, 1, 3, 0], 'V': [9, 5, 1, 1, 0]
                    }

                    for aa in protein_sequence:
                        aa = aa.upper()
                        if aa in p_aa_info:
                            p_atom_counts['H'] += p_aa_info[aa][0]
                            p_atom_counts['C'] += p_aa_info[aa][1]
                            p_atom_counts['N'] += p_aa_info[aa][2]
                            p_atom_counts['O'] += p_aa_info[aa][3]
                            p_atom_counts['S'] += p_aa_info[aa][4]

                    return p_atom_counts

                def p_calculate_physicochemical_properties(protein_sequence):
                    if not p_is_valid_protein_sequence(protein_sequence):
                        return [None] * 35

                    p_protein_analyzer = ProteinAnalysis(protein_sequence)

                    p_theoretical_pI = p_protein_analyzer.isoelectric_point()
                    p_aliphatic_index = sum(kd[aa] for aa in protein_sequence) / len(protein_sequence)
                    p_positive_residues = sum(protein_sequence.count(aa) for aa in ['R', 'K', 'H'])
                    p_negative_residues = sum(protein_sequence.count(aa) for aa in ['D', 'E'])
                    p_aromatic_count = p_protein_analyzer.aromaticity() * len(protein_sequence)
                    p_polar_amino_acids = set("STNQ")
                    p_non_polar_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
                    p_polar_count = sum(protein_sequence.count(aa) for aa in p_polar_amino_acids)
                    p_nonpolar_count = sum(protein_sequence.count(aa) for aa in p_non_polar_amino_acids)
                    p_amino_acid_composition = p_protein_analyzer.get_amino_acids_percent()
                    p_molecular_weight = p_protein_analyzer.molecular_weight()
                    p_instability_index = p_protein_analyzer.instability_index()
                    p_aromaticity = p_protein_analyzer.aromaticity()
                    p_helix_fraction = p_protein_analyzer.secondary_structure_fraction()[0]
                    p_strand_fraction = p_protein_analyzer.secondary_structure_fraction()[1]
                    p_coil_fraction = p_protein_analyzer.secondary_structure_fraction()[2]
                    p_charge_at_pH_7 = p_protein_analyzer.charge_at_pH(7.0)
                    p_gravy = p_protein_analyzer.gravy()
                    p_amphipathicity = p_calculate_amphipathicity(protein_sequence)
                    p_gravy_last_50 = p_protein_analyzer.gravy()
                    p_molar_extinction_coefficient = p_protein_analyzer.molar_extinction_coefficient()

                    return [p_theoretical_pI, p_aliphatic_index, p_positive_residues, p_negative_residues,
                            p_aromatic_count,
                            p_polar_count, p_nonpolar_count, p_amino_acid_composition, p_molecular_weight,
                            p_instability_index,
                            p_aromaticity, p_helix_fraction, p_strand_fraction, p_coil_fraction, p_charge_at_pH_7,
                            p_gravy,
                            p_amphipathicity,
                            p_gravy_last_50, p_molar_extinction_coefficient]

                def p_calculate_amphipathicity(protein_sequence):
                    p_hydrophobic_moment_scale = kd
                    p_hydrophobic_moment = sum(p_hydrophobic_moment_scale[aa] for aa in protein_sequence)
                    p_mean_hydrophobicity = p_hydrophobic_moment / len(protein_sequence)
                    return p_hydrophobic_moment - p_mean_hydrophobicity

                def p_process_single_protein(protein_sequence):
                    p_atom_counts = p_calculate_atom_counts(protein_sequence)
                    p_physicochemical_properties = p_calculate_physicochemical_properties(protein_sequence)
                    p_total_atoms = sum(p_atom_counts.values())

                    p_result_dict = {'p_Sequence': protein_sequence,
                                     'p_H_Count': p_atom_counts['H'],
                                     'p_C_Count': p_atom_counts['C'],
                                     'p_N_Count': p_atom_counts['N'],
                                     'p_O_Count': p_atom_counts['O'],
                                     'p_S_Count': p_atom_counts['S'],
                                     'p_TotalAtoms_Count': p_total_atoms}

                    p_result_dict.update({
                        'p_Theoretical.pI': p_physicochemical_properties[0],
                        'p_Aliphatic.Index': p_physicochemical_properties[1],
                        'p_Positive.Residues': p_physicochemical_properties[2],
                        'p_Negative.Residues': p_physicochemical_properties[3],
                        'p_Aromatic.Count': p_physicochemical_properties[4],
                        'p_Polar.Count': p_physicochemical_properties[5],
                        'p_Nonpolar.Count': p_physicochemical_properties[6]
                    })

                    amino_acids = ['A', 'R', 'N', 'D', 'C', 'E', 'Q', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T',
                                   'W', 'Y', 'V']
                    for i, aa in enumerate(amino_acids):
                        p_result_dict['p_' + aa + '_Percent'] = p_physicochemical_properties[7].get(aa, 0)

                    p_result_dict.update({
                        'p_Molecular.Weight': p_physicochemical_properties[8],
                        'p_Instability.Index': p_physicochemical_properties[9],
                        'p_Aromaticity': p_physicochemical_properties[10],
                        'p_Helix.Fraction': p_physicochemical_properties[11],
                        'p_Strand.Fraction': p_physicochemical_properties[12],
                        'p_Coil.Fraction': p_physicochemical_properties[13],
                        'p_Charge.at.pH.7.0': p_physicochemical_properties[14],
                        'p_Gravy': p_physicochemical_properties[15],
                        'p_Amphipathicity': p_physicochemical_properties[16],
                        'p_GRAVY.Last.50': p_physicochemical_properties[17],
                        'p_Molar.Extinction.Coefficient': p_physicochemical_properties[18]
                    })

                    return p_result_dict

                r_result = p_process_single_protein(protein_sequence)
                epitopes = find_epitopes(protein_sequence, window_size=15)
                epi = []
                for i in range(len(epitopes[0])):
                    result = process_single_protein(epitopes[0][i], epitopes[1][i], epitopes[2][i])
                    epi.append(result)

                df = pd.DataFrame(epi)
                file_name = 'epitopes_results.csv'
                df.to_csv(file_name)
                df_d = pd.read_csv(file_name)
                st.header("The epitope information")
                st.dataframe(df_d)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['subject'] = "Thank you for using our tool"
                body = f"The Epitope results  for mhc-2 of {protein_sequence}"
                msg.attach(MIMEText(body, 'html'))
                filename = 'epitopes_results.csv'
                attachment = open(filename, 'rb')
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                msg.attach(p)
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.send_message(msg)
                server.quit()
                st.header('Email sent')

                csv_dt = convert_df_to_csv(df_d)
                csv_lnk = create_download_link(csv_dt, "Epitope_information.csv", "text/csv")
                st.markdown(csv_lnk, unsafe_allow_html=True)

                pro = []
                for i in range(len(epi)):
                    r_result = p_process_single_protein(protein_sequence)
                    pro.append(r_result)

                df_p = pd.DataFrame(pro)
                file_name = 'p_Sequence.csv'
                df_p.to_csv(file_name)
                df_d1 = pd.read_csv(file_name)
                st.header("The Protein sequence information")
                st.dataframe(df_d1)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['subject'] = "Thank you for using our tool"
                body = f"The protein sequence for mhc-2 of {protein_sequence}"
                msg.attach(MIMEText(body, 'html'))
                filename = 'p_Sequence.csv'
                attachment = open(filename, 'rb')
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                msg.attach(p)
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.send_message(msg)
                server.quit()
                st.header('Email sent')

                csv_dt = convert_df_to_csv(df_d1)
                csv_lnk = create_download_link(csv_dt, "Protein_sequence_information.csv", "text/csv")
                st.markdown(csv_lnk, unsafe_allow_html=True)

                df1 = pd.read_csv('epitopes_results.csv')
                df2 = pd.read_csv('p_Sequence.csv')
                merged_df = pd.merge(df1, df2, how='inner')
                merged_df.to_csv('result.csv', index=False)
                print("Merged CSV file has been created.")

                final_res = pd.read_csv('result.csv')

                inps = ['start', 'end', 'R_Percent', 'D_Percent', 'Q_Percent', 'H_Percent',
                        'I_Percent', 'L_Percent',
                        'K_Percent', 'S_Percent', 'Theoretical.pI',
                        'Aliphatic.Index', 'Helix.Fraction', 'Charge.at.pH.7.0', 'Amphipathicity',
                        'p_Molecular.Weight', 'p_Instability.Index', 'p_Helix.Fraction',
                        'p_Amphipathicity', 'p_Aliphatic.Index',
                        'p_H_Count', 'p_C_Count', 'p_N_Count',
                        'p_O_Count', 'p_S_Count', 'p_TotalAtoms_Count',
                        'p_A_Percent',
                        'p_D_Percent',
                        'p_E_Percent', 'p_G_Percent',
                        'p_I_Percent', 'p_K_Percent',
                        'p_F_Percent', 'p_T_Percent',
                        'p_V_Percent',
                        ]
                columns_to_extract = [final_res[j].values[:len(final_res)] for j in inps]
                columns_data = dict(zip(inps, columns_to_extract))
                columns_df = pd.DataFrame(columns_data)
                columns_df.to_csv('extracted_columns.csv')
                bagging_pred = []
                extra_trees_pred = []
                random_forest_pred = []
                df = pd.read_csv('extracted_columns.csv')
                print(df.columns)

                for i in range(len(df)):
                    print(df.end.values[i])
                    print(
                        '-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f'FOR THE {final_res.epitope[i]} the value if 1-> epitope and o-> non-epitope')
                    print(
                        '------------------------------------------------------------------------------------------------------------')

                    inp = [df.start.values[i], df.end.values[i], df.R_Percent.values[i], df.D_Percent.values[i],
                           df.Q_Percent.values[i], df.H_Percent.values[i],
                           df.I_Percent.values[i], df.L_Percent.values[i], df.K_Percent.values[i],
                           df.S_Percent.values[i], df['Theoretical.pI'].values[i], df['Aliphatic.Index'].values[i],
                           df['Helix.Fraction'].values[i], df['Charge.at.pH.7.0'].values[i],
                           df['Amphipathicity'].values[i],
                           df['p_Molecular.Weight'].values[i], df['p_Instability.Index'].values[i],
                           df['p_Helix.Fraction'].values[i],
                           df['p_Amphipathicity'].values[i], df['p_Aliphatic.Index'].values[i],
                           df['p_H_Count'].values[i],
                           df['p_C_Count'].values[i], df['p_N_Count'].values[i], df['p_O_Count'].values[i],
                           df['p_S_Count'].values[i], df['p_TotalAtoms_Count'].values[i], df['p_A_Percent'].values[i],
                           df['p_D_Percent'].values[i], df['p_E_Percent'].values[i], df['p_G_Percent'].values[i],
                           df['p_I_Percent'].values[i], df['p_K_Percent'].values[i], df['p_F_Percent'].values[i],
                           df['p_T_Percent'].values[i], df['p_V_Percent'].values[i]]

                    bagging = joblib.load('Bagging_tar_mhc1.pkl')
                    pred_bag = bagging.predict([inp])
                    bagging_pred.append(pred_bag[0])
                    print("The prediction using Bagging ", pred_bag)

                    extratree = joblib.load('extratree_tar_mhc1.pkl')
                    predict = extratree.predict([inp])
                    extra_trees_pred.append(predict[0])
                    print("The extra tree prediction ", predict)

                    randomfor = joblib.load('randomforest_tar_mhc1.pkl')
                    random_pred = randomfor.predict([inp])
                    random_forest_pred.append(random_pred[0])
                    print("The random forest ", random_pred)

                df = pd.read_csv('result.csv')
                print(df.columns)
                epitopes = []
                xg_boost = []
                lgbm_score = []
                start_val = []
                end_val = []

                for i in range(len(df)):
                    print('-------------------------------------------')
                    epitopes.append(df.epitope.values[i])
                    start_val.append(df.start.values[i])
                    end_val.append(df.end.values[i])
                    print("---------------------------------------------")
                    print(df.epitope.values[i])

                    print('---------------------------------------------')
                    score_inp = [df.start.values[i], df.end.values[i],
                                 df['A_Percent'].values[i], df['R_Percent'].values[i],
                                 df['N_Percent'].values[i], df['D_Percent'].values[i],
                                 df['C_Percent'].values[i], df['E_Percent'].values[i],
                                 df['Q_Percent'].values[i], df['G_Percent'].values[i], df['H_Percent'].values[i],
                                 df['I_Percent'].values[i], df['L_Percent'].values[i], df['K_Percent'].values[i],
                                 df['M_Percent'].values[i], df['F_Percent'].values[i], df['P_Percent'].values[i],
                                 df['S_Percent'].values[i], df['T_Percent'].values[i], df['W_Percent'].values[i],
                                 df['Y_Percent'].values[i], df['V_Percent'].values[i],
                                 df['H_Count'].values[i], df['C_Count'].values[i], df['N_Count'].values[i],
                                 df['S_Count'].values[i],
                                 df['TotalAtoms_Count'].values[i],
                                 df['Theoretical.pI'].values[i], df['Aliphatic.Index'].values[i],
                                 df['Positive.Residues'].values[i], df['Negative.Residues'].values[i],
                                 df['Aromatic.Count'].values[i], df['Polar.Count'].values[i],
                                 df['Nonpolar.Count'].values[i], df['Molecular.Weight'].values[i],
                                 df['Instability.Index'].values[i], df['Aromaticity'].values[i],
                                 df['Helix.Fraction'].values[i], df['Strand.Fraction'].values[i],
                                 df['Coil.Fraction'].values[i],
                                 df['Charge.at.pH.7.0'].values[i], df['Amphipathicity'].values[i],
                                 df['GRAVY.Last.50'].values[i],
                                 df['p_Instability.Index'].values[i], df['p_Helix.Fraction'].values[i],
                                 df['p_Strand.Fraction'].values[i], df['p_Coil.Fraction'].values[i],
                                 df['p_Charge.at.pH.7.0'].values[i],
                                 df['p_Amphipathicity'].values[i], df['p_Aliphatic.Index'].values[i],
                                 df['p_Aromatic.Count'].values[i], df['p_Nonpolar.Count'].values[i],
                                 df['p_H_Count'].values[i],
                                 df['p_C_Count'].values[i], df['p_O_Count'].values[i],
                                 df['p_TotalAtoms_Count'].values[i],
                                 df['p_R_Percent'].values[i],
                                 df['p_N_Percent'].values[i], df['p_D_Percent'].values[i],
                                 df['p_E_Percent'].values[i],
                                 df['p_L_Percent'].values[i],
                                 df['p_T_Percent'].values[i], df['p_W_Percent'].values[i]]

                    xgb = joblib.load('xgb_score_mhc1.pkl')
                    xgb_pred = xgb.predict([score_inp])
                    print("The xgb_pred ", xgb_pred)
                    xg_boost.append(xgb_pred[0])

                    lgb = joblib.load('lgb_score_mhc1.pkl')
                    lgbm_prediction = lgb.predict([score_inp])
                    lgbm_score.append(lgbm_prediction[0])
                    print('The lgbm prediction ', lgbm_prediction)

                kolaskar_df = pd.DataFrame({
                    "start": start_val,
                    "end": end_val,
                    "Epitope": epitopes,
                    "XGB_predicted_score": xg_boost,
                    "KOLASKAR_SCORE": lgbm_score,
                    "Extra_tree_Target": extra_trees_pred,
                    "bagging_Target": bagging_pred,
                    "Random_forest_Target": random_forest_pred,
                })

                kolaskar_df.to_csv('kolaskar.csv')
                df_kolaskar = pd.read_csv("kolaskar.csv")

                def protein_to_numerical(sequence):
                    if isinstance(sequence, str):
                        aa_hydrophobicity = {
                            'A': 1.8, 'C': 2.5, 'D': -3.5, 'E': -3.5, 'F': 2.8,
                            'G': -0.4, 'H': -3.2, 'I': 4.5, 'K': -3.9, 'L': 3.8,
                            'M': 1.9, 'N': -3.5, 'P': -1.6, 'Q': -3.5, 'R': -4.5,
                            'S': -0.8, 'T': -0.7, 'V': 4.2, 'W': -0.9, 'Y': -1.3
                        }
                        numerical_seq = [aa_hydrophobicity.get(aa, 0.5) for aa in
                                         sequence.upper()]  # Convert to uppercase
                        return sum(numerical_seq) / len(numerical_seq) if len(
                            numerical_seq) > 0 else 0.5  # Handle empty sequences
                    else:
                        raise TypeError("Input must be a string representing a protein sequence.")

                df_res = pd.read_csv('result.csv')
                lgbm_hla = []
                hist_hla = []
                for i in range(len(df_res)):
                    hla_inp = [df_res['A_Percent'].values[i], df_res['R_Percent'].values[i],
                               df_res['N_Percent'].values[i],
                               df_res['D_Percent'].values[i], df_res['Q_Percent'].values[i],
                               df_res['G_Percent'].values[i],
                               df_res['H_Percent'].values[i], df_res['F_Percent'].values[i],
                               df_res['S_Percent'].values[i],
                               df_res['T_Percent'].values[i], df_res['H_Count'].values[i], df_res['C_Count'].values[i],
                               df_res['N_Count'].values[i], df_res['O_Count'].values[i],
                               df_res['TotalAtoms_Count'].values[i],
                               df_res['Theoretical.pI'].values[i], df_res['Positive.Residues'].values[i],
                               df_res['Negative.Residues'].values[i], df_res['Aromatic.Count'].values[i],
                               df_res['Polar.Count'].values[i], df_res['Nonpolar.Count'].values[i],
                               df_res['Molecular.Weight'].values[i],
                               df_res['Helix.Fraction'].values[i], df_res['Strand.Fraction'].values[i],
                               df_res['Charge.at.pH.7.0'].values[i], df_res['p_Aromaticity'].values[i],
                               df_res['p_Strand.Fraction'].values[i],
                               df_res['p_Coil.Fraction'].values[i], df_res['p_Gravy'].values[i],
                               df_res['p_Aliphatic.Index'].values[i], df_res['p_GRAVY.Last.50'].values[i],
                               df_res['p_A_Percent'].values[i], df_res['p_G_Percent'].values[i],
                               df_res['p_H_Percent'].values[i], df_res['p_F_Percent'].values[i],
                               df_res['p_T_Percent'].values[i], df_res['p_W_Percent'].values[i],
                               df_res['p_Y_Percent'].values[i], df_res['p_V_Percent'].values[i], 1,
                               protein_to_numerical(text_input)]
                    clear_catche()
                    lgbm = joblib.load('lgbm_hla.pkl')
                    lgbm_hla.append(lgbm.predict([hla_inp])[0])
                    print("The LGBM prediction ", lgbm.predict([hla_inp])[0])

                    hist = joblib.load('hist_hla.pkl')
                    hist_hla.append(hist.predict([hla_inp])[0])
                    print("The Hist_prediction ", hist.predict([hla_inp])[0])

                score_df = pd.DataFrame({
                    "start": start_val,
                    "end": end_val,
                    "Epitope": epitopes,
                    "XGB_predicted_score": xg_boost,
                    "KOLASKAR_SCORE": lgbm_score,
                    "Extra_tree_Target": extra_trees_pred,
                    "bagging_Target": bagging_pred,
                    "Random_forest_Target": random_forest_pred,
                    "lgbm_hla": lgbm_hla,
                    "hist_hla": hist_hla
                })

                score_df.to_csv("final_output.csv")
                score = pd.read_csv('final_output.csv')
                st.header("The Machine Learning Classifier results")
                st.write(score)
                csv_dt = convert_df_to_csv(score)
                csv_lnk = create_download_link(csv_dt, "ML_Classification_output.csv", "text/csv")
                st.markdown(csv_lnk, unsafe_allow_html=True)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['subject'] = "Thank you for using our tool"
                body = f"The Machine Learning Classifier results for mhc-2 of {protein_sequence}"
                msg.attach(MIMEText(body, 'html'))
                filename = 'final_output.csv'
                attachment = open(filename, 'rb')
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                msg.attach(p)
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.send_message(msg)
                server.quit()
                st.header('Email sent')


                print(score['Random_forest_Target'].values)
                print(score['Extra_tree_Target'].values)
                count_ones = score[['Extra_tree_Target', 'Random_forest_Target', 'bagging_Target']].sum(axis=1)
                score['Target'] = (count_ones > 2).astype(int)
                score.to_csv('target_final.csv')
                df_final = pd.read_csv('target_final.csv')
                df = df_final['lgbm_hla']

                amino_acid_values = {
                    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5,
                    'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
                    'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15,
                    'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20,
                    'U': 21, 'V': 22, 'W': 23, 'X': 24, 'Y': 25, 'Z': 26
                }

                def calculate_numerical_score(hla):
                    hla = str(hla)
                    alleles = hla.split('/')
                    total_score = 0
                    for allele in alleles:
                        amino_acid_sequence = ''.join(char for char in allele if char.isalpha())
                        numeric_parts = ''.join(char for char in allele if char.isdigit())
                        for amino_acid in amino_acid_sequence:
                            total_score += amino_acid_values.get(amino_acid, 0)
                        if numeric_parts:
                            total_score += float(numeric_parts)
                    return total_score

                def find_nearest_hla(total_score, hla_strings, k=10):
                    nearest_hla_list = []
                    hla_strings_sorted = sorted(hla_strings,
                                                key=lambda hla: abs(calculate_numerical_score(hla) - total_score))
                    for hla in hla_strings_sorted[:k]:
                        nearest_hla_list.append(hla)
                    return nearest_hla_list

                data = pd.read_csv('hla.csv')
                hla_output = []
                pred = []
                hla_strings = [str(hla) for hla in data['HLA'].values]
                for i in range(len(df_final)):
                    nearest_hla_list = find_nearest_hla(df_final['lgbm_hla'].values[i], hla_strings, k=5)
                    print("10 Nearest HLA Strings:")
                    for i, hla in enumerate(nearest_hla_list, start=1):
                        print(hla)
                        pred.append(hla)
                        if len(pred) == 5:
                            hla_output.append(set(pred))
                            pred = []
                df_final['hla_values'] = hla_output
                df_final.to_csv("expected.csv")
                df_d3 = pd.read_csv("expected.csv")
                target = df_d3[['Extra_tree_Target', 'Random_forest_Target','bagging_Target']].sum(axis=1)
                print('---------------------------------------------')
                print(target)
                df_d3['Target'] = (target >=2).astype(int)
                print(df_d3.Target)
                print('-------------------------------------------------------')
                df_tar = df_d3[df_d3['Target'] == 1]
                if len(df_tar.Target.values) <= 30:
                    df_tar.to_csv('target.csv')
                    df_tab = pd.read_csv('target.csv')
                    print(df_tab.columns)
                    col = ['start', 'end', 'Epitope', 'hla_values', 'KOLASKAR_SCORE']
                    df_tab[col].to_csv("final_epitope.csv")
                    st.header('Final Predicted Cancer Epitopes')
                    st.write("ANALYSIS COMPLETED")
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg['subject'] = "THANK YOU FOR USING OUR TOOL"
                    body = f"THIS IS FINAL CSV FILE WITH FINAL PREDICTED EPITOPES of mhc-2 of {protein_sequence}"
                    msg.attach(MIMEText(body, 'html'))
                    filename = 'final_epitope.csv'
                    attachment = open(filename, 'rb')
                    p = MIMEBase('application', 'octet-stream')
                    p.set_payload((attachment).read())
                    encoders.encode_base64(p)
                    p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                    msg.attach(p)
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(sender_email, password)
                    text = msg.as_string()
                    server.send_message(msg)
                    server.quit()
                    st.header('Email sent')

                    st.dataframe(df_tab[col])
                    csv_d = convert_df_to_csv(df_tab[col])
                    c_lnk = create_download_link(csv_d, "final_epitopes.csv", "text/csv")
                    st.markdown(c_lnk, unsafe_allow_html=True)

                else:
                    values = df_d3['KOLASKAR_SCORE'].sort_values(ascending=False).values
                    val = []
                    for i in range(len(values)):
                        val.append(values[i])
                        if len(val) == 30:
                            break
                    epitope = []
                    hla = []
                    starts = []
                    ends = []
                    score = []
                    for i in val:
                        df_val = df_d3[df_d3['KOLASKAR_SCORE'] == i]
                        epitope.append(df_val.Epitope)
                        hla.append(set(df_val.hla_values))
                        starts.append(df_val.start)
                        ends.append(df_val.end)
                        score.append(df_val.KOLASKAR_SCORE)

                    data_dict = {
                        'Epitope': epitope,
                        'HLA': hla,
                        'Start': starts,
                        'End': ends,
                        'Kolaskar_score': score
                    }
                    df_l = pd.DataFrame(data_dict)
                    df_l = df_l.explode('Epitope').explode('HLA').explode('Start').explode('End').explode(
                        'Kolaskar_score')
                    df_l.reset_index(drop=True, inplace=True)
                    print(df)
                    st.header('Final Predicted Cancer Epitopes')
                    st.write("ANALYSIS COMPLETED")
                    df_l.to_csv("final_epi.csv")
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg['subject'] = "Thank you for using our tool "
                    body = f"FINAL CSV FILE WITH FINAL PREDICTED EPITOPES of mhc-2 of  {protein_sequence}"
                    msg.attach(MIMEText(body, 'html'))
                    filename = 'final_epi.csv'
                    attachment = open(filename, 'rb')
                    p = MIMEBase('application', 'octet-stream')
                    p.set_payload((attachment).read())
                    encoders.encode_base64(p)
                    p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                    msg.attach(p)
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(sender_email, password)
                    text = msg.as_string()
                    server.send_message(msg)
                    server.quit()
                    st.header('Email sent')
                    st.dataframe(df_l)
                    df_csv = convert_df_to_csv(df_l)
                    c_d_l = create_download_link(df_csv, 'final_epitopes.csv', "text/csv")
                    st.markdown(c_d_l, unsafe_allow_html=True)

                clear_catche()
            elif prediction_option == 'BOTH' and text_input:
                status_text = st.empty()
                for i in range(6):
                    time.sleep(9)
                    status_text.text(f'****⏳Analysis Initiated:***')
                    st.write(f"[{i + 1}] ", text1[i])

                protein_sequence = text_input

                def find_epitopes(sequence, window_size=10):
                    epitopes = []
                    start = []
                    end = []
                    for i in range(len(sequence) - window_size + 1):
                        epitope = sequence[i:i + window_size]
                        epitopes.append(epitope)
                        start.append(i)
                        end.append(i + window_size - 1)
                    return (epitopes, start, end)

                def is_valid_protein_sequence(peptide_sequence):
                    valid_letters = set("ACDEFGHIKLMNPQRSTVWY")
                    return set(peptide_sequence) <= valid_letters

                def calculate_atom_counts(peptide_sequence):
                    atom_counts = {'H': 0, 'C': 0, 'N': 0, 'O': 0, 'S': 0}
                    aa_info = {
                        'A': [5, 3, 1, 1, 0], 'R': [17, 6, 4, 2, 0], 'N': [8, 4, 2, 2, 0], 'D': [7, 4, 1, 3, 0],
                        'C': [7, 3, 1, 1, 1], 'E': [9, 5, 1, 3, 0], 'Q': [10, 5, 2, 2, 0], 'G': [3, 2, 1, 1, 0],
                        'H': [11, 6, 3, 2, 0], 'I': [11, 6, 1, 2, 0], 'L': [11, 6, 1, 2, 0], 'K': [14, 6, 2, 2, 0],
                        'M': [11, 5, 1, 2, 1], 'F': [11, 9, 1, 1, 0], 'P': [9, 5, 1, 1, 0], 'S': [9, 3, 1, 2, 0],
                        'T': [11, 4, 1, 2, 0], 'W': [14, 11, 2, 1, 0], 'Y': [12, 6, 1, 3, 0], 'V': [9, 5, 1, 1, 0]
                    }
                    for aa in peptide_sequence:
                        aa = aa.upper()
                        if aa in aa_info:
                            atom_counts['H'] += aa_info[aa][0]
                            atom_counts['C'] += aa_info[aa][1]
                            atom_counts['N'] += aa_info[aa][2]
                            atom_counts['O'] += aa_info[aa][3]
                            atom_counts['S'] += aa_info[aa][4]

                    return atom_counts

                def calculate_physicochemical_properties(peptide_sequence):
                    if not is_valid_protein_sequence(peptide_sequence):
                        return [None] * 35
                    protein_analyzer = ProteinAnalysis(peptide_sequence)
                    theoretical_pI = protein_analyzer.isoelectric_point()
                    aliphatic_index = sum(kd[aa] for aa in peptide_sequence) / len(peptide_sequence)
                    positive_residues = sum(peptide_sequence.count(aa) for aa in ['R', 'K', 'H'])
                    negative_residues = sum(peptide_sequence.count(aa) for aa in ['D', 'E'])
                    aromatic_count = protein_analyzer.aromaticity() * len(peptide_sequence)
                    polar_amino_acids = set("STNQ")
                    non_polar_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
                    polar_count = sum(peptide_sequence.count(aa) for aa in polar_amino_acids)
                    nonpolar_count = sum(peptide_sequence.count(aa) for aa in non_polar_amino_acids)
                    amino_acid_composition = protein_analyzer.get_amino_acids_percent()
                    molecular_weight = protein_analyzer.molecular_weight()
                    instability_index = protein_analyzer.instability_index()
                    aromaticity = protein_analyzer.aromaticity()
                    helix_fraction = protein_analyzer.secondary_structure_fraction()[0]
                    strand_fraction = protein_analyzer.secondary_structure_fraction()[1]
                    coil_fraction = protein_analyzer.secondary_structure_fraction()[2]
                    charge_at_pH_7 = protein_analyzer.charge_at_pH(7.0)
                    gravy = protein_analyzer.gravy()
                    amphipathicity = calculate_amphipathicity(peptide_sequence)
                    gravy_last_50 = protein_analyzer.gravy()
                    molar_extinction_coefficient = protein_analyzer.molar_extinction_coefficient()

                    return [theoretical_pI, aliphatic_index, positive_residues, negative_residues, aromatic_count,
                            polar_count, nonpolar_count, amino_acid_composition, molecular_weight, instability_index,
                            aromaticity, helix_fraction, strand_fraction, coil_fraction, charge_at_pH_7, gravy,
                            amphipathicity,
                            gravy_last_50, molar_extinction_coefficient]

                def calculate_amphipathicity(peptide_sequence):
                    hydrophobic_moment_scale = kd
                    hydrophobic_moment = sum(hydrophobic_moment_scale[aa] for aa in peptide_sequence)
                    mean_hydrophobicity = hydrophobic_moment / len(peptide_sequence)
                    return hydrophobic_moment - mean_hydrophobicity

                def process_single_protein(peptide_sequence, start, end):
                    atom_counts = calculate_atom_counts(peptide_sequence)
                    physicochemical_properties = calculate_physicochemical_properties(peptide_sequence)
                    total_atoms = sum(atom_counts.values())

                    result_dict = {'epitope': peptide_sequence,
                                   'start': start,
                                   'end': end,
                                   'H_Count': atom_counts['H'],
                                   'C_Count': atom_counts['C'],
                                   'N_Count': atom_counts['N'],
                                   'O_Count': atom_counts['O'],
                                   'S_Count': atom_counts['S'],
                                   'TotalAtoms_Count': total_atoms}

                    result_dict.update({
                        'Theoretical.pI': physicochemical_properties[0],
                        'Aliphatic.Index': physicochemical_properties[1],
                        'Positive.Residues': physicochemical_properties[2],
                        'Negative.Residues': physicochemical_properties[3],
                        'Aromatic.Count': physicochemical_properties[4],
                        'Polar.Count': physicochemical_properties[5],
                        'Nonpolar.Count': physicochemical_properties[6]
                    })

                    amino_acids = ['A', 'R', 'N', 'D', 'C', 'E', 'Q', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T',
                                   'W',
                                   'Y', 'V']
                    for i, aa in enumerate(amino_acids):
                        result_dict[aa + '_Percent'] = physicochemical_properties[7].get(aa, 0)

                    result_dict.update({
                        'Molecular.Weight': physicochemical_properties[8],
                        'Instability.Index': physicochemical_properties[9],
                        'Aromaticity': physicochemical_properties[10],
                        'Helix.Fraction': physicochemical_properties[11],
                        'Strand.Fraction': physicochemical_properties[12],
                        'Coil.Fraction': physicochemical_properties[13],
                        'Charge.at.pH.7.0': physicochemical_properties[14],
                        'Gravy': physicochemical_properties[15],
                        'Amphipathicity': physicochemical_properties[16],
                        'GRAVY.Last.50': physicochemical_properties[17],
                        'Molar.Extinction.Coefficient': physicochemical_properties[18]
                    })

                    return result_dict

                def p_is_valid_protein_sequence(protein_sequence):
                    p_valid_letters = set("ACDEFGHIKLMNPQRSTVWY")
                    return set(protein_sequence) <= p_valid_letters

                def p_calculate_atom_counts(protein_sequence):
                    p_atom_counts = {'H': 0, 'C': 0, 'N': 0, 'O': 0, 'S': 0}
                    p_aa_info = {
                        'A': [5, 3, 1, 1, 0], 'R': [17, 6, 4, 2, 0], 'N': [8, 4, 2, 2, 0], 'D': [7, 4, 1, 3, 0],
                        'C': [7, 3, 1, 1, 1], 'E': [9, 5, 1, 3, 0], 'Q': [10, 5, 2, 2, 0], 'G': [3, 2, 1, 1, 0],
                        'H': [11, 6, 3, 2, 0], 'I': [11, 6, 1, 2, 0], 'L': [11, 6, 1, 2, 0], 'K': [14, 6, 2, 2, 0],
                        'M': [11, 5, 1, 2, 1], 'F': [11, 9, 1, 1, 0], 'P': [9, 5, 1, 1, 0], 'S': [9, 3, 1, 2, 0],
                        'T': [11, 4, 1, 2, 0], 'W': [14, 11, 2, 1, 0], 'Y': [12, 6, 1, 3, 0], 'V': [9, 5, 1, 1, 0]
                    }

                    for aa in protein_sequence:
                        aa = aa.upper()
                        if aa in p_aa_info:
                            p_atom_counts['H'] += p_aa_info[aa][0]
                            p_atom_counts['C'] += p_aa_info[aa][1]
                            p_atom_counts['N'] += p_aa_info[aa][2]
                            p_atom_counts['O'] += p_aa_info[aa][3]
                            p_atom_counts['S'] += p_aa_info[aa][4]


                    return p_atom_counts

                clear_catche()

                def p_calculate_physicochemical_properties(protein_sequence):
                    if not p_is_valid_protein_sequence(protein_sequence):
                        return [None] * 35

                    p_protein_analyzer = ProteinAnalysis(protein_sequence)

                    p_theoretical_pI = p_protein_analyzer.isoelectric_point()
                    p_aliphatic_index = sum(kd[aa] for aa in protein_sequence) / len(protein_sequence)
                    p_positive_residues = sum(protein_sequence.count(aa) for aa in ['R', 'K', 'H'])
                    p_negative_residues = sum(protein_sequence.count(aa) for aa in ['D', 'E'])
                    p_aromatic_count = p_protein_analyzer.aromaticity() * len(protein_sequence)
                    p_polar_amino_acids = set("STNQ")
                    p_non_polar_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
                    p_polar_count = sum(protein_sequence.count(aa) for aa in p_polar_amino_acids)
                    p_nonpolar_count = sum(protein_sequence.count(aa) for aa in p_non_polar_amino_acids)
                    p_amino_acid_composition = p_protein_analyzer.get_amino_acids_percent()
                    p_molecular_weight = p_protein_analyzer.molecular_weight()
                    p_instability_index = p_protein_analyzer.instability_index()
                    p_aromaticity = p_protein_analyzer.aromaticity()
                    p_helix_fraction = p_protein_analyzer.secondary_structure_fraction()[0]
                    p_strand_fraction = p_protein_analyzer.secondary_structure_fraction()[1]
                    p_coil_fraction = p_protein_analyzer.secondary_structure_fraction()[2]
                    p_charge_at_pH_7 = p_protein_analyzer.charge_at_pH(7.0)
                    p_gravy = p_protein_analyzer.gravy()
                    p_amphipathicity = p_calculate_amphipathicity(protein_sequence)
                    p_gravy_last_50 = p_protein_analyzer.gravy()
                    p_molar_extinction_coefficient = p_protein_analyzer.molar_extinction_coefficient()

                    return [p_theoretical_pI, p_aliphatic_index, p_positive_residues, p_negative_residues,
                            p_aromatic_count,
                            p_polar_count, p_nonpolar_count, p_amino_acid_composition, p_molecular_weight,
                            p_instability_index,
                            p_aromaticity, p_helix_fraction, p_strand_fraction, p_coil_fraction, p_charge_at_pH_7,
                            p_gravy,
                            p_amphipathicity,
                            p_gravy_last_50, p_molar_extinction_coefficient]

                def p_calculate_amphipathicity(protein_sequence):
                    p_hydrophobic_moment_scale = kd
                    p_hydrophobic_moment = sum(p_hydrophobic_moment_scale[aa] for aa in protein_sequence)
                    p_mean_hydrophobicity = p_hydrophobic_moment / len(protein_sequence)
                    return p_hydrophobic_moment - p_mean_hydrophobicity

                def p_process_single_protein(protein_sequence):
                    p_atom_counts = p_calculate_atom_counts(protein_sequence)
                    p_physicochemical_properties = p_calculate_physicochemical_properties(protein_sequence)
                    p_total_atoms = sum(p_atom_counts.values())

                    p_result_dict = {'p_Sequence': protein_sequence,
                                     'p_H_Count': p_atom_counts['H'],
                                     'p_C_Count': p_atom_counts['C'],
                                     'p_N_Count': p_atom_counts['N'],
                                     'p_O_Count': p_atom_counts['O'],
                                     'p_S_Count': p_atom_counts['S'],
                                     'p_TotalAtoms_Count': p_total_atoms}

                    p_result_dict.update({
                        'p_Theoretical.pI': p_physicochemical_properties[0],
                        'p_Aliphatic.Index': p_physicochemical_properties[1],
                        'p_Positive.Residues': p_physicochemical_properties[2],
                        'p_Negative.Residues': p_physicochemical_properties[3],
                        'p_Aromatic.Count': p_physicochemical_properties[4],
                        'p_Polar.Count': p_physicochemical_properties[5],
                        'p_Nonpolar.Count': p_physicochemical_properties[6]
                    })

                    amino_acids = ['A', 'R', 'N', 'D', 'C', 'E', 'Q', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T',
                                   'W', 'Y', 'V']
                    for i, aa in enumerate(amino_acids):
                        p_result_dict['p_' + aa + '_Percent'] = p_physicochemical_properties[7].get(aa, 0)

                    p_result_dict.update({
                        'p_Molecular.Weight': p_physicochemical_properties[8],
                        'p_Instability.Index': p_physicochemical_properties[9],
                        'p_Aromaticity': p_physicochemical_properties[10],
                        'p_Helix.Fraction': p_physicochemical_properties[11],
                        'p_Strand.Fraction': p_physicochemical_properties[12],
                        'p_Coil.Fraction': p_physicochemical_properties[13],
                        'p_Charge.at.pH.7.0': p_physicochemical_properties[14],
                        'p_Gravy': p_physicochemical_properties[15],
                        'p_Amphipathicity': p_physicochemical_properties[16],
                        'p_GRAVY.Last.50': p_physicochemical_properties[17],
                        'p_Molar.Extinction.Coefficient': p_physicochemical_properties[18]
                    })

                    return p_result_dict

                r_result = p_process_single_protein(protein_sequence)
                epitopes = find_epitopes(protein_sequence, window_size=10)
                epi = []
                for i in range(len(epitopes[0])):
                    result = process_single_protein(epitopes[0][i], epitopes[1][i], epitopes[2][i])
                    epi.append(result)

                df = pd.DataFrame(epi)
                file_name = 'epitopes_results.csv'
                df.to_csv(file_name)
                df_d = pd.read_csv(file_name)
                st.header("The epitope information")
                st.dataframe(df_d)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['subject'] = "Thank you for using our tool"
                body = f"The epitope  results for mhc-1 of {protein_sequence}"
                msg.attach(MIMEText(body, 'html'))
                filename = 'epitopes_results.csv'
                attachment = open(filename, 'rb')
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                msg.attach(p)
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.send_message(msg)
                server.quit()
                st.header('Email sent')


                csv_dt = convert_df_to_csv(df_d)
                csv_lnk = create_download_link(csv_dt, "Epitope_information.csv", "text/csv")
                st.markdown(csv_lnk, unsafe_allow_html=True)

                pro = []
                for i in range(len(epi)):
                    r_result = p_process_single_protein(protein_sequence)
                    pro.append(r_result)

                df_p = pd.DataFrame(pro)
                file_name = 'p_Sequence.csv'
                df_p.to_csv(file_name)
                df_d1 = pd.read_csv(file_name)
                st.header("The Protein sequence information")
                st.dataframe(df_d1)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['subject'] = "Thank you for using our tool"
                body = f"The P_Sequence results for mhc-1 of {protein_sequence}"
                msg.attach(MIMEText(body, 'html'))
                filename = 'p_Sequence.csv'
                attachment = open(filename, 'rb')
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                msg.attach(p)
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.send_message(msg)
                server.quit()
                st.header('Email sent')


                csv_dt = convert_df_to_csv(df_d1)
                csv_lnk = create_download_link(csv_dt, "Protein_Sequence_information.csv", "text/csv")
                st.markdown(csv_lnk, unsafe_allow_html=True)

                df1 = pd.read_csv('epitopes_results.csv')
                df2 = pd.read_csv('p_Sequence.csv')
                merged_df = pd.merge(df1, df2, how='inner')
                merged_df.to_csv('result.csv', index=False)
                print("Merged CSV file has been created.")

                final_res = pd.read_csv('result.csv')

                inps = ['start', 'end', 'R_Percent', 'D_Percent', 'Q_Percent', 'H_Percent',
                        'I_Percent', 'L_Percent',
                        'K_Percent', 'S_Percent', 'Theoretical.pI',
                        'Aliphatic.Index', 'Helix.Fraction', 'Charge.at.pH.7.0', 'Amphipathicity',
                        'p_Molecular.Weight', 'p_Instability.Index', 'p_Helix.Fraction',
                        'p_Amphipathicity', 'p_Aliphatic.Index',
                        'p_H_Count', 'p_C_Count', 'p_N_Count',
                        'p_O_Count', 'p_S_Count', 'p_TotalAtoms_Count',
                        'p_A_Percent',
                        'p_D_Percent',
                        'p_E_Percent', 'p_G_Percent',
                        'p_I_Percent', 'p_K_Percent',
                        'p_F_Percent', 'p_T_Percent',
                        'p_V_Percent',
                        ]

                clear_catche()

                columns_to_extract = [final_res[j].values[:len(final_res)] for j in inps]
                columns_data = dict(zip(inps, columns_to_extract))
                columns_df = pd.DataFrame(columns_data)
                columns_df.to_csv('extracted_columns.csv')
                bagging_pred = []
                extra_trees_pred = []
                random_forest_pred = []
                df = pd.read_csv('extracted_columns.csv')
                print(df.columns)

                for i in range(len(df)):
                    print(df.end.values[i])
                    print(
                        '-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f'FOR THE {final_res.epitope[i]} the value if 1-> epitope and o-> non-epitope')
                    print(
                        '------------------------------------------------------------------------------------------------------------')

                    inp = [df.start.values[i], df.end.values[i], df.R_Percent.values[i], df.D_Percent.values[i],
                           df.Q_Percent.values[i], df.H_Percent.values[i],
                           df.I_Percent.values[i], df.L_Percent.values[i], df.K_Percent.values[i],
                           df.S_Percent.values[i], df['Theoretical.pI'].values[i], df['Aliphatic.Index'].values[i],
                           df['Helix.Fraction'].values[i], df['Charge.at.pH.7.0'].values[i],
                           df['Amphipathicity'].values[i],
                           df['p_Molecular.Weight'].values[i], df['p_Instability.Index'].values[i],
                           df['p_Helix.Fraction'].values[i],
                           df['p_Amphipathicity'].values[i], df['p_Aliphatic.Index'].values[i],
                           df['p_H_Count'].values[i],
                           df['p_C_Count'].values[i], df['p_N_Count'].values[i], df['p_O_Count'].values[i],
                           df['p_S_Count'].values[i], df['p_TotalAtoms_Count'].values[i], df['p_A_Percent'].values[i],
                           df['p_D_Percent'].values[i], df['p_E_Percent'].values[i], df['p_G_Percent'].values[i],
                           df['p_I_Percent'].values[i], df['p_K_Percent'].values[i], df['p_F_Percent'].values[i],
                           df['p_T_Percent'].values[i], df['p_V_Percent'].values[i]]

                    bagging = joblib.load('Bagging_tar_mhc1.pkl')
                    pred_bag = bagging.predict([inp])
                    bagging_pred.append(pred_bag[0])
                    print("The prediction using Bagging ", pred_bag)

                    extratree = joblib.load('extratree_tar_mhc1.pkl')
                    predict = extratree.predict([inp])
                    extra_trees_pred.append(predict[0])
                    print("The extra tree prediction ", predict)

                    randomfor = joblib.load('randomforest_tar_mhc1.pkl')
                    random_pred = randomfor.predict([inp])
                    random_forest_pred.append(random_pred[0])
                    print("The random forest ", random_pred)

                df = pd.read_csv('result.csv')
                print(df.columns)
                epitopes = []
                xg_boost = []
                lgbm_score = []
                start_val = []
                end_val = []

                for i in range(len(df)):
                    print('-------------------------------------------')
                    epitopes.append(df.epitope.values[i])
                    start_val.append(df.start.values[i])
                    end_val.append(df.end.values[i])
                    print("---------------------------------------------")
                    print(df.epitope.values[i])

                    print('---------------------------------------------')
                    score_inp = [df.start.values[i], df.end.values[i],
                                 df['A_Percent'].values[i], df['R_Percent'].values[i],
                                 df['N_Percent'].values[i], df['D_Percent'].values[i],
                                 df['C_Percent'].values[i], df['E_Percent'].values[i],
                                 df['Q_Percent'].values[i], df['G_Percent'].values[i], df['H_Percent'].values[i],
                                 df['I_Percent'].values[i], df['L_Percent'].values[i], df['K_Percent'].values[i],
                                 df['M_Percent'].values[i], df['F_Percent'].values[i], df['P_Percent'].values[i],
                                 df['S_Percent'].values[i], df['T_Percent'].values[i], df['W_Percent'].values[i],
                                 df['Y_Percent'].values[i], df['V_Percent'].values[i],
                                 df['H_Count'].values[i], df['C_Count'].values[i], df['N_Count'].values[i],
                                 df['S_Count'].values[i],
                                 df['TotalAtoms_Count'].values[i],
                                 df['Theoretical.pI'].values[i], df['Aliphatic.Index'].values[i],
                                 df['Positive.Residues'].values[i], df['Negative.Residues'].values[i],
                                 df['Aromatic.Count'].values[i], df['Polar.Count'].values[i],
                                 df['Nonpolar.Count'].values[i], df['Molecular.Weight'].values[i],
                                 df['Instability.Index'].values[i], df['Aromaticity'].values[i],
                                 df['Helix.Fraction'].values[i], df['Strand.Fraction'].values[i],
                                 df['Coil.Fraction'].values[i],
                                 df['Charge.at.pH.7.0'].values[i], df['Amphipathicity'].values[i],
                                 df['GRAVY.Last.50'].values[i],
                                 df['p_Instability.Index'].values[i], df['p_Helix.Fraction'].values[i],
                                 df['p_Strand.Fraction'].values[i], df['p_Coil.Fraction'].values[i],
                                 df['p_Charge.at.pH.7.0'].values[i],
                                 df['p_Amphipathicity'].values[i], df['p_Aliphatic.Index'].values[i],
                                 df['p_Aromatic.Count'].values[i], df['p_Nonpolar.Count'].values[i],
                                 df['p_H_Count'].values[i],
                                 df['p_C_Count'].values[i], df['p_O_Count'].values[i],
                                 df['p_TotalAtoms_Count'].values[i],
                                 df['p_R_Percent'].values[i],
                                 df['p_N_Percent'].values[i], df['p_D_Percent'].values[i],
                                 df['p_E_Percent'].values[i],
                                 df['p_L_Percent'].values[i],
                                 df['p_T_Percent'].values[i], df['p_W_Percent'].values[i]]

                    xgb = joblib.load('xgb_score_mhc1.pkl')
                    xgb_pred = xgb.predict([score_inp])
                    print("The xgb_pred ", xgb_pred)
                    xg_boost.append(xgb_pred[0])

                    lgb = joblib.load('lgb_score_mhc1.pkl')
                    lgbm_prediction = lgb.predict([score_inp])
                    lgbm_score.append(lgbm_prediction[0])
                    print('The lgbm prediction ', lgbm_prediction)

                kolaskar_df = pd.DataFrame({
                    "start": start_val,
                    "end": end_val,
                    "Epitope": epitopes,
                    "XGB_predicted_score": xg_boost,
                    "KOLASKAR_SCORE": lgbm_score,
                    "Extra_tree_Target": extra_trees_pred,
                    "bagging_Target": bagging_pred,
                    "Random_forest_Target": random_forest_pred,
                })
                clear_catche()

                kolaskar_df.to_csv('kolaskar.csv')
                df_kolaskar = pd.read_csv("kolaskar.csv")

                def protein_to_numerical(sequence):
                    if isinstance(sequence, str):
                        aa_hydrophobicity = {
                            'A': 1.8, 'C': 2.5, 'D': -3.5, 'E': -3.5, 'F': 2.8,
                            'G': -0.4, 'H': -3.2, 'I': 4.5, 'K': -3.9, 'L': 3.8,
                            'M': 1.9, 'N': -3.5, 'P': -1.6, 'Q': -3.5, 'R': -4.5,
                            'S': -0.8, 'T': -0.7, 'V': 4.2, 'W': -0.9, 'Y': -1.3
                        }
                        numerical_seq = [aa_hydrophobicity.get(aa, 0.5) for aa in
                                         sequence.upper()]  # Convert to uppercase
                        return sum(numerical_seq) / len(numerical_seq) if len(
                            numerical_seq) > 0 else 0.5  # Handle empty sequences
                    else:
                        raise TypeError("Input must be a string representing a protein sequence.")

                df_res = pd.read_csv('result.csv')
                lgbm_hla = []
                hist_hla = []
                for i in range(len(df_res)):
                    hla_inp = [df_res['A_Percent'].values[i], df_res['R_Percent'].values[i],
                               df_res['N_Percent'].values[i],
                               df_res['D_Percent'].values[i], df_res['Q_Percent'].values[i],
                               df_res['G_Percent'].values[i],
                               df_res['H_Percent'].values[i], df_res['F_Percent'].values[i],
                               df_res['S_Percent'].values[i],
                               df_res['T_Percent'].values[i], df_res['H_Count'].values[i], df_res['C_Count'].values[i],
                               df_res['N_Count'].values[i], df_res['O_Count'].values[i],
                               df_res['TotalAtoms_Count'].values[i],
                               df_res['Theoretical.pI'].values[i], df_res['Positive.Residues'].values[i],
                               df_res['Negative.Residues'].values[i], df_res['Aromatic.Count'].values[i],
                               df_res['Polar.Count'].values[i], df_res['Nonpolar.Count'].values[i],
                               df_res['Molecular.Weight'].values[i],
                               df_res['Helix.Fraction'].values[i], df_res['Strand.Fraction'].values[i],
                               df_res['Charge.at.pH.7.0'].values[i], df_res['p_Aromaticity'].values[i],
                               df_res['p_Strand.Fraction'].values[i],
                               df_res['p_Coil.Fraction'].values[i], df_res['p_Gravy'].values[i],
                               df_res['p_Aliphatic.Index'].values[i], df_res['p_GRAVY.Last.50'].values[i],
                               df_res['p_A_Percent'].values[i], df_res['p_G_Percent'].values[i],
                               df_res['p_H_Percent'].values[i], df_res['p_F_Percent'].values[i],
                               df_res['p_T_Percent'].values[i], df_res['p_W_Percent'].values[i],
                               df_res['p_Y_Percent'].values[i], df_res['p_V_Percent'].values[i], 0,
                               protein_to_numerical(text_input)]

                    lgbm = joblib.load('lgbm_hla.pkl')
                    lgbm_hla.append(lgbm.predict([hla_inp])[0])
                    print("The LGBM prediction ", lgbm.predict([hla_inp])[0])

                    hist = joblib.load('hist_hla.pkl')
                    hist_hla.append(hist.predict([hla_inp])[0])
                    print("The Hist_prediction ", hist.predict([hla_inp])[0])

                score_df = pd.DataFrame({
                    "start": start_val,
                    "end": end_val,
                    "Epitope": epitopes,
                    "XGB_predicted_score": xg_boost,
                    "KOLASKAR_SCORE": lgbm_score,
                    "Extra_tree_Target": extra_trees_pred,
                    "bagging_Target": bagging_pred,
                    "Random_forest_Target": random_forest_pred,
                    "lgbm_hla": lgbm_hla,
                    "hist_hla": hist_hla
                })

                score_df.to_csv("final_output.csv")
                score = pd.read_csv('final_output.csv')
                st.header("The Machine Learning Classifier results")
                st.dataframe(score)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['subject'] = "Thank you for using our tool"
                body = f"The Machine Learning Classifier results for mhc-1 of {protein_sequence}"
                msg.attach(MIMEText(body, 'html'))
                filename = 'final_output.csv'
                attachment = open(filename, 'rb')
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                msg.attach(p)
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.send_message(msg)
                server.quit()
                st.header('Email sent')

                csv_dt = convert_df_to_csv(score)
                csv_lnk = create_download_link(csv_dt, "ML_Classification_output.csv", "text/csv")
                st.markdown(csv_lnk, unsafe_allow_html=True)

                print(score['Random_forest_Target'].values)
                print(score['Extra_tree_Target'].values)
                count_ones = score[['Extra_tree_Target', 'Random_forest_Target', 'bagging_Target']].sum(axis=1)
                score['Target'] = (count_ones > 2).astype(int)
                score.to_csv('target_final.csv')
                df_final = pd.read_csv('target_final.csv')
                df = df_final['lgbm_hla']

                amino_acid_values = {
                    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5,
                    'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
                    'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15,
                    'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20,
                    'U': 21, 'V': 22, 'W': 23, 'X': 24, 'Y': 25, 'Z': 26
                }

                def calculate_numerical_score(hla):
                    hla = str(hla)
                    alleles = hla.split('/')
                    total_score = 0
                    for allele in alleles:
                        amino_acid_sequence = ''.join(char for char in allele if char.isalpha())
                        numeric_parts = ''.join(char for char in allele if char.isdigit())
                        for amino_acid in amino_acid_sequence:
                            total_score += amino_acid_values.get(amino_acid, 0)
                        if numeric_parts:
                            total_score += float(numeric_parts)
                    return total_score

                def find_nearest_hla(total_score, hla_strings, k=10):
                    nearest_hla_list = []
                    hla_strings_sorted = sorted(hla_strings,
                                                key=lambda hla: abs(calculate_numerical_score(hla) - total_score))
                    for hla in hla_strings_sorted[:k]:
                        nearest_hla_list.append(hla)
                    return nearest_hla_list

                data = pd.read_csv('hla.csv')
                hla_output = []
                pred = []
                hla_strings = [str(hla) for hla in data['HLA'].values]
                for i in range(len(df_final)):
                    nearest_hla_list = find_nearest_hla(df_final['lgbm_hla'].values[i], hla_strings, k=5)
                    print("10 Nearest HLA Strings:")
                    for i, hla in enumerate(nearest_hla_list, start=1):
                        print(hla)
                        pred.append(hla)
                        if len(pred) == 5:
                            hla_output.append(set(pred))
                            pred = []

                df_final['hla_values'] = hla_output
                df_final.to_csv("expected.csv")
                df_d3 = pd.read_csv("expected.csv")
                target = df_d3[['Extra_tree_Target', 'Random_forest_Target','bagging_Target']].sum(axis=1)
                print('---------------------------------------------')
                print(target)
                df_d3['Target'] = (target >=2).astype(int)
                print(df_d3.Target)
                print('-------------------------------------------------------')
                df_tar = df_d3[df_d3['Target'] == 1]
                if len(df_tar.Target.values) <= 30:
                    df_tar.to_csv('target.csv')
                    df_tab = pd.read_csv('target.csv')
                    print(df_tab.columns)
                    col = ['start', 'end', 'Epitope', 'hla_values', 'KOLASKAR_SCORE']
                    st.header('Final Predicted Cancer Epitopes for MHC-1')
                    st.write("ANALYSIS COMPLETED")
                    df_tab[col].to_csv("final_epitopes.csv")
                    st.header("ANALYSIS COMPLETED")
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg['subject'] = "Thank you for using our tool"
                    body = f"FINAL CSV FILE OF FINAL PREDICTED EPITOPES for mhc-1 of {protein_sequence}"
                    msg.attach(MIMEText(body, 'html'))
                    filename = 'final_epitopes.csv'
                    attachment = open(filename, 'rb')
                    p = MIMEBase('application', 'octet-stream')
                    p.set_payload((attachment).read())
                    encoders.encode_base64(p)
                    p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                    msg.attach(p)
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(sender_email, password)
                    text = msg.as_string()
                    server.send_message(msg)
                    server.quit()
                    st.header('Email sent')

                    st.dataframe(df_tab[col])
                    csv_d = convert_df_to_csv(df_tab[col])
                    c_lnk = create_download_link(csv_d, "final_epitopes.csv", "text/csv")
                    st.markdown(c_lnk, unsafe_allow_html=True)

                else:
                    values = df_d3['KOLASKAR_SCORE'].sort_values(ascending=False).values
                    val = []
                    for i in range(len(values)):
                        val.append(values[i])
                        if len(val) == 30:
                            break
                    epitope = []
                    hla = []
                    starts = []
                    ends = []
                    score = []

                    for i in val:
                        df_val = df_d3[df_d3['KOLASKAR_SCORE'] == i]
                        epitope.append(df_val.Epitope)
                        hla.append(set(df_val.hla_values))
                        starts.append(df_val.start)
                        ends.append(df_val.end)
                        score.append(df_val.KOLASKAR_SCORE)

                    data_dict = {
                        'Epitope': epitope,
                        'HLA': hla,
                        'Start': starts,
                        'End': ends,
                        "Kolaskar_score": score
                    }
                    df_1 = pd.DataFrame(data_dict)
                    df_1 = df_1.explode('Epitope').explode('HLA').explode('Start').explode('End').explode(
                        "Kolaskar_score")
                    df_1.reset_index(drop=True, inplace=True)
                    print(df_1)
                    st.header("Final Predicted Cancer Epitopes for MHC-1")
                    st.write("ANALYSIS COMPLETED")
                    st.write(
                        'These final epitopes are generated with at least 2 of the models predicted them as epitopes')
                    st.write("ANALYSIS COMPLETED")
                    st.dataframe(df_1)
                    df_1.to_csv("final_one.csv")

                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg['subject'] = "Thank your for using our tool"
                    body = f"FINAL CSV FILE OF FINALLY PREDICTED EPITOPES for mhc-1 of sequence given {protein_sequence}"
                    msg.attach(MIMEText(body, 'html'))
                    filename = 'final_one.csv'
                    attachment = open(filename, 'rb')
                    p = MIMEBase('application', 'octet-stream')
                    p.set_payload((attachment).read())
                    encoders.encode_base64(p)
                    p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                    msg.attach(p)
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(sender_email, password)
                    text = msg.as_string()
                    server.send_message(msg)
                    server.quit()
                    st.header('Email sent')

                    csv_lk = convert_df_to_csv(df_1)
                    csv_l = create_download_link(csv_lk, 'final_epitopes.csv', "text/csv")
                    st.markdown(csv_l, unsafe_allow_html=True)

                clear_catche()

                status_text = st.empty()
                for i in range(6):
                    time.sleep(9)
                    status_text.text(f'****⏳Analysis Initiated:***')
                    st.write(f"[{i + 1}] ",text2[i])

                protein_sequence = text_input

                def find_epitopes(sequence, window_size=15):
                    epitopes = []
                    start = []
                    end = []
                    for i in range(len(sequence) - window_size + 1):
                        epitope = sequence[i:i + window_size]
                        epitopes.append(epitope)
                        start.append(i)
                        end.append(i + window_size - 1)
                    return (epitopes, start, end)

                def is_valid_protein_sequence(peptide_sequence):
                    valid_letters = set("ACDEFGHIKLMNPQRSTVWY")
                    return set(peptide_sequence) <= valid_letters

                def calculate_atom_counts(peptide_sequence):
                    atom_counts = {'H': 0, 'C': 0, 'N': 0, 'O': 0, 'S': 0}
                    aa_info = {
                        'A': [5, 3, 1, 1, 0], 'R': [17, 6, 4, 2, 0], 'N': [8, 4, 2, 2, 0], 'D': [7, 4, 1, 3, 0],
                        'C': [7, 3, 1, 1, 1], 'E': [9, 5, 1, 3, 0], 'Q': [10, 5, 2, 2, 0], 'G': [3, 2, 1, 1, 0],
                        'H': [11, 6, 3, 2, 0], 'I': [11, 6, 1, 2, 0], 'L': [11, 6, 1, 2, 0], 'K': [14, 6, 2, 2, 0],
                        'M': [11, 5, 1, 2, 1], 'F': [11, 9, 1, 1, 0], 'P': [9, 5, 1, 1, 0], 'S': [9, 3, 1, 2, 0],
                        'T': [11, 4, 1, 2, 0], 'W': [14, 11, 2, 1, 0], 'Y': [12, 6, 1, 3, 0], 'V': [9, 5, 1, 1, 0]
                    }
                    for aa in peptide_sequence:
                        aa = aa.upper()
                        if aa in aa_info:
                            atom_counts['H'] += aa_info[aa][0]
                            atom_counts['C'] += aa_info[aa][1]
                            atom_counts['N'] += aa_info[aa][2]
                            atom_counts['O'] += aa_info[aa][3]
                            atom_counts['S'] += aa_info[aa][4]

                    return atom_counts

                def calculate_physicochemical_properties(peptide_sequence):
                    if not is_valid_protein_sequence(peptide_sequence):
                        return [None] * 35
                    protein_analyzer = ProteinAnalysis(peptide_sequence)
                    theoretical_pI = protein_analyzer.isoelectric_point()
                    aliphatic_index = sum(kd[aa] for aa in peptide_sequence) / len(peptide_sequence)
                    positive_residues = sum(peptide_sequence.count(aa) for aa in ['R', 'K', 'H'])
                    negative_residues = sum(peptide_sequence.count(aa) for aa in ['D', 'E'])
                    aromatic_count = protein_analyzer.aromaticity() * len(peptide_sequence)
                    polar_amino_acids = set("STNQ")
                    non_polar_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
                    polar_count = sum(peptide_sequence.count(aa) for aa in polar_amino_acids)
                    nonpolar_count = sum(peptide_sequence.count(aa) for aa in non_polar_amino_acids)
                    amino_acid_composition = protein_analyzer.get_amino_acids_percent()
                    molecular_weight = protein_analyzer.molecular_weight()
                    instability_index = protein_analyzer.instability_index()
                    aromaticity = protein_analyzer.aromaticity()
                    helix_fraction = protein_analyzer.secondary_structure_fraction()[0]
                    strand_fraction = protein_analyzer.secondary_structure_fraction()[1]
                    coil_fraction = protein_analyzer.secondary_structure_fraction()[2]
                    charge_at_pH_7 = protein_analyzer.charge_at_pH(7.0)
                    gravy = protein_analyzer.gravy()
                    amphipathicity = calculate_amphipathicity(peptide_sequence)
                    gravy_last_50 = protein_analyzer.gravy()
                    molar_extinction_coefficient = protein_analyzer.molar_extinction_coefficient()

                    return [theoretical_pI, aliphatic_index, positive_residues, negative_residues, aromatic_count,
                            polar_count, nonpolar_count, amino_acid_composition, molecular_weight, instability_index,
                            aromaticity, helix_fraction, strand_fraction, coil_fraction, charge_at_pH_7, gravy,
                            amphipathicity,
                            gravy_last_50, molar_extinction_coefficient]

                def calculate_amphipathicity(peptide_sequence):
                    hydrophobic_moment_scale = kd
                    hydrophobic_moment = sum(hydrophobic_moment_scale[aa] for aa in peptide_sequence)
                    mean_hydrophobicity = hydrophobic_moment / len(peptide_sequence)
                    return hydrophobic_moment - mean_hydrophobicity

                def process_single_protein(peptide_sequence, start, end):
                    atom_counts = calculate_atom_counts(peptide_sequence)
                    physicochemical_properties = calculate_physicochemical_properties(peptide_sequence)
                    total_atoms = sum(atom_counts.values())

                    result_dict = {'epitope': peptide_sequence,
                                   'start': start,
                                   'end': end,
                                   'H_Count': atom_counts['H'],
                                   'C_Count': atom_counts['C'],
                                   'N_Count': atom_counts['N'],
                                   'O_Count': atom_counts['O'],
                                   'S_Count': atom_counts['S'],
                                   'TotalAtoms_Count': total_atoms}

                    result_dict.update({
                        'Theoretical.pI': physicochemical_properties[0],
                        'Aliphatic.Index': physicochemical_properties[1],
                        'Positive.Residues': physicochemical_properties[2],
                        'Negative.Residues': physicochemical_properties[3],
                        'Aromatic.Count': physicochemical_properties[4],
                        'Polar.Count': physicochemical_properties[5],
                        'Nonpolar.Count': physicochemical_properties[6]
                    })

                    amino_acids = ['A', 'R', 'N', 'D', 'C', 'E', 'Q', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T',
                                   'W',
                                   'Y', 'V']
                    for i, aa in enumerate(amino_acids):
                        result_dict[aa + '_Percent'] = physicochemical_properties[7].get(aa, 0)

                    result_dict.update({
                        'Molecular.Weight': physicochemical_properties[8],
                        'Instability.Index': physicochemical_properties[9],
                        'Aromaticity': physicochemical_properties[10],
                        'Helix.Fraction': physicochemical_properties[11],
                        'Strand.Fraction': physicochemical_properties[12],
                        'Coil.Fraction': physicochemical_properties[13],
                        'Charge.at.pH.7.0': physicochemical_properties[14],
                        'Gravy': physicochemical_properties[15],
                        'Amphipathicity': physicochemical_properties[16],
                        'GRAVY.Last.50': physicochemical_properties[17],
                        'Molar.Extinction.Coefficient': physicochemical_properties[18]
                    })

                    return result_dict

                def p_is_valid_protein_sequence(protein_sequence):
                    p_valid_letters = set("ACDEFGHIKLMNPQRSTVWY")
                    return set(protein_sequence) <= p_valid_letters

                def p_calculate_atom_counts(protein_sequence):
                    p_atom_counts = {'H': 0, 'C': 0, 'N': 0, 'O': 0, 'S': 0}
                    p_aa_info = {
                        'A': [5, 3, 1, 1, 0], 'R': [17, 6, 4, 2, 0], 'N': [8, 4, 2, 2, 0], 'D': [7, 4, 1, 3, 0],
                        'C': [7, 3, 1, 1, 1], 'E': [9, 5, 1, 3, 0], 'Q': [10, 5, 2, 2, 0], 'G': [3, 2, 1, 1, 0],
                        'H': [11, 6, 3, 2, 0], 'I': [11, 6, 1, 2, 0], 'L': [11, 6, 1, 2, 0], 'K': [14, 6, 2, 2, 0],
                        'M': [11, 5, 1, 2, 1], 'F': [11, 9, 1, 1, 0], 'P': [9, 5, 1, 1, 0], 'S': [9, 3, 1, 2, 0],
                        'T': [11, 4, 1, 2, 0], 'W': [14, 11, 2, 1, 0], 'Y': [12, 6, 1, 3, 0], 'V': [9, 5, 1, 1, 0]
                    }

                    for aa in protein_sequence:
                        aa = aa.upper()
                        if aa in p_aa_info:
                            p_atom_counts['H'] += p_aa_info[aa][0]
                            p_atom_counts['C'] += p_aa_info[aa][1]
                            p_atom_counts['N'] += p_aa_info[aa][2]
                            p_atom_counts['O'] += p_aa_info[aa][3]
                            p_atom_counts['S'] += p_aa_info[aa][4]

                    return p_atom_counts

                def p_calculate_physicochemical_properties(protein_sequence):
                    if not p_is_valid_protein_sequence(protein_sequence):
                        return [None] * 35

                    p_protein_analyzer = ProteinAnalysis(protein_sequence)

                    p_theoretical_pI = p_protein_analyzer.isoelectric_point()
                    p_aliphatic_index = sum(kd[aa] for aa in protein_sequence) / len(protein_sequence)
                    p_positive_residues = sum(protein_sequence.count(aa) for aa in ['R', 'K', 'H'])
                    p_negative_residues = sum(protein_sequence.count(aa) for aa in ['D', 'E'])
                    p_aromatic_count = p_protein_analyzer.aromaticity() * len(protein_sequence)
                    p_polar_amino_acids = set("STNQ")
                    p_non_polar_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
                    p_polar_count = sum(protein_sequence.count(aa) for aa in p_polar_amino_acids)
                    p_nonpolar_count = sum(protein_sequence.count(aa) for aa in p_non_polar_amino_acids)
                    p_amino_acid_composition = p_protein_analyzer.get_amino_acids_percent()
                    p_molecular_weight = p_protein_analyzer.molecular_weight()
                    p_instability_index = p_protein_analyzer.instability_index()
                    p_aromaticity = p_protein_analyzer.aromaticity()
                    p_helix_fraction = p_protein_analyzer.secondary_structure_fraction()[0]
                    p_strand_fraction = p_protein_analyzer.secondary_structure_fraction()[1]
                    p_coil_fraction = p_protein_analyzer.secondary_structure_fraction()[2]
                    p_charge_at_pH_7 = p_protein_analyzer.charge_at_pH(7.0)
                    p_gravy = p_protein_analyzer.gravy()
                    p_amphipathicity = p_calculate_amphipathicity(protein_sequence)
                    p_gravy_last_50 = p_protein_analyzer.gravy()
                    p_molar_extinction_coefficient = p_protein_analyzer.molar_extinction_coefficient()

                    return [p_theoretical_pI, p_aliphatic_index, p_positive_residues, p_negative_residues,
                            p_aromatic_count,
                            p_polar_count, p_nonpolar_count, p_amino_acid_composition, p_molecular_weight,
                            p_instability_index,
                            p_aromaticity, p_helix_fraction, p_strand_fraction, p_coil_fraction, p_charge_at_pH_7,
                            p_gravy,
                            p_amphipathicity,
                            p_gravy_last_50, p_molar_extinction_coefficient]

                clear_catche()

                def p_calculate_amphipathicity(protein_sequence):
                    p_hydrophobic_moment_scale = kd
                    p_hydrophobic_moment = sum(p_hydrophobic_moment_scale[aa] for aa in protein_sequence)
                    p_mean_hydrophobicity = p_hydrophobic_moment / len(protein_sequence)
                    return p_hydrophobic_moment - p_mean_hydrophobicity

                def p_process_single_protein(protein_sequence):
                    p_atom_counts = p_calculate_atom_counts(protein_sequence)
                    p_physicochemical_properties = p_calculate_physicochemical_properties(protein_sequence)
                    p_total_atoms = sum(p_atom_counts.values())

                    p_result_dict = {'p_Sequence': protein_sequence,
                                     'p_H_Count': p_atom_counts['H'],
                                     'p_C_Count': p_atom_counts['C'],
                                     'p_N_Count': p_atom_counts['N'],
                                     'p_O_Count': p_atom_counts['O'],
                                     'p_S_Count': p_atom_counts['S'],
                                     'p_TotalAtoms_Count': p_total_atoms}

                    p_result_dict.update({
                        'p_Theoretical.pI': p_physicochemical_properties[0],
                        'p_Aliphatic.Index': p_physicochemical_properties[1],
                        'p_Positive.Residues': p_physicochemical_properties[2],
                        'p_Negative.Residues': p_physicochemical_properties[3],
                        'p_Aromatic.Count': p_physicochemical_properties[4],
                        'p_Polar.Count': p_physicochemical_properties[5],
                        'p_Nonpolar.Count': p_physicochemical_properties[6]
                    })

                    amino_acids = ['A', 'R', 'N', 'D', 'C', 'E', 'Q', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T',
                                   'W', 'Y', 'V']
                    for i, aa in enumerate(amino_acids):
                        p_result_dict['p_' + aa + '_Percent'] = p_physicochemical_properties[7].get(aa, 0)

                    p_result_dict.update({
                        'p_Molecular.Weight': p_physicochemical_properties[8],
                        'p_Instability.Index': p_physicochemical_properties[9],
                        'p_Aromaticity': p_physicochemical_properties[10],
                        'p_Helix.Fraction': p_physicochemical_properties[11],
                        'p_Strand.Fraction': p_physicochemical_properties[12],
                        'p_Coil.Fraction': p_physicochemical_properties[13],
                        'p_Charge.at.pH.7.0': p_physicochemical_properties[14],
                        'p_Gravy': p_physicochemical_properties[15],
                        'p_Amphipathicity': p_physicochemical_properties[16],
                        'p_GRAVY.Last.50': p_physicochemical_properties[17],
                        'p_Molar.Extinction.Coefficient': p_physicochemical_properties[18]
                    })

                    return p_result_dict

                r_result = p_process_single_protein(protein_sequence)
                epitopes = find_epitopes(protein_sequence, window_size=15)
                epi = []
                for i in range(len(epitopes[0])):
                    result = process_single_protein(epitopes[0][i], epitopes[1][i], epitopes[2][i])
                    epi.append(result)

                df = pd.DataFrame(epi)
                file_name = 'epitopes_results.csv'
                df.to_csv(file_name)
                df_d = pd.read_csv(file_name)
                st.header("The epitope information")
                st.dataframe(df_d)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['subject'] = "Thank you for using our tool"
                body = f"The epitope results for mhc-2 of {protein_sequence}"
                msg.attach(MIMEText(body, 'html'))
                filename = 'epitopes_results.csv'
                attachment = open(filename, 'rb')
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                msg.attach(p)
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.send_message(msg)
                server.quit()
                st.header('Email sent')


                csv_dt = convert_df_to_csv(df_d)
                csv_lnk = create_download_link(csv_dt, "Epitope_information.csv", "text/csv")
                st.markdown(csv_lnk, unsafe_allow_html=True)

                pro = []
                for i in range(len(epi)):
                    r_result = p_process_single_protein(protein_sequence)
                    pro.append(r_result)

                df_p = pd.DataFrame(pro)
                file_name = 'p_Sequence.csv'
                df_p.to_csv(file_name)
                df_d1 = pd.read_csv(file_name)
                st.header("The Protein sequence information")
                st.dataframe(df_d1)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['subject'] = "Thank you for using our tool"
                body = f"The p_sequence results for mhc-1 of {protein_sequence}"
                msg.attach(MIMEText(body, 'html'))
                filename = 'p_Sequence.csv'
                attachment = open(filename, 'rb')
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                msg.attach(p)
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.send_message(msg)
                server.quit()
                st.header('Email sent')


                csv_dt = convert_df_to_csv(df_d1)
                csv_lnk = create_download_link(csv_dt, "Protein_sequence_information.csv", "text/csv")
                st.markdown(csv_lnk, unsafe_allow_html=True)

                df1 = pd.read_csv('epitopes_results.csv')
                df2 = pd.read_csv('p_Sequence.csv')
                merged_df = pd.merge(df1, df2, how='inner')
                merged_df.to_csv('result.csv', index=False)
                print("Merged CSV file has been created.")

                final_res = pd.read_csv('result.csv')

                inps = ['start', 'end', 'R_Percent', 'D_Percent', 'Q_Percent', 'H_Percent',
                        'I_Percent', 'L_Percent',
                        'K_Percent', 'S_Percent', 'Theoretical.pI',
                        'Aliphatic.Index', 'Helix.Fraction', 'Charge.at.pH.7.0', 'Amphipathicity',
                        'p_Molecular.Weight', 'p_Instability.Index', 'p_Helix.Fraction',
                        'p_Amphipathicity', 'p_Aliphatic.Index',
                        'p_H_Count', 'p_C_Count', 'p_N_Count',
                        'p_O_Count', 'p_S_Count', 'p_TotalAtoms_Count',
                        'p_A_Percent',
                        'p_D_Percent',
                        'p_E_Percent', 'p_G_Percent',
                        'p_I_Percent', 'p_K_Percent',
                        'p_F_Percent', 'p_T_Percent',
                        'p_V_Percent',
                        ]
                columns_to_extract = [final_res[j].values[:len(final_res)] for j in inps]
                columns_data = dict(zip(inps, columns_to_extract))
                columns_df = pd.DataFrame(columns_data)
                columns_df.to_csv('extracted_columns.csv')
                bagging_pred = []
                extra_trees_pred = []
                random_forest_pred = []
                df = pd.read_csv('extracted_columns.csv')
                print(df.columns)

                for i in range(len(df)):
                    print(df.end.values[i])
                    print(
                        '-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                    print(f'FOR THE {final_res.epitope[i]} the value if 1-> epitope and o-> non-epitope')
                    print(
                        '------------------------------------------------------------------------------------------------------------')

                    inp = [df.start.values[i], df.end.values[i], df.R_Percent.values[i], df.D_Percent.values[i],
                           df.Q_Percent.values[i], df.H_Percent.values[i],
                           df.I_Percent.values[i], df.L_Percent.values[i], df.K_Percent.values[i],
                           df.S_Percent.values[i], df['Theoretical.pI'].values[i], df['Aliphatic.Index'].values[i],
                           df['Helix.Fraction'].values[i], df['Charge.at.pH.7.0'].values[i],
                           df['Amphipathicity'].values[i],
                           df['p_Molecular.Weight'].values[i], df['p_Instability.Index'].values[i],
                           df['p_Helix.Fraction'].values[i],
                           df['p_Amphipathicity'].values[i], df['p_Aliphatic.Index'].values[i],
                           df['p_H_Count'].values[i],
                           df['p_C_Count'].values[i], df['p_N_Count'].values[i], df['p_O_Count'].values[i],
                           df['p_S_Count'].values[i], df['p_TotalAtoms_Count'].values[i], df['p_A_Percent'].values[i],
                           df['p_D_Percent'].values[i], df['p_E_Percent'].values[i], df['p_G_Percent'].values[i],
                           df['p_I_Percent'].values[i], df['p_K_Percent'].values[i], df['p_F_Percent'].values[i],
                           df['p_T_Percent'].values[i], df['p_V_Percent'].values[i]]

                    bagging = joblib.load('Bagging_tar_mhc1.pkl')
                    pred_bag = bagging.predict([inp])
                    bagging_pred.append(pred_bag[0])
                    print("The prediction using Bagging ", pred_bag)

                    extratree = joblib.load('extratree_tar_mhc1.pkl')
                    predict = extratree.predict([inp])
                    extra_trees_pred.append(predict[0])
                    print("The extra tree prediction ", predict)

                    randomfor = joblib.load('randomforest_tar_mhc1.pkl')
                    random_pred = randomfor.predict([inp])
                    random_forest_pred.append(random_pred[0])
                    print("The random forest ", random_pred)

                df = pd.read_csv('result.csv')
                print(df.columns)
                epitopes = []
                xg_boost = []
                lgbm_score = []
                start_val = []
                end_val = []

                clear_catche()

                for i in range(len(df)):
                    print('-------------------------------------------')
                    epitopes.append(df.epitope.values[i])
                    start_val.append(df.start.values[i])
                    end_val.append(df.end.values[i])
                    print("---------------------------------------------")
                    print(df.epitope.values[i])

                    print('---------------------------------------------')
                    score_inp = [df.start.values[i], df.end.values[i],
                                 df['A_Percent'].values[i], df['R_Percent'].values[i],
                                 df['N_Percent'].values[i], df['D_Percent'].values[i],
                                 df['C_Percent'].values[i], df['E_Percent'].values[i],
                                 df['Q_Percent'].values[i], df['G_Percent'].values[i], df['H_Percent'].values[i],
                                 df['I_Percent'].values[i], df['L_Percent'].values[i], df['K_Percent'].values[i],
                                 df['M_Percent'].values[i], df['F_Percent'].values[i], df['P_Percent'].values[i],
                                 df['S_Percent'].values[i], df['T_Percent'].values[i], df['W_Percent'].values[i],
                                 df['Y_Percent'].values[i], df['V_Percent'].values[i],
                                 df['H_Count'].values[i], df['C_Count'].values[i], df['N_Count'].values[i],
                                 df['S_Count'].values[i],
                                 df['TotalAtoms_Count'].values[i],
                                 df['Theoretical.pI'].values[i], df['Aliphatic.Index'].values[i],
                                 df['Positive.Residues'].values[i], df['Negative.Residues'].values[i],
                                 df['Aromatic.Count'].values[i], df['Polar.Count'].values[i],
                                 df['Nonpolar.Count'].values[i], df['Molecular.Weight'].values[i],
                                 df['Instability.Index'].values[i], df['Aromaticity'].values[i],
                                 df['Helix.Fraction'].values[i], df['Strand.Fraction'].values[i],
                                 df['Coil.Fraction'].values[i],
                                 df['Charge.at.pH.7.0'].values[i], df['Amphipathicity'].values[i],
                                 df['GRAVY.Last.50'].values[i],
                                 df['p_Instability.Index'].values[i], df['p_Helix.Fraction'].values[i],
                                 df['p_Strand.Fraction'].values[i], df['p_Coil.Fraction'].values[i],
                                 df['p_Charge.at.pH.7.0'].values[i],
                                 df['p_Amphipathicity'].values[i], df['p_Aliphatic.Index'].values[i],
                                 df['p_Aromatic.Count'].values[i], df['p_Nonpolar.Count'].values[i],
                                 df['p_H_Count'].values[i],
                                 df['p_C_Count'].values[i], df['p_O_Count'].values[i],
                                 df['p_TotalAtoms_Count'].values[i],
                                 df['p_R_Percent'].values[i],
                                 df['p_N_Percent'].values[i], df['p_D_Percent'].values[i],
                                 df['p_E_Percent'].values[i],
                                 df['p_L_Percent'].values[i],
                                 df['p_T_Percent'].values[i], df['p_W_Percent'].values[i]]

                    xgb = joblib.load('xgb_score_mhc1.pkl')
                    xgb_pred = xgb.predict([score_inp])
                    print("The xgb_pred ", xgb_pred)
                    xg_boost.append(xgb_pred[0])

                    lgb = joblib.load('lgb_score_mhc1.pkl')
                    lgbm_prediction = lgb.predict([score_inp])
                    lgbm_score.append(lgbm_prediction[0])
                    print('The lgbm prediction ', lgbm_prediction)

                kolaskar_df = pd.DataFrame({
                    "start": start_val,
                    "end": end_val,
                    "Epitope": epitopes,
                    "XGB_predicted_score": xg_boost,
                    "KOLASKAR_SCORE": lgbm_score,
                    "Extra_tree_Target": extra_trees_pred,
                    "bagging_Target": bagging_pred,
                    "Random_forest_Target": random_forest_pred,
                })

                kolaskar_df.to_csv('kolaskar.csv')
                df_kolaskar = pd.read_csv("kolaskar.csv")

                def protein_to_numerical(sequence):
                    if isinstance(sequence, str):
                        aa_hydrophobicity = {
                            'A': 1.8, 'C': 2.5, 'D': -3.5, 'E': -3.5, 'F': 2.8,
                            'G': -0.4, 'H': -3.2, 'I': 4.5, 'K': -3.9, 'L': 3.8,
                            'M': 1.9, 'N': -3.5, 'P': -1.6, 'Q': -3.5, 'R': -4.5,
                            'S': -0.8, 'T': -0.7, 'V': 4.2, 'W': -0.9, 'Y': -1.3
                        }
                        numerical_seq = [aa_hydrophobicity.get(aa, 0.5) for aa in
                                         sequence.upper()]  # Convert to uppercase
                        return sum(numerical_seq) / len(numerical_seq) if len(
                            numerical_seq) > 0 else 0.5  # Handle empty sequences
                    else:
                        raise TypeError("Input must be a string representing a protein sequence.")

                df_res = pd.read_csv('result.csv')
                lgbm_hla = []
                hist_hla = []
                for i in range(len(df_res)):
                    hla_inp = [df_res['A_Percent'].values[i], df_res['R_Percent'].values[i],
                               df_res['N_Percent'].values[i],
                               df_res['D_Percent'].values[i], df_res['Q_Percent'].values[i],
                               df_res['G_Percent'].values[i],
                               df_res['H_Percent'].values[i], df_res['F_Percent'].values[i],
                               df_res['S_Percent'].values[i],
                               df_res['T_Percent'].values[i], df_res['H_Count'].values[i], df_res['C_Count'].values[i],
                               df_res['N_Count'].values[i], df_res['O_Count'].values[i],
                               df_res['TotalAtoms_Count'].values[i],
                               df_res['Theoretical.pI'].values[i], df_res['Positive.Residues'].values[i],
                               df_res['Negative.Residues'].values[i], df_res['Aromatic.Count'].values[i],
                               df_res['Polar.Count'].values[i], df_res['Nonpolar.Count'].values[i],
                               df_res['Molecular.Weight'].values[i],
                               df_res['Helix.Fraction'].values[i], df_res['Strand.Fraction'].values[i],
                               df_res['Charge.at.pH.7.0'].values[i], df_res['p_Aromaticity'].values[i],
                               df_res['p_Strand.Fraction'].values[i],
                               df_res['p_Coil.Fraction'].values[i], df_res['p_Gravy'].values[i],
                               df_res['p_Aliphatic.Index'].values[i], df_res['p_GRAVY.Last.50'].values[i],
                               df_res['p_A_Percent'].values[i], df_res['p_G_Percent'].values[i],
                               df_res['p_H_Percent'].values[i], df_res['p_F_Percent'].values[i],
                               df_res['p_T_Percent'].values[i], df_res['p_W_Percent'].values[i],
                               df_res['p_Y_Percent'].values[i], df_res['p_V_Percent'].values[i], 1,
                               protein_to_numerical(text_input)]

                    lgbm = joblib.load('lgbm_hla.pkl')
                    lgbm_hla.append(lgbm.predict([hla_inp])[0])
                    print("The LGBM prediction ", lgbm.predict([hla_inp])[0])

                    hist = joblib.load('hist_hla.pkl')
                    hist_hla.append(hist.predict([hla_inp])[0])
                    print("The Hist_prediction ", hist.predict([hla_inp])[0])

                score_df = pd.DataFrame({
                    "start": start_val,
                    "end": end_val,
                    "Epitope": epitopes,
                    "XGB_predicted_score": xg_boost,
                    "KOLASKAR_SCORE": lgbm_score,
                    "Extra_tree_Target": extra_trees_pred,
                    "bagging_Target": bagging_pred,
                    "Random_forest_Target": random_forest_pred,
                    "lgbm_hla": lgbm_hla,
                    "hist_hla": hist_hla
                })

                score_df.to_csv("final_output.csv")
                score = pd.read_csv('final_output.csv')
                st.header("Machine Learning Classifier Results")
                st.dataframe(score)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['subject'] = "Thank you for using our tool"
                body = f"The Machine Learning Classifier results for mhc-2 of {protein_sequence}"
                msg.attach(MIMEText(body, 'html'))
                filename = 'final_output.csv'
                attachment = open(filename, 'rb')
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                msg.attach(p)
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.send_message(msg)
                server.quit()
                st.header('Email sent')

                csv_dt = convert_df_to_csv(score)
                csv_lnk = create_download_link(csv_dt, "ML_Classification_output.csv", "text/csv")
                st.markdown(csv_lnk, unsafe_allow_html=True)

                print(score['Random_forest_Target'].values)
                print(score['Extra_tree_Target'].values)
                count_ones = score[['Extra_tree_Target', 'Random_forest_Target', 'bagging_Target']].sum(axis=1)
                score['Target'] = (count_ones > 2).astype(int)
                score.to_csv('target_final.csv')
                df_final = pd.read_csv('target_final.csv')
                df = df_final['lgbm_hla']

                amino_acid_values = {
                    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5,
                    'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
                    'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15,
                    'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20,
                    'U': 21, 'V': 22, 'W': 23, 'X': 24, 'Y': 25, 'Z': 26
                }

                def calculate_numerical_score(hla):
                    hla = str(hla)
                    alleles = hla.split('/')
                    total_score = 0
                    for allele in alleles:
                        amino_acid_sequence = ''.join(char for char in allele if char.isalpha())
                        numeric_parts = ''.join(char for char in allele if char.isdigit())
                        for amino_acid in amino_acid_sequence:
                            total_score += amino_acid_values.get(amino_acid, 0)
                        if numeric_parts:
                            total_score += float(numeric_parts)
                    return total_score
                clear_catche()

                def find_nearest_hla(total_score, hla_strings, k=10):
                    nearest_hla_list = []
                    hla_strings_sorted = sorted(hla_strings,
                                                key=lambda hla: abs(calculate_numerical_score(hla) - total_score))
                    for hla in hla_strings_sorted[:k]:
                        nearest_hla_list.append(hla)
                    return nearest_hla_list

                data = pd.read_csv('hla.csv')
                hla_output = []
                pred = []
                hla_strings = [str(hla) for hla in data['HLA'].values]
                for i in range(len(df_final)):
                    nearest_hla_list = find_nearest_hla(df_final['lgbm_hla'].values[i], hla_strings, k=5)
                    print("10 Nearest HLA Strings:")
                    for i, hla in enumerate(nearest_hla_list, start=1):
                        print(hla)
                        pred.append(hla)
                        if len(pred) == 5:
                            hla_output.append(set(pred))
                            pred = []

                df_final['hla_values'] = hla_output
                df_final.to_csv("expected.csv")
                df_d3 = pd.read_csv("expected.csv")
                target = df_d3[['Extra_tree_Target', 'Random_forest_Target','bagging_Target']].sum(axis=1)
                print('---------------------------------------------')
                print(target)
                df_d3['Target'] = (target >=2 ).astype(int)
                print(df_d3.Target)
                print('-------------------------------------------------------')
                df_tar = df_d3[df_d3['Target'] == 1]
                if len(df_tar.Target.values) <= 30:
                    df_tar.to_csv('target.csv')
                    df_tab = pd.read_csv('target.csv')
                    print(df_tab.columns)
                    col = ['start', 'end', 'Epitope', 'hla_values', 'KOLASKAR_SCORE']
                    st.header("Final Predicted Cancer Epitopes for MHC-2")
                    st.write("ANALYSIS COMPLETED")
                    df_tab[col].to_csv("final_epitopes.csv")
                    st.header("ANALYSIS COMPLETED")
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg['subject'] = "Thank you for using our tool"
                    body = f"FINAL CSV FILE OF FINAL PREDICTED EPITOPES for mhc-2 of {protein_sequence}"
                    msg.attach(MIMEText(body, 'html'))
                    filename = 'final_epitopes.csv'
                    attachment = open(filename, 'rb')
                    p = MIMEBase('application', 'octet-stream')
                    p.set_payload((attachment).read())
                    encoders.encode_base64(p)
                    p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                    msg.attach(p)
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(sender_email, password)
                    text = msg.as_string()
                    server.send_message(msg)
                    server.quit()
                    st.header('Email sent')

                    st.dataframe(df_tab[col])
                    csv_dt = convert_df_to_csv(df_tab[col])
                    csv_lnk = create_download_link(csv_dt, "final_epitopes.csv", "text/csv")
                    st.markdown(csv_lnk, unsafe_allow_html=True)

                else:
                    values = df_d3['KOLASKAR_SCORE'].sort_values(ascending=False).values
                    val = []
                    for i in range(len(values)):
                        val.append(values[i])
                        if len(val) == 30:
                            break
                    epitope = []
                    hla = []
                    starts = []
                    ends = []
                    score = []
                    for i in val:
                        df_val = df_d3[df_d3['KOLASKAR_SCORE'] == i]
                        epitope.append(df_val.Epitope)
                        hla.append(set(df_val.hla_values))
                        starts.append(df_val.start)
                        ends.append(df_val.end)
                        score.append(df_val.KOLASKAR_SCORE)

                    data_dict = {
                        'Epitope': epitope,
                        'HLA': hla,
                        'Start': starts,
                        'End': ends,
                        "kolaskar_score": score,
                    }
                    df_l = pd.DataFrame(data_dict)
                    df_l = df_l.explode('Epitope').explode('HLA').explode('Start').explode('End').explode(
                        'kolaskar_score')
                    df_l.reset_index(drop=True, inplace=True)
                    print(df)
                    clear_catche()
                    st.header("Final Predicted Cancer Epitopes for MHC-2")
                    st.write('These final epitopes are generated with at least 2 of the models predicted them as epitopes')
                    st.write("ANALYSIS COMPLETED")
                    st.dataframe(df_l)

                    df_l.to_csv("final_epi.csv")
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg['subject'] = "Thank your for using our tool"
                    body = f"FINAL CSV FILE OF FINALLY PREDICTED EPITOPES for mhc-2 of sequence given {protein_sequence}"
                    msg.attach(MIMEText(body, 'html'))
                    filename = 'final_epi.csv'
                    attachment = open(filename, 'rb')
                    p = MIMEBase('application', 'octet-stream')
                    p.set_payload((attachment).read())
                    encoders.encode_base64(p)
                    p.add_header('Content-disposition', 'attachment; filename= %s' % filename)
                    msg.attach(p)
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(sender_email, password)
                    text = msg.as_string()
                    server.send_message(msg)
                    server.quit()
                    st.header('Email sent')

                    csv_data = convert_df_to_csv(df_l)
                    csv_link = create_download_link(csv_data, "final_epitopes.csv", "text/csv")
                    st.markdown(csv_link, unsafe_allow_html=True)


    elif page == "About":
        st.title("About Us")
        st.write("""
    ## Motivation
    In the quest to enhance cancer immunotherapy, epitope prediction plays a pivotal role in identifying potential targets for vaccine development. In this study, we present an integrated pipeline comprising three distinct models aimed at epitope prediction and prioritization for cancer immunotherapy. 

    ## Contact Information
    If you have any questions or feedback, please feel free to reach out to us:
    - Email: genomicsinsights@gmail.com


    ##  Cite
   
    Dhanushkumar T, Sunila BG, Sripad Rama Hebbar, Prasanna Kumar Selvam, Karthick Vasudevan. VaxOptiML: Leveraging Machine Learning for Accurate Prediction of MHC-I & II Epitopes for Optimized Cancer Immunotherapy. bioRxiv. 2024 Jun 12:2024-06.
    """)

    # Help page content
    elif page == "Help":
        st.title("Help & Support")
        st.write("""
    ## Getting Started
    To get started with this app, follow these steps:
    Inputs Requirements:
    1. Tumor antigen Protein sequence   
    2. Specify the type of MHC requirement (MHC-1 or MHC-2 or both)
    3. The given protein sequence will be chunked into peptides (probable epitopes) and feature of those peptides will be generated.
    4. The input protein sequence features will be extracted and results will be generated
    5. For more information refer https://github.com/Genomicsinsights/VaxOptiML/blob/main/README.md

    ## Standalone package 
    Please follow the steps below to use our standalone package. 
     """)
        st.image("standalone.png", width=700)
   

if __name__ == "__main__":
    main()

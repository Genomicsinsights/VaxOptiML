VaxOptiML

    Authors-list
  Sripad Rama Hebbar, Dhanushkumar T, Sunila BG,  Karthick Vasudevan*


    Synopsis 

Our integrated pipeline employs three models for epitope prediction in cancer immunotherapy. Through advanced machine learning techniques and curated datasets, we accurately predict epitopes, personalize HLA pairing, and prioritize targets based on immunogenicity. Rigorous evaluation showcases superior performance over existing approaches, with visual representations emphasizing our ensemble model's efficacy in expediting epitope discovery and vaccine design for cancer immunotherapy. 

    The code works by the mentioned below steps  

Input protein will be chunked, and features of those peptides will be generated.

- Peptides will be divided into epitopes and non-epitopes based on 0 and 1 annotations.
- Antigenic scores will be generated for those peptides.
- HLAs of those peptides will be generated.
- Finally, based on the antigenic score and epitope nature, final probable epitopes will be generated along with starting and ending positions.





      Getting started
  
 <img width="763" alt="Screenshot 2024-06-26 151021" src="https://github.com/danukumar111999/VaxOptiML/assets/172895426/a1e793ce-372f-416a-8602-1f0bf10b3acd">






Inputs Requirements:
1. Tumour antigen Protein sequence
2. Specify the type of MHC requirement
   

        Preliminary Outputs:
![Screenshot 2024-05-09 135205](https://github.com/sripad2020/aaa/assets/59697056/bbe98dba-cc77-46ce-82a2-e3c21baca954)


The given protein sequence will be chunked into peptides (probable epitopes)  and feature of those peptides will be generated.


![Screenshot 2024-05-09 135722](https://github.com/sripad2020/aaa/assets/59697056/d4ee347d-5d37-4364-aa27-fc70f6bcd06e)


The input protein sequence features will be extracted


<img width="551" alt="Screenshot 2024-06-27 121753" src="https://github.com/Genomicsinsights/VaxOptiML/assets/173452018/25b91d9b-eaf0-425c-82c2-6ce951e9ea4a">


The Machine Learning Classifier results for chunked epitopes will be generated 


<img width="475" alt="image" src="https://github.com/danukumar111999/VaxOptiML/assets/172895426/09a69051-805e-473a-8713-8f24cf3addef">


Final  epitope with it's K-T score along the HLA'S it binds will be generated

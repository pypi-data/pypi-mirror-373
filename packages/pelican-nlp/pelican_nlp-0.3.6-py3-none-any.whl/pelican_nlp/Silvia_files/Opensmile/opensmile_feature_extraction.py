import csv
import os
from typing import List

import audiofile
import opensmile
import glob

audio_dir = "C:\\Users\\Acer\\Documents\\Silvia\\UMC_Language and schizophrenia\\Research assistant\\Projects\\Language and sex hormones\\P009"
files: List[str] = glob.glob('C:\\Users\\Acer\\Documents\\Silvia\\UMC_Language and schizophrenia\\PhD\\Projects\\Interns\\Language and sex hormones\\P009\\*.wav')


#extract whole audiofile
#if wish to be shortended, fill in argument 'duration'
results = []
for file in files:
    print(file)
    storage = {}
    signal, sampling_rate = audiofile.read(
        file,
        always_2d=True,
        #duration=
        #offset=
    )

#extract eGeMAPSv02 feature set
    smile = opensmile.Smile(
        feature_set=opensmile.FeatureSet.eGeMAPSv02,
        feature_level=opensmile.FeatureLevel.Functionals,
    )

    ##print(smile.feature_names)


    output = smile.process_signal(
        signal,
        sampling_rate
    )
    print(output)

#save output
    storage['p_nr'] = file[0:4]
    for feature in smile.feature_names:
        storage[feature] = output[feature]

    results.append(storage)

csv_columns = results[0].keys()
csv_file = "C:\\Users\\Acer\\Documents\\Silvia\\UMC_Language and schizophrenia\\Research assistant\\Projects\\Language and sex hormones\\Opensmile_results.csv"

with open(csv_file, 'w', newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(csv_columns)
    for i in range (len(results)): #iterate over particpants' results
        data = results[i]
        new_array = []
        for t in data: #iterate all features in participants' results
            if t == 'p_nr': #in first column, insert particpant number
                new_array.append(files[i].split(os.sep)[-1]) #filesplit takes only participant number (and not the whole path) #append inserts data in the empty array
            else: #for all other columns insert feature value
                new_array.append(float(data[t]))
        writer.writerow(new_array)





#!/usr/bin/env python3

from masster.sample import Sample

# test file 
test_file = "massistant/data/examples/2025_01_14_VW_7600_LpMx_DBS_CID_2min_TOP15_030msecMS1_005msecReac_CE35_DBS-ON_3.wiff"

# load example file
sample = Sample(test_file)
sample.find_features(chrom_peak_snr=10, noise=500, chrom_fwhm=1.0)
sample.find_adducts()
sample.find_ms2()
# save to h5 and featureXML
sample.save()

test_file2 = test_file.replace(".wiff", ".h5")
sample2 = Sample()
sample2.load(test_file2)

# delete .h5 and .featureXML files
import os

os.remove(test_file2)
os.remove(test_file2.replace(".h5", ".featureXML"))

cd /Users/jjaenes/euler-home/batch-infer/projects/alphafold3-polymer-bonds-tests
delete all

load alphafold3_predictions/1AAR_polybonds/1AAR_polybonds_model.cif.gz
load alphafold3_predictions/1AAR_seqonly/1AAR_seqonly_model.cif.gz
load rcsb/1AAR.pdb1

remove solvent

align 1AAR_polybonds_model, 1AAR
align 1AAR_seqonly_model, 1AAR

set_name 1AAR, 1AAR_polybonds_ref
copy 1AAR_seqonly_ref, 1AAR_polybonds_ref

set grid_mode,1
set grid_slot, 1, 1AAR_polybonds_model
set grid_slot, 1, 1AAR_polybonds_ref
set grid_slot, 2, 1AAR_seqonly_model
set grid_slot, 2, 1AAR_seqonly_ref

color gray
color green, 1AAR_polybonds_model
color blue, 1AAR_seqonly_model

### cut below here and paste into script ###
set_view (\
     0.125071391,   -0.877262235,   -0.463409424,\
     0.940419734,    0.253664643,   -0.226385966,\
     0.316153526,   -0.407496840,    0.856725216,\
     0.000000000,    0.000000000, -151.957122803,\
    18.200216293,    7.735980988,    6.016460419,\
   128.788955688,  175.125289917,  -20.000000000 )
### cut above here and paste into script ###

set ray_opaque_background, 0
png /Users/jjaenes/euler-home/batch-infer/projects/alphafold3-polymer-bonds/examples/visualise/1AAR.png, width=4cm, height=2cm, dpi=600, ray=1

/* Importing data from CSV file */
DATA holes;
    INFILE "C:\Users\micah\OneDrive\Documents\Msstate_grad_project\Polypipe_program\testing_matrix_with_mm.csv" DLM=',' FIRSTOBS=2;
    INPUT TestID :8. Hole_Size_in :8.3 Conventional_Diameter_mm :8.4 Count :8. Measured_Diameter_in :$10. Measured_Diameter_mm :8.4;
RUN;

/* Display the dataset */
proc print data=holes;
run;

/* Clean the data by removing rows with 'Error' or zero values in Measured Diameter (mm) */
data holes_clean;
    set holes;
    if Measured_Diameter_mm = . or Measured_Diameter_mm = 0 then delete;
run;

/* Display the cleaned dataset */
proc print data=holes_clean;
run;

/* Sort the dataset by TestID */
proc sort data=holes_clean;
    by TestID;
run;

/* Perform paired t-tests for each TestID */
proc ttest data=holes_clean;
    by TestID;
    paired Conventional_Diameter_mm Measured_Diameter_mm;
run;

/* Display the final dataset */
proc print data=holes_clean;
run;

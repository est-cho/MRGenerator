# MRGenerator

To execute MRGenerator, initial MR and the field experiment data are required. 
The field experiment data may include the time-series data and the invariants used in the system.
Use the parameters below to specify the files for generator MRs:
- `-i`: initial MR
- `-d`: time-series data, such as the sensor or actuation values
- `-c`: invariatns or constants, such as goal or threshold values

To execute the program, use the command `python main.py` with the parameters described above.

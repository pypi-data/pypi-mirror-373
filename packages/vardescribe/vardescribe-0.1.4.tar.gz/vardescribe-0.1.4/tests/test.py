import numpy as np
import pandas as pd
# from vardescribe import vardescribe

import sys
import os

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from vardescribe.core import vardescribe

my_scalar = 2
my_list = [1, 2, 3, 4, 5]
my_numpy_array = np.array([[1, 2], [3, 4]])
my_dict = {
    "name": "John Doe",
    "age": 30,
    "is_student": False
}
student_data = {
    'student_id': [101, 102, 103, 104, 105],
    'major': ['Computer Science', 'Biology', 'Business', 'Art History', 'Computer Science'],
    'gpa': [3.8, 3.2, 3.5, 3.9, 3.1],
    'credits_earned': [90, 65, 80, 110, 55],
    'is_scholarship': [True, False, True, True, False]
}
my_df = pd.DataFrame(student_data)

#describe variables
vardescribe(my_scalar)
print('\n')
vardescribe(my_list)
print('\n')
vardescribe(my_numpy_array)
print('\n')
vardescribe(my_dict)
print('\n')
vardescribe(my_df)
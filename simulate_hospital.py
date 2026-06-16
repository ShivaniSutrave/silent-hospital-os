import pandas as pd
import numpy as np
import random

np.random.seed(42)

roles = ['Doctor', 'Nurse', 'Patient', 'Receptionist']
locations = ['Room 1', 'Room 2', 'ICU', 'Reception', 'Ward A']
statuses = ['Waiting', 'In Transit', 'Available', 'Busy']

data = []
for i in range(50):
    role = roles[i % 4]
    location = locations[i % 5]
    status = statuses[i % 4]
    data.append({
        'event_id': i + 1,
        'role': role,
        'location': location,
        'status': status,
        'wait_time_mins': i * 2,
        'connected': i % 2 == 0
    })

df = pd.DataFrame(data)
print(df)
df.to_csv('hospital_data.csv', index=False)
print('Done! hospital_data.csv created!')
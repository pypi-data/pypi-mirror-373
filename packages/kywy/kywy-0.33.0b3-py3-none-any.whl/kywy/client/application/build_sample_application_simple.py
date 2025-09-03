import pandas as pd

from ...client.kawa_client import KawaClient
from ...client.kawa_decorators import kawa_tool

from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
from faker import Faker


def kawa():
    k = KawaClient(kawa_api_url='http://localhost:4200')
    k.set_api_key(api_key_file='/Users/emmanuel/doc/local-pristine/.key')
    k.set_active_workspace_id(workspace_id='79')
    return k


from kywy.client.kawa_client import KawaClient
from kywy.client.kawa_decorators import kawa_tool
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
from faker import Faker
from kywy.client.kawa_client import KawaClient
from kywy.client.kawa_decorators import kawa_tool
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
from faker import Faker


app = kawa().app(
    application_name='Potato Monitoring System',
    sidebar_color='#8B4513',
)


## 📝 Applied from patch "INITIAL SCRIPT"

@kawa_tool(
    outputs={'sensor_id': str, 'location': str, 'field_id': str, 'sensor_type': str, 'installation_date': date,
             'status': float}
)
def sensor_data_generator():
    fake = Faker()
    data = []
    sensor_types = ['Soil Moisture', 'Temperature', 'Humidity', 'pH Level', 'Light Sensor', 'Disease Detection']
    locations = ['North Field', 'South Field', 'East Field', 'West Field', 'Storage Facility A', 'Storage Facility B',
                 'Greenhouse 1', 'Greenhouse 2']

    for i in range(150):
        sensor_id = f"sensor{i + 1:03d}"
        location = np.random.choice(locations)
        field_id = f"field{np.random.randint(1, 21):03d}"
        sensor_type = np.random.choice(sensor_types)
        installation_date = fake.date_between(start_date='-2y', end_date='today')
        status = 1.0 if np.random.random() > 0.05 else 0.0  # 95% operational

        data.append([sensor_id, location, field_id, sensor_type, installation_date, status])

    df = pd.DataFrame(data, columns=['sensor_id', 'location', 'field_id', 'sensor_type', 'installation_date', 'status'])
    return df


@kawa_tool(
    outputs={'reading_id': str, 'sensor_id': str, 'timestamp': datetime, 'value': float, 'unit': str,
             'alert_level': str}
)
def sensor_readings_generator():
    fake = Faker()
    data = []

    # Generate readings for 150 sensors over the last 6 months
    for sensor_num in range(1, 151):
        sensor_id = f"sensor{sensor_num:03d}"

        # Generate multiple readings per sensor
        num_readings = np.random.randint(100, 300)

        for j in range(num_readings):
            reading_id = f"read{sensor_num:03d}{j + 1:03d}"
            timestamp = fake.date_time_between(start_date='-6M', end_date='now')

            # Different value ranges based on sensor type (simulated)
            sensor_type_sim = np.random.choice(['moisture', 'temperature', 'humidity', 'ph', 'light', 'disease'])

            if sensor_type_sim == 'moisture':
                value = np.random.normal(45, 15)  # Soil moisture percentage
                unit = 'percentage'
            elif sensor_type_sim == 'temperature':
                value = np.random.normal(18, 8)  # Temperature in Celsius
                unit = 'celsius'
            elif sensor_type_sim == 'humidity':
                value = np.random.normal(65, 20)  # Humidity percentage
                unit = 'percentage'
            elif sensor_type_sim == 'ph':
                value = np.random.normal(6.2, 1.2)  # pH level
                unit = 'ph'
            elif sensor_type_sim == 'light':
                value = np.random.normal(25000, 8000)  # Lux
                unit = 'lux'
            else:  # disease
                value = np.random.choice([0, 1, 2, 3])  # Disease severity index
                unit = 'index'

            # Determine alert level based on value ranges
            if sensor_type_sim == 'moisture' and (value < 20 or value > 80):
                alert_level = 'Critical'
            elif sensor_type_sim == 'temperature' and (value < 5 or value > 35):
                alert_level = 'Critical'
            elif sensor_type_sim == 'humidity' and (value < 30 or value > 90):
                alert_level = 'Warning'
            elif sensor_type_sim == 'ph' and (value < 5.5 or value > 7.5):
                alert_level = 'Warning'
            elif sensor_type_sim == 'disease' and value >= 2:
                alert_level = 'Critical'
            else:
                alert_level = 'Normal'

            data.append([reading_id, sensor_id, timestamp, value, unit, alert_level])

    df = pd.DataFrame(data, columns=['reading_id', 'sensor_id', 'timestamp', 'value', 'unit', 'alert_level'])
    return df


@kawa_tool(
    outputs={'field_id': str, 'field_name': str, 'crop_variety': str, 'planting_date': date, 'expected_harvest': date,
             'area_hectares': float, 'soil_type': str}
)
def potato_fields_generator():
    fake = Faker()
    data = []

    crop_varieties = ['Russet Burbank', 'Yukon Gold', 'Red Pontiac', 'Fingerling', 'Purple Majesty',
                      'German Butterball', 'Kennebec', 'Atlantic']
    soil_types = ['Sandy Loam', 'Clay Loam', 'Silt Loam', 'Sandy', 'Clay', 'Peat']
    field_names = ['Northfield Estate', 'Sunrise Acres', 'Golden Valley', 'Riverside Plot', 'Highland Fields',
                   'Meadowbrook', 'Sunset Ridge', 'Green Pastures', 'Rolling Hills', 'Pine Creek Fields',
                   'Oakwood Plantation', 'Valley View Farm', 'Maple Grove', 'Cedar Point', 'Willow Creek',
                   'Harvest Moon Fields', 'Morning Glory', 'Autumn Acres', 'Silver Lake Farm', 'Copper Hill']

    for i in range(1, 21):
        field_id = f"field{i:03d}"
        field_name = field_names[i - 1]
        crop_variety = np.random.choice(crop_varieties)
        planting_date = fake.date_between(start_date='-8M', end_date='-2M')
        expected_harvest = planting_date + timedelta(days=np.random.randint(90, 150))
        area_hectares = np.random.uniform(2.5, 45.0)
        soil_type = np.random.choice(soil_types)

        data.append([field_id, field_name, crop_variety, planting_date, expected_harvest, area_hectares, soil_type])

    df = pd.DataFrame(data, columns=['field_id', 'field_name', 'crop_variety', 'planting_date', 'expected_harvest',
                                     'area_hectares', 'soil_type'])
    return df


@kawa_tool(
    outputs={'alert_id': str, 'sensor_id': str, 'alert_type': str, 'severity': str, 'timestamp': datetime,
             'resolved': float, 'resolution_time': datetime, 'description': str}
)
def alerts_generator():
    fake = Faker()
    data = []

    alert_types = ['Low Moisture', 'High Temperature', 'Disease Detected', 'pH Imbalance', 'High Humidity',
                   'Sensor Malfunction', 'Low Light', 'Storage Issue']
    severities = ['Low', 'Medium', 'High', 'Critical']

    for i in range(200):
        alert_id = f"alert{i + 1:04d}"
        sensor_id = f"sensor{np.random.randint(1, 151):03d}"
        alert_type = np.random.choice(alert_types)
        severity = np.random.choice(severities)
        timestamp = fake.date_time_between(start_date='-3M', end_date='now')
        resolved = 1.0 if np.random.random() > 0.3 else 0.0  # 70% resolved

        if resolved == 1.0:
            resolution_time = timestamp + timedelta(hours=np.random.randint(1, 48))
        else:
            resolution_time = timestamp  # Not yet resolved

        descriptions = {
            'Low Moisture': 'Soil moisture levels below optimal range for potato growth',
            'High Temperature': 'Temperature exceeding recommended levels for potato cultivation',
            'Disease Detected': 'Potential disease symptoms detected in potato crop',
            'pH Imbalance': 'Soil pH levels outside optimal range for potato growth',
            'High Humidity': 'Humidity levels too high, risk of fungal diseases',
            'Sensor Malfunction': 'Sensor not responding or providing inconsistent readings',
            'Low Light': 'Light levels insufficient for optimal growth',
            'Storage Issue': 'Storage conditions not optimal for potato preservation'
        }

        description = descriptions.get(alert_type, 'General alert condition detected')

        data.append([alert_id, sensor_id, alert_type, severity, timestamp, resolved, resolution_time, description])

    df = pd.DataFrame(data, columns=['alert_id', 'sensor_id', 'alert_type', 'severity', 'timestamp', 'resolved',
                                     'resolution_time', 'description'])
    return df


sensor_dataset = app.create_dataset(
    name='Sensor Network',
    generator=sensor_data_generator,
)

readings_dataset = app.create_dataset(
    name='Sensor Readings',
    generator=sensor_readings_generator,
)

fields_dataset = app.create_dataset(
    name='Potato Fields',
    generator=potato_fields_generator,
)

alerts_dataset = app.create_dataset(
    name='System Alerts',
    generator=alerts_generator,
)

model = app.create_model(
    dataset=readings_dataset,
)

## 📝 Applied from patch "INITIAL SCRIPT"


## 📝 Applied from patch "INITIAL SCRIPT"


## 📝 Applied from patch "patch-2025-08-27T10:21:43.py"


## 📝 Applied from patch "patch-2025-08-27T10:22:29.py"


app.publish()

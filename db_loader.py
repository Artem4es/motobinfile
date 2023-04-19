import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import Item

load_dotenv()

PASSWORD = os.environ('PSGL_PASS')

engine = create_engine(f'postgresql://postgres:{PASSWORD}@localhost/postgres')
Session = sessionmaker(bind=engine)
session = Session()

data = []
with open('files1.csv', 'r') as f:
    for line in f:
        if line == '\n':
            continue
        brand, model, number = line.strip().split(',')
        data.append(
            {
                'brand': brand.strip(),
                'model': model.strip(),
                'number': number.strip(),
                'price': 50,
                'description': 'XDF BIN file definition',
                'details': 'If you need Race features or more details-feel free to contact us via our contact form!',
            }
        )

session.bulk_insert_mappings(Item, data)
session.commit()

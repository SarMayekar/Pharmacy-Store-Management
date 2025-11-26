from app import db, Distributor

# Add the distributor
dist = Distributor(name='DistributorMulti', contact_number='1234567890', trade_type='Retail')
db.session.add(dist)
db.session.commit()
print("Distributor added")

from webapp.app import db

class Property(db.Model):
    compute_id = db.Column(db.Integer, primary_key=True)
    postal_code = db.Column(db.Integer)
    address = db.Column(db.String())
    price = db.Column(db.Float)
    def __repr__(self):
        return '<Address {}>'.format(self.address)
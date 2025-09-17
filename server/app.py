from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET API</h1>'

# POST route for baked_goods
@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    # Get form data from the request
    name = request.form.get('name')
    price = request.form.get('price')
    bakery_id = request.form.get('bakery_id')
    
    # Validate required fields
    if not name or not price or not bakery_id:
        return jsonify({'error': 'Missing required fields: name, price, or bakery_id'}), 400
    
    try:
        # Convert price to float
        price = float(price)
        
        # Create new baked good
        baked_good = BakedGood(
            name=name,
            price=price,
            bakery_id=bakery_id
        )
        
        # Add to database and commit
        db.session.add(baked_good)
        db.session.commit()
        
        # Return the created baked good as JSON with 201 status
        return jsonify(baked_good.to_dict()), 201
        
    except ValueError:
        return jsonify({'error': 'Price must be a valid number'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# PATCH route for bakeries
@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return jsonify({'error': 'Bakery not found'}), 404
    
    # Update the name if provided in form data
    if 'name' in request.form:
        bakery.name = request.form.get('name')
    
    db.session.commit()
    return jsonify(bakery.to_dict())

# DELETE route for baked_goods
@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)
    if not baked_good:
        return jsonify({'error': 'Baked good not found'}), 404
    
    try:
        db.session.delete(baked_good)
        db.session.commit()
        return jsonify({'message': 'Baked good deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# GET all bakeries
@app.route('/bakeries', methods=['GET'])
def get_bakeries():
    bakeries = Bakery.query.all()
    return jsonify([bakery.to_dict() for bakery in bakeries])

# GET bakery by ID
@app.route('/bakeries/<int:id>', methods=['GET'])
def get_bakery(id):
    bakery = Bakery.query.get(id)
    if bakery:
        return jsonify(bakery.to_dict())
    return jsonify({'error': 'Bakery not found'}), 404

# GET all baked goods
@app.route('/baked_goods', methods=['GET'])
def get_baked_goods():
    baked_goods = BakedGood.query.all()
    return jsonify([bg.to_dict() for bg in baked_goods])

# GET baked good by ID
@app.route('/baked_goods/<int:id>', methods=['GET'])
def get_baked_good(id):
    baked_good = BakedGood.query.get(id)
    if baked_good:
        return jsonify(baked_good.to_dict())
    return jsonify({'error': 'Baked good not found'}), 404

if __name__ == '__main__':
    app.run(port=5555, debug=True)
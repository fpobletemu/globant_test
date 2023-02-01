from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost:3306/globantbd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


##Creacion de tabla Categoria
class Categoria(db.Model):
    cat_id = db.Column(db.Integer,primary_key=True)
    cat_nom = db.Column(db.String(100))
    cat_desp = db.Column(db.String(100))

    def __init__(self,cat_nom,cat_desp):
        self.cat_nom = cat_nom
        self.cat_desp = cat_desp


##Creacion de tabla Jobs
class Jobs(db.Model):
    job_id = db.Column(db.Integer,primary_key=True)
    job_desc = db.Column(db.String(100))

    def __init__(self, job_desc):
        self.job_desc = job_desc


with app.app_context():
    db.create_all()

#Esquema Categoria
class CategoriaSchema(ma.Schema):
    class Meta:
        fields = (
            'cat_id',
            'cat_nom',
            'cat_desp'
        )

#Esquema Categoria
class JobsSchema(ma.Schema):
    class Meta:
        fields = (
            'job_id',
            'job_desc'
        )

#Una sola respuesta
categoria_schema = CategoriaSchema()
job_schema = JobsSchema()

#Muchas respuestas
categorias_schema = CategoriaSchema(many = True)
jobs_schema = JobsSchema(many = True)


#GET
@app.route('/categoria',methods=['GET'])
def get_categorias():
    all_categorias = Categoria.query.all()
    result = categorias_schema.dump(all_categorias)
    return jsonify(result)

##Get Jobs
@app.route('/jobs',methods=['GET'])
def get_jobs():
    all_jobs = Jobs.query.all()
    result = jobs_schema.dump(all_jobs)
    return jsonify(result)

## GET JOB x ID
@app.route('/jobs/<id>',methods=['GET'])
def get_job_x_id(id):
    un_job = Jobs.query.get(id)    
    return job_schema.jsonify(un_job)


## POST
@app.route('/jobs',methods=['POST'])
def insert_job():

    data = request.get_json(force=True)
    job_id = data['job_id']
    job_desc = data['job_desc']

    n_record = Jobs(job_id,job_desc)

    db.session.add(n_record)
    db.session.commit()
    return job_schema.jsonify(n_record)



## Mensaje de bienvenida
@app.route('/',methods=['GET'])
def index():
    return jsonify({'mensaje':'Bienvenido'})

if __name__ =="__main__":
    app.run(debug=True)
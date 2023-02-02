### Fernando Poblete Muñoz 2023
### Prueba Tecnica: API REST , Python Flask
### Falta: Autenticación con token para seguridad, limitar la inserción de 1 a 1000 rows a la vez
### Falta: Crear Dockerfile
### Falta: Crear backups en Avro
### Falta: Readme y documentacion

from flask import Flask,jsonify,request, render_template, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from os.path import join, dirname, realpath


import pandas as pd


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost:3306/apidatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload folder
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

db = SQLAlchemy(app)
ma = Marshmallow(app)

def NotNullColumn(*args,**kwargs):
    kwargs["nullable"] = kwargs.get("nullable",False)
    return db.Column(*args,**kwargs)


class Jobs(db.Model):
    __tablename__ = "jobs"
    job_id = NotNullColumn(db.Integer,primary_key=True)
    job_name = NotNullColumn(db.String(100))

    def __init__(self, job_desc):
        self.job_desc = job_desc


class Departments(db.Model):
    __tablename__ = "departments"
    department_id = NotNullColumn(db.Integer,primary_key=True)
    department_name = NotNullColumn(db.String(100))

    def __init__(self,department_name):
        self.department_name = department_name

class Hired_Employees(db.Model):
    __tablename__ = "hired_employees"
    he_id = NotNullColumn(db.Integer,primary_key=True)
    he_name = NotNullColumn(db.String(100))
    he_datetime = NotNullColumn(db.String(100))
    he_department_id = NotNullColumn(db.Integer)
    he_job_id = NotNullColumn(db.Integer)

    def __init__(self,he_name,he_datetime,he_department_id,he_job_id):
        self.he_name = he_name
        self.he_datetime = he_datetime
        self.he_department_id = he_department_id
        self.he_job_id = he_job_id


with app.app_context():
    db.create_all()


# Esquemas
class JobsSchema(ma.Schema):
    class Meta:
        fields = (
            'job_id',
            'job_name'
        )

class DepartmentSchema(ma.Schema):
    class Meta:
        fields = (
            'department_id',
            'department_name'
        )

class HESchema(ma.Schema):
    class Meta:
        fields = (
            'he_id',
            'he_name',
            'he_datetime',
            'he_department_id',
            'he_job_id'
        )


#Una sola respuesta
job_schema = JobsSchema()
department_schema = DepartmentSchema()
HE_schema = HESchema()

#Muchas respuestas
jobs_schema = JobsSchema(many = True)
departments_schema = DepartmentSchema(many = True)
HEs_schema = HESchema(many = True)

##### Routes ######

@app.route("/")
def index():
    return "<h1>Bienvenido a mi API</h1>"


##Get Jobs
@app.route('/jobs',methods=['GET'])
def get_jobs():
    all_jobs = Jobs.query.all()
    result = jobs_schema.dump(all_jobs)
    return jsonify(result)

##Get Departmnets
@app.route('/departments',methods=['GET'])
def get_departments():
    all_departments = Departments.query.all()
    result = departments_schema.dump(all_departments)
    return jsonify(result)

##Get Hired Employees
@app.route('/hired_employees',methods=['GET'])
def get_hired_employees():
    all_hired_employees = Hired_Employees.query.all()
    result = HEs_schema.dump(all_hired_employees)
    return jsonify(result)

@app.route('/upload_file')
def upload_file():
    return render_template('upload_file.html')


# def insert_row():
#     return 0


def parseCSV(filepath,table_flag):

    if table_flag == 'jobs':        
        col_rules = {'jobs_id':'int','jobs_name':'string'}
    elif table_flag == 'deparments':        
        col_rules = {'department_id':'int','department_name':'string'}
    elif table_flag == 'hired_employees':        
        col_rules = {'he_id':'int','he_name':'string','he_datetime':'string','he_department_id':'int','he_job_id':'int'}
    col_names =  [col for col in col_rules.keys()]


    df = pd.read_csv(filepath,names=col_names, header=None, dtype='string') 
    

    if df.shape[0] < 1 or df.shape[0] > 1000:
        return 'Cantidad de lineas fuera de los rangos [1 a 1000]'
    else:
        #### Trabajando en validacion de reglas...
        ### probablemente cambie esto y valide al intentar insertar en la BBDD
        for col in df.columns:
            df[col] = df[col].astype(col_rules[col])

        ### Luego del parseo del archivo se intentará cargar la info
        # cargarData()




@app.route("/upload_file", methods=['POST'])
def uploadFiles():
      # get the uploaded file
      uploaded_file = request.files['file']
      loadTo = request.form['tablas']

      if uploaded_file.filename != '':
           file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
           uploaded_file.save(file_path)

           parseCSV(file_path,table_flag = loadTo)

      
      
    #   return "Archivo Cargado"
      return redirect(url_for('upload_file'))


if __name__ =="__main__":
    app.run(debug=True)
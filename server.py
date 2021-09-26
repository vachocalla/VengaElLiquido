import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import time as tt
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, redirect,render_template,flash,send_file
# Flask,flash,request,redirect,send_file,render_template

app = Flask(__name__)
FILE_FOLDER = 'C:/VicAR Corp/102 VicAR Software - VicSoft/2021/VengaElLiquido/uploads/'
#FILE_FOLDER = 'C:/Users/RYZEN 7/Desktop/Python/sample/ventas/uploads/'
# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = FILE_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

resultsData = {}

def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

@app.route('/verificarlista', methods=[ 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            #print('no file')
            return jsonify( 
                status= "failed"
            )
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            #print('no filename')
            return jsonify( 
                status= "failed"
            )
        else:
            filename = encrypt_string(file.filename)+secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            resultsData[filename] = []
            #df = pd.ExcelFile(FILE_FOLDER+filename)
            dfs = pd.read_excel(FILE_FOLDER+filename, sheet_name=None)
            df = dfs[ list(dfs.keys())[0] ]
            #df['CI'] = df['CI'].apply( lambda x : str(x).strip() )
            df['CI'] = df.iloc[:, 0].apply( lambda x : str(x).strip() )
            #df['Fecha Nacimiento'] = df['Fecha Nacimiento'].apply( lambda x : str(x).strip()[0:10] )
            df['Fecha Nacimiento'] = df.iloc[:, 1].apply( lambda x : str(x).strip()[0:10] )
            df['url'] = r'https://sus.minsalud.gob.bo/buscar_vacuna_pagina?nrodocumento_vacuna='+df['CI']+'&fechanacimiento_vacuna='+df['Fecha Nacimiento']+'&complemento_vacuna='
            #df['data']= {"ci": df['CI'], "fn": df['Fecha Nacimiento'], "url": +df['url']}
            print("------")
            processes = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                for i in range( len(df['url']) ):
                    processes.append(executor.submit(mevacuneCheck, {"name": filename, "CI": df.loc[i]['CI'], "Fecha Nacimiento": df.loc[i]['Fecha Nacimiento'], "url": df.loc[i]['url'], "continue":True} ))
                    tt.sleep(0.005)

            for task in as_completed(processes):
                print(task.result())
                return jsonify(
                    status = "success",
                    data = resultsData[filename]
                )

    return jsonify( 
        status= "failed"
    )
    #return render_template('upload_file.html')

@app.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = FILE_FOLDER + filename
    #return send_file(file_path, as_attachment=False, attachment_filename='')
    return send_file(file_path, as_attachment=False)

# CRUD ( CREATE, READ, UPDATE, DELETE )

# CREATE
@app.route('/mevacune', methods=['POST'])
def mevacune():
    json = request.json
    url = r'https://sus.minsalud.gob.bo/buscar_vacuna_pagina?nrodocumento_vacuna='+json['ci']+'&fechanacimiento_vacuna='+json['fecha_nacimiento']+'&complemento_vacuna='
    try:
        table = pd.read_html(url) # Returns list of all tables on page
        df = table[0] # Select table of interest
        return jsonify( 
            vacunado= "si",
            nombre= df.loc[0]['Nombre'],
            dosis= df.loc[0]['Dosis'],
            fecha= df.loc[0]['Fecha vacunacion']
        )
    except:
        return jsonify( 
            vacunado= "no"
        )

def mevacuneCheck(data):
    global resultsData
    print("--------------")
    #print(data)
    url = data['url']
    try:
        table = pd.read_html(url) # Returns list of all tables on page
        df = table[0] # Select table of interest
        resultsData[data['name']].append({
            "vacunado": "si",
            "CI": data['CI'],
            "Fecha Nacimiento": data['Fecha Nacimiento'],
            "nombre": df.loc[0]['Nombre'],
            "dosis": df.loc[0]['Dosis'],
            "fecha": df.loc[0]['Fecha vacunacion']
        })
    except Exception as e:
        print("qqqq: ", e)
        resultsData[data['name']].append({
            "vacunado": "no",
            "CI": data['CI'],
            "Fecha Nacimiento": data['Fecha Nacimiento']
        })
    

# READ
""" @app.route('/productos/<id>', methods=['GET'])
def producto_read_one(id):
    prod = producto.find_producto(id)
    return jsonify( 
        status= "success",
        data={'id': prod.id, 
            'nombre' : prod.nombre, 
            'descripcion': prod.descripcion,
            'url_imagen': prod.url_imagen, 
            'precio': prod.precio,
            'like': prod.like,
            'dislike': prod.dislike}
    ) """

# READ
""" @app.route('/productos', methods=['GET'])
def producto_read_all():
    prods = producto.find_all_producto()
    productos_data = []
    for valor in prods:
        productos_data.append({'id': valor.id,
                                'nombre': valor.nombre,
                                'descripcion': valor.descripcion,
                                'url_imagen': valor.url_imagen,
                                'precio': valor.precio,
                                'like': valor.like,
                                'dislike': valor.dislike, })
    return jsonify( 
        status= "success",
        data = productos_data
    ) """

# UPDATE
""" @app.route('/productos/<id>', methods=['PUT','PATCH'])
def producto_update(id):
    json = request.json
    producto.update_producto(id, json['nombre'], json['descripcion'], json['precio'], url_imagen=json['url_imagen'],like=json['like'],dislike=json['dislike'])
    return jsonify( 
        status= "success",
    ) """

# DELETE
""" @app.route('/productos/<id>', methods=['DELETE'])
def producto_delete(id):
    producto.delete_producto(id)
    return jsonify( 
        status= "success",
    ) """


@app.route('/')
def index():
    #https://sus.minsalud.gob.bo/buscar_vacuna_pagina?nrodocumento_vacuna=5721370&fechanacimiento_vacuna=1988-01-06&complemento_vacuna=
    #r = requests.get('https://sus.minsalud.gob.bo/buscar_vacuna_pagina?nrodocumento_vacuna=5721370&fechanacimiento_vacuna=1988-01-06&complemento_vacuna=',verify=False)
    #print(r.text)
    #print(r.status_code)
    
    url = r'https://sus.minsalud.gob.bo/buscar_vacuna_pagina?nrodocumento_vacuna=5721370&fechanacimiento_vacuna=1988-01-06&complemento_vacuna='
    #url = r'https://sus.minsalud.gob.bo/buscar_vacuna_pagina?nrodocumento_vacuna=661074&fechanacimiento_vacuna=1957-12-26&complemento_vacuna='
    try:
        table = pd.read_html(url) # Returns list of all tables on page
        df = table[0] # Select table of interest
        print(df)
        print(df.loc[0]['Nombre'])
        print(df.loc[0]['Dosis'])
        print(df.loc[0]['Fecha vacunacion'])
    except:
        print("No vacunado")

    
    
    

    #s=r.text
    #table = etree.HTML(s).find("body/div/div/div/div/table")
    #print(table)
    #rows = iter(table)
    #headers = [col.text for col in next(rows)]
    #for row in rows:
    #    values = [col.text for col in row]
    #    print(dict(zip(headers, values)))

    return "Python CURSO"

app.run(host="0.0.0.0", port=6789, debug=True)
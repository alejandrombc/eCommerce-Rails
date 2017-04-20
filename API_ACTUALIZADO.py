from flask import Flask, request, json
from flask_restful import Resource, Api, reqparse, abort
from datetime import datetime, date, time, timedelta
import jwt, calendar, hashlib, time, re
from flaskext.mysql import MySQL


errors = {
    'UsuarioExistente': {
        'message': "Este usuario ya existe",
        'register_value' : False,
        'status': 409,
    },
    'RecursoNoExistente': {
        'message': "El recurso con ese ID no existe",
        'status': 410,
        'resource_value': False,
    },
   	'ErrorLogin': {
        'message': "Las credenciales ingresadas no son validas",
        'status': 410,
        'login_value': False,
    },
    'ProductoNotFound': {
        'message': "El producto seleccionado no existe",
        'status': 404,
        'product_value': False,
    },
    'ProductoYaCreado': {
        'message': "El producto que sea ingresar ya esta creado",
        'status': 410,
        'product_value': False,
    },
   	'ErrorPeticion': {
        'message': "Error en la peticion",
        'status': 400,
        'err_value': False,
    },
    'ErrorAlDecodificar': {
        'message': "Error al decodificar el token",
        'status': 412,
        'login_value': False,
    }
}


success = {
    'RegistroCompletado': {
        'message': "Usuario registrado con exito!",
        'register_value' : True,
        'status': 201,
    },
    'LoginCompletado':{
    	'message': "Login realizado exitosamente",
    	'access_token' : True,
    	'status' : 200,
    	'login_value' : True
    },
    'ProductoAgregado':{
    	'message': "Producto creado exitosamente",
    	'status' : 200,
    	'product_value' : True
    },
    'ProductoEditado':{
    	'message': "Producto editado exitosamente",
    	'status' : 200,
    	'product_value' : True
    },
    'ProductoEliminado':{
    	'message': "Producto eliminado exitosamente",
    	'status' : 200,
    	'product_value' : True
    }
}


app = Flask(__name__)
api = Api(app, errors=errors)
mysql = MySQL()
mysql.init_app(app)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
# app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'jgastore'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.secret_key = "Estodeberiaserandom"

class Register(Resource):
	def post(self):
		data = request.get_json()

		if ('email' not in data) or ('password' not in data) or \
		(re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', data['email']) == None) or \
		(len(str(data['password'])) < 8):
			return errors['ErrorPeticion'], 400

		con = mysql.connect()
		cursor = con.cursor()

		if ('nombre') not in data:
			data['nombre'] = None
		if ('apellido') not in data:
			data['apellido'] = None
		if ('username') not in data:
			data['username'] = data['email'].split("@")[0]
		if ('fotoPerfil') not in data:
			data['fotoPerfil'] = None
		if ('fechaNacimiento') not in data:
			data['fechaNacimiento'] = None
		if ('genero') not in data:
			data['genero'] = None
		if ('telefono') not in data:
			data['telefono'] = None
		if ('ciudad') not in data:
			data['ciudad'] = None

		hashinput_email = hashlib.sha256(str(data['email']).encode('utf-8')).hexdigest() #Le hice cifrado sha256
		cursor.execute("SELECT email from cliente WHERE email=%s", (hashinput_email))
		email_actual = cursor.fetchone()
		if(email_actual != None): return errors['UsuarioExistente'], 409
		hashinput_password = hashlib.sha256(str(data['password']).encode('utf-8')).hexdigest() #Le hice cifrado sha256

		cursor.execute("INSERT INTO cliente VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (hashinput_email, data['nombre'], data['apellido'], data['username'], hashinput_password, data['fotoPerfil'],data['fechaNacimiento'],data['genero'],data['telefono'],data['ciudad']))
		con.commit()
		return success['RegistroCompletado'], 201

class Login(Resource):
	def post(self):

		data = request.get_json()
		#EDITAR PARA QUE SIRVA BIEN! (QUITAR CIFRADO PARA FACILIDADES)
		if ('email' not in data) or ('password' not in data):
			return errors['ErrorPeticion'], 400

		hashinput_usuario = hashlib.sha256(str(data['email']).encode('utf-8')).hexdigest() #Le hice cifrado sha256
		hashinput_password = hashlib.sha256(str(data['password']).encode('utf-8')).hexdigest() #Le hice cifrado sha256

		con = mysql.connect()
		cursor = con.cursor()

		cursor.execute("SELECT * FROM cliente WHERE email=%s AND password=%s", (hashinput_usuario, hashinput_password))
		check_log = cursor.fetchone()


		if(check_log != None):
			# check_log.update({'login_value' : True})
			datos = dict(email=data['email'], nombre=check_log[1], apellido=check_log[2], username=check_log[3], 
						password=data['password'], fotoPerfil=check_log[5], fechaNacimiento=check_log[6], genero=check_log[7], 
						telefono=check_log[8], ciudad=check_log[9], login_value=True)
			return datos

		return errors['ErrorLogin'], 410


class Product(Resource):
	def get(self, idP):

		con = mysql.connect()
		cursor = con.cursor()

		cursor.execute("SELECT * FROM producto WHERE idProducto=%s", (idP))
		producto = cursor.fetchone()

		if(producto != None): return dict(id=producto[0], nombre=producto[1], descripcion=producto[2], foto=producto[3], precio=producto[4], cantVendida=producto[5], idCategoria=producto[6])

		return errors['ProductoNotFound'], 404

	def put(self, idP):
		producto = request.get_json()

		con = mysql.connect()
		cursor = con.cursor()

		cursor.execute("SELECT * from producto WHERE idProducto=%s", (idP))
		hay_producto = cursor.fetchone()

		if(hay_producto == None): return errors['ProductoNotFound'], 404

		if('nombre' not in producto or producto['nombre'] == None): producto['nombre'] = hay_producto[1]
		if('descripcion' not in producto or producto['descripcion'] == None): producto['descripcion'] = hay_producto[2]
		if('foto' not in producto or producto['foto'] == None): producto['foto'] = hay_producto[3]
		if('precio' not in producto or producto['precio'] == None): producto['precio'] = hay_producto[4]	
		if('cantVendida' not in producto or producto['cantVendida'] == None): producto['cantVendida'] = hay_producto[5]	
		if('idCategoria' not in producto or producto['idCategoria'] == None): producto['idCategoria'] = hay_producto[6]	


		cursor.execute("UPDATE producto SET nombre=%s, descripcion=%s, foto=%s, precio=%s, cantVendida=%s, idCategoria=%s WHERE idProducto=%s", (producto['nombre'], producto['descripcion'], producto['foto'], producto['precio'], producto['cantVendida'], producto['idCategoria'], idP))
		con.commit()

		return success['ProductoEditado'], 200

	def delete(self, idP):
		con = mysql.connect()
		cursor = con.cursor()

		cursor.execute("SELECT * from producto WHERE idProducto=%s", (idP))
		hay_producto = cursor.fetchone()

		if(hay_producto == None): return errors['ProductoNotFound'], 404

		cursor.execute("DELETE FROM  producto WHERE idProducto=%s", (idP))
		con.commit()

		return success['ProductoEliminado'], 200

class ProductList(Resource):
	def get(self):
		con = mysql.connect()
		cursor = con.cursor()

		cursor.execute("SELECT * FROM producto ORDER BY cantVendida DESC")
		data = cursor.fetchall()

		return ([dict(id=producto[0], nombre=producto[1], descripcion=producto[2], foto=producto[3], precio=producto[4], cantVendida=producto[5], idCategoria=producto[6]) for producto in data])

	def post(self):
		producto = request.get_json()

		con = mysql.connect()
		cursor = con.cursor()

		if ('nombre' not in producto) or ('precio' not in producto):
			return errors['ErrorPeticion'], 400


		if ('foto') not in producto:
			producto['foto'] = None
		if ('cantVendida') not in producto:
			producto['cantVendida'] = 0
		if ('idCategoria') not in producto:
			producto['idCategoria'] = 1
		if ('descripcion') not in producto:
			producto['descripcion'] = None


		cursor.execute("INSERT INTO producto (nombre, descripcion, foto, precio, cantVendida, idCategoria) VALUES (%s,%s,%s,%s,%s,%s)", (producto['nombre'], producto['descripcion'], producto['foto'], producto['precio'], producto['cantVendida'], producto['idCategoria']))
		con.commit()

		return success['ProductoAgregado'], 200

class InfoUser(Resource):
	def get(self):

		usuario = request.headers.get('access_token')
		con = mysql.connect()
		cursor = con.cursor()

		if(usuario != None): 
			try:
				decod = jwt.decode(usuario, 'secret')
			except jwt.InvalidTokenError:
				return errors['ErrorAlDecodificar'], 412
			cursor.execute("SELECT * FROM cliente WHERE email=%s", (decod['sub']))
			data = cursor.fetchone()
			return dict(nombre=data[1], apellido=data[2], fotoPerfil=data[5], fechaNacimiento=data[6], genero=data[7], telefono=data[8], ciudad=data[9])
		return errors['RecursoNoExistente'], 404


class MultipleProducts(Resource):
	def post(self):
		productos = request.get_json()

		if(productos['ids'] != None):
			con = mysql.connect()
			cursor = con.cursor()

			sql='SELECT * FROM producto WHERE idProducto IN (%s)' 
			in_p=', '.join(list(map(lambda x: '%s', productos['ids'])))
			sql = sql % in_p

			cursor.execute(sql, productos['ids'])
			productos_general = cursor.fetchall()

			return ([dict(id=producto[0], nombre=producto[1], descripcion=producto[2], foto=producto[3], precio=producto[4], cantVendida=producto[5], idCategoria=producto[6], product_value=True) for producto in productos_general])
		else:
			return errors['ProductoNotFound'], 404 #REVISAR


class Categories(Resource):
	def get(self, idC):

		con = mysql.connect()
		cursor = con.cursor()

		cursor.execute("SELECT * FROM producto WHERE idCategoria=%s", (idC))
		productos = cursor.fetchall()

		if(productos != None): return ([dict(id=producto[0], nombre=producto[1], descripcion=producto[2], foto=producto[3], precio=producto[4], cantVendida=producto[5], idCategoria=producto[6], product_value=True) for producto in productos])

		return {}


class ProductAlfabeticamente(Resource):
	def get(self, idAlfabeticamente):

		con = mysql.connect()
		cursor = con.cursor()

		if(idAlfabeticamente == str(1)):
			cursor.execute("SELECT * FROM producto ORDER BY nombre DESC")
		else:
			cursor.execute("SELECT * FROM producto ORDER BY nombre ASC")

		data = cursor.fetchall()

		return ([dict(id=producto[0], nombre=producto[1], descripcion=producto[2], foto=producto[3], precio=producto[4], cantVendida=producto[5], idCategoria=producto[6]) for producto in data])




class ProductPrecio(Resource):
	def get(self, idPrecio):

		con = mysql.connect()
		cursor = con.cursor()

		if(idPrecio == str(1)):
			cursor.execute("SELECT * FROM producto ORDER BY precio DESC")
		else:
			cursor.execute("SELECT * FROM producto ORDER BY precio ASC")

		data = cursor.fetchall()

		return ([dict(id=producto[0], nombre=producto[1], descripcion=producto[2], foto=producto[3], precio=producto[4], cantVendida=producto[5], idCategoria=producto[6]) for producto in data])


class ActualizarVenta(Resource):
	def post(self):
		productos = request.get_json()

		if(productos['ids'] != None):
			con = mysql.connect()
			cursor = con.cursor()

			sql='UPDATE producto SET cantVendida=cantVendida+1 WHERE idProducto IN (%s)' 
			in_p=', '.join(list(map(lambda x: '%s', productos['ids'])))
			sql = sql % in_p

			cursor.execute(sql, productos['ids'])
			
			con.commit()
			return success['ProductoEditado'], 200

		else:
			return errors['ProductoNotFound'], 404 #REVISAR

class ProductoBusqueda(Resource):
	def post(self):
		productos = request.get_json()

		if(productos['query'] != None):
			con = mysql.connect()
			cursor = con.cursor()

			cursor.execute("SELECT * FROM producto WHERE " +
				"nombre LIKE '%"+productos['query']+"%' OR descripcion LIKE '%"+productos['query']+"%'" )

			
			data = cursor.fetchall()
			return ([dict(id=producto[0], nombre=producto[1], descripcion=producto[2], foto=producto[3], precio=producto[4], cantVendida=producto[5], idCategoria=producto[6]) for producto in data])

		else:
			return errors['ProductoNotFound'], 404 #REVISAR




api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Product, '/product/<string:idP>', endpoint='prod_ep')
api.add_resource(ProductList, '/product')
api.add_resource(ProductAlfabeticamente, '/product_alfabeticamente/<string:idAlfabeticamente>')
api.add_resource(ProductPrecio, '/product_precio/<string:idPrecio>')
api.add_resource(ActualizarVenta, '/nueva_compra')
api.add_resource(ProductoBusqueda, '/producto_buscar')
api.add_resource(Categories, '/categories/<string:idC>')
api.add_resource(MultipleProducts, '/products')
api.add_resource(InfoUser, '/user')


if __name__ == '__main__':
	app.run(debug=True) # , host="192.168.0.105" ->Para otra IP
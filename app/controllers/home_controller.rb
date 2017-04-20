class HomeController < ApplicationController
  $API_URL = "localhost:5000" #Url del API

  def index
  	vars = request.query_parameters
  	if user_signed_in?  
  		if session[:carro] == nil
  			session[:carro] = []
  		end
  	else
      session[:carro] = nil
    end

    if session[:alfabeticamente] == nil
    	session[:alfabeticamente] = 1
    end

    if session[:precio] == nil
    	session[:precio] = 1
    end

  	@products = JSON.parse(open("http://"+$API_URL+"/product").read, {:symbolize_names => true})

  	if vars['action_do'] == "succesfull_register"
  		flash.now["success"] = "Registro exitoso, por favor inicie sesión"

  	elsif vars['action_do'] == "succesfull_add"
  		flash.now["success"] = "Producto agregado al carro exitosamente"

  	elsif vars['action_do'] == "succesfull_delete"
		flash.now["success"] = "Producto eliminado del carro exitosamente"
  	
	elsif vars['action_do'] == "succesfull_addProduct"
		flash.now["success"] = "Producto creado exitosamente"

	elsif vars['action_do'] == "succesfull_deleteProduct"
		flash.now["success"] = "Producto eliminado exitosamente"

	elsif vars['action_do'] == "succesfull_editProduct"
		flash.now["success"] = "Producto editado exitosamente"

	elsif vars['action_do'] == "succesfull_addComment"
		flash.now["success"] = "Comentario agregado al diario de "+current_user.username
  	end	


  end




  def showregisterAPI
  	render(:action => 'registro')
  end


  def sendregisterAPI
  	#Realizo la peticion al API con los parametros introducidos
  	uri = URI('http://'+$API_URL+'/login')
	req = Net::HTTP::Post.new(uri, 'Content-Type' => 'application/json')
	req.body = {email: params[:email], password: params[:password]}.to_json
	res = Net::HTTP.start(uri.hostname, uri.port) do |http|
		http.request(req)
	end
	data = JSON.parse(res.body) #Aqui esta la respuesta del API
	if(data['login_value']) #Se logeo correctamente
		hay_email = User.find_by_email(data['email'])
		if(!hay_email) #El usuario no existe
			@user = User.create(:email => data['email'], :password => data['password'], :password_confirmation => data['password'], 
								:nombre => data['nombre'], :apellido => data['apellido'], :username => data['username'],
								:fotoPerfil => data["fotoPerfil"], :genero => data['genero'], 
								:telefono => data['telefono'])
		end
	end
  	redirect_to controller: 'home', action: 'index', action_do: "succesfull_register"
  end

  def showPerfil

  	@comentarios = Comentario.where(:user_id => current_user.id)

  	render(:action => 'perfil')
  end

  def prepurchase
  	@data = []
  	if(session[:carro].size != 0)
	  	uri = URI('http://'+$API_URL+'/products')
		req = Net::HTTP::Post.new(uri, 'Content-Type' => 'application/json')
		req.body = {ids: session[:carro]}.to_json
		res = Net::HTTP.start(uri.hostname, uri.port) do |http|
			http.request(req)
		end
		@data = JSON.parse(res.body) #Aqui esta la respuesta del API
	end

	for product_in_car in session[:carro]
		producto_esta = false
		for product_in_api in @data
			puts()
			if product_in_car == product_in_api['id']
				producto_esta = true
			end
		end
		if !producto_esta
			session[:carro].delete(product_in_car)
		end
	end

  	render(:action => 'precompra')
  end
  
  def showProduct
  	product_id = params[:id]
  	@product = JSON.parse(open("http://"+$API_URL+"/product/"+product_id).read, {:symbolize_names => true})
  	render(:action => 'product')
  end


  def addCarro
  	session[:carro].push((params[:id]).to_i)

  	redirect_to controller: 'home', action: 'index', action_do: "succesfull_add"

  end

  def deleteCarro
  	session[:carro].delete((params[:id]).to_i)
  	redirect_to controller: 'home', action: 'index', action_do: "succesfull_delete"

  end

  def addProducto
	uri = URI('http://'+$API_URL+'/product')
	req = Net::HTTP::Post.new(uri, 'Content-Type' => 'application/json')
	req.body = {nombre: params[:nombre], precio: params[:precio], 
				foto: params[:foto], idCategoria: ((params[:idCategoria]).to_i), 
				descripcion: params[:descripcion]}.to_json
	res = Net::HTTP.start(uri.hostname, uri.port) do |http|
		http.request(req)
	end
	@data = JSON.parse(res.body) #Aqui esta la respuesta del API

	redirect_to controller: 'home', action: 'index', action_do: "succesfull_addProduct"
  end


  def showCat
	id_categoria = params[:categoria]
	@products = JSON.parse(open("http://"+$API_URL+"/categories/"+id_categoria).read, {:symbolize_names => true})
  	@category = id_categoria.to_i
 	
 	render(:action => 'showCategory')
  end

  def showAlfa
  	if session[:alfabeticamente] == 1
  		session[:alfabeticamente] = 2
  	else
  		session[:alfabeticamente] = 1
  	end

  	id_alfabeticamente = params[:id]
  	@products = JSON.parse(open("http://"+$API_URL+"/product_alfabeticamente/"+id_alfabeticamente).read, {:symbolize_names => true})
  
  	render(:action => "showAlfabeticamente")
  end


  def showPrec
  	if session[:precio] == 1
  		session[:precio] = 2
  	else
  		session[:precio] = 1
  	end
  	
  	id_precio = params[:id]
  	@products = JSON.parse(open("http://"+$API_URL+"/product_precio/"+id_precio).read, {:symbolize_names => true})
  
  	render(:action => "showPrecio")
  end

  def deleteProd

  	#Para borrar en caso que el producto este en el carro NO SIRVE AUN
	for product_in_car in session[:carro]
		if((product_in_car).to_i == (params[:id]).to_i)
			session[:carro].delete((params[:id]).to_i)
		end
	end

  	#Hago la peticion delete al API
  	uri = URI('http://'+$API_URL+'/product/'+params[:id])
	http = Net::HTTP.new(uri.host, uri.port)
	req = Net::HTTP::Delete.new(uri.path)
	res = http.request(req)

	redirect_to controller: 'home', action: 'index', action_do: "succesfull_deleteProduct"

  end

  def updateProdshow

	product_id = params[:id]
  	@product = JSON.parse(open("http://"+$API_URL+"/product/"+product_id).read, {:symbolize_names => true})
  	render(:action => "updateProducto")

  end

  def updateProdsend
  	uri = URI('http://'+$API_URL+'/product/'+params[:id])
  	req = Net::HTTP::Put.new(uri, 'Content-Type' => 'application/json')
	req.body = {nombre: params[:nombre], precio: params[:precio], 
				foto: params[:foto], idCategoria: ((params[:idCategoria]).to_i), 
				descripcion: params[:descripcion]}.to_json
	response = Net::HTTP.new(uri.host, uri.port).start {|http| http.request(req) }
	puts response.code

	redirect_to controller: 'home', action: 'index', action_do: "succesfull_editProduct"

  end


  def mostrarCheckout
  	@data = []
  	if(session[:carro].size != 0)
	  	uri = URI('http://'+$API_URL+'/products')
		req = Net::HTTP::Post.new(uri, 'Content-Type' => 'application/json')
		req.body = {ids: session[:carro]}.to_json
		res = Net::HTTP.start(uri.hostname, uri.port) do |http|
			http.request(req)
		end
		@data = JSON.parse(res.body) #Aqui esta la respuesta del API
	end
  	render(:action => "mostrarCheckout")

  end

  def mostrarFactura
  	@factura = {nombre: params[:id_first_name], apellido: params[:id_last_name],
  				dir: params[:id_address_line_1], apart: params[:id_address_line_2], 
  				ciudad: params[:id_city], estado: params[:id_state],
  				cod_pos: params[:codigo_postal], tel: params[:telefono],
  				nomtar: params[:name_on_card], tarjeta: params[:card_number],
  				expM: params[:card_exp_month], expA: params[:card_exp_year],
  				cvc: params[:card_cvc]}


  	@data = []
  	if(session[:carro].size != 0)
	  	uri = URI('http://'+$API_URL+'/nueva_compra')
		req = Net::HTTP::Post.new(uri, 'Content-Type' => 'application/json')
		req.body = {ids: session[:carro]}.to_json
		res = Net::HTTP.start(uri.hostname, uri.port) do |http|
			http.request(req)
		end
		

		uri = URI('http://'+$API_URL+'/products')
		req = Net::HTTP::Post.new(uri, 'Content-Type' => 'application/json')
		req.body = {ids: session[:carro]}.to_json
		res = Net::HTTP.start(uri.hostname, uri.port) do |http|
			http.request(req)
		end

		@data = JSON.parse(res.body) #Aqui esta la respuesta del API

	end

	session[:carro].clear

  	render(:action => "mostrarFactura")
  end

  def createComentario

  	@user = User.find(current_user.id)
	@comment = @user.comentarios.create(:cuerpo => params[:cuerpo])

  	redirect_to controller: 'home', action: 'index', action_do: "succesfull_addComment"
  end

  def busqueda

  		uri = URI('http://'+$API_URL+'/producto_buscar')
		req = Net::HTTP::Post.new(uri, 'Content-Type' => 'application/json')
		req.body = {query: params[:busqueda]}.to_json
		res = Net::HTTP.start(uri.hostname, uri.port) do |http|
			http.request(req)
		end

		@products = JSON.parse(res.body) #Aqui esta la respuesta del API
  		
  		render(:action => "mostrarBusqueda")
  end

end
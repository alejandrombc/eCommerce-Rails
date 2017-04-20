Rails.application.routes.draw do
  devise_for :users, :controllers => { registrations: 'registrations', home: 'home' }
	  
  #RUTA DE REGISTRO  
    get "registroapi", to: "home#showregisterAPI", as: 'registershow'
    post "registroapi",  to: "home#sendregisterAPI", as: 'registershowsend'

  #RUTA DEL PERFIL DE USUARIO
    get "perfil", to: "home#showPerfil", as: "showPerfil"

  #RUTA DEL CARRITO 
    get "prepurchase", to: "home#prepurchase", as: "prepurchase" #Carro de compra
    post "producto/:id", to: "home#addCarro", as: "addcar" #Agregar al carro
    delete "producto/:id", to: "home#deleteCarro", as: "deletecar" #Eliminar del carro


  #RUTA DEL PRODUCTO
    get "producto/:id", to: "home#showProduct", as: "producto" #Producto individual

    post "addProducto", to: "home#addProducto", as: "addProducto" #Agrear un nuevo producto

    get "categoria/:categoria", to: "home#showCat", as: "showCat" #Filtrado por categoria

    get "orden/alfabeticamente/:id", to: "home#showAlfa", as: "showAlfabeticamente" #Filtrado alfabeticamente
   
    get "orden/precio/:id", to: "home#showPrec", as: "showPrecio" #Filtrado por precio

    delete "producto/:id/delete", to: "home#deleteProd", as:"deleteProducto" #Eliminacion del producto

    get "producto/:id/editar", to: "home#updateProdshow", as:"updateProductoShow" #Pantalla de edicion
    post "updateProducto", to: "home#updateProdsend", as: "updateProducto" #Edicion del producto


  #RUTA DE PAGO
    get "checkout", to: "home#mostrarCheckout", as: "mostrarCheckout" #Mostrar el checkout
    post "factura", to: "home#mostrarFactura", as: "mostrarFactura"

  #RUTA DE COMENTARIO
    post "createComentario", to: "home#createComentario", as: "createComentario" #Post nuevo comentario

  #RUTA DE BUSQUEDA
    get "busqueda", to: "home#busqueda", as: "nuevaBusqueda"
    
  #ROOT DE LA PAGINA
    root 'home#index', as: "root"


  # For details on the DSL available within this file, see http://guides.rubyonrails.org/routing.html
end

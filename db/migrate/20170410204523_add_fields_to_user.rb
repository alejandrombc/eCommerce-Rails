class AddFieldsToUser < ActiveRecord::Migration[5.0]
  def change
    add_column :users, :nombre, :string
    add_column :users, :apellido, :string
    add_column :users, :username, :string
    add_column :users, :fotoPerfil, :string
    add_column :users, :fechaNacimineto, :date
    add_column :users, :genero, :char
    add_column :users, :telefono, :string
    add_column :users, :ciudad, :string
  end
end

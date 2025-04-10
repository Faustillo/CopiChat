from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Inicializa la base de datos
def init_db():
    conn = sqlite3.connect('mensajes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria_id INTEGER,
            etiqueta TEXT NOT NULL,
            contenido TEXT NOT NULL,
            FOREIGN KEY(categoria_id) REFERENCES categorias(id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return redirect(url_for('usuario'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect('mensajes.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        if 'nueva_categoria' in request.form:
            nombre = request.form['nueva_categoria']
            cursor.execute('INSERT INTO categorias (nombre) VALUES (?)', (nombre,))
        elif 'etiqueta' in request.form:
            etiqueta = request.form['etiqueta']
            contenido = request.form['contenido']
            categoria_id = request.form['categoria_id']
            cursor.execute('INSERT INTO mensajes (categoria_id, etiqueta, contenido) VALUES (?, ?, ?)',
                           (categoria_id, etiqueta, contenido))
        conn.commit()

    cursor.execute('SELECT * FROM categorias')
    categorias = cursor.fetchall()

    mensajes_por_categoria = {}
    for cat in categorias:
        cursor.execute('SELECT * FROM mensajes WHERE categoria_id = ?', (cat[0],))
        mensajes_por_categoria[cat[1]] = cursor.fetchall()

    conn.close()
    return render_template('admin.html', categorias=categorias, mensajes=mensajes_por_categoria)

@app.route('/usuario')
def usuario():
    conn = sqlite3.connect('mensajes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categorias')
    categorias = cursor.fetchall()

    mensajes_por_categoria = {}
    for cat in categorias:
        cursor.execute('SELECT * FROM mensajes WHERE categoria_id = ?', (cat[0],))
        mensajes_por_categoria[cat[1]] = cursor.fetchall()

    conn.close()
    return render_template('usuario.html', mensajes=mensajes_por_categoria)

@app.route('/editar_mensaje/<int:id>', methods=['POST'])
def editar_mensaje(id):
    nueva_etiqueta = request.form['etiqueta']
    nuevo_contenido = request.form['contenido']

    conn = sqlite3.connect('mensajes.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE mensajes SET etiqueta = ?, contenido = ? WHERE id = ?', 
                   (nueva_etiqueta, nuevo_contenido, id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/eliminar_mensaje/<int:id>', methods=['POST'])
def eliminar_mensaje(id):
    conn = sqlite3.connect('mensajes.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM mensajes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/eliminar_categoria/<categoria_nombre>', methods=['POST'])
def eliminar_categoria(categoria_nombre):
    conn = sqlite3.connect('mensajes.db')
    cursor = conn.cursor()

    # Buscar categoría por nombre
    cursor.execute('SELECT id FROM categorias WHERE nombre = ?', (categoria_nombre,))
    result = cursor.fetchone()

    if result:
        categoria_id = result[0]

        # Eliminar mensajes asociados
        cursor.execute('DELETE FROM mensajes WHERE categoria_id = ?', (categoria_id,))
        # Eliminar la categoría
        cursor.execute('DELETE FROM categorias WHERE id = ?', (categoria_id,))
        conn.commit()

    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

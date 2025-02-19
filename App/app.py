from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Animal

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Ganti dengan kunci rahasia Anda
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)  # Ambil nomor halaman dari query string
    per_page = 5  # Jumlah hewan per halaman
    search_query = request.args.get('search', '')  # Ambil query pencarian dari query string

    if search_query:
        animals = Animal.query.filter(
            (Animal.nama.ilike(f'%{search_query}%')) | 
            (Animal.jenis.ilike(f'%{search_query}%'))
        ).paginate(page=page, per_page=per_page, error_out=False)
    else:
        animals = Animal.query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('index.html', animals=animals, search_query=search_query)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('User  registered successfully!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Mengeluarkan pengguna dari sesi
    flash('You have been logged out.')  # Menampilkan pesan logout
    return redirect(url_for('login'))  # Mengarahkan kembali ke halaman login

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_user.html')

@app.route('/add_animal', methods=['GET', 'POST'])
@login_required
def add_animal():
    if request.method == 'POST':
        nama = request.form['nama']
        jenis = request.form['jenis']
        umur = request.form['umur']
        pemilik_id = current_user.user_id  # Menggunakan ID pengguna yang sedang login
        new_animal = Animal(nama=nama, jenis=jenis, umur=umur, pemilik_id=pemilik_id)
        db.session.add(new_animal)
        db.session.commit()
        flash('Animal added successfully!')
        return redirect(url_for('index'))
    return render_template('add_animal.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            # Logika untuk mengirim email reset password bisa ditambahkan di sini
            flash('Check your email for instructions to reset your password.')
            return redirect(url_for('login'))
        else:
            flash('Email not found.')
    return render_template('reset_password.html')

@app.route('/dashboard')
@login_required
def dashboard():
    total_animals = Animal.query.count()  # Menghitung total hewan
    total_users = User.query.count()  # Menghitung total pengguna
    return render_template('dashboard.html', total_animals=total_animals, total_users=total_users)

@app.route('/edit_animal/<int:animal_id>', methods=['GET', 'POST'])
@login_required
def edit_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)  # Ambil hewan berdasarkan ID
    if request.method == 'POST':
        animal.nama = request.form['nama']
        animal.jenis = request.form['jenis']
        animal.umur = request.form['umur']
        db.session.commit()
        flash('Animal updated successfully!')
        return redirect(url_for('index'))
    return render_template('edit_animal.html', animal=animal)

@app.route('/delete_animal/<int:animal_id>', methods=['POST'])
@login_required
def delete_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)  # Ambil hewan berdasarkan ID
    db.session.delete(animal)  # Hapus hewan dari database
    db.session.commit()
    flash('Animal deleted successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
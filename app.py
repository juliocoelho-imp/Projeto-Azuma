import os
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv  

load_dotenv()

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS (NUVEM) ---

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave_secreta'

db = SQLAlchemy(app)

# --- MODELOS (Tabelas) ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(60), nullable=False)
    chamados = db.relationship('Chamado', backref='usuario', lazy=True)
    comentarios = db.relationship('Comentario', backref='autor', lazy=True)

class Chamado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    empresa = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='Aberto')
    prioridade = db.Column(db.String(20), default='Média')
    categoria = db.Column(db.String(50), default='Geral')
    operador = db.Column(db.String(50), nullable=True)
    mesa = db.Column(db.String(20), nullable=True)
    
    # Tempo
    tempo_gasto = db.Column(db.Integer, default=0)
    inicio_atendimento = db.Column(db.DateTime, nullable=True)
    
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    comentarios_lista = db.relationship('Comentario', backref='chamado', lazy=True, order_by="Comentario.data_criacao")

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(10), default='Publico')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    chamado_id = db.Column(db.Integer, db.ForeignKey('chamado.id'), nullable=False)

# --- FILTROS DE TEMPO  ---

@app.template_filter('format_time')
def format_time(seconds):
    if not seconds: seconds = 0
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}h {m:02d}m"

@app.template_filter('time_ago')
def time_ago(date):
    if not date: return ""
    now = datetime.utcnow()
    diff = now - date
    
    seconds = diff.total_seconds()
    minutes = int(seconds // 60)
    hours = int(minutes // 60)
    days = int(hours // 24)

    if seconds < 60:
        return "Agora mesmo"
    elif minutes < 60:
        return f"há {minutes} min"
    elif hours < 24:
        return f"há {hours} horas"
    elif days == 1:
        return "Ontem"
    else:
        return f"há {days} dias"

# --- ROTAS ---

@app.route('/')
def index(): 
    return redirect(url_for('tickets'))

@app.route('/tickets')
def tickets():
    query = Chamado.query
    if request.args.get('status'): 
        query = query.filter_by(status=request.args.get('status'))
    if request.args.get('empresa'): 
        query = query.filter(Chamado.empresa.ilike(f"%{request.args.get('empresa')}%"))
    
    lista_chamados = query.order_by(Chamado.id.desc()).all()
    empresas = [r.empresa for r in db.session.query(Chamado.empresa).distinct().all() if r.empresa]
    
    # Lógica para calcular o tempo visual em tempo real
    now = datetime.utcnow()
    for c in lista_chamados:
        if c.inicio_atendimento:
            delta = (now - c.inicio_atendimento).total_seconds()
            c.tempo_atual_visual = c.tempo_gasto + int(delta)
        else:
            c.tempo_atual_visual = c.tempo_gasto

    return render_template('tickets.html', chamados=lista_chamados, empresas_disponiveis=empresas)

@app.route('/toggle_timer/<int:id>')
def toggle_timer(id):
    chamado = Chamado.query.get_or_404(id)
    now = datetime.utcnow()
    
    if chamado.inicio_atendimento:
        # PAUSAR
        delta = (now - chamado.inicio_atendimento).total_seconds()
        chamado.tempo_gasto += int(delta)
        chamado.inicio_atendimento = None
    else:
        # PLAY
        chamado.inicio_atendimento = now
        chamado.status = 'Em Andamento'
        
    db.session.commit()
    return redirect(url_for('tickets'))

# --- Finalizar com comentário ---
@app.route('/finalizar/<int:id>', methods=['POST'])
def finalizar(id):
    chamado = Chamado.query.get_or_404(id)
    usuario = Usuario.query.first() 
    
    # Para o timer se estiver rodando
    if chamado.inicio_atendimento:
        now = datetime.utcnow()
        delta = (now - chamado.inicio_atendimento).total_seconds()
        chamado.tempo_gasto += int(delta)
        chamado.inicio_atendimento = None
    
    # Chamado de encerramento
    texto_resolucao = request.form.get('resolucao')
    if texto_resolucao:
        comentario = Comentario(
            texto=f"✅ CHAMADO ENCERRADO.\nSolução: {texto_resolucao}",
            tipo='Publico',
            usuario_id=usuario.id,
            chamado_id=chamado.id
        )
        db.session.add(comentario)

    # status -> Concluído
    chamado.status = 'Concluído'
    db.session.commit()
    
    return redirect(url_for('tickets'))

@app.route('/comentar/<int:id>', methods=['POST'])
def comentar(id):
    usuario = Usuario.query.first()
    novo_comentario = Comentario(
        texto=request.form.get('texto'),
        tipo='Privado' if request.form.get('privado') else 'Publico',
        usuario_id=usuario.id,
        chamado_id=id
    )
    db.session.add(novo_comentario)
    db.session.commit()
    return redirect(url_for('tickets'))

@app.route('/criar_chamado', methods=['POST'])
def criar_chamado():
    usuario = Usuario.query.first()
    if not usuario:
        usuario = Usuario(nome='Admin', email='admin@teste.com', senha='123')
        db.session.add(usuario)
        db.session.commit()

    novo = Chamado(
        titulo=request.form.get('titulo'), 
        descricao=request.form.get('descricao'),
        categoria=request.form.get('categoria'), 
        prioridade=request.form.get('prioridade'),
        mesa=request.form.get('mesa'), 
        operador=request.form.get('operador'),
        empresa=request.form.get('empresa'), 
        usuario_id=usuario.id
    )
    db.session.add(novo)
    db.session.commit()
    return redirect(url_for('tickets'))

@app.route('/editar_chamado/<int:id>', methods=['POST'])
def editar_chamado(id):
    chamado = Chamado.query.get_or_404(id)
    chamado.status = request.form.get('status')
    chamado.operador = request.form.get('operador')
    chamado.categoria = request.form.get('categoria')
    chamado.prioridade = request.form.get('prioridade')
    chamado.mesa = request.form.get('mesa')
    chamado.empresa = request.form.get('empresa')
    db.session.commit()
    return redirect(url_for('tickets'))

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not Usuario.query.first():
            user = Usuario(nome='Admin', email='admin@help.com', senha='123')
            db.session.add(user)
            db.session.commit()
            
    app.run(debug=True)
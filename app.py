import os
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, inspect as sa_inspect
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave_secreta'

db = SQLAlchemy(app)

# --- MODELOS ---
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
    data_limite = db.Column(db.DateTime, nullable=True)   # NOVO: SLA / Prazo

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


# --- CONTEXT PROCESSOR: injeta contadores globais na sidebar ---
@app.context_processor
def inject_globals():
    try:
        abertos_count = Chamado.query.filter(
            Chamado.status.in_(['Aberto', 'Em Andamento'])
        ).count()
    except Exception:
        abertos_count = 0
    return dict(abertos_count=abertos_count)


# --- FILTROS DE TEMPLATE ---
@app.template_filter('format_time')
def format_time(seconds):
    if not seconds:
        seconds = 0
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}h {m:02d}m"

@app.template_filter('time_ago')
def time_ago(date):
    if not date:
        return ""
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

@app.template_filter('format_datetime')
def format_datetime(date):
    if not date:
        return ""
    return date.strftime('%d/%m/%Y %H:%M')


# --- ROTAS ---

@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    abertos      = Chamado.query.filter_by(status='Aberto').count()
    em_andamento = Chamado.query.filter_by(status='Em Andamento').count()
    pausados     = Chamado.query.filter_by(status='Pausado').count()
    concluidos   = Chamado.query.filter_by(status='Concluído').count()
    total        = Chamado.query.count()

    # Tempo médio dos chamados concluídos
    concluidos_lista = Chamado.query.filter_by(status='Concluído').all()
    tempo_medio = 0
    if concluidos_lista:
        tempo_medio = sum(c.tempo_gasto for c in concluidos_lista) // len(concluidos_lista)

    # Por prioridade (apenas não concluídos)
    alta  = Chamado.query.filter_by(prioridade='Alta') .filter(Chamado.status != 'Concluído').count()
    media = Chamado.query.filter_by(prioridade='Média').filter(Chamado.status != 'Concluído').count()
    baixa = Chamado.query.filter_by(prioridade='Baixa').filter(Chamado.status != 'Concluído').count()

    meus = Chamado.query.filter_by(usuario_id=1).count()

    # Últimos 8 chamados
    ultimos = Chamado.query.order_by(Chamado.id.desc()).limit(8).all()

    # Chamados urgentes: Alta prioridade e ainda abertos
    urgentes = Chamado.query.filter_by(prioridade='Alta').filter(
        Chamado.status.in_(['Aberto', 'Em Andamento', 'Pausado'])
    ).order_by(Chamado.id.asc()).limit(5).all()

    # Chamados sem operador atribuído
    sem_operador = Chamado.query.filter(
        (Chamado.operador == None) | (Chamado.operador == ''),
        Chamado.status != 'Concluído'
    ).count()

    # Chamados ativos agora (timer ligado)
    ativos_agora = Chamado.query.filter(
        Chamado.inicio_atendimento != None
    ).all()

    # Distribuição por categoria
    from sqlalchemy import func
    categorias = db.session.query(
        Chamado.categoria, func.count(Chamado.id).label('total')
    ).filter(Chamado.status != 'Concluído').group_by(Chamado.categoria).all()

    # Distribuição por operador
    por_operador = db.session.query(
        Chamado.operador, func.count(Chamado.id).label('total')
    ).filter(
        Chamado.operador != None,
        Chamado.operador != '',
        Chamado.status != 'Concluído'
    ).group_by(Chamado.operador).order_by(func.count(Chamado.id).desc()).limit(5).all()

    # Chamados com prazo vencido
    agora = datetime.utcnow()
    try:
        vencidos = Chamado.query.filter(
            Chamado.data_limite < agora,
            Chamado.status != 'Concluído'
        ).count()
    except Exception:
        vencidos = 0

    return render_template('dashboard.html',
        abertos=abertos, em_andamento=em_andamento,
        pausados=pausados, concluidos=concluidos,
        total=total, tempo_medio=tempo_medio,
        alta=alta, media=media, baixa=baixa,
        meus=meus, ultimos=ultimos, vencidos=vencidos,
        urgentes=urgentes, sem_operador=sem_operador,
        ativos_agora=ativos_agora, categorias=categorias,
        por_operador=por_operador
    )


@app.route('/tickets')
def tickets():
    query = Chamado.query

    # Filtros
    status_filter     = request.args.get('status', '')
    empresa_filter    = request.args.get('empresa', '')
    prioridade_filter = request.args.get('prioridade', '')
    busca             = request.args.get('busca', '').strip()
    ordem             = request.args.get('ordem', 'recente')

    if status_filter:
        query = query.filter_by(status=status_filter)
    if empresa_filter:
        query = query.filter(Chamado.empresa.ilike(f"%{empresa_filter}%"))
    if prioridade_filter:
        query = query.filter_by(prioridade=prioridade_filter)
    if busca:
        query = query.filter(
            db.or_(
                Chamado.titulo.ilike(f"%{busca}%"),
                Chamado.descricao.ilike(f"%{busca}%"),
                Chamado.empresa.ilike(f"%{busca}%"),
                Chamado.operador.ilike(f"%{busca}%")
            )
        )

    # Ordenação
    if ordem == 'prioridade':
        prioridade_map = {'Alta': 1, 'Média': 2, 'Baixa': 3}
        lista_chamados = sorted(query.all(), key=lambda c: prioridade_map.get(c.prioridade, 4))
    elif ordem == 'tempo':
        lista_chamados = sorted(query.all(), key=lambda c: c.tempo_gasto, reverse=True)
    elif ordem == 'prazo':
        lista_chamados = sorted(
            query.all(),
            key=lambda c: c.data_limite if c.data_limite else datetime(9999, 12, 31)
        )
    else:  # recente
        lista_chamados = query.order_by(Chamado.id.desc()).all()

    empresas = [r.empresa for r in db.session.query(Chamado.empresa).distinct().all() if r.empresa]

    # Tempo visual em tempo real e status de prazo
    now = datetime.utcnow()
    for c in lista_chamados:
        if c.inicio_atendimento:
            delta = (now - c.inicio_atendimento).total_seconds()
            c.tempo_atual_visual = c.tempo_gasto + int(delta)
        else:
            c.tempo_atual_visual = c.tempo_gasto

        # Calcular status do prazo
        if c.data_limite and c.status != 'Concluído':
            diff = (c.data_limite - now).total_seconds()
            if diff < 0:
                c.prazo_status = 'vencido'
            elif diff < 3600:
                c.prazo_status = 'urgente'
            elif diff < 86400:
                c.prazo_status = 'proximo'
            else:
                c.prazo_status = 'ok'
        else:
            c.prazo_status = None

    return render_template('tickets.html',
        chamados=lista_chamados,
        empresas_disponiveis=empresas,
        busca_atual=busca,
        status_atual=status_filter,
        prioridade_atual=prioridade_filter,
        ordem_atual=ordem
    )


@app.route('/toggle_timer/<int:id>')
def toggle_timer(id):
    chamado = Chamado.query.get_or_404(id)
    now = datetime.utcnow()
    if chamado.inicio_atendimento:
        delta = (now - chamado.inicio_atendimento).total_seconds()
        chamado.tempo_gasto += int(delta)
        chamado.inicio_atendimento = None
    else:
        chamado.inicio_atendimento = now
        chamado.status = 'Em Andamento'
    db.session.commit()
    return redirect(url_for('tickets'))


@app.route('/finalizar/<int:id>', methods=['POST'])
def finalizar(id):
    chamado = Chamado.query.get_or_404(id)
    usuario = Usuario.query.first()

    if chamado.inicio_atendimento:
        now = datetime.utcnow()
        delta = (now - chamado.inicio_atendimento).total_seconds()
        chamado.tempo_gasto += int(delta)
        chamado.inicio_atendimento = None

    texto_resolucao = request.form.get('resolucao')
    if texto_resolucao:
        comentario = Comentario(
            texto=f"✅ CHAMADO ENCERRADO.\nSolução: {texto_resolucao}",
            tipo='Publico',
            usuario_id=usuario.id,
            chamado_id=chamado.id
        )
        db.session.add(comentario)

    chamado.status = 'Concluído'
    db.session.commit()
    return redirect(url_for('tickets'))


@app.route('/reabrir/<int:id>')
def reabrir(id):
    """Reabre um chamado já concluído."""
    chamado = Chamado.query.get_or_404(id)
    usuario = Usuario.query.first()
    chamado.status = 'Aberto'
    comentario = Comentario(
        texto="🔄 Chamado reaberto.",
        tipo='Publico',
        usuario_id=usuario.id,
        chamado_id=chamado.id
    )
    db.session.add(comentario)
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

    data_limite = None
    data_limite_str = request.form.get('data_limite', '').strip()
    if data_limite_str:
        try:
            data_limite = datetime.strptime(data_limite_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            pass

    novo = Chamado(
        titulo=request.form.get('titulo'),
        descricao=request.form.get('descricao'),
        categoria=request.form.get('categoria'),
        prioridade=request.form.get('prioridade'),
        mesa=request.form.get('mesa'),
        operador=request.form.get('operador'),
        empresa=request.form.get('empresa'),
        data_limite=data_limite,
        usuario_id=usuario.id
    )
    db.session.add(novo)
    db.session.commit()
    return redirect(url_for('tickets'))


@app.route('/editar_chamado/<int:id>', methods=['POST'])
def editar_chamado(id):
    chamado = Chamado.query.get_or_404(id)

    titulo = request.form.get('titulo', '').strip()
    descricao = request.form.get('descricao', '').strip()
    if titulo:
        chamado.titulo = titulo
    if descricao:
        chamado.descricao = descricao

    chamado.status     = request.form.get('status')
    chamado.operador   = request.form.get('operador')
    chamado.categoria  = request.form.get('categoria')
    chamado.prioridade = request.form.get('prioridade')
    chamado.mesa       = request.form.get('mesa')
    chamado.empresa    = request.form.get('empresa')

    data_limite_str = request.form.get('data_limite', '').strip()
    if data_limite_str:
        try:
            chamado.data_limite = datetime.strptime(data_limite_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            pass
    else:
        chamado.data_limite = None

    db.session.commit()
    return redirect(url_for('tickets'))


@app.route('/em_breve/<pagina>')
def em_breve(pagina):
    """Página temporária para seções ainda não implementadas."""
    nomes = {
        'projetos': ('Projetos', 'bi-kanban-fill'),
        'clientes': ('Clientes', 'bi-people-fill'),
        'inventario': ('Inventário', 'bi-box-seam-fill'),
        'configuracoes': ('Configurações', 'bi-gear-fill'),
    }
    nome, icone = nomes.get(pagina, ('Página', 'bi-circle'))
    return render_template('em_breve.html', nome=nome, icone=icone)


# --- MIGRAÇÃO AUTOMÁTICA DE COLUNAS NOVAS ---
def _run_migrations():
    """Adiciona colunas novas em tabelas existentes sem apagar dados."""
    try:
        inspector = sa_inspect(db.engine)
        cols = [c['name'] for c in inspector.get_columns('chamado')]
        with db.engine.connect() as conn:
            if 'data_limite' not in cols:
                conn.execute(text("ALTER TABLE chamado ADD COLUMN data_limite TIMESTAMP"))
                conn.commit()
    except Exception as e:
        print(f"[migration] aviso: {e}")


# --- INICIALIZAÇÃO ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        _run_migrations()
        if not Usuario.query.first():
            user = Usuario(nome='Admin', email='admin@help.com', senha='123')
            db.session.add(user)
            db.session.commit()
    app.run(debug=True, port="5001")


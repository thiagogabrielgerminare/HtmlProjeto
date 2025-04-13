from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Configuração do banco de dados PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://avnadmin:AVNS_IUFw8-OfVH7bf8zuL_l@pg-23037034-germinare-1db6.f.aivencloud.com:27088/dbMarketSpin?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)

# Modelos
class Produto(db.Model):
    __tablename__ = 'produto'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer)
    categoria = db.Column(db.String(50))
    imagem = db.Column(db.String(255))
    parcelamento = db.Column(db.String(100))
    preco_pix = db.Column(db.Float)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

class Pedido(db.Model):
    __tablename__ = 'pedido'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    data = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(50), default='Pendente')
    total = db.Column(db.Float)

class ItemPedido(db.Model):
    __tablename__ = 'item_pedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'))
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'))
    quantidade = db.Column(db.Integer)
    preco_unitario = db.Column(db.Float)

# Rotas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        cliente = Cliente.query.filter_by(email=email).first()
        
        if cliente and cliente.senha == senha:
            session['cliente_id'] = cliente.id
            session['cliente_nome'] = cliente.nome
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('pag_inicial'))
        else:
            flash('Email ou senha incorretos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            email = request.form.get('email')
            senha = request.form.get('senha')
            
            if not all([nome, email, senha]):
                flash('Preencha todos os campos', 'danger')
                return redirect(url_for('cadastro'))
            
            if Cliente.query.filter_by(email=email).first():
                flash('Email já cadastrado', 'danger')
                return redirect(url_for('cadastro'))
            
            novo_cliente = Cliente(
                nome=nome,
                email=email,
                senha=senha
            )
            
            db.session.add(novo_cliente)
            db.session.commit()
            
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erro no cadastro: {str(e)}', 'danger')
            return redirect(url_for('cadastro'))
    
    return render_template('cadastro.html')

@app.route('/inicio')
def pag_inicial():
    if 'cliente_id' not in session:
        return redirect(url_for('login'))
    
    produtos = {
        'madeiras': Produto.query.filter_by(categoria='Madeiras').limit(4).all(),
        'borrachas': Produto.query.filter_by(categoria='Borrachas').limit(4).all(),
        'raquetes': Produto.query.filter_by(categoria='Raquetes').limit(4).all(),
        'bolas': Produto.query.filter_by(categoria='Bolas').limit(4).all()
    }
    return render_template('pag_inicial.html', produtos=produtos)

@app.route('/categoria/<categoria>')
def categoria(categoria):
    if 'cliente_id' not in session:
        return redirect(url_for('login'))
    
    produtos = Produto.query.filter_by(categoria=categoria).all()
    return render_template('categoria.html',
                         produtos=produtos,
                         categoria=categoria)

@app.route('/produto/<int:id>')
def produto(id):
    produto = Produto.query.get_or_404(id)
    return render_template('produto.html', produto=produto)

@app.route('/produto/<int:produto_id>')
def ver_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    return render_template('produto.html', produto=produto)

@app.route('/adicionar_carrinho', methods=['POST'])
def adicionar_carrinho():
    if 'cliente_id' not in session:
        return jsonify({'success': False, 'message': 'Faça login primeiro'})
    
    data = request.get_json()
    produto_id = data.get('produto_id')
    quantidade = int(data.get('quantidade', 1))
    
    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({'success': False, 'message': 'Produto não encontrado'})
    
    if hasattr(produto, 'estoque') and produto.estoque < quantidade:
        return jsonify({'success': False, 'message': 'Quantidade indisponível em estoque'})
    
    if 'carrinho' not in session:
        session['carrinho'] = []
    
    item_existente = next((item for item in session['carrinho'] if item['produto_id'] == produto_id), None)
    
    if item_existente:
        item_existente['quantidade'] += quantidade
    else:
        session['carrinho'].append({
            'produto_id': produto_id,
            'quantidade': quantidade,
            'preco_unitario': float(produto.preco),
            'nome': produto.nome,
            'imagem': produto.imagem
        })
    
    session.modified = True
    return jsonify({
        'success': True, 
        'total_itens': len(session['carrinho']),
        'message': 'Produto adicionado ao carrinho!'
    })

@app.route('/remover_item_carrinho', methods=['POST'])
def remover_item_carrinho():
    if 'cliente_id' not in session:
        return jsonify({'success': False, 'message': 'Faça login primeiro'})
    
    produto_id = request.json.get('produto_id')
    
    if 'carrinho' not in session:
        return jsonify({'success': False, 'message': 'Carrinho vazio'})
    
    carrinho = session['carrinho']
    novo_carrinho = [item for item in carrinho if item['produto_id'] != produto_id]
    
    if len(novo_carrinho) == len(carrinho):
        return jsonify({'success': False, 'message': 'Produto não encontrado no carrinho'})
    
    session['carrinho'] = novo_carrinho
    session.modified = True
    
    total = sum(item['preco_unitario'] * item['quantidade'] for item in novo_carrinho)
    
    return jsonify({
        'success': True,
        'total_itens': len(novo_carrinho),
        'total': total
    })

@app.route('/carrinho')
def carrinho():
    if 'cliente_id' not in session:
        return redirect(url_for('login'))
    
    carrinho = session.get('carrinho', [])
    produtos = []
    total = 0
    
    for item in carrinho:
        produto = {
            'id': item['produto_id'],
            'nome': item['nome'],
            'imagem': item['imagem'],
            'preco': item['preco_unitario'],
            'quantidade': item['quantidade'],
            'subtotal': item['preco_unitario'] * item['quantidade']
        }
        produtos.append(produto)
        total += produto['subtotal']
    
    return render_template('carrinho.html', produtos=produtos, total=total)

@app.route('/finalizar_pedido', methods=['POST'])
def finalizar_pedido():
    if 'cliente_id' not in session:
        return redirect(url_for('login'))
    
    if 'carrinho' not in session or not session['carrinho']:
        flash('Seu carrinho está vazio', 'warning')
        return redirect(url_for('carrinho'))
    
    try:
        novo_pedido = Pedido(
            cliente_id=session['cliente_id'],
            status='Finalizado',
            total=sum(item['preco_unitario'] * item['quantidade'] for item in session['carrinho'])
        )
        
        db.session.add(novo_pedido)
        db.session.commit()
        
        for item in session['carrinho']:
            novo_item = ItemPedido(
                pedido_id=novo_pedido.id,
                produto_id=item['produto_id'],
                quantidade=item['quantidade'],
                preco_unitario=item['preco_unitario']
            )
            db.session.add(novo_item)
            
            produto = Produto.query.get(item['produto_id'])
            if produto.estoque < item['quantidade']:
                flash(f'Quantidade indisponível para {produto.nome}', 'danger')
                db.session.rollback()
                return redirect(url_for('carrinho'))
            
            produto.estoque -= item['quantidade']
        
        db.session.commit()
        
        session.pop('carrinho', None)
        
        flash('Pedido finalizado com sucesso!', 'success')
        return redirect(url_for('meus_pedidos'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao finalizar pedido: {str(e)}', 'danger')
        return redirect(url_for('carrinho'))

@app.route('/cancelar_pedido/<int:pedido_id>', methods=['POST'])
def cancelar_pedido(pedido_id):
    if 'cliente_id' not in session:
        return redirect(url_for('login'))
    
    pedido = Pedido.query.get_or_404(pedido_id)
    
    if pedido.cliente_id != session['cliente_id']:
        flash('Acesso não autorizado', 'danger')
        return redirect(url_for('meus_pedidos'))
    
    if pedido.status not in ['Finalizado', 'Processando']:
        flash('Pedido não pode ser cancelado neste estágio', 'warning')
        return redirect(url_for('meus_pedidos'))
    
    try:
        pedido.status = 'Cancelado'
        
        itens = ItemPedido.query.filter_by(pedido_id=pedido.id).all()
        for item in itens:
            produto = Produto.query.get(item.produto_id)
            produto.estoque += item.quantidade
        
        db.session.commit()
        
        flash('Pedido cancelado com sucesso. Os itens foram devolvidos ao estoque.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cancelar pedido: {str(e)}', 'danger')
    
    return redirect(url_for('meus_pedidos'))

@app.route('/meus_pedidos')
def meus_pedidos():
    if 'cliente_id' not in session:
        return redirect(url_for('login'))
    
    pedidos = Pedido.query.filter_by(cliente_id=session['cliente_id']).order_by(Pedido.data.desc()).all()
    
    pedidos_completos = []
    for pedido in pedidos:
        itens = ItemPedido.query.filter_by(pedido_id=pedido.id).all()
        produtos = []
        for item in itens:
            produto = Produto.query.get(item.produto_id)
            produtos.append({
                'nome': produto.nome,
                'quantidade': item.quantidade,
                'preco': item.preco_unitario,
                'subtotal': item.quantidade * item.preco_unitario
            })
        
        pedidos_completos.append({
            'id': pedido.id,
            'data': pedido.data,
            'status': pedido.status,
            'total': pedido.total,
            'produtos': produtos
        })
    
    return render_template('meus_pedidos.html', pedidos=pedidos_completos)

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'cliente_id' not in session:
        return redirect(url_for('login'))
    
    cliente = Cliente.query.get(session['cliente_id'])
    
    if request.method == 'POST':
        novo_nome = request.form.get('novo_nome')
        senha_atual = request.form['senha_atual']
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        if cliente.senha != senha_atual:
            flash('Senha atual incorreta', 'danger')
            return redirect(url_for('perfil'))
        
        if novo_nome and novo_nome != cliente.nome:
            cliente.nome = novo_nome
            session['cliente_nome'] = novo_nome
        
        if nova_senha:
            if nova_senha != confirmar_senha:
                flash('As novas senhas não coincidem', 'danger')
                return redirect(url_for('perfil'))
            
            cliente.senha = nova_senha
        
        try:
            db.session.commit()
            flash('Alterações salvas com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar perfil: {str(e)}', 'danger')
        
        return redirect(url_for('perfil'))
    
    return render_template('perfil.html', cliente=cliente)

@app.route('/pagamento')
def pagamento():
    if 'cliente_id' not in session:
        return redirect(url_for('login'))
    
    if 'carrinho' not in session or not session['carrinho']:
        flash('Seu carrinho está vazio', 'warning')
        return redirect(url_for('carrinho'))
    
    carrinho = session['carrinho']
    subtotal = sum(item['preco_unitario'] * item['quantidade'] for item in carrinho)
    frete = 15.00
    total = subtotal + frete
    
    produtos = []
    for item in carrinho:
        produto = {
            'id': item['produto_id'],
            'nome': item['nome'],
            'imagem': item['imagem'],
            'preco': item['preco_unitario'],
            'quantidade': item['quantidade'],
            'subtotal': item['preco_unitario'] * item['quantidade']
        }
        produtos.append(produto)
    
    return render_template('pagamento.html',
                         produtos=produtos,
                         subtotal=subtotal,
                         frete=frete,
                         total=total)

@app.route('/get_carrinho_count')
def get_carrinho_count():
    return jsonify({
        'total_itens': len(session.get('carrinho', []))
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)    
MarketSpin - Loja de Tênis de Mesa
MarketSpin é uma loja online especializada em produtos para tênis de mesa, oferecendo uma variedade de itens como madeiras, borrachas, raquetes, bolas e acessórios. O projeto inclui funcionalidades completas de e-commerce como cadastro de usuários, carrinho de compras, checkout e histórico de pedidos.


Funcionalidades:
  - Cadastro e autenticação de usuários
  
  - Navegação por categorias de produtos
  
  - Carrinho de compras com ajuste de quantidades
  
  - Checkout com múltiplas formas de pagamento
  
  - Perfil do usuário com histórico de pedidos
  
  - Sistema de gerenciamento de estoque


Bibliotecas Necessárias:
Para que o projeto funcione corretamente, você precisará instalar as seguintes bibliotecas Python:
pip install flask flask-sqlalchemy psycopg2-binary werkzeug


Dependências do Front-end:
O projeto utiliza as seguintes bibliotecas externas que são carregadas via CDN:

  - Font Awesome (para ícones):
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">


Configuração do Banco de Dados:
O projeto está configurado para usar PostgreSQL. Você precisará:

Criar um banco de dados PostgreSQL

Configurar a string de conexão no arquivo app.py:    
  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuário:senha@localhost/nome_do_banco'


Como Executar
Clone o repositório

Instale as dependências

Configure o banco de dados

Execute o aplicativo Flask:
  python app.py
  
O aplicativo estará disponível em http://localhost:5000


Licença
Este projeto está licenciado sob a licença MIT. Consulte o arquivo LICENSE para obter mais informações.

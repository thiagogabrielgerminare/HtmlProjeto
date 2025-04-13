function atualizarContadorCarrinho() {
    fetch('/get_carrinho_count')
        .then(response => response.json())
        .then(data => {
            const contadores = document.querySelectorAll('.contador');
            contadores.forEach(contador => {
                contador.textContent = data.total_itens;
            });
        });
}

function adicionarAoCarrinho(produtoId, quantidade = 1) {
    fetch('/adicionar_carrinho', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            produto_id: produtoId,
            quantidade: quantidade
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            atualizarContadorCarrinho();
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.textContent = 'Produto adicionado ao carrinho!';
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        } else {
            alert(data.message);
        }
    });
}

document.querySelectorAll('.botao-comprar').forEach(button => {
    button.addEventListener('click', function() {
        const produtoId = this.getAttribute('data-produto-id');
        adicionarAoCarrinho(produtoId);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    atualizarContadorCarrinho();
});

document.getElementById('finalizar-compra').addEventListener('click', function() {
    window.location.href = "{{ url_for('pagamento') }}";
});
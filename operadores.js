// OPERADORES
// clientes cujo código seja IGUAL que 100
db.clientes.find( {codigo: {$eq: 100} });

// produtos cuja unidade seja IGUAL a especificada
db.produtos.find( { unidade: { $eq: "CX" } } );

// pedidos cuja forma de pagamento seja DIFERENTE de PIX
db.pedidos.find( { forma_pagamento: { $ne: "PIX" } });

// clientes cujo código seja MENOR que 102
db.clientes.find( {codigo: {$lt: 102} });

// produtos cujo código seja MENOR IGUAL a 6
db.produtos.find( {codigo: {$lte: 6} });

// pedidos cujo número seja MAIOR que 1010
db.pedidos.find( {numero_pedido: {$gt: 1010} });

// pedidos cujos itens tenham quantidade MAIOR IGUAL a 2
db.pedidos.find(
  { "itens.quantidade": { $gte: 2 } },
  { _id: 0, numero_pedido: 1, "itens.codigo_produto": 1, "itens.quantidade": 1 }
);

// produtos que tenham as 2 tags específicas
db.produtos.find( { tags: { $all: ["informatica", "gamer"] } } );

// produtos que tenham uma das 2 tags especificadas
db.produtos.find( { tags: { $in: ["periferico", "gamer"] } });

// produtos que não tenham nenhuma das 2 tags especificadas
db.produtos.find( { tags: { $nin: ["gabinete", "fonte"] } });

// pedidos que tenham status_pedido IGUAL a um dos status apontados
db.pedidos.find( { $or: [ { status_pedido: "Aguardando pagamento"} 
                        , { status_pedido: "Em processamento" } ]}
, { _id: 0, data_pedido: 0, valor_pago: 0, itens: 0}
);

// pedidos que tenham status_pedido DIFERENTE dos apontados
db.pedidos.find( { $nor: [ { status_pedido: "Entregue"} 
                         , { status_pedido: "Cancelado" } 
                         , { status_pedido: "Aguardando pagamento" } ] }
, { _id: 0, data_pedido: 0, valor_pago: 0, itens: 0, codigo_cliente: 0, forma_pagamento: 0});

// clientes cujo nome CONTENHA o trecho especificado
db.clientes.find( { nome: { $regex: /Carlos/ } } , {_id:0, data_nascimento:0});

// itens de pedido cuja quantidade seja PAR
db.pedidos.find(
  { "itens.quantidade": { $mod: [2, 0] } },
  { _id: 0, numero_pedido: 1, "itens.codigo_produto": 1, "itens.quantidade": 1 }
);

// pedidos que contenham o campo SISTEMA_OPERACIONAL
db.produtos.find( { "sistema_operacional": { $exists: true } });
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

// AGREGAÇÕES
//quantidade de produtos cadastrados
db.produtos.countDocuments()

//quantidade de clientes cadastrados
db.clientes.countDocuments()

//quantidade de pedidos no sistema
db.pedidos.countDocuments()

//quantidade de pedidos no sistema por status
db.pedidos.aggregate([  {$group: { _id: '$status_pedido' , Quantidade: { $sum: 1 } } } ])

//quantidade de pedidos no sistema por data
db.pedidos.aggregate([  {$group: 
{ _id: { $dateToString: { format: "%Y-%m-%d", date: "$data_pedido" } } ,
Quantidade: { $sum: 1 } } }
, {$sort: {_id: 1}}])

//quantidade geral de produto em estoque
db.produtos.aggregate([ {$group: { _id: null
                   , Quantidade: {$sum: '$qtde_estoque'} } } ])

//quantidade de produto em estoque por categoria
db.produtos.aggregate([ {$group: { _id: '$categoria', 
                     Quantidade: {$sum: '$qtde_estoque'},
                       Produtos: {$sum: 1} } } ])

//vendas por dia
db.pedidos.aggregate([ 
{$match: { status_pedido: { $nin: ["Cancelado", "Aguardando pagamento"] } } }, 
{$group: { _id: { $dateToString: { format: "%Y-%m-%d", date: "$data_pedido" } },
  Qtde_Pedidos: { $sum: 1 }, Total_Vendas: { $sum: '$valor_pago' } } }
, {$sort: { _id: 1} } 
]) 

//vendas por dia agrupado por categoria
db.pedidos.aggregate([
  { $match: { status_pedido: { $nin: ["Cancelado", "Aguardando pagamento"] } } },
  { $unwind: "$itens" },
  { $lookup: {
      from: "produtos",
      localField: "itens.codigo_produto",
      foreignField: "codigo",
      as: "produto"
  }},
  { $unwind: "$produto" },
  { $group: {
      _id: {
        data:      { $dateToString: { format: "%Y-%m-%d", date: "$data_pedido" } },
        categoria: "$produto.categoria"
      },
      Total_Vendas: { $sum: "$itens.preco" },
      Qtde_Itens:   { $sum: "$itens.quantidade" }
  }},
  { $sort: { "_id.data": 1, "_id.categoria": 1 } },
  { $project: {
      _id: 0,
      Data:         "$_id.data",
      Categoria:    "$_id.categoria",
      Total_Vendas: 1,
      Qtde_Itens:   1
  }}
]);

//tiquete médio por forma de pagamento
db.pedidos.aggregate([
  { $match: { status_pedido: 
             { $nin: ["Cancelado", "Aguardando pagamento"] } } },
  { $group: {
      _id: "$forma_pagamento",
      Total_Vendas: { $sum: "$valor_pago" },
      Qtde_Pedidos: { $sum: 1 }
    }
  },
  { $project: {
      _id: 0,
      Forma_Pagamento: "$_id",
      Total_Vendas: 1,
      Qtde_Pedidos: 1,
      Ticket_Medio: { $divide: ["$Total_Vendas", "$Qtde_Pedidos"] }
    }
  },
  { $sort: { Ticket_Medio: -1 } }
]);

//tiquete médio por dia
db.pedidos.aggregate([
  { $match: { status_pedido: 
              { $nin: ["Cancelado", "Aguardando pagamento"] } } },
  { $group: {
      _id: { $dateToString: 
              { format: "%Y-%m-%d", date: "$data_pedido" } },
      Total_Vendas: { $sum: "$valor_pago" },
      Qtde_Pedidos: { $sum: 1 }
    }
  },
  { $project: {
      _id: 0,
      Periodo: "$_id",
      Total_Vendas: 1,
      Qtde_Pedidos: 1,
      Total_Vendas: 1,
      Ticket_Medio: { $divide: ["$Total_Vendas", "$Qtde_Pedidos"] }
    }
  },  { $sort: { Tickey_Medio: -1 } }
]);

// produtos mais vendidos
db.pedidos.aggregate([
  { $match: { status_pedido: 
              { $nin: ["Cancelado", "Aguardando pagamento"] } } },
  { $unwind: "$itens" },
  { $group: {
      _id: "$itens.codigo_produto",
      Qtde_Vendida: { $sum: "$itens.quantidade" },
      Receita:      { $sum: "$itens.preco" }
  }},
  { $lookup: {
      from: "produtos",
      localField: "_id",
      foreignField: "codigo",
      as: "produto"
  }},
  { $unwind: "$produto" },
  { $project: {
      _id: 0,
      Codigo: "$_id",
      Descricao: "$produto.descricao",
      Categoria: "$produto.categoria",
      Qtde_Vendida: 1,
      Receita: 1
  }},
  { $sort: { Receita: -1 } }
]);

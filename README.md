\# Usando MongoDB para uma Loja de Produtos de Informática



Projeto acadêmico de Banco de Dados 2 — Ciência de Dados para Negócios.



\## 🎯 Objetivo



Demonstrar, em uma aplicação Streamlit interativa, o uso do \*\*MongoDB\*\*

(modelagem, operadores, agregações) e do \*\*Prophet\*\* (séries temporais

e backtest) aplicados a uma loja de informática.



\## 🚀 Como executar localmente



```bash

git clone https://github.com/<seu-usuario>/loja-mongodb-prophet.git

cd loja-mongodb-prophet

pip install -r requirements.txt

streamlit run app.py

```



\## 🌐 Deploy no Streamlit Cloud



1\. Suba o repositório no GitHub.

2\. Acesse https://share.streamlit.io e conecte o repositório.

3\. Aponte para `app.py`.

4\. Em \*\*Secrets\*\*, adicione `MONGO\_URI` com a string de conexão.



\## 🗂️ Estrutura



\- `app.py` — entrypoint

\- `config/settings.py` — \*\*todas as cores e constantes em um só lugar\*\*

\- `core/` — lógica de negócio

\- `ui/` — seções e estilos

\- `textos/` — explicações editoriais (editáveis sem mexer no código)



\## ✏️ Como editar as explicações



\- Agregações: `textos/explicacoes\_agregadores.py`

\- Séries: `textos/explicacoes\_series.py`

\- Backtest: `textos/explicacoes\_backtest.py`



\## 🎨 Como trocar as cores



Edite `config/settings.py` no dicionário `CORES`.



\## 👤 Autor



Denis Tchobnian Cardoso — RA 2721542522018




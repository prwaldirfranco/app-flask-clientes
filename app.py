from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from datetime import datetime
import os
import plotly.express as px

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# ---------------- Arquivos CSV ----------------
CSV_CLIENTES = 'clientes.csv'
CSV_FUNCIONARIOS = 'funcionarios.csv'

# ---------------- Funções Auxiliares ----------------
def load_data(file):
    if os.path.exists(file):
        return pd.read_csv(file, encoding='utf-8')
    else:
        return pd.DataFrame()

def save_data(df, file):
    df.to_csv(file, index=False, encoding='utf-8')

def load_clientes():
    df = load_data(CSV_CLIENTES)
    if df.empty:
        df = pd.DataFrame(columns=['Nome','Telefone','Email','Empresa','Observacoes','DataCadastro','Status'])
    return df

def save_clientes(df):
    save_data(df, CSV_CLIENTES)

def load_funcionarios():
    df = load_data(CSV_FUNCIONARIOS)
    if df.empty:
        df = pd.DataFrame(columns=['Nome','Cargo','Email','Telefone','Atribuicoes','Observacoes','Status'])
    return df

def save_funcionarios(df):
    save_data(df, CSV_FUNCIONARIOS)

# ---------------- ROTAS CLIENTES ----------------
@app.route('/', methods=['GET'])
def index():
    search = request.args.get('search', '')
    df = load_clientes()
    if search:
        df = df[df['Nome'].str.contains(search, case=False, na=False)]
    clientes = df.to_dict('records')
    return render_template('index.html', clientes=clientes, search=search)

@app.route('/form_cliente', methods=['GET', 'POST'])
def form_cliente():
    df = load_clientes()
    idx = request.args.get('id')
    cliente = {}

    if idx is not None:
        idx = int(idx)
        if idx < len(df):
            cliente = df.iloc[idx].to_dict()

    if request.method == 'POST':
        data = {
            'Nome': request.form['Nome'],
            'Telefone': request.form['Telefone'],
            'Email': request.form['Email'],
            'Empresa': request.form['Empresa'],
            'Observacoes': request.form.get('Observacoes', ''),
            'DataCadastro': datetime.now().strftime('%Y-%m-%d'),
            'Status': request.form['Status']
        }

        if idx is not None:
            df.iloc[idx] = data
            flash('Cliente atualizado com sucesso!', 'success')
        else:
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            flash('Cliente cadastrado com sucesso!', 'success')

        save_clientes(df)
        return redirect(url_for('index'))

    return render_template('form_cliente.html', cliente=cliente, idx=idx)

@app.route('/delete_cliente/<int:idx>')
def delete_cliente(idx):
    df = load_clientes()
    if idx < len(df):
        df = df.drop(idx).reset_index(drop=True)
        save_clientes(df)
        flash('Cliente excluído com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard_clientes')
def dashboard_clientes():
    df = load_clientes()
    total_clientes = len(df)
    ativos = len(df[df['Status'] == 'Ativo'])
    inativos = len(df[df['Status'] == 'Inativo'])

    if total_clientes > 0:
        fig = px.pie(df, names='Status', title='Clientes Ativos vs Inativos',
                     color='Status', color_discrete_map={'Ativo':'green','Inativo':'red'})
        graph_html = fig.to_html(full_html=False)
    else:
        graph_html = "<p>Sem dados para exibir.</p>"

    return render_template('dashboard_clientes.html',
                           total_clientes=total_clientes,
                           ativos=ativos,
                           inativos=inativos,
                           graph_html=graph_html)

# ---------------- ROTAS FUNCIONÁRIOS ----------------
@app.route('/funcionarios', methods=['GET'])
def funcionarios():
    search = request.args.get('search', '')
    df = load_funcionarios()
    if search:
        df = df[df['Nome'].str.contains(search, case=False, na=False)]
    funcionarios = df.to_dict('records')
    return render_template('funcionarios.html', funcionarios=funcionarios, search=search)

@app.route('/form_funcionario', methods=['GET', 'POST'])
def form_funcionario():
    df = load_funcionarios()
    idx = request.args.get('id')
    funcionario = {}

    if idx is not None:
        idx = int(idx)
        if idx < len(df):
            funcionario = df.iloc[idx].to_dict()

    if request.method == 'POST':
        data = {
            'Nome': request.form['Nome'],
            'Cargo': request.form['Cargo'],
            'Email': request.form['Email'],
            'Telefone': request.form['Telefone'],
            'Atribuicoes': request.form['Atribuicoes'],
            'Observacoes': request.form.get('Observacoes', ''),
            'Status': request.form['Status']
        }

        if idx is not None:
            df.iloc[idx] = data
            flash('Funcionário atualizado com sucesso!', 'success')
        else:
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            flash('Funcionário cadastrado com sucesso!', 'success')

        save_funcionarios(df)
        return redirect(url_for('funcionarios'))

    return render_template('form_funcionario.html', funcionario=funcionario, idx=idx)

@app.route('/delete_funcionario/<int:idx>')
def delete_funcionario(idx):
    df = load_funcionarios()
    if idx < len(df):
        df = df.drop(idx).reset_index(drop=True)
        save_funcionarios(df)
        flash('Funcionário excluído com sucesso!', 'success')
    return redirect(url_for('funcionarios'))

@app.route('/dashboard_funcionarios')
def dashboard_funcionarios():
    df = load_funcionarios()
    total_func = len(df)
    ativos = len(df[df['Status'] == 'Ativo'])
    inativos = len(df[df['Status'] == 'Inativo'])

    df['QtdAtribuicoes'] = df['Atribuicoes'].fillna('').apply(lambda x: len([a for a in x.split(';') if a.strip() != '']))

    if total_func > 0:
        fig = px.bar(df, x='Nome', y='QtdAtribuicoes', color='Status',
                     color_discrete_map={'Ativo':'green','Inativo':'red'},
                     title='Número de Atribuições por Funcionário')
        graph_html = fig.to_html(full_html=False)
    else:
        graph_html = "<p>Sem dados para exibir.</p>"

    return render_template('dashboard_funcionarios.html',
                           total_func=total_func,
                           ativos=ativos,
                           inativos=inativos,
                           graph_html=graph_html)

# ---------------- RODAR APP ----------------
if __name__ == '__main__':
    app.run(debug=True)

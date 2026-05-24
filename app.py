import sys
import json
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from parse_excel import parse_excel
import anthropic

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

app = Flask(__name__)

BASE_DIR   = Path(__file__).parent
# DATA_DIR can be overridden by env var to point to a persistent volume on Railway
DATA_DIR   = Path(os.environ.get('DATA_DIR', str(BASE_DIR / 'data')))
DATA_FILE  = DATA_DIR / 'financial_data.json'
UPLOAD_DIR = DATA_DIR / 'uploads'

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Only used when running locally on the machine where the file lives
DEFAULT_EXCEL = Path(r'C:\Users\Martins & Reis\Desktop\FDC - Novus Auditiva\Fluxo de caixa 2026 - Novus Juvevê.xlsx')


def get_api_key():
    key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not key:
        env_path = BASE_DIR / '.env'
        if env_path.exists():
            for line in env_path.read_text(encoding='utf-8').splitlines():
                if line.startswith('ANTHROPIC_API_KEY='):
                    key = line.split('=', 1)[1].strip()
    return key


def auto_load():
    if DEFAULT_EXCEL.exists() and not DATA_FILE.exists():
        try:
            data = parse_excel(str(DEFAULT_EXCEL))
            DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f'[OK] Dados carregados de: {DEFAULT_EXCEL.name}')
        except Exception as e:
            print(f'[ERR] Erro ao carregar dados: {e}')


@app.route('/')
def dashboard():
    return render_template('index.html')


@app.route('/api/data')
def api_data():
    if DATA_FILE.exists():
        return app.response_class(
            response=DATA_FILE.read_text(encoding='utf-8'),
            status=200,
            mimetype='application/json'
        )
    return jsonify({'error': 'Nenhum dado carregado. Clique em "Atualizar dados" e envie o arquivo Excel.'})


@app.route('/api/upload', methods=['POST'])
def api_upload():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado.'}), 400
    f = request.files['file']
    if not f.filename.lower().endswith('.xlsx'):
        return jsonify({'success': False, 'message': 'Somente arquivos .xlsx sao aceitos.'}), 400
    save_path = UPLOAD_DIR / 'latest.xlsx'
    f.save(str(save_path))
    try:
        data = parse_excel(str(save_path))
        DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        return jsonify({'success': True, 'message': f'Dados atualizados em {data["ultima_atualizacao"]}'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao processar o arquivo: {e}'}), 500


@app.route('/api/ask', methods=['POST'])
def api_ask():
    body = request.get_json(silent=True) or {}
    question = (body.get('question') or '').strip()
    if not question:
        return jsonify({'error': 'Pergunta vazia.'}), 400
    if not DATA_FILE.exists():
        return jsonify({'error': 'Dados financeiros nao carregados.'}), 400

    api_key = get_api_key()
    if not api_key or 'CONFIGURE' in api_key:
        return jsonify({'error': 'Chave da API nao configurada. Adicione ANTHROPIC_API_KEY nas variaveis de ambiente.'}), 500

    financial_data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
    context = _build_context(financial_data)

    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model='claude-opus-4-5',
            max_tokens=1024,
            system=(
                'Voce e um assistente financeiro especializado da Novus Auditiva. '
                'Responda perguntas sobre o fluxo de caixa de forma clara, objetiva e profissional em portugues brasileiro. '
                'Use o formato R$ X.XXX,XX para valores monetarios. '
                'Seja conciso mas completo. Se os dados nao tiverem a informacao exata, explique o que esta disponivel.'
            ),
            messages=[{'role': 'user', 'content': f'{context}\n\nPergunta: {question}'}]
        )
        return jsonify({'answer': msg.content[0].text, 'question': question})
    except Exception as e:
        return jsonify({'error': f'Erro na consulta IA: {e}'}), 500


def _build_context(data):
    months = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']

    def fmt(v):
        s = f'R$ {abs(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        return f'-{s}' if v < 0 else s

    lines = [
        f'DADOS FINANCEIROS - {data.get("empresa", "Novus Auditiva")} - {data.get("ano", "2026")}',
        f'Ultima atualizacao: {data.get("ultima_atualizacao", "N/A")}',
        f'Mes com dados mais recentes: {data.get("mes_atual", "N/A")}',
        '',
    ]
    for cat in data.get('categorias', []):
        non_zero = {m: cat['values'][m] for m in months if cat['values'].get(m, 0) != 0}
        if not non_zero and cat.get('total', 0) == 0:
            continue
        lines.append(f'{cat["label"]} | Total anual: {fmt(cat["total"])}')
        for m, v in non_zero.items():
            lines.append(f'  {m}: {fmt(v)}')
    return '\n'.join(lines)


if __name__ == '__main__':
    auto_load()
    port = int(os.environ.get('PORT', 5000))
    print(f'\n[Novus Auditiva] Acesse: http://localhost:{port}')
    app.run(debug=False, port=port, host='0.0.0.0')

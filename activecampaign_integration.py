"""
Sistema de Qualificação de Leads - Integração ActiveCampaign
Programa Organick 2.0

Este servidor recebe webhooks do ActiveCampaign, calcula a pontuação
e retorna a classificação para o ActiveCampaign.
"""

from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações ActiveCampaign
AC_URL = "https://organicknm.api-us1.com"
AC_API_KEY = "2bf8c04b1bb5eb77e3aa39e10be70eb7fd8d20e2679787fe6ff153bd112a089939a06220"

# Mapeamento de campos personalizados do ActiveCampaign para as perguntas do sistema
FIELD_MAPPING = {
    'cartao': '%POSSUI_CARTAO_DE_CREDITO%',
    'rendaMkt': '%RENDA_DO_MKT_DIGITAL%',
    'rendaExtra': '%RENDA_ALM_DO_MKT%',
    'tempoArea': '%TEMPO_DE_ATUAO_NA_REA%',
    'clientes': '%QUANTOS_CLIENTES_POSSUI%',
    'status': '%ESTGIO_PROFISSIONAL%',
    'comprouCurso': '%JA_COMPROU_CURSO_OU_MENTORIA%',
    'investimento': '%QUANTO_JA_INVESTIU_EM_EDUCACAO%',
    'conheceNick': '%COMO_FICOU_SABENDO_DO_PROGRAMA%',
    'objetivo': '%OBJETIVOS_COM_O_PO%',
    'comprometimento': '%VAI_DEDICAR_1H_POR_DIA%'
}

# Sistema de pontuação (idêntico ao sistema HTML)
PONTUACAO = {
    'cartao': {
        'Sim, com meu próprio cartão.': 10,
        'Sim, com o cartão dos meus pais.': 5,
        'Sim, com um cartão de terceiro (de amigos, parentes, etc).': 3,
        'Não tenho cartão de crédito.': 0
    },
    'rendaMkt': {
        '+ de R$8.000,00': 12,
        'Entre R$5.000,00 e R$8.000,00': 10,
        'Entre R$ 3.000,00 e R$ 5.000,00': 8,
        'Entre R$ 2.000,00 e R$ 3.000,00': 6,
        'Entre R$ 1.000,00 e R$ 2.000,00': 4,
        'Entre R$ 100,00 e R$ 1.000,00': 2,
        'Ainda não tenho renda': 0
    },
    'rendaExtra': {
        '+ de R$8.000,00': 8,
        'Entre R$5.000,00 e R$8.000,00': 7,
        'Entre R$ 3.000,00 e R$ 5.000,00': 6,
        'Entre R$ 2.000,00 e R$ 3.000,00': 5,
        'Entre R$ 1.000,00 e R$ 1.000,00': 3,
        'Não tenho.': 8
    },
    'tempoArea': {
        'Mais de 5 anos': 10,
        '3 a 5 anos': 9,
        '2 a 3 anos': 8,
        '1 a 2 anos': 6,
        'Menos de 1 ano': 3,
        'Nenhum desses': 1,
        'Estou estudando': 1
    },
    'clientes': {
        '5': 10,
        '4': 9,
        '6': 9,
        '3': 8,
        '7': 8,
        '+8': 10,
        '2': 6,
        '1': 5,
        '0': 2
    },
    'status': {
        'Dono de uma agência/empresa': 5,
        'Freelancer': 5,
        'Funcionário em agência': 3,
        'Outro': 2
    },
    'comprouCurso': {
        'Sim': 8,
        'Não': 2
    },
    'investimento': {
        'Mais de R$ 5000 reais': 12,
        'Entre R$ 3.001 e R$ 5.000': 10,
        'Entre R$ 1.000 e R$ 3.000': 6,
        'Menos de 1 mil reais': 3
    },
    'conheceNick': {
        'Mais de 1 ano': 5,
        '6 meses a 1 ano': 4,
        '3 a 6 meses': 4,
        '1 a 3 meses': 2,
        'Menos de 1 mês': 1,
        'Não o conheço': 0
    },
    'objetivo': {
        'Quero abrir minha própria agência de marketing do zero': 10,
        'Já tenho uma agência, mas quero organizar e escalar': 10,
        'Já faço freelas, mas quero organizar e escalar': 10,
        'Trabalho para outra agência e quero criar meu próprio negócio': 9,
        'Tenho um negócio (ex: loja, estética, consultório) e quero aplicar conteúdo nele': 4,
        'Tenho um trabalho CLT em outra área, mas quero migrar pro digital': 7,
        'Trabalho na área criativa, mas ainda estou entendendo qual caminho seguir': 5,
        'Outro (vou explicar mais pra frente)': 3
    },
    'comprometimento': {
        'Sim! Tô com sangue nos olhos e totalmente comprometido.': 10,
        'Sim, entendo que isso exige esforço e estou pronto pra isso.': 9,
        'Sim, vai ser puxado, mas sei que é o que preciso agora.': 8,
        'Tenho minhas dúvidas, mas acho que consigo me organizar.': 5,
        'Ainda não tenho certeza se consigo manter esse ritmo.': 3,
        'Provavelmente eu não conseguiria me dedicar com constância.': 0,
        'Sendo honesto(a), não estou disposto a assumir esse nível de compromisso.': 0,
        'Não sou comprometido o suficiente pra seguir algo assim.': 0
    }
}


def encontrar_pontos(pergunta_id, resposta):
    """Encontra a pontuação baseada na resposta"""
    if not resposta or pergunta_id not in PONTUACAO:
        return 0
    
    resposta_str = str(resposta).strip().lower()
    
    for opcao, pontos in PONTUACAO[pergunta_id].items():
        opcao_lower = opcao.lower()
        if resposta_str == opcao_lower or resposta_str in opcao_lower or opcao_lower in resposta_str:
            return pontos
    
    return 0


def calcular_pontuacao(campos_contato):
    """Calcula a pontuação total do lead"""
    pontuacao_total = 0
    detalhes = []
    
    for pergunta_id, campo_ac in FIELD_MAPPING.items():
        resposta = campos_contato.get(campo_ac, '')
        pontos = encontrar_pontos(pergunta_id, resposta)
        pontuacao_total += pontos
        
        detalhes.append({
            'pergunta': pergunta_id,
            'resposta': resposta,
            'pontos': pontos
        })
    
    return pontuacao_total, detalhes


def obter_classificacao(pontuacao):
    """Retorna a classificação baseada na pontuação"""
    if pontuacao >= 80:
        return {
            'tag': 'PO - SUPER QUALIFICADO',
            'status': 'SUPER QUALIFICADO'
        }
    elif pontuacao >= 60:
        return {
            'tag': 'PO - QUALIFICADO',
            'status': 'QUALIFICADO'
        }
    elif pontuacao >= 40:
        return {
            'tag': 'PO - PRÉ-QUALIFICADO',
            'status': 'PRÉ-QUALIFICADO'
        }
    else:
        return {
            'tag': 'PO - DESQUALIFICADO',
            'status': 'DESQUALIFICADO'
        }


def buscar_contato_ac(contact_id):
    """Busca os dados do contato no ActiveCampaign"""
    url = f"{AC_URL}/api/3/contacts/{contact_id}"
    headers = {
        'Api-Token': AC_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Dados recebidos do AC: {data}")
        return data
    except Exception as e:
        logger.error(f"Erro ao buscar contato: {e}")
        return None


def atualizar_contato_ac(contact_id, pontuacao, classificacao):
    """Atualiza o contato no ActiveCampaign com a pontuação e tag"""
    headers = {
        'Api-Token': AC_API_KEY,
        'Content-Type': 'application/json'
    }
    
    # 1. Atualizar campo personalizado de pontuação
    url_field = f"{AC_URL}/api/3/contacts/{contact_id}"
    data_field = {
        "contact": {
            "fieldValues": [
                {
                    "field": "PONTUACAO_QUALIFICACAO_PO",  # Nome do campo no AC
                    "value": str(pontuacao)
                }
            ]
        }
    }
    
    try:
        response = requests.put(url_field, headers=headers, json=data_field)
        response.raise_for_status()
        logger.info(f"Campo atualizado para contato {contact_id}: {pontuacao} pontos")
    except Exception as e:
        logger.error(f"Erro ao atualizar campo: {e}")
    
    # 2. Adicionar tag de classificação
    url_tag = f"{AC_URL}/api/3/contactTags"
    data_tag = {
        "contactTag": {
            "contact": contact_id,
            "tag": classificacao['tag']
        }
    }
    
    try:
        response = requests.post(url_tag, headers=headers, json=data_tag)
        response.raise_for_status()
        logger.info(f"Tag adicionada para contato {contact_id}: {classificacao['tag']}")
    except Exception as e:
        logger.error(f"Erro ao adicionar tag: {e}")
    
    # 3. Atualizar campo de status
    url_status = f"{AC_URL}/api/3/contacts/{contact_id}"
    data_status = {
        "contact": {
            "fieldValues": [
                {
                    "field": "STATUS_QUALIFICAO_LEAD",  # Campo do AC
                    "value": classificacao['status']
                }
            ]
        }
    }
    
    try:
        response = requests.put(url_status, headers=headers, json=data_status)
        response.raise_for_status()
        logger.info(f"Status atualizado para contato {contact_id}: {classificacao['status']}")
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {e}")


@app.route('/webhook/activecampaign', methods=['POST'])
def webhook_activecampaign():
    """Endpoint que recebe o webhook do ActiveCampaign"""
    try:
        data = request.json
        logger.info(f"Webhook recebido: {data}")
        
        # Extrair ID do contato
        contact_id = data.get('contact', {}).get('id')
        
        if not contact_id:
            return jsonify({'error': 'Contact ID não encontrado'}), 400
        
        # Buscar dados completos do contato
        contato_dados = buscar_contato_ac(contact_id)
        
        if not contato_dados:
            return jsonify({'error': 'Não foi possível buscar dados do contato'}), 500
        
        # Extrair campos personalizados com validação
        campos_contato = {}
        
        if isinstance(contato_dados, dict):
            contact_data = contato_dados.get('contact', contato_dados)
            
            if isinstance(contact_data, dict):
                field_values = contact_data.get('fieldValues', [])
                
                if isinstance(field_values, list):
                    for field in field_values:
                        if isinstance(field, dict):
                            field_id = field.get('field')
                            field_value = field.get('value')
                            if field_id:
                                campos_contato[field_id] = field_value
        
        logger.info(f"Campos extraídos: {campos_contato}")
        
        # Calcular pontuação
        pontuacao_total, detalhes = calcular_pontuacao(campos_contato)
        
        # Obter classificação
        classificacao = obter_classificacao(pontuacao_total)
        
        logger.info(f"Contato {contact_id} - Pontuação: {pontuacao_total} - Classificação: {classificacao['status']}")
        
        # Atualizar ActiveCampaign
        atualizar_contato_ac(contact_id, pontuacao_total, classificacao)
        
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'pontuacao': pontuacao_total,
            'classificacao': classificacao['status'],
            'tag': classificacao['tag'],
            'detalhes': detalhes
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Endpoint para verificar se o servidor está rodando"""
    return jsonify({'status': 'OK', 'message': 'Servidor ativo'}), 200


@app.route('/test-contact/<contact_id>', methods=['GET'])
def test_contact(contact_id):
    """Endpoint de teste para processar um contato específico"""
    try:
        # Buscar dados do contato
        contato_dados = buscar_contato_ac(contact_id)
        
        if not contato_dados:
            return jsonify({'error': 'Contato não encontrado'}), 404
        
        logger.info(f"Tipo de contato_dados: {type(contato_dados)}")
        logger.info(f"Conteúdo: {contato_dados}")
        
        # Extrair campos - com validação de tipo
        campos_contato = {}
        
        # Verificar se é um dict e se tem a chave 'contact'
        if isinstance(contato_dados, dict):
            contact_data = contato_dados.get('contact', contato_dados)
            
            if isinstance(contact_data, dict):
                field_values = contact_data.get('fieldValues', [])
                
                if isinstance(field_values, list):
                    for field in field_values:
                        if isinstance(field, dict):
                            field_id = field.get('field')
                            field_value = field.get('value')
                            if field_id:
                                campos_contato[field_id] = field_value
        
        logger.info(f"Campos extraídos: {campos_contato}")
        
        # Calcular
        pontuacao_total, detalhes = calcular_pontuacao(campos_contato)
        classificacao = obter_classificacao(pontuacao_total)
        
        # Atualizar
        atualizar_contato_ac(contact_id, pontuacao_total, classificacao)
        
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'pontuacao': pontuacao_total,
            'classificacao': classificacao['status'],
            'tag': classificacao['tag'],
            'campos_encontrados': len(campos_contato),
            'detalhes': detalhes
        }), 200
        
    except Exception as e:
        logger.error(f"Erro completo: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("🚀 Servidor de integração ActiveCampaign iniciado!")
    logger.info("📡 Webhook URL: http://seu-servidor.com/webhook/activecampaign")
    app.run(host='0.0.0.0', port=5000, debug=True)

# 🚀 GUIA DE CONFIGURAÇÃO - INTEGRAÇÃO ACTIVECAMPAIGN

## 📋 VISÃO GERAL

Sistema automático que:
1. ✅ Recebe webhook do ActiveCampaign quando lead preenche Typeform
2. ✅ Calcula pontuação de qualificação (0-100)
3. ✅ Retorna para ActiveCampaign:
   - Campo: `PONTUAÇÃO DE QUALIFICAÇÃO PO` (valor numérico)
   - Campo: `STATUS QUALIFICAÇÃO LEAD` (texto da classificação)
   - Tag: `PO - SUPER QUALIFICADO` / `PO - QUALIFICADO` / `PO - PRÉ-QUALIFICADO` / `PO - DESQUALIFICADO`

---

## 🛠️ PASSO 1: HOSPEDAR O SERVIDOR

Você precisa hospedar o arquivo `activecampaign_integration.py` em um servidor.

### Opções de hospedagem:

#### Opção A: **Render.com** (RECOMENDADO - Gratuito)
1. Crie conta em https://render.com
2. Clique em "New" → "Web Service"
3. Conecte seu GitHub ou faça upload do código
4. Configure:
   - Environment: Python 3
   - Build Command: `pip install flask requests`
   - Start Command: `python activecampaign_integration.py`
5. Deploy!
6. Copie a URL: `https://seu-app.onrender.com`

#### Opção B: **Railway.app** (Gratuito)
1. Crie conta em https://railway.app
2. "New Project" → "Deploy from GitHub"
3. Configure variáveis de ambiente
4. Deploy automático
5. Copie a URL gerada

#### Opção C: **PythonAnywhere** (Gratuito)
1. Crie conta em https://www.pythonanywhere.com
2. Upload do arquivo
3. Configure Web App
4. Ative o servidor

#### Opção D: **Seu próprio servidor** (VPS/Cloud)
```bash
# Instalar dependências
pip install flask requests

# Rodar servidor
python activecampaign_integration.py
```

---

## 🔧 PASSO 2: CONFIGURAR CAMPOS NO ACTIVECAMPAIGN

Você precisa criar 2 campos personalizados novos:

### Campo 1: **PONTUAÇÃO DE QUALIFICAÇÃO PO**
- Tipo: `Número`
- Nome: `PONTUAÇÃO DE QUALIFICAÇÃO PO`
- Personalize o ID: `PONTUACAO_QUALIFICACAO_PO`

### Campo 2: **STATUS QUALIFICAÇÃO LEAD**
- Tipo: `Texto`
- Nome: `STATUS QUALIFICAÇÃO LEAD`
- Personalize o ID: `STATUS_QUALIFICAO_LEAD`

---

## 🏷️ PASSO 3: CRIAR TAGS NO ACTIVECAMPAIGN

Crie as 4 tags de classificação:
1. `PO - SUPER QUALIFICADO`
2. `PO - QUALIFICADO`
3. `PO - PRÉ-QUALIFICADO`
4. `PO - DESQUALIFICADO`

---

## ⚙️ PASSO 4: CONFIGURAR AUTOMAÇÃO NO ACTIVECAMPAIGN

### Criar Automação:

1. **Vá em**: Automações → Criar Automação

2. **Trigger (Gatilho)**:
   - Tipo: `Tag is added to a contact`
   - Tag: `typeform-integration-Aplicações_-_PROGRAMA_ORGANICK_[NOVO]`

3. **Ação 1**: Esperar (opcional - 1 minuto para garantir que campos foram preenchidos)

4. **Ação 2**: Webhook
   - URL: `https://SEU-SERVIDOR.com/webhook/activecampaign`
   - Método: `POST`
   - Event: `subscribe`
   - Body (JSON):
   ```json
   {
     "contact": {
       "id": "%CONTACTID%",
       "email": "%EMAIL%",
       "firstName": "%FIRSTNAME%",
       "lastName": "%LASTNAME%"
     }
   }
   ```

5. **Salvar e Ativar** a automação!

---

## 🧪 PASSO 5: TESTAR A INTEGRAÇÃO

### Teste Manual:
Acesse no navegador:
```
https://SEU-SERVIDOR.com/test-contact/ID_DO_CONTATO
```

Substitua `ID_DO_CONTATO` por um ID real de teste.

### Teste Real:
1. Preencha o Typeform com dados de teste
2. Aguarde a tag ser adicionada no ActiveCampaign
3. A automação deve disparar automaticamente
4. Verifique se o contato recebeu:
   - ✅ Pontuação no campo
   - ✅ Status no campo
   - ✅ Tag de classificação

---

## 📊 MAPEAMENTO DE CAMPOS

O sistema busca estas informações dos campos do ActiveCampaign:

| Pergunta | Campo ActiveCampaign |
|----------|---------------------|
| Tem cartão de crédito? | `%POSSUI_CARTAO_DE_CREDITO%` |
| Renda mensal com marketing digital | `%RENDA_DO_MKT_DIGITAL%` |
| Renda além do marketing | `%RENDA_ALM_DO_MKT%` |
| Tempo de atuação na área | `%TEMPO_DE_ATUAO_NA_REA%` |
| Quantidade de clientes atuais | `%QUANTOS_CLIENTES_POSSUI%` |
| Status profissional | `%ESTGIO_PROFISSIONAL%` |
| Já comprou curso ou mentoria? | `%JA_COMPROU_CURSO_OU_MENTORIA%` |
| Quanto já investiu em conhecimento? | `%QUANTO_JA_INVESTIU_EM_EDUCACAO%` |
| Tempo que conhece o Nick | `%COMO_FICOU_SABENDO_DO_PROGRAMA%` |
| Objetivo com o Programa Organick | `%OBJETIVOS_COM_O_PO%` |
| Comprometimento (1h por dia) | `%VAI_DEDICAR_1H_POR_DIA%` |

---

## 🎯 CLASSIFICAÇÕES

| Pontuação | Classificação | Tag |
|-----------|--------------|-----|
| 80-100 pts | SUPER QUALIFICADO | `PO - SUPER QUALIFICADO` |
| 60-79 pts | QUALIFICADO | `PO - QUALIFICADO` |
| 40-59 pts | PRÉ-QUALIFICADO | `PO - PRÉ-QUALIFICADO` |
| 0-39 pts | DESQUALIFICADO | `PO - DESQUALIFICADO` |

---

## 🔍 LOGS E MONITORAMENTO

O servidor gera logs de todas as operações:
- ✅ Webhook recebido
- ✅ Dados extraídos
- ✅ Pontuação calculada
- ✅ Campos atualizados
- ✅ Tags adicionadas
- ❌ Erros (se houver)

---

## ❓ TROUBLESHOOTING

### Problema: Webhook não dispara
**Solução**: Verifique se a URL está correta e se o servidor está online (teste `/health`)

### Problema: Campos não atualizam
**Solução**: Verifique se os IDs dos campos estão corretos no ActiveCampaign

### Problema: Tags não são adicionadas
**Solução**: Verifique se as tags foram criadas exatamente com os nomes especificados

### Problema: Pontuação incorreta
**Solução**: Verifique se as respostas no Typeform estão escritas exatamente como no código

---

## 🆘 SUPORTE

Para debug, acesse:
- Health check: `https://SEU-SERVIDOR.com/health`
- Teste manual: `https://SEU-SERVIDOR.com/test-contact/ID`
- Logs do servidor: Na plataforma de hospedagem

---

## 🎉 PRONTO!

Sua integração está configurada! Agora todo lead que preencher o Typeform será automaticamente qualificado e receberá sua pontuação e tag no ActiveCampaign! 🚀

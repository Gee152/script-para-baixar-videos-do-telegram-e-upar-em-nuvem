# Documentação do Bot: Telegram ➔ TeraBox 🚀

Este bot automatiza o processo de baixar vídeos de um canal do Telegram, verificar sua integridade técnica e enviá-los para uma pasta específica no TeraBox, economizando espaço em disco local e garantindo que apenas arquivos saudáveis sejam armazenados.

## 🏗️ Arquitetura do Sistema

O bot utiliza seu computador como uma **"Ponte de Sincronização"**:
1. **Fonte**: Canal do Telegram (via biblioteca Telethon).
2. **Processamento**: Seu computador (Validação OpenCV).
3. **Destino**: Nuvem TeraBox (via API interna reversa).

---

## 🛠️ Funcionalidades Principais

### 1. Inteligência de Nuvem (Skip Automático)
Antes de qualquer download, o bot consulta o TeraBox. Se o vídeo (identificado pela hashtag ex: `#F0685`) já estiver na pasta destino `/PROGRAMACAO/Front/Alura/`, o bot **pula** para a próxima mensagem sem baixar nada.

### 2. Validação Técnica (Check de Vídeo)
Após o download, o script não confia apenas no tamanho do arquivo. Ele abre o vídeo usando o **OpenCV (`cv2`)** e tenta ler o primeiro frame.
- **Se o vídeo rodar**: Segue para o upload.
- **Se estiver corrompido**: O arquivo é deletado do PC e o bot tenta baixar novamente do Telegram (até 3 tentativas).

### 3. Pipeline de Upload (Host Japonês)
O upload é feito em 3 etapas para garantir segurança:
- **Precreate**: Solicita permissão e recebe um `uploadid`.
- **Upload**: Envia o arquivo para o servidor de dados `c-jp.terabox.com`.
- **Create**: Finaliza o registro do arquivo na sua conta.

### 4. Limpeza Automática de Disco
Assim que o upload é confirmado pelo TeraBox, o arquivo local na pasta `Aulas_Baixadas` é **removido permanentemente**. Isso permite processar terabytes de vídeo mesmo com pouco espaço no HD local.

---

## 🔑 Configurações e Tokens

O bot utiliza tokens capturados manualmente do navegador para simular sua sessão:
- **`TB (ndus)`**: Seu token de sessão principal.
- **`JS_TOKEN`**: Token de segurança CSRF (necessário para as chamadas `/api/`).
- **`app_id`**: Configurado como `250528` (ID padrão da plataforma web).

---

## 🚀 Como Executar

### Pré-requisitos
Certifique-se de ter as bibliotecas instaladas:
```bash
pip install telethon opencv-python requests
```

### Execução
Basta iniciar o script principal:
```bash
python index.py
```

---

## ⚠️ Manutenção e Erros Comuns

> [!IMPORTANT]
> **Token Expirado**: Se você receber erros como `403 Forbidden` ou `10054 Connection Reset`, seu `JS_TOKEN` ou `ndus` podem ter expirado. 
> **Solução**: Faça login no TeraBox pelo Chrome, abra o F12 (Network), capture uma nova URL de `precreate` e atualize os tokens no topo do `index.py`.

> [!WARNING]
> **Alterações na API**: O TeraBox pode mudar os caminhos da API (ex: mudar de `api/precreate` para outro nome). O script foi desenhado de forma modular em `terabox.py` para facilitar ajustes rápidos nessas URLs.

---

## 📁 Estrutura de Arquivos
- **[index.py](file:///c:/Users/gabri/OneDrive/Documentos/python/index.py)**: Lógica de controle, Telegram e loop principal.
- **[terabox.py](file:///c:/Users/gabri/OneDrive/Documentos/python/terabox.py)**: Motor de comunicação com o TeraBox.

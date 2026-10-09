# Importamos as ferramentas do Telethon
from telethon import TelegramClient
import os
import re
import cv2  # Para verificar se o vídeo está OK
from terabox import TeraBox  # Nossa classe de upload
import asyncio

# --- CONFIGURAÇÕES INICIAIS ---
api_id = '31860233'  # Ex: 1234567
api_hash = 'YvuJ2hTteHuizgWfMg-CuHC-Vvdz1tdDqLZSt9N2'
canal_id = -1001808574783
TB='YvuJ2hTteHuidg5WYMHjM7lwhLp7hC4-O_xVjFH3'
JS_TOKEN = 'B35E7DD8C0A866FDA6E3EC993B8FF9E331AF41DCD73239621FD120140CD5816C59BD3540A647AC021BD7A8E57DF6CD0AE5B99183771731FD58A6692062FFA018'
PASTA_TERABOX = "/PROGRAMACAO/FullCycles"

client = TelegramClient('minha_sessao', api_id, api_hash)
tb = TeraBox(TB, js_token=JS_TOKEN)

def verificar_video(caminho):
    """Retorna True se o vídeo carregar corretamente, False caso contrário."""
    try:
        cap = cv2.VideoCapture(caminho)
        if not cap.isOpened():
            return False
        ret, frame = cap.read()
        cap.release()
        return ret
    except Exception as e:
        print(f"Erro na verificação técnica: {e}")
        return False

async def main():
    print("A iniciar a ligação ao Telegram...")
    
    pasta_destino = "Aulas_Baixadas"
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    print("A analisar todas as mensagens do canal. Isto pode demorar um pouco...")
    
    # Vamos ler todas as mensagens do canal. 
    # reverse=True faz com que ele leia da mensagem mais antiga para a mais nova (ordem cronológica).
    async for mensagem in client.iter_messages(canal_id, reverse=True):
        
        # 1º Passo: Garantir que a mensagem tem texto e tem um arquivo (vídeo ou documento)
        if mensagem.text and (mensagem.video or mensagem.document):
            
            # 2º Passo: A Lupa Inteligente (RegEx)
            # r'#F?\d+' significa: Procura por "#" opcionalmente seguido de "F" e um ou mais dígitos
            padrao_encontrado = re.search(r'#F?\d+', mensagem.text)
            
            # Se a lupa encontrou o padrão na mensagem...
            if padrao_encontrado:
                # Extraímos o texto exato que ele encontrou (ex: '#F0021' ou '#001')
                hashtag = padrao_encontrado.group(0)
                
                caminho_arquivo = f"{pasta_destino}/{hashtag}.mp4"
                caminho_remoto = f"{PASTA_TERABOX}/{hashtag}.mp4"
                
                # 3º Passo: Verificar se o vídeo já existe no TeraBox (não mais localmente)
                if tb.verificar_se_existe(caminho_remoto):
                    print(f"Já Concluído, proximo ...")
                    continue # Salta para a próxima mensagem
                
                # Inicia o download com tentativas
                tentativas = 3
                sucesso = False
                
                while tentativas > 0 and not sucesso:
                    print(f"Vídeo encontrado! A iniciar o download de {hashtag} (Tentativas restantes: {tentativas})...")
                    try:
                        # Usar a mensagem inteira é mais robusto que mensagem.media
                        await client.download_media(mensagem, file=caminho_arquivo)
                        
                        # Verificação de integridade
                        if verificar_video(caminho_arquivo):
                            print(f"Vídeo {hashtag} verificado e carregando com sucesso!")
                            
                            # Upload para o TeraBox
                            print(f"A iniciar upload para o TeraBox: {caminho_remoto}")
                            try:
                                tb.upload_file(caminho_arquivo, caminho_remoto)
                                print(f"Upload concluído com sucesso para o TeraBox!")
                                
                                # Limpeza Local: Remove o vídeo do PC após subir para a nuvem
                                if os.path.exists(caminho_arquivo):
                                    os.remove(caminho_arquivo)
                                    print(f"Arquivo local removido para economizar espaço.")
                                
                                sucesso = True
                            except Exception as up_err:
                                print(f"Erro no upload para o TeraBox: {up_err}")
                                # Se o upload falhar, podemos decidir se deletamos ou não. 
                                # Aqui, vamos assumir que o download foi OK e o problema foi conexão/API.
                                sucesso = True # Para não ficar em loop de download se o problema for o TeraBox
                        else:
                            print(f"Vídeo {hashtag} está corrompido ou não carrega. A apagar e tentar novamente...")
                            if os.path.exists(caminho_arquivo):
                                os.remove(caminho_arquivo)
                            tentativas -= 1
                            await asyncio.sleep(2) # Pequena pausa antes de tentar de novo
                            
                    except Exception as e:
                        import traceback
                        print(f"Erro ao processar {hashtag}: {e}")
                        traceback.print_exc() # Mostra o erro completo no terminal
                        tentativas -= 1
            else:
                # Log opcional para mensagens que não batem com o padrão (útil para debug)
                # print(f"Mensagem ignorada (sem hashtag válida): {mensagem.text[:30]}...")
                pass

# Liga o nosso script
with client:
    client.loop.run_until_complete(main())
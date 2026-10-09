import os
from terabox import TeraBox
import cv2
import numpy as np

# Configurações
TB='YvuJ2hTteHuidg5WYMHjM7lwhLp7hC4-O_xVjFH3'
JS_TOKEN = 'B35E7DD8C0A866FDA6E3EC993B8FF9E331AF41DCD73239621FD120140CD5816C59BD3540A647AC021BD7A8E57DF6CD0AE5B99183771731FD58A6692062FFA018'
TEST_PATH = "/PROGRAMACAO/Front/Alura/teste_bot.txt"

def test_terabox():
    print("Testando TeraBox...")
    tb = TeraBox(TB, js_token=JS_TOKEN)
    dummy_file = "teste.txt"
    with open(dummy_file, "w") as f:
        f.write("Teste de upload do bot")
    
    try:
        res = tb.upload_file(dummy_file, TEST_PATH)
        print("Upload de teste OK:", res)
    except Exception as e:
        print("Erro no teste de TeraBox:", e)
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)

def test_video_val():
    print("\nTestando Validação de Vídeo...")
    # Criar um vídeo dummy válido
    video_path = "valid_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 20.0, (640,480))
    for _ in range(10):
        frame = np.random.randint(0, 255, (480,640,3), dtype=np.uint8)
        out.write(frame)
    out.release()
    
    # Criar um arquivo inválido
    invalid_path = "corrupt.mp4"
    with open(invalid_path, "w") as f:
        f.write("não é um vídeo")

    def verificar(caminho):
        cap = cv2.VideoCapture(caminho)
        if not cap.isOpened():
            return False
        ret, frame = cap.read()
        cap.release()
        return ret

    print(f"Vídeo válido: {verificar(video_path)}")
    print(f"Vídeo inválido: {verificar(invalid_path)}")
    
    os.remove(video_path)
    os.remove(invalid_path)

if __name__ == "__main__":
    test_video_val()
    test_terabox()

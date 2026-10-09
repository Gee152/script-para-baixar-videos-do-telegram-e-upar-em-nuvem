import requests
import os
import hashlib
import json

class TeraBox:
    def __init__(self, ndus, js_token=None):
        self.ndus = ndus
        self.js_token = js_token
        self.app_id = "250528"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": f"ndus={self.ndus}",
            "Referer": "https://www.terabox.com/main"
        })

    def _get_dp_logid(self):
        import random
        # Ajustado para 20 dígitos conforme exemplo do usuário
        return "".join([str(random.randint(0, 9)) for _ in range(20)])

    def verificar_se_existe(self, remote_path):
        """Verifica se o arquivo já existe no TeraBox usando paginação."""
        parent_dir = os.path.dirname(remote_path).replace("\\", "/")
        filename = os.path.basename(remote_path)
        
        page = 1
        max_pages = 50
        
        while page <= max_pages:
            params = {
                "app_id": self.app_id,
                "web": "1",
                "channel": "dubox",
                "clienttype": "5", # Alterado de 0 para 5
                "jsToken": self.js_token,
                "dp-logid": self._get_dp_logid(),
                "dir": parent_dir,
                "num": "100", # Alinhado com a URL do usuário
                "page": str(page),
                "order": "name", # Alinhado com a URL do usuário
                "desc": "0",     # Alinhado com a URL do usuário
                "showempty": "0" # Adicionado
            }
            
            url_list = "https://www.terabox.com/api/list"
            try:
                res = self._request("GET", url_list, params=params)
                errno = res.get("errno")
                file_list = res.get("list", [])
                
                if errno == 0:
                    if not file_list:
                        return False
                        
                    for item in file_list:
                        if item.get("server_filename") == filename or item.get("path") == remote_path:
                            print(f"Sucesso: {filename} encontrado na página {page} do TeraBox.")
                            return True
                    
                    if len(file_list) < 100:
                        return False
                    
                    page += 1
                elif errno == -6:
                    print("Erro: Sessão (NDUS) expirada ou inválida.")
                    return False
                else:
                    print(f"Erro na API TeraBox (errno {errno}) ao listar página {page}.")
                    return False
            except Exception as e:
                print(f"Erro ao verificar existência no TeraBox: {e}")
                return False
        
        return False

    def _request(self, method, url, **kwargs):
        resp = self.session.request(method, url, **kwargs)
        try:
            res_json = resp.json()
            return res_json
        except Exception:
            print(f"Erro ao decodificar JSON em {url}. Status: {resp.status_code}")
            try:
                # Tenta printar o texto com encoding seguro
                safe_text = resp.text[:500].encode('ascii', 'ignore').decode('ascii')
                print(f"Resposta bruta: {safe_text}")
            except:
                print("Não foi possível exibir a resposta bruta.")
            raise Exception(f"Falha na comunicação com TeraBox (Status {resp.status_code})")

    def _get_md5(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _get_logid(self):
        import time
        import base64
        import random
        # Gera um logid similar ao capturado pelo usuário
        t = str(int(time.time() * 1000))
        r = str(random.random())
        return base64.b64encode(f"{t}{r}".encode()).decode()

    def upload_file(self, local_path, remote_path):
        file_size = os.path.getsize(local_path)
        file_md5 = self._get_md5(local_path)
        
        # 1. Precreate
        params = {
            "app_id": self.app_id,
            "web": "1",
            "channel": "dubox",
            "clienttype": "5", # Alterado de 0 para 5
            "jsToken": self.js_token,
            "dp-logid": self._get_dp_logid()
        }
        
        data = {
            "path": remote_path,
            "size": file_size,
            "isdir": 0,
            "block_list": json.dumps([file_md5]),
            "autoinit": 1
        }
        
        url_precreate = "https://www.terabox.com/api/precreate"
        res_json = self._request("POST", url_precreate, params=params, data=data)
        print(f"Resultado Precreate: {res_json}")
        
        if res_json.get("errno") != 0:
            raise Exception(f"Erro no precreate: {res_json}")
            
        uploadid = res_json.get("uploadid")
        
        # 2. Upload
        # Usando o host japonês identificado pelo usuário
        url_upload = "https://c-jp.terabox.com/rest/2.0/pcs/superfile2"
        up_params = {
            "method": "upload",
            "app_id": self.app_id,
            "channel": "dubox",
            "clienttype": "5", # Alterado de 0 para 5
            "web": "1",
            "logid": self._get_logid(),
            "path": remote_path,
            "uploadid": uploadid,
            "uploadsign": "0",
            "partseq": "0"
        }
        
        print(f"Iniciando envio real para: {url_upload}")
        try:
            with open(local_path, "rb") as f:
                files = {"file": f}
                res_up = self._request("POST", url_upload, params=up_params, files=files)
            
            if res_up.get("errno") is not None and res_up.get("errno") != 0:
                 raise Exception(f"Erro no upload: {res_up}")
            
            # Se não tem errno e tem md5, é sucesso no Superfile2
            if "md5" in res_up:
                print("Pedaço enviado com sucesso!")
            else:
                 raise Exception(f"Upload falhou ou resposta inesperada: {res_up}")
        except Exception as e:
            print(f"Falha de conexão com servidor de dados: {e}")
            raise e
        
        # 3. Create
        url_create = "https://www.terabox.com/api/create"
        create_params = {
            "app_id": self.app_id,
            "web": "1",
            "channel": "dubox",
            "clienttype": "5", # Alterado de 0 para 5
            "jsToken": self.js_token,
            "dp-logid": self._get_dp_logid()
        }
        create_data = {
            "path": remote_path,
            "size": file_size,
            "isdir": 0,
            "uploadid": uploadid,
            "block_list": json.dumps([file_md5])
        }
        
        final_json = self._request("POST", url_create, params=create_params, data=create_data)
        
        if final_json.get("errno") != 0:
            raise Exception(f"Erro no create: {final_json}")
            
        return final_json

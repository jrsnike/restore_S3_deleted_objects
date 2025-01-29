import boto3
import json
from datetime import datetime, timezone
from botocore.exceptions import BotoCoreError, ClientError

# Configurações iniciais
BUCKET_NAME = ""       # Informe o nome do bucket 
START_DATE = datetime.fromisoformat("2025-01-19T00:00:00+00:00")  # Informe a partir de qual data vai ser restaurado
MAX_BATCH_SIZE = 1000  # Número máximo de objetos por chamada de delete

# Cliente S3
s3_client = boto3.client("s3")

# Solicita ao usuário o prefixo (pasta)
PREFIX = input("Informe o prefixo (pasta) no bucket (deixe vazio para considerar o bucket inteiro): ")  # Informe a pasta a ser restaurada ou deixe em branco para o bucket completo

# Obtém os marcadores de exclusão
try:
    print(f"Obtendo marcadores de exclusão no bucket {BUCKET_NAME}...")

    params = {
        "Bucket": BUCKET_NAME
    }

    if PREFIX:
        params["Prefix"] = PREFIX

    delete_markers = []

    while True:
        response = s3_client.list_object_versions(**params)
        markers = response.get("DeleteMarkers", [])

        # Filtra os marcadores pelo LastModified
        for marker in markers:
            if marker["LastModified"].replace(tzinfo=timezone.utc) > START_DATE:
                delete_markers.append({
                    "Key": marker["Key"],
                    "VersionId": marker["VersionId"]
                })

        # Verifica se há mais páginas
        if response.get("IsTruncated"):
            params["KeyMarker"] = response.get("NextKeyMarker")
            params["VersionIdMarker"] = response.get("NextVersionIdMarker")
        else:
            break

except (BotoCoreError, ClientError) as error:
    print(f"Erro ao obter marcadores de exclusão: {error}")
    exit(1)

if not delete_markers:
    print(f"Nenhum marcador de exclusão encontrado após {START_DATE} para o prefixo '{PREFIX}'.")
    exit(0)

# Exibe o número total de marcadores de exclusão
total_markers = len(delete_markers)
print(f"Total de marcadores de exclusão encontrados: {total_markers}")

# Remove os marcadores de exclusão em lotes
print("Removendo marcadores de exclusão...")
batch = []
removed_count = 0

try:
    for marker in delete_markers:
        batch.append(marker)

        if len(batch) >= MAX_BATCH_SIZE:
            delete_json = {"Objects": batch}
            s3_client.delete_objects(Bucket=BUCKET_NAME, Delete=delete_json)

            removed_count += len(batch)
            percent_complete = (removed_count / total_markers) * 100
            print(f"\rProgresso: {percent_complete:.2f}% ({removed_count}/{total_markers}) concluído.", end="")

            batch.clear()

    # Se houver objetos restantes no lote, faça o delete final
    if batch:
        delete_json = {"Objects": batch}
        s3_client.delete_objects(Bucket=BUCKET_NAME, Delete=delete_json)

        removed_count += len(batch)
        percent_complete = (removed_count / total_markers) * 100
        print(f"Progresso: {percent_complete:.2f}% ({removed_count}/{total_markers}) concluído.")

    print("Restauro concluído!")

except (BotoCoreError, ClientError) as error:
    print(f"Erro ao deletar objetos: {error}")
    exit(1)


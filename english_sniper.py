import re
import sys
import os
import nltk
from nltk.stem import WordNetLemmatizer

# --- CONFIGURAÇÃO NLTK (Baixa o dicionário se não tiver) ---
try:
    nltk.data.find('corpora/wordnet.zip')
except LookupError:
    print("Downloading WordNet dictionary for English...")
    nltk.download('wordnet')
    nltk.download('omw-1.4')
# -----------------------------------------------------------

def gerar_guia_sniper(caminho_arquivo_entrada, nome_arquivo_saida="Guia_Sniper_EN.txt"):
    try:
        lemmatizer = WordNetLemmatizer()
    except Exception as e:
        print(f"Error loading lemmatizer: {e}")
        return

    try:
        with open(caminho_arquivo_entrada, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except FileNotFoundError:
        print("Error: File not found.")
        return

    print("Processing English subtitles and selecting the best candidates...")

    # Regex: Timestamp + Texto (Padrão SRT universal)
    padrao_bloco = r'(\d{2}:\d{2}:\d{2},\d{3}) --> \d{2}:\d{2}:\d{2},\d{3}\n([\s\S]*?)(?=\n\d+\n|\Z)'
    blocos = re.findall(padrao_bloco, conteudo)

    # Dicionário principal
    dados_palavras = {}
    contador_chegada = 0

    # Stopwords em Inglês (Palavras para ignorar)
    stopwords = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 
        'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 
        'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 
        'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 
        'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 
        'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 
        'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 
        'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 
        'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 
        'give', 'day', 'most', 'us', 'is', 'are', 'was', 'were', 'been',
        'has', 'had', 'does', 'did', 'very', 'really', 'should', 'might',
        'must', 'don', 've', 'll', 're', 'm', 'd', 's', 't', 'gon', 'na',
        'got', 'much', 'many', 'lot', 'etc', 'yeah', 'hey', 'oh', 'ok',
        'okay', 'yes', 'right', 'here', 'thing', 'things'
    }

# --- PROCESSAMENTO ---
    try:
        for tempo, texto_bruto in blocos:
            # Remove tags HTML e limpa para exibição
            texto_limpo_leitura = re.sub(r'<.*?>', '', texto_bruto).replace('\n', ' ').strip()
            
            # Limpa para análise (apenas letras a-z)
            texto_para_analise = re.sub(r'[^a-zA-Z\s-]', '', texto_bruto).lower()
            palavras_linha = texto_para_analise.split()

            for palavra in palavras_linha:
                if len(palavra) < 2: continue
                
                try:
                    # Lematização em Inglês (running -> run, cats -> cat)
                    lema = lemmatizer.lemmatize(palavra)
                    
                    if lema not in stopwords and palavra not in stopwords:
                        if lema not in dados_palavras:
                            contador_chegada += 1
                            dados_palavras[lema] = {
                                'lema': lema,
                                'id_chegada': contador_chegada, # ID cronológico
                                'time': tempo,
                                'freq': 1,
                                'example': texto_limpo_leitura
                            }
                        else:
                            dados_palavras[lema]['freq'] += 1
                except:
                    continue

        if not dados_palavras:
            print("No valid words found.")
            return
    except Exception as e:
        print(f"Error saving file: {e}")

    # --- SEPARAÇÃO E FILTRAGEM (A Lógica Sniper) ---
    todos_itens = list(dados_palavras.values())

    # LISTA 1: Top 30 Mais Frequentes (Alta Frequência)
    # Critério: Maior frequência primeiro
    lista_freq = [x for x in todos_itens if x['freq'] > 3]
    lista_freq.sort(key=lambda x: x['freq'], reverse=True)
    top_30_frequentes = lista_freq[:30]

    # LISTA 2: Top 50 Específicas (Frequência 2 ou 3)
    # Critério: Maior tamanho primeiro (palavras mais complexas/técnicas)
    lista_raras = [x for x in todos_itens if 2 <= x['freq'] <= 3]
    lista_raras.sort(key=lambda x: (-len(x['lema']), x['lema']))
    top_50_raras = lista_raras[:50]

    # LISTA 3: Top 50 Únicas (Frequência 1)
    # Critério: Maior tamanho primeiro
    lista_unicas = [x for x in todos_itens if x['freq'] == 1]
    lista_unicas.sort(key=lambda x: (-len(x['lema']), x['lema']))
    top_50_unicas = lista_unicas[:50]

    if os.path.exists(nome_arquivo_saida):
        print(f"\nWARNING: The file '{nome_arquivo_saida}' ALREADY EXISTS.")
        while True:
            resp = input("Do you want to [O]verwrite or create a [N]ew file? (O/N): ").strip().upper()
            
            if resp == 'O':
                print("-> Overwriting file...")
                break # Sai do loop e mantém o nome original
            
            elif resp == 'N':
                # Lógica para criar nome único (ex: arquivo_1.txt)
                base, ext = os.path.splitext(nome_arquivo_saida)
                contador = 1
                novo_nome = f"{base}_{contador}{ext}"
                
                # Procura o próximo número livre
                while os.path.exists(novo_nome):
                    contador += 1
                    novo_nome = f"{base}_{contador}{ext}"
                
                nome_arquivo_saida = novo_nome
                print(f"-> Creating a new file: {nome_arquivo_saida}")
                break
            else:
                print("Invalid option. Enter O or N.")

    # --- SALVAR RELATÓRIO ---
    print(f"Generating Sniper Guide in '{nome_arquivo_saida}'...")
    
    with open(nome_arquivo_saida, "w", encoding="utf-8") as f:
        f.write("="*130 + "\n")
        f.write(f"SNIPER STUDY GUIDE (ENGLISH): {caminho_arquivo_entrada}\n")
        f.write("Columns: FREQ (Frequency) | ID (Order of appearance) | TIME (Minute) | CONTEXT\n")
        f.write("="*130 + "\n\n")
        
        def escrever_tabela(titulo, lista, descricao):
            f.write("="*130 + "\n")
            f.write(f"{titulo} (Total listed: {len(lista)})\n")
            f.write(f"DESCRIPTION: {descricao}\n")
            f.write("="*130 + "\n")
            f.write(f"{'FREQ':<6} | {'WORD':<20} | {'ID':<5} | {'TIME':<12} | {'CONTEXT (REAL PHRASE)'}\n")
            f.write("-" * 130 + "\n")
            
            for item in lista:
                exemplo_curto = item['example'][:65] + "..." if len(item['example']) > 65 else item['example']
                f.write(f"{item['freq']:<6} | {item['lema']:<20} | #{item['id_chegada']:<4} | {item['time']:<12} | {exemplo_curto}\n")
            f.write("\n\n")

        escrever_tabela("TABLE 1: THE VITAL ONES (TOP 30 FREQUENCY)", top_30_frequentes, 
                        "The words that are repeated most often in the video. The basis for understanding.")
        
        escrever_tabela("TABELA 2: VOCABULÁRIO TÉCNICO (TOP 50 RARAS - 2 ou 3x)", top_50_raras, 
                        "Specific words ordered by SIZE (Complexity). The 'flavor' of the video.")
        
        escrever_tabela("TABELA 3: DETALHES DE OURO (TOP 50 ÚNICAS - 1x)", top_50_unicas, 
                        "Long, complex words that appeared only once. Fine details.")

    print("Success! The 3 elite lists have been generated.")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    try:
        nome_entrada = input("English SRT file: ").replace('"', '')
        nome_saida = "Sniper_EN_" + nome_entrada.replace(".srt", "") + ".txt"
        gerar_guia_sniper(nome_entrada, nome_saida)
    except Exception as e:
        print(f"Error: {e}")
    input("\nPress Enter to exit...")

import re
import sys
import os
import nltk
from nltk.stem import WordNetLemmatizer

# --- CONFIGURAÇÃO NLTK ---
try:
    nltk.data.find('corpora/wordnet.zip')
except LookupError:
    print("Downloading WordNet dictionary for English...")
    nltk.download('wordnet')
    nltk.download('omw-1.4')
# -------------------------

def gerar_guia_multiplo_en(caminho_arquivo_entrada, nome_arquivo_saida="Guia_Contexto_Multiplo_EN.txt"):
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

    print("Mapping multiple phrases to each word (English)...")

    # Regex padrão SRT para capturar tempo e texto
    padrao_bloco = r'(\d{2}:\d{2}:\d{2},\d{3}) --> \d{2}:\d{2}:\d{2},\d{3}\n([\s\S]*?)(?=\n\d+\n|\Z)'
    blocos = re.findall(padrao_bloco, conteudo)

    # Estrutura: lema -> { 'freq': 0, 'exemplos': [ {'tempo': t, 'texto': txt}, ... ] }
    dados_palavras = {}
    
    # Stopwords em Inglês
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
        'okay', 'yes', 'right', 'here', 'thing', 'things', 'hello', 'please',
        'thank', 'thanks', 'bye', 'hi'
    }

    # --- PROCESSAMENTO ---
    for tempo, texto_bruto in blocos:
        # Limpa para exibição (remove HTML)
        texto_limpo_leitura = re.sub(r'<.*?>', '', texto_bruto).replace('\n', ' ').strip()
        
        # Limpa para análise (apenas letras a-z)
        texto_para_analise = re.sub(r'[^a-zA-Z\s-]', '', texto_bruto).lower()
        palavras_linha = texto_para_analise.split()

        for palavra in palavras_linha:
            if len(palavra) < 2: continue
            
            try:
                # Lematização (Inglês)
                lema = lemmatizer.lemmatize(palavra)
                
                if lema not in stopwords and palavra not in stopwords:
                    if lema not in dados_palavras:
                        dados_palavras[lema] = {
                            'lema': lema,
                            'freq': 1,
                            'examples': [{'time': tempo, 'text': texto_limpo_leitura}]
                        }
                    else:
                        dados_palavras[lema]['freq'] += 1
                        # Lógica do "Máximo 5 frases"
                        lista_ex = dados_palavras[lema]['examples']
                        if len(lista_ex) < 5:
                            # Evita adicionar a exata mesma frase repetida no mesmo timestamp
                            if lista_ex[-1]['text'] != texto_limpo_leitura:
                                lista_ex.append({'time': tempo, 'text': texto_limpo_leitura})
            except:
                continue

    if not dados_palavras:
        print("No valid words found.")
        return

    # --- FILTRAGEM (As Duas Primeiras Tabelas) ---
    todos_itens = list(dados_palavras.values())

    # TABELA 1: Top 30 Frequência (Alta)
    lista_freq = [x for x in todos_itens if x['freq'] > 3]
    lista_freq.sort(key=lambda x: x['freq'], reverse=True)
    top_30_frequentes = lista_freq[:30]

    # TABELA 2: Top 50 Raras (2 a 3 vezes) - Ordenadas por Tamanho (Complexidade)
    lista_raras = [x for x in todos_itens if 2 <= x['freq'] <= 3]
    lista_raras.sort(key=lambda x: (-len(x['lema']), x['lema']))
    top_50_raras = lista_raras[:50]

    if os.path.exists(nome_arquivo_saida):
        print(f"\nWARNING: The file '{output_filename}' ALREADY EXISTS.")
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

    # --- SALVAR RELATÓRIO FORMATADO ---
    print(f"Generating Multiple Guide in '{nome_arquivo_saida}'...")
    
    try:
        with open(nome_arquivo_saida, "w", encoding="utf-8") as f:
            f.write("="*100 + "\n")
            f.write(f"EXPANDED STUDY GUIDE (ENGLISH - UP TO 5 SENTENCES): {caminho_arquivo_entrada}\n")
            f.write("="*100 + "\n\n")
            
            def escrever_bloco(titulo, lista, descricao):
                f.write("="*100 + "\n")
                f.write(f"{titulo}\n")
                f.write(f"DESCRIPTION: {descricao}\n")
                f.write("="*100 + "\n")
                
                for i, item in enumerate(lista, 1):
                    # Cabeçalho da Palavra
                    f.write(f"\n{i}. WORD: {item['lema'].upper()} (Total Frequency: {item['freq']})\n")
                    f.write("-" * 80 + "\n")
                    
                    # Lista de Frases (Até 5)
                    for j, ex in enumerate(item['examples'], 1):
                        frase = ex['text']
                        f.write(f"   {j}. [{ex['time']}] {frase}\n")
                f.write("\n\n")

            escrever_bloco("TABLE 1: THE VITAL ONES (TOP 30 FREQUENCY)", top_30_frequentes, 
                            "Very common words in English. Showing up to 5 variations in usage.")
            
            escrever_bloco("TABLE 2: TECHNICAL VOCABULARY (TOP 50 - 2 or 3 times)", top_50_raras, 
                            "Specific words ordered by size. All occurrences listed.")

        print("Success! File generated with example lists.")
    except Exception as e:
        print(f"Error saving file: {e}")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    try:
        nome_entrada = input("English SRT file: ").replace('"', '')
        nome_saida = "Master_EN_" + os.path.splitext(os.path.basename(nome_entrada))[0] + ".txt"
        gerar_guia_multiplo_en(nome_entrada, nome_saida)
    except Exception as e:
        print(f"Error: {e}")
    input("\nPress Enter to exit...")

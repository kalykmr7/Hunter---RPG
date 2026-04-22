import os

# Nome do arquivo de saída
output_file = "contexto_projeto.txt"
# Pastas que você quer ignorar
ignore_dirs = {'.git', '__pycache__', 'venv', '.env'}

with open(output_file, "w", encoding="utf-8") as outfile:
    for root, dirs, files in os.walk("."):
        # Remove pastas ignoradas da busca
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file.endswith(".py") and file != "unificar.py":
                filepath = os.path.join(root, file)
                outfile.write(f"\n--- ARQUIVO: {filepath} ---\n")
                with open(filepath, "r", encoding="utf-8") as infile:
                    outfile.write(infile.read())
                outfile.write("\n")

print(f"Sucesso! Tudo foi salvo em: {output_file}")
import os

# Caminho base dos arquivos CSS dentro do pacote
CSS_DIR = os.path.join(
	os.path.dirname(__file__),
	"..", "static", "enap_designsystem", "blocks"
)
BUNDLE_FILE = os.path.join(CSS_DIR, "bundle.css")

def generate_bundle():
	included_files = []

	with open(BUNDLE_FILE, "w", encoding="utf-8") as bundle:
		for dirpath, _, filenames in os.walk(CSS_DIR):
			for fname in filenames:
				if fname.endswith(".css") and fname != "bundle.css":
					path = os.path.join(dirpath, fname)
					rel_path = os.path.relpath(path, CSS_DIR)

					with open(path, "r", encoding="utf-8") as f:
						bundle.write(f"/* === {rel_path} === */\n")
						bundle.write(f.read())
						bundle.write("\n\n")

					included_files.append(rel_path)

	print()  # linha em branco no terminal

	if included_files:
		print(f"✅ Gerado: {BUNDLE_FILE}")
		print(f"Arquivos incluídos no bundle ({len(included_files)}):")
		for f in included_files:
			print(f" - {f}")
	else:
		print(f"⚠️  Nenhum CSS incluído! Verifique se há arquivos .css dentro de {CSS_DIR}")
		print("🔍 Dica: Crie arquivos .css nos componentes ou revise a estrutura de pastas.")

if __name__ == "__main__":
	generate_bundle()

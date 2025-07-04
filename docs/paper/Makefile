# Makefile for StarCraft II Mathematical Model Paper

# Variables
TEX = xelatex
TEXFLAGS = -interaction=nonstopmode -halt-on-error
MAIN = report
PDF = $(MAIN).pdf
TEX_FILE = $(MAIN).tex

# Build targets
.PHONY: all clean view version backup help

# Default target
all: $(PDF)

# Build PDF from TeX
$(PDF): $(TEX_FILE)
	@echo "Building PDF with XeLaTeX..."
	$(TEX) $(TEXFLAGS) $(TEX_FILE)
	@echo "First pass complete, running again for references..."
	$(TEX) $(TEXFLAGS) $(TEX_FILE)
	@echo "PDF built successfully: $(PDF)"

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	rm -f *.aux *.log *.out *.toc *.synctex.gz *.fdb_latexmk *.fls *.nav *.snm *.vrb
	@echo "Clean complete"

# View PDF
view: $(PDF)
	@echo "Opening PDF..."
	@if command -v open >/dev/null 2>&1; then \
		open $(PDF); \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open $(PDF); \
	else \
		echo "Please open $(PDF) manually"; \
	fi

# Create versioned backup
version: $(PDF)
	@echo "Creating versioned backup..."
	@VERSION=$$(date +%Y%m%d_%H%M%S); \
	mkdir -p versions/backup_$$VERSION; \
	cp $(TEX_FILE) versions/backup_$$VERSION/; \
	cp $(PDF) versions/backup_$$VERSION/; \
	echo "Backup created in versions/backup_$$VERSION/"

# Create a new version
new-version:
	@read -p "Enter version number (e.g., v2.1): " VERSION; \
	mkdir -p versions/$$VERSION; \
	cp $(TEX_FILE) versions/$$VERSION/; \
	cp $(PDF) versions/$$VERSION/ 2>/dev/null || true; \
	echo "New version $$VERSION created in versions/$$VERSION/"

# Help message
help:
	@echo "StarCraft II Mathematical Model Paper - Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make          - Build the PDF"
	@echo "  make clean    - Remove temporary files"
	@echo "  make view     - Build and open the PDF"
	@echo "  make version  - Create timestamped backup"
	@echo "  make new-version - Create a new named version"
	@echo "  make help     - Show this help message"
	@echo ""
	@echo "Requirements:"
	@echo "  - XeLaTeX with Chinese font support"
	@echo "  - fontspec and xeCJK packages"
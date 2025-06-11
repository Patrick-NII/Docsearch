import PyPDF2
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DocumentLoader:
    """Chargeur de documents PDF et TXT"""
    
    def __init__(self):
        self.supported_extensions = {'.pdf', '.txt'}
    
    def load_documents(self, source_dir: str = "./source") -> list:
        """
        Charge tous les documents supportés d'un répertoire
        
        Args:
            source_dir: Chemin vers le répertoire source
            
        Returns:
            Liste des documents chargés
        """
        source_path = Path(source_dir)
        if not source_path.exists():
            logger.warning(f"Le répertoire {source_dir} n'existe pas")
            return []
        
        documents = []
        
        for file_path in source_path.iterdir():
            if file_path.suffix.lower() in self.supported_extensions:
                try:
                    if file_path.suffix.lower() == '.pdf':
                        doc = self.load_pdf(file_path)
                    else:
                        doc = self.load_txt(file_path)
                    
                    documents.append(doc)
                    logger.info(f"Document chargé: {file_path.name}")
                    
                except Exception as e:
                    logger.error(f"Erreur lors du chargement de {file_path}: {e}")
        
        return documents
    
    def load_pdf(self, file_path: Path) -> dict:
        """
        Charge un fichier PDF et extrait le texte
        
        Args:
            file_path: Chemin vers le fichier PDF
            
        Returns:
            Dictionnaire contenant le texte et les métadonnées
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                
                metadata = {
                    "source": str(file_path),
                    "filename": file_path.name,
                    "file_type": "pdf",
                    "total_pages": len(pdf_reader.pages),
                    "file_size": file_path.stat().st_size
                }
                
                logger.info(f"PDF chargé: {file_path.name} ({len(pdf_reader.pages)} pages)")
                
                return {
                    "text": text,
                    "metadata": metadata
                }
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement du PDF {file_path}: {e}")
            raise
    
    def load_txt(self, file_path: Path) -> dict:
        """
        Charge un fichier texte
        
        Args:
            file_path: Chemin vers le fichier texte
            
        Returns:
            Dictionnaire contenant le texte et les métadonnées
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            metadata = {
                "source": str(file_path),
                "filename": file_path.name,
                "file_type": "txt",
                "file_size": file_path.stat().st_size
            }
            
            logger.info(f"Fichier texte chargé: {file_path.name}")
            
            return {
                "text": text,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du fichier texte {file_path}: {e}")
            raise 